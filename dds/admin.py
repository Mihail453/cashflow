from django.contrib import admin
from .models import Status, Type, Category, SubCategory, CashFlow

class UserFilteredAdmin(admin.ModelAdmin):
    """Базовый класс для фильтрации объектов по пользователю"""
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # при создании нового объекта
            obj.user = request.user
        obj.save()


@admin.register(Status)
class StatusAdmin(UserFilteredAdmin):
    list_display = ("id", "name", "user")
    search_fields = ("name",)
    list_filter = ("user",)

@admin.register(Category)
class CategoryAdmin(UserFilteredAdmin):
    list_display = ("id", "name", "type", "user")
    list_filter = ("type", "user")
    search_fields = ("name",)

@admin.register(SubCategory)
class SubCategoryAdmin(UserFilteredAdmin):
    list_display = ("id", "name", "category", "user")
    list_filter = ("category", "user")
    search_fields = ("name",)

@admin.register(CashFlow)
class CashFlowAdmin(UserFilteredAdmin):
    list_display = ("date", "status", "type", "category", "subcategory", "amount", "comment", "user")
    list_filter = ("status", "type", "category", "subcategory", "date", "user")
    search_fields = ("comment",)
    ordering = ("-date",)

@admin.register(Type)
class TypeAdmin(UserFilteredAdmin):
    list_display = ("id", "name", "user")
    search_fields = ("name",)
    list_filter = ("user",)
