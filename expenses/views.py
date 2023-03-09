import csv
import datetime
import json
import xlwt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from .models import Category, Expense
from userpreferences.models import UserPreference
from django.http import HttpResponse
from reportlab.pdfgen import canvas


def search_expenses(request):
    """
    __startswith - позволяет фильтровать объекты по началу значения поля.
    Таким образом можно фильтровать значения, которые начинаются с определённой подстроки
    Метод startswith() чувствителен к регистру, для поиска строк без учета регистра можете использовать
    метод istartswith().

    __icontains является оператором фильтрации,
    который используется для выполнения поиска внутри значения поля, не учитывая регистр символов.
    """
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        # request.body тип json
        # .get Возвращает значение из словаря по указанному ключу.
        expenses = \
            Expense.objects.filter(amount__istartswith=search_str, owner=request.user) | \
            Expense.objects.filter(date__istartswith=search_str, owner=request.user) | \
            Expense.objects.filter(description__icontains=search_str, owner=request.user) | \
            Expense.objects.filter(category__icontains=search_str, owner=request.user)
        data = expenses.values()
        # values возвращает объект QuerySet, где каждый объект модели представлен в виде словаря
        # list(data) для конвертации в массив из QuerySet
        # safe=False Ответ JSON в Django установлен save=True по умолчанию,
        # это заставляет JSON принимать тип данных {Dictionaries} и ничего больше.
        # Итак, в этот момент любые данные, отправленные вопреки {Dictionaries}, фактически вызовут ошибки.
        # Таким образом, установка параметра False влияет на получение JSON любого типа данных Python.
        # False потому что это позволяет JSON принимать как {Dictionaries}, так и другие типы.
        # JsonResponse для передачи в виде JSON
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'expenses': expenses,
        'page_obj': page_obj,
    }

    if UserPreference.objects.filter(user=request.user).exists():
        currency = UserPreference.objects.get(user=request.user).currency
        context['currency'] = currency
    return render(request, 'expenses/index.html', context)


@login_required(login_url='/authentication/login')
def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)
    elif request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        # crude_category = request.POST['category']
        category = request.POST['category']
        expense_data = request.POST['expense_data']
        if not amount:
            messages.error(request, 'The amount is empty')
            return render(request, 'expenses/add_expense.html', context)
        if not description:
            messages.error(request, 'The description is empty')
            return render(request, 'expenses/add_expense.html', context)
        Expense.objects.create(
            amount=amount,
            date=expense_data,
            description=description,
            owner=request.user,
            category=category)
        messages.success(request, 'The expense was successfully saved')
        return redirect('expenses')
    return render(request, 'expenses/add_expense.html', context)


@login_required(login_url='/authentication/login')
def edit_expense(request, expense_id):
    expense = Expense.objects.get(pk=expense_id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'categories': categories,
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit-expense.html', context)
    elif request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        # crude_category = request.POST['category']
        category = request.POST['category']
        expense_data = request.POST['expense_data']
        if not amount:
            messages.error(request, 'The amount is empty')
            return render(request, 'expenses/edit-expense.html', context)
        if not description:
            messages.error(request, 'The description is empty')
            return render(request, 'expenses/edit-expense.html', context)

        expense.amount = amount
        expense.date = expense_data
        expense.description = description
        expense.category = category
        expense.owner = request.user
        expense.save()
        messages.success(request, 'The expense was successfully updated')
        return redirect('expenses')


def expense_delete(request, expense_id):
    expense = Expense.objects.get(pk=expense_id)
    expense.delete()
    messages.success(request, 'The expense was successfully removed')
    return redirect('expenses')


def expense_category_summary(request):
    today = datetime.date.today()
    six_months_ago = today - datetime.timedelta(days=182)
    # __gte больше или равно
    expenses = Expense.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=today)
    category_list = list(set(map(lambda expense: expense.category, expenses)))
    # Берём список расходов expenses и проходимся по каждому элементу с помощью анонимной функции
    # map возращает итератор, который мы конвертируем в множество для уникальных значений
    # далее конвертируем в список для удобного использования

    def get_expense_category_amount(category):
        amount = 0
        filter_query = expenses.filter(category=category)
        for item in filter_query:
            amount += item.amount
        return amount

    final_dct = {}
    # for expense in expenses:
    for category in category_list:
        final_dct[category] = get_expense_category_amount(category)
    return JsonResponse({'expense_category_data': final_dct}, safe=False)


def stats_view(request):
    return render(request, 'expenses/stats.html')


def export_csv(request):
    """
    объект HttpResponse используется для отправки CSV-файла в качестве ответа на запрос.
    Тип содержимого "text/csv" указывает браузеру клиента, что ответ содержит данные в формате CSV
    """
    response = HttpResponse(content_type='text/csv')
    current_date = datetime.datetime.now().date()
    formatted_date = current_date.strftime('%d %B %Y')
    response['Content-Disposition'] = f'attachment; filename=Expense {formatted_date}.csv'
    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])
    expenses = Expense.objects.filter(owner=request.user)
    for expense in expenses:
        writer.writerow([expense.amount, expense.description, expense.category, expense.date])
    return response


def export_excel(request):
    """
    Создаём response в виде ms-excel
    Задаём название файла и его настройки.
    Кодировка
    Задаём название страницы
    Количество строк 0
    Задаём стиль шрифта для названий заголовков
    Задаём столбцы
    Записываем столбцы.
    Параметры ws.write:
    row - номер строки
    col - номер столбца
    label - текст
    style - стиль, в данном случае шрифт
    Далее задаём новый стиль шрифта, чтобы всё не было жирным
    rows. Один элемент - кортеж со значениями.
    Заполняем таблицу, сохраняем.
    """
    response = HttpResponse(content_type='application/ms-excel')
    current_date = datetime.datetime.now().date()
    formatted_date = current_date.strftime('%d %B %Y')
    response['Content-Disposition'] = f'attachment; filename=Expense {formatted_date}.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Amount', 'Description', 'Category', 'Date']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()
    rows = Expense.objects.filter(owner=request.user).values_list('amount', 'description', 'category', 'date')
    # Вызывается метод values_list, который извлекает значения указанных полей
    # из каждого объекта в QuerySet и возвращает их в виде кортежа.
    # rows будет содержать QuerySet с кортежами
    for row in rows:
        row_num += 1
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    wb.save(response)
    return response

