import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import RequestForm, TargetGroupForm
from .models import Analysis, Request, TargetGroup
from .services import compute_coefficient, generate_recommendations


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class TargetGroupModelTest(TestCase):
    def setUp(self):
        self.group = TargetGroup.objects.create(
            title='Молодёжь',
            description='18–25 лет',
            min_budget=Decimal('100.00'),
            max_budget=Decimal('500.00'),
        )

    def test_str(self):
        self.assertEqual(str(self.group), 'Молодёжь')

    def test_verbose_name(self):
        self.assertEqual(TargetGroup._meta.verbose_name, 'Целевая группа')

    def test_verbose_name_plural(self):
        self.assertEqual(TargetGroup._meta.verbose_name_plural, 'Целевые группы')

    def test_description_blank_by_default(self):
        group = TargetGroup.objects.create(title='Пустая')
        self.assertEqual(group.description, '')

    def test_budget_nullable(self):
        group = TargetGroup.objects.create(title='Без бюджета')
        self.assertIsNone(group.min_budget)
        self.assertIsNone(group.max_budget)


class RequestModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('alice', password='pass123!')
        self.req = Request.objects.create(
            user=self.user,
            min_price=Decimal('100.00'),
            max_price=Decimal('300.00'),
        )

    def test_str_contains_username(self):
        self.assertIn('alice', str(self.req))

    def test_str_contains_pk(self):
        self.assertIn(str(self.req.pk), str(self.req))

    def test_created_at_defaults_to_today(self):
        self.assertEqual(self.req.created_at, datetime.date.today())

    def test_verbose_name(self):
        self.assertEqual(
            Request._meta.verbose_name, 'Запрос на формирование рекомендаций'
        )

    def test_verbose_name_plural(self):
        self.assertEqual(
            Request._meta.verbose_name_plural, 'Запросы на формирование рекомендаций'
        )

    def test_ordering_newest_first(self):
        older = Request.objects.create(
            user=self.user,
            min_price=Decimal('10'),
            max_price=Decimal('20'),
            created_at=datetime.date(2020, 1, 1),
        )
        qs = list(Request.objects.filter(user=self.user))
        self.assertGreater(qs[0].created_at, older.created_at)


class AnalysisModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('bob', password='pass123!')
        self.group = TargetGroup.objects.create(
            title='Бизнес', min_budget=Decimal('200'), max_budget=Decimal('600')
        )
        self.req = Request.objects.create(
            user=self.user, min_price=Decimal('100'), max_price=Decimal('400')
        )
        self.analysis = Analysis.objects.create(
            target_group=self.group, request=self.req, coefficient=0.75
        )

    def test_str_contains_coefficient(self):
        self.assertIn('0.75', str(self.analysis))

    def test_str_contains_group_name(self):
        self.assertIn('Бизнес', str(self.analysis))

    def test_verbose_name(self):
        self.assertEqual(Analysis._meta.verbose_name, 'Рекомендация')

    def test_verbose_name_plural(self):
        self.assertEqual(Analysis._meta.verbose_name_plural, 'Рекомендации')

    def test_related_name_analyses(self):
        self.assertEqual(self.req.analyses.count(), 1)


# ---------------------------------------------------------------------------
# Service tests
# ---------------------------------------------------------------------------

class ComputeCoefficientTest(TestCase):
    def test_identical_ranges_return_one(self):
        c = compute_coefficient(Decimal('100'), Decimal('300'), Decimal('100'), Decimal('300'))
        self.assertAlmostEqual(c, 1.0)

    def test_no_overlap_returns_zero(self):
        c = compute_coefficient(Decimal('100'), Decimal('200'), Decimal('300'), Decimal('400'))
        self.assertAlmostEqual(c, 0.0)

    def test_partial_overlap(self):
        # intersection [200,300]=100, union [100,400]=300
        c = compute_coefficient(Decimal('100'), Decimal('300'), Decimal('200'), Decimal('400'))
        self.assertAlmostEqual(c, 100 / 300)

    def test_request_inside_group_range(self):
        # intersection [150,250]=100, union [100,300]=200
        c = compute_coefficient(Decimal('150'), Decimal('250'), Decimal('100'), Decimal('300'))
        self.assertAlmostEqual(c, 100 / 200)

    def test_group_inside_request_range(self):
        # intersection [200,300]=100, union [100,400]=300
        c = compute_coefficient(Decimal('100'), Decimal('400'), Decimal('200'), Decimal('300'))
        self.assertAlmostEqual(c, 100 / 300)

    def test_none_min_budget_returns_zero(self):
        c = compute_coefficient(Decimal('100'), Decimal('300'), None, Decimal('200'))
        self.assertAlmostEqual(c, 0.0)

    def test_none_max_budget_returns_zero(self):
        c = compute_coefficient(Decimal('100'), Decimal('300'), Decimal('100'), None)
        self.assertAlmostEqual(c, 0.0)

    def test_touching_ranges_return_zero(self):
        c = compute_coefficient(Decimal('100'), Decimal('200'), Decimal('200'), Decimal('300'))
        self.assertAlmostEqual(c, 0.0)


class GenerateRecommendationsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('carol', password='pass123!')
        self.g1 = TargetGroup.objects.create(
            title='G1', min_budget=Decimal('50'), max_budget=Decimal('200')
        )
        self.g2 = TargetGroup.objects.create(
            title='G2', min_budget=Decimal('500'), max_budget=Decimal('800')
        )
        self.g_no_budget = TargetGroup.objects.create(title='NoBudget')
        self.req = Request.objects.create(
            user=self.user, min_price=Decimal('100'), max_price=Decimal('300')
        )

    def test_creates_one_analysis_per_group(self):
        generate_recommendations(self.req)
        self.assertEqual(Analysis.objects.filter(request=self.req).count(), 3)

    def test_refreshes_on_second_call(self):
        generate_recommendations(self.req)
        generate_recommendations(self.req)
        self.assertEqual(Analysis.objects.filter(request=self.req).count(), 3)

    def test_group_without_budget_gets_zero_coefficient(self):
        generate_recommendations(self.req)
        a = Analysis.objects.get(request=self.req, target_group=self.g_no_budget)
        self.assertAlmostEqual(a.coefficient, 0.0)

    def test_overlapping_group_has_positive_coefficient(self):
        generate_recommendations(self.req)
        a = Analysis.objects.get(request=self.req, target_group=self.g1)
        self.assertGreater(a.coefficient, 0.0)

    def test_non_overlapping_group_has_zero_coefficient(self):
        generate_recommendations(self.req)
        a = Analysis.objects.get(request=self.req, target_group=self.g2)
        self.assertAlmostEqual(a.coefficient, 0.0)


# ---------------------------------------------------------------------------
# Form tests
# ---------------------------------------------------------------------------

class RequestFormTest(TestCase):
    def test_valid_form(self):
        form = RequestForm(data={'min_price': '100.00', 'max_price': '300.00'})
        self.assertTrue(form.is_valid())

    def test_equal_prices_is_valid(self):
        form = RequestForm(data={'min_price': '100.00', 'max_price': '100.00'})
        self.assertTrue(form.is_valid())

    def test_max_less_than_min_is_invalid(self):
        form = RequestForm(data={'min_price': '300.00', 'max_price': '100.00'})
        self.assertFalse(form.is_valid())
        self.assertIn('max_price', form.errors)

    def test_negative_min_price_is_invalid(self):
        form = RequestForm(data={'min_price': '-10.00', 'max_price': '100.00'})
        self.assertFalse(form.is_valid())
        self.assertIn('min_price', form.errors)

    def test_negative_max_price_is_invalid(self):
        form = RequestForm(data={'min_price': '10.00', 'max_price': '-5.00'})
        self.assertFalse(form.is_valid())

    def test_missing_fields_is_invalid(self):
        form = RequestForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('min_price', form.errors)
        self.assertIn('max_price', form.errors)


