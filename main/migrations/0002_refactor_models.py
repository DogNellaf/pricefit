import datetime

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0001_initial'),
    ]

    operations = [
        # TargetGroup: add verbose_name_plural and new fields
        migrations.AlterModelOptions(
            name='targetgroup',
            options={
                'verbose_name': 'Целевая группа',
                'verbose_name_plural': 'Целевые группы',
            },
        ),
        migrations.AlterField(
            model_name='targetgroup',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Название'),
        ),
        migrations.AddField(
            model_name='targetgroup',
            name='description',
            field=models.TextField(blank=True, verbose_name='Описание'),
        ),
        migrations.AddField(
            model_name='targetgroup',
            name='min_budget',
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=12,
                null=True, verbose_name='Минимальный бюджет',
            ),
        ),
        migrations.AddField(
            model_name='targetgroup',
            name='max_budget',
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=12,
                null=True, verbose_name='Максимальный бюджет',
            ),
        ),
        # Request: fix frozen default, convert prices to Decimal, add verbose names
        migrations.AlterModelOptions(
            name='request',
            options={
                'verbose_name': 'Запрос на формирование рекомендаций',
                'verbose_name_plural': 'Запросы на формирование рекомендаций',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AlterField(
            model_name='request',
            name='created_at',
            field=models.DateField(default=datetime.date.today, verbose_name='Создан'),
        ),
        migrations.AlterField(
            model_name='request',
            name='min_price',
            field=models.DecimalField(
                decimal_places=2, max_digits=12, verbose_name='Минимальная цена'
            ),
        ),
        migrations.AlterField(
            model_name='request',
            name='max_price',
            field=models.DecimalField(
                decimal_places=2, max_digits=12, verbose_name='Максимальная цена'
            ),
        ),
        migrations.AlterField(
            model_name='request',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name='Пользователь',
            ),
        ),
        # Analysis: rename koef -> coefficient, fix typo in verbose_name, add related_name
        migrations.RenameField(
            model_name='analysis',
            old_name='koef',
            new_name='coefficient',
        ),
        migrations.AlterField(
            model_name='analysis',
            name='coefficient',
            field=models.FloatField(verbose_name='Коэффициент корреляции'),
        ),
        migrations.AlterField(
            model_name='analysis',
            name='target_group',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='main.targetgroup',
                verbose_name='Целевая группа',
            ),
        ),
        migrations.AlterField(
            model_name='analysis',
            name='request',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='analyses',
                to='main.request',
                verbose_name='Запрос',
            ),
        ),
        migrations.AlterModelOptions(
            name='analysis',
            options={
                'verbose_name': 'Рекомендация',
                'verbose_name_plural': 'Рекомендации',
                'ordering': ['-coefficient'],
            },
        ),
    ]
