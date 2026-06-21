from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import RequestForm, TargetGroupForm
from .models import Analysis, Request, TargetGroup
from .services import generate_recommendations


def home(request):
    context = {}
    if request.user.is_authenticated:
        context['recent_requests'] = Request.objects.filter(user=request.user)[:5]
        context['total_requests'] = Request.objects.filter(user=request.user).count()
        context['total_groups'] = TargetGroup.objects.count()
    return render(request, 'main/home.html', context)


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Аккаунт успешно создан.')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


# --- Requests ---

@login_required
def request_list(request):
    user_requests = Request.objects.filter(user=request.user)
    return render(request, 'main/request_list.html', {'requests': user_requests})


@login_required
def request_create(request):
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, 'Запрос создан.')
            return redirect('request_detail', pk=obj.pk)
    else:
        form = RequestForm()
    return render(request, 'main/request_form.html', {'form': form, 'title': 'Новый запрос'})


@login_required
def request_detail(request, pk):
    req = get_object_or_404(Request, pk=pk)
    if req.user != request.user and not request.user.is_staff:
        raise PermissionDenied
    analyses = req.analyses.select_related('target_group').order_by('-coefficient')
    return render(request, 'main/request_detail.html', {'req': req, 'analyses': analyses})


@login_required
def request_edit(request, pk):
    req = get_object_or_404(Request, pk=pk)
    if req.user != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        form = RequestForm(request.POST, instance=req)
        if form.is_valid():
            form.save()
            messages.success(request, 'Запрос обновлён.')
            return redirect('request_detail', pk=req.pk)
    else:
        form = RequestForm(instance=req)
    return render(request, 'main/request_form.html', {'form': form, 'title': 'Редактировать запрос', 'req': req})


@login_required
@require_POST
def request_delete(request, pk):
    req = get_object_or_404(Request, pk=pk)
    if req.user != request.user:
        raise PermissionDenied
    req.delete()
    messages.success(request, 'Запрос удалён.')
    return redirect('request_list')


@login_required
@require_POST
def request_analyze(request, pk):
    req = get_object_or_404(Request, pk=pk)
    if req.user != request.user and not request.user.is_staff:
        raise PermissionDenied
    if not TargetGroup.objects.exists():
        messages.warning(request, 'Целевые группы не найдены. Добавьте группы перед анализом.')
        return redirect('request_detail', pk=req.pk)
    generate_recommendations(req)
    messages.success(request, 'Анализ выполнен.')
    return redirect('request_detail', pk=req.pk)


# --- Target Groups ---

def target_group_list(request):
    groups = TargetGroup.objects.all()
    return render(request, 'main/target_group_list.html', {'groups': groups})


@login_required
def target_group_create(request):
    if not request.user.is_staff:
        raise PermissionDenied
    if request.method == 'POST':
        form = TargetGroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Группа создана.')
            return redirect('target_group_list')
    else:
        form = TargetGroupForm()
    return render(
        request,
        'main/target_group_form.html',
        {'form': form, 'title': 'Новая целевая группа'},
    )


@login_required
def target_group_edit(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied
    group = get_object_or_404(TargetGroup, pk=pk)
    if request.method == 'POST':
        form = TargetGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Группа обновлена.')
            return redirect('target_group_list')
    else:
        form = TargetGroupForm(instance=group)
    return render(
        request,
        'main/target_group_form.html',
        {'form': form, 'title': 'Редактировать группу', 'group': group},
    )


@login_required
@require_POST
def target_group_delete(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied
    group = get_object_or_404(TargetGroup, pk=pk)
    group.delete()
    messages.success(request, 'Группа удалена.')
    return redirect('target_group_list')
