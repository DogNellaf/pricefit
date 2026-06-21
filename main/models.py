import datetime

from django.contrib.auth.models import User
from django.db import models


class TargetGroup(models.Model):
    title = models.CharField('Название', max_length=255)
    description = models.TextField('Описание', blank=True)
    min_budget = models.DecimalField(
        'Минимальный бюджет', max_digits=12, decimal_places=2, null=True, blank=True
    )
    max_budget = models.DecimalField(
        'Максимальный бюджет', max_digits=12, decimal_places=2, null=True, blank=True
    )

    class Meta:
        verbose_name = 'Целевая группа'
        verbose_name_plural = 'Целевые группы'

    def __str__(self):
        return self.title


class Request(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    created_at = models.DateField('Создан', default=datetime.date.today)
    min_price = models.DecimalField('Минимальная цена', max_digits=12, decimal_places=2)
    max_price = models.DecimalField('Максимальная цена', max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Запрос на формирование рекомендаций'
        verbose_name_plural = 'Запросы на формирование рекомендаций'
        ordering = ['-created_at']

    def __str__(self):
        return f'Запрос #{self.pk} от {self.user} ({self.created_at})'


class Analysis(models.Model):
    target_group = models.ForeignKey(
        TargetGroup, on_delete=models.CASCADE, verbose_name='Целевая группа'
    )
    request = models.ForeignKey(
        Request, on_delete=models.CASCADE, verbose_name='Запрос', related_name='analyses'
    )
    coefficient = models.FloatField('Коэффициент корреляции')

    class Meta:
        verbose_name = 'Рекомендация'
        verbose_name_plural = 'Рекомендации'
        ordering = ['-coefficient']

    def __str__(self):
        return f'{self.target_group} — {self.coefficient:.2f}'
