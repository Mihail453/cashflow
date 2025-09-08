from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib import admin

admin.site.site_header = "Управление Денежными потоками"  # Заголовок сверху
admin.site.site_title = "Денежные потоки"                 # Название в браузерной вкладке
admin.site.index_title = "Панель администратора"  


class Status(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"
        unique_together = ("user", "name")

    def __str__(self):
        return self.name


class Type(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Тип"
        verbose_name_plural = "Типы"
        unique_together = ("user", "name")

    def __str__(self):
        return self.name


class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.ForeignKey(Type, on_delete=models.CASCADE, related_name="categories")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        unique_together = ("user", "name", "type")

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")

    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"
        unique_together = ("user", "name", "category")

    def __str__(self):
        return self.name


class CashFlow(models.Model):
    """Запись движения денежных средств"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cashflows")
    date = models.DateField(auto_now_add=False, auto_now=True)
    status = models.ForeignKey(Status, on_delete=models.PROTECT, verbose_name="Статус")
    type = models.ForeignKey(Type, on_delete=models.PROTECT, verbose_name='Тип')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Категория')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.PROTECT, verbose_name='Подкатегория')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Сумма')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"

    def clean(self):
        if self.subcategory.category != self.category:
            raise ValidationError("Подкатегория не соответствует выбранной категории.")
        if self.category.type != self.type:
            raise ValidationError("Категория не соответствует выбранному типу.")

    def __str__(self):
        return f"{self.date} | {self.type} | {self.category} | {self.amount} ₽"