class TargetGroupFormTest(TestCase):
    def test_valid_minimal(self):
        form = TargetGroupForm(data={'title': 'Test', 'description': ''})
        self.assertTrue(form.is_valid())

    def test_valid_with_budget(self):
        form = TargetGroupForm(
            data={'title': 'Test', 'description': '', 'min_budget': '100', 'max_budget': '500'}
        )
        self.assertTrue(form.is_valid())

    def test_max_budget_less_than_min_is_invalid(self):
        form = TargetGroupForm(
            data={'title': 'Test', 'description': '', 'min_budget': '500', 'max_budget': '100'}
        )
        self.assertFalse(form.is_valid())
        self.assertIn('max_budget', form.errors)

    def test_equal_budgets_is_valid(self):
        form = TargetGroupForm(
            data={'title': 'Test', 'description': '', 'min_budget': '100', 'max_budget': '100'}
        )
        self.assertTrue(form.is_valid())

    def test_missing_title_is_invalid(self):
        form = TargetGroupForm(data={'title': '', 'description': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)


# ---------------------------------------------------------------------------
# View tests
# ---------------------------------------------------------------------------

class HomeViewTest(TestCase):
    def test_anonymous_get(self):
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'main/home.html')

    def test_authenticated_context(self):
        user = User.objects.create_user('dave', password='pass123!')
        self.client.login(username='dave', password='pass123!')
        resp = self.client.get(reverse('home'))
        self.assertIn('total_requests', resp.context)
        self.assertIn('total_groups', resp.context)


class RegisterViewTest(TestCase):
    def test_get(self):
        resp = self.client.get(reverse('register'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'registration/register.html')

    def test_successful_registration(self):
        resp = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'Str0ng!Pass#99',
            'password2': 'Str0ng!Pass#99',
        })
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertRedirects(resp, '/')

    def test_authenticated_user_is_redirected(self):
        User.objects.create_user('existing', password='pass123!')
        self.client.login(username='existing', password='pass123!')
        resp = self.client.get(reverse('register'))
        self.assertRedirects(resp, '/')


class RequestViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('eve', password='pass123!')
        self.other = User.objects.create_user('frank', password='pass123!')
        self.req = Request.objects.create(
            user=self.user, min_price=Decimal('100'), max_price=Decimal('200')
        )

    def test_list_requires_login(self):
        resp = self.client.get(reverse('request_list'))
        self.assertRedirects(resp, f'/accounts/login/?next={reverse("request_list")}')

    def test_list_shows_only_own_requests(self):
        Request.objects.create(
            user=self.other, min_price=Decimal('10'), max_price=Decimal('20')
        )
        self.client.login(username='eve', password='pass123!')
        resp = self.client.get(reverse('request_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(list(resp.context['requests']), [self.req])

    def test_create_get(self):
        self.client.login(username='eve', password='pass123!')
        resp = self.client.get(reverse('request_create'))
        self.assertEqual(resp.status_code, 200)

    def test_create_post_valid(self):
        self.client.login(username='eve', password='pass123!')
        resp = self.client.post(reverse('request_create'), {'min_price': '50', 'max_price': '150'})
        new_req = Request.objects.filter(user=self.user, min_price=Decimal('50')).first()
        self.assertIsNotNone(new_req)
        self.assertRedirects(resp, reverse('request_detail', args=[new_req.pk]))

    def test_create_post_invalid_returns_form(self):
        self.client.login(username='eve', password='pass123!')
        resp = self.client.post(reverse('request_create'), {'min_price': '200', 'max_price': '50'})
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'max_price', 'Максимальная цена должна быть не меньше минимальной.')

    def test_detail_owner_can_view(self):
        self.client.login(username='eve', password='pass123!')
        resp = self.client.get(reverse('request_detail', args=[self.req.pk]))
        self.assertEqual(resp.status_code, 200)

    def test_detail_other_user_gets_403(self):
        self.client.login(username='frank', password='pass123!')
        resp = self.client.get(reverse('request_detail', args=[self.req.pk]))
        self.assertEqual(resp.status_code, 403)

    def test_detail_staff_can_view_any(self):
        staff = User.objects.create_user('staff', password='pass123!', is_staff=True)
        self.client.login(username='staff', password='pass123!')
        resp = self.client.get(reverse('request_detail', args=[self.req.pk]))
        self.assertEqual(resp.status_code, 200)

    def test_edit_get(self):
        self.client.login(username='eve', password='pass123!')
        resp = self.client.get(reverse('request_edit', args=[self.req.pk]))
        self.assertEqual(resp.status_code, 200)

    def test_edit_post(self):
        self.client.login(username='eve', password='pass123!')
        self.client.post(
            reverse('request_edit', args=[self.req.pk]),
            {'min_price': '150', 'max_price': '350'},
        )
        self.req.refresh_from_db()
        self.assertEqual(self.req.min_price, Decimal('150'))

    def test_edit_other_user_gets_403(self):
        self.client.login(username='frank', password='pass123!')
        resp = self.client.post(
            reverse('request_edit', args=[self.req.pk]),
            {'min_price': '1', 'max_price': '2'},
        )
        self.assertEqual(resp.status_code, 403)

    def test_delete_removes_request(self):
        self.client.login(username='eve', password='pass123!')
        pk = self.req.pk
        self.client.post(reverse('request_delete', args=[pk]))
        self.assertFalse(Request.objects.filter(pk=pk).exists())

    def test_delete_requires_post(self):
        self.client.login(username='eve', password='pass123!')
        resp = self.client.get(reverse('request_delete', args=[self.req.pk]))
        self.assertEqual(resp.status_code, 405)

    def test_delete_other_user_gets_403(self):
        self.client.login(username='frank', password='pass123!')
        resp = self.client.post(reverse('request_delete', args=[self.req.pk]))
        self.assertEqual(resp.status_code, 403)

    def test_analyze_generates_recommendations(self):
        TargetGroup.objects.create(title='G', min_budget=Decimal('50'), max_budget=Decimal('250'))
        self.client.login(username='eve', password='pass123!')
        resp = self.client.post(reverse('request_analyze', args=[self.req.pk]))
        self.assertRedirects(resp, reverse('request_detail', args=[self.req.pk]))
        self.assertEqual(Analysis.objects.filter(request=self.req).count(), 1)

    def test_analyze_warns_when_no_groups(self):
        self.client.login(username='eve', password='pass123!')
        resp = self.client.post(reverse('request_analyze', args=[self.req.pk]))
        messages_out = [str(m) for m in resp.wsgi_request._messages]
        self.assertTrue(any('группы' in m.lower() for m in messages_out))


class TargetGroupViewsTest(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('gstaff', password='pass123!', is_staff=True)
        self.regular = User.objects.create_user('greg', password='pass123!')
        self.group = TargetGroup.objects.create(
            title='Existing Group', min_budget=Decimal('100'), max_budget=Decimal('400')
        )

    def test_list_is_public(self):
        resp = self.client.get(reverse('target_group_list'))
        self.assertEqual(resp.status_code, 200)

    def test_create_get_requires_staff(self):
        self.client.login(username='greg', password='pass123!')
        resp = self.client.get(reverse('target_group_create'))
        self.assertEqual(resp.status_code, 403)

    def test_create_get_staff(self):
        self.client.login(username='gstaff', password='pass123!')
        resp = self.client.get(reverse('target_group_create'))
        self.assertEqual(resp.status_code, 200)

    def test_create_post_staff(self):
        self.client.login(username='gstaff', password='pass123!')
        self.client.post(
            reverse('target_group_create'),
            {'title': 'New Group', 'description': ''},
        )
        self.assertTrue(TargetGroup.objects.filter(title='New Group').exists())

    def test_edit_get_staff(self):
        self.client.login(username='gstaff', password='pass123!')
        resp = self.client.get(reverse('target_group_edit', args=[self.group.pk]))
        self.assertEqual(resp.status_code, 200)

    def test_edit_post_staff(self):
        self.client.login(username='gstaff', password='pass123!')
        self.client.post(
            reverse('target_group_edit', args=[self.group.pk]),
            {'title': 'Renamed', 'description': ''},
        )
        self.group.refresh_from_db()
        self.assertEqual(self.group.title, 'Renamed')

    def test_edit_requires_staff(self):
        self.client.login(username='greg', password='pass123!')
        resp = self.client.post(
            reverse('target_group_edit', args=[self.group.pk]),
            {'title': 'Hacked', 'description': ''},
        )
        self.assertEqual(resp.status_code, 403)

    def test_delete_staff(self):
        self.client.login(username='gstaff', password='pass123!')
        pk = self.group.pk
        self.client.post(reverse('target_group_delete', args=[pk]))
        self.assertFalse(TargetGroup.objects.filter(pk=pk).exists())

    def test_delete_requires_staff(self):
        self.client.login(username='greg', password='pass123!')
        resp = self.client.post(reverse('target_group_delete', args=[self.group.pk]))
        self.assertEqual(resp.status_code, 403)
        self.assertTrue(TargetGroup.objects.filter(pk=self.group.pk).exists())

    def test_delete_requires_post(self):
        self.client.login(username='gstaff', password='pass123!')
        resp = self.client.get(reverse('target_group_delete', args=[self.group.pk]))
        self.assertEqual(resp.status_code, 405)
