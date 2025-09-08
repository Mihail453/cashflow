from django import forms
from .models import CashFlow, Category, SubCategory, Status, Type
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "password1": forms.PasswordInput(attrs={"class": "form-control"}),
            "password2": forms.PasswordInput(attrs={"class": "form-control"}),
        }

class CashFlowForm(forms.ModelForm):
    """Форма для создания/редактирования записи ДДС"""

    class Meta:
        model = CashFlow
        fields = ["status", "type", "category", "subcategory", "amount", "comment"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "type": forms.Select(attrs={"class": "form-select", "onchange": "updateCategories()"}),
            "category": forms.Select(attrs={"class": "form-select", "onchange": "updateSubcategories()"}),
            "subcategory": forms.Select(attrs={"class": "form-select"}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # <- получаем пользователя
        super().__init__(*args, **kwargs)

        # Фильтруем справочники по пользователю
        if user:
            self.fields['status'].queryset = Status.objects.filter(user=user)
            self.fields['type'].queryset = Type.objects.filter(user=user)
            self.fields['category'].queryset = Category.objects.filter(user=user)
            self.fields['subcategory'].queryset = SubCategory.objects.filter(user=user)

        # Плейсхолдеры
        self.fields['status'].empty_label = "Выберите статус"
        self.fields['type'].empty_label = "Выберите тип"
        self.fields['category'].empty_label = "Выберите категорию"
        self.fields['subcategory'].empty_label = "Выберите подкатегорию (необязательно)"

        # Для редактирования — оставляем текущие связи
        if self.instance and self.instance.pk:
            self.fields['category'].queryset = Category.objects.filter(type=self.instance.type, user=user)
            self.fields['subcategory'].queryset = SubCategory.objects.filter(category=self.instance.category, user=user)
        else:
            # Для новой записи — пустые queryset, пока не выбран тип/категория
            self.fields['category'].queryset = Category.objects.none()
            self.fields['subcategory'].queryset = SubCategory.objects.none()

        # Поддержка динамического фильтра через AJAX
        if 'type' in self.data:
            try:
                type_id = int(self.data.get('type'))
                self.fields['category'].queryset = Category.objects.filter(type_id=type_id, user=user)
            except (ValueError, TypeError):
                pass

        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = SubCategory.objects.filter(category_id=category_id, user=user)
            except (ValueError, TypeError):
                pass

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        subcategory = cleaned_data.get("subcategory")
        type_ = cleaned_data.get("type")

        if not category:
            self.add_error("category", "Это поле обязательно.")
        if not type_:
            self.add_error("type", "Это поле обязательно.")

        if subcategory and category and subcategory.category != category:
            self.add_error("subcategory", "Подкатегория не соответствует выбранной категории.")

        if category and type_ and category.type != type_:
            self.add_error("category", "Категория не соответствует выбранному типу.")
