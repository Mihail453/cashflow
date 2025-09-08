from django.shortcuts import render, get_object_or_404, redirect
from .models import CashFlow, Status, Type, Category, SubCategory
from .forms import CashFlowForm, UserRegisterForm
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

# Регистрация
def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # сразу авторизуем
            return redirect("index")
    else:
        form = UserRegisterForm()
    return render(request, "register.html", {"form": form})

# API для AJAX
@login_required
def api_categories(request):
    type_id = request.GET.get('type_id')
    categories = Category.objects.filter(user=request.user)
    if type_id:
        categories = categories.filter(type_id=type_id)
    return JsonResponse(list(categories.values('id', 'name')), safe=False)

@login_required
def api_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = SubCategory.objects.filter(user=request.user)
    if category_id:
        subcategories = subcategories.filter(category_id=category_id)
    return JsonResponse(list(subcategories.values('id', 'name')), safe=False)

# Управление категориями
@login_required
def category_management(request):
    categories = Category.objects.filter(user=request.user).select_related('type').prefetch_related('subcategories')
    types = Type.objects.filter(user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_category':
            category_name = request.POST.get('category_name')
            type_id = request.POST.get('type')
            subcategory_name = request.POST.get('subcategory_name')
            
            if category_name and type_id:
                category = Category.objects.create(
                    name=category_name, 
                    type_id=type_id,
                    user=request.user
                )
                
                if subcategory_name:
                    SubCategory.objects.create(
                        name=subcategory_name,
                        category=category,
                        user=request.user
                    )
                    messages.success(request, f'Категория "{category_name}" и подкатегория "{subcategory_name}" добавлены')
                else:
                    messages.success(request, f'Категория "{category_name}" добавлена')
            
            return redirect('category_management')
        
        elif action == 'add_subcategory':
            category_id = request.POST.get('category_id')
            subcategory_name = request.POST.get('subcategory_name')
            
            if category_id and subcategory_name:
                category = get_object_or_404(Category, id=category_id, user=request.user)
                SubCategory.objects.create(
                    name=subcategory_name,
                    category=category,
                    user=request.user
                )
                messages.success(request, f'Подкатегория "{subcategory_name}" добавлена в "{category.name}"')
            
            return redirect('category_management')
        
        elif action == 'edit_category':
            category_id = request.POST.get('category_id')
            category_name = request.POST.get('category_name')
            type_id = request.POST.get('type')
            
            if category_id and category_name and type_id:
                category = get_object_or_404(Category, id=category_id, user=request.user)
                category.name = category_name
                category.type_id = type_id
                category.save()
                messages.success(request, 'Категория обновлена')
            
            return redirect('category_management')
        
        elif action == 'edit_subcategory':
            subcategory_id = request.POST.get('subcategory_id')
            subcategory_name = request.POST.get('subcategory_name')
            
            if subcategory_id and subcategory_name:
                subcategory = get_object_or_404(SubCategory, id=subcategory_id, user=request.user)
                subcategory.name = subcategory_name
                subcategory.save()
                messages.success(request, 'Подкатегория обновлена')
            
            return redirect('category_management')
        
        elif action == 'delete_category':
            category_id = request.POST.get('category_id')
            category = get_object_or_404(Category, id=category_id, user=request.user)
            category_name = category.name
            category.delete()
            messages.success(request, f'Категория "{category_name}" удалена')
            return redirect('category_management')
        
        elif action == 'delete_subcategory':
            subcategory_id = request.POST.get('subcategory_id')
            subcategory = get_object_or_404(SubCategory, id=subcategory_id, user=request.user)
            subcategory_name = subcategory.name
            subcategory.delete()
            messages.success(request, f'Подкатегория "{subcategory_name}" удалена')
            return redirect('category_management')
    
    return render(request, 'category_management.html', {
        'categories': categories,
        'types': types
    })

# Управление типами
@login_required
def type_management(request):
    types = Type.objects.filter(user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            name = request.POST.get('name')
            if name:
                Type.objects.create(name=name, user=request.user)
                messages.success(request, 'Тип добавлен')
            return redirect('type_management')
        
        elif action == 'edit':
            type_id = request.POST.get('type_id')
            type_obj = get_object_or_404(Type, id=type_id, user=request.user)
            type_obj.name = request.POST.get('name')
            type_obj.save()
            messages.success(request, 'Тип обновлен')
            return redirect('type_management')
            
        elif action == 'delete':
            type_id = request.POST.get('type_id')
            type_obj = get_object_or_404(Type, id=type_id, user=request.user)
            type_obj.delete()
            messages.success(request, 'Тип удален')
            return redirect('type_management')
    
    return render(request, 'type_management.html', {'types': types})

# Управление статусами
@login_required
def status_management(request):
    statuses = Status.objects.filter(user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            name = request.POST.get('name')
            if name:
                Status.objects.create(name=name, user=request.user)
                messages.success(request, 'Статус добавлен')
            return redirect('status_management')
            
        elif action == 'edit':
            status_id = request.POST.get('status_id')
            status_obj = get_object_or_404(Status, id=status_id, user=request.user)
            status_obj.name = request.POST.get('name')
            status_obj.save()
            messages.success(request, 'Статус обновлен')
            return redirect('status_management')
            
        elif action == 'delete':
            status_id = request.POST.get('status_id')
            status_obj = get_object_or_404(Status, id=status_id, user=request.user)
            status_obj.delete()
            messages.success(request, 'Статус удален')
            return redirect('status_management')
    
    return render(request, 'status_management.html', {'statuses': statuses})

# Главная страница
@login_required
def index(request):
    cashflows = CashFlow.objects.filter(user=request.user).order_by("-date")

    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    status_id = request.GET.get("status")
    type_id = request.GET.get("type")
    category_id = request.GET.get("category")

    if start_date:
        cashflows = cashflows.filter(date__gte=start_date)
    if end_date:
        cashflows = cashflows.filter(date__lte=end_date)
    if status_id:
        cashflows = cashflows.filter(status_id=status_id)
    if type_id:
        cashflows = cashflows.filter(type_id=type_id)
    if category_id:
        cashflows = cashflows.filter(category_id=category_id)

    context = {
        "cashflows": cashflows,
        "statuses": Status.objects.filter(user=request.user),
        "types": Type.objects.filter(user=request.user),
        "categories": Category.objects.filter(user=request.user),
    }
    return render(request, "index.html", context)

# CRUD для ДДС
@login_required
def add_cashflow(request):
    if request.method == "POST":
        form = CashFlowForm(request.POST, user=request.user)
        if form.is_valid():
            cashflow = form.save(commit=False)
            cashflow.user = request.user
            cashflow.save()
            return redirect("index")
    else:
        form = CashFlowForm(user=request.user)
    return render(request, "form.html", {"form": form, "title": "Добавить запись"})

@login_required
def edit_cashflow(request, pk):
    obj = get_object_or_404(CashFlow, pk=pk, user=request.user)
    if request.method == "POST":
        form = CashFlowForm(request.POST, instance=obj, user=request.user)
        if form.is_valid():
            cashflow = form.save(commit=False)
            cashflow.user = request.user
            cashflow.save()
            return redirect("index")
    else:
        form = CashFlowForm(instance=obj, user=request.user)
    return render(request, "form.html", {"form": form, "title": "Редактировать запись"})

@login_required
def delete_cashflow(request, pk):
    obj = get_object_or_404(CashFlow, pk=pk, user=request.user)
    if request.method == "POST":
        obj.delete()
        return redirect("index")
    return render(request, "confirm_delete.html", {"object": obj})
