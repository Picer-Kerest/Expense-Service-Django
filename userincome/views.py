import csv
import datetime
import json
import xlwt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from .models import Source, Income
from userpreferences.models import UserPreference


def search_incomes(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        incomes = \
            Income.objects.filter(amount__istartswith=search_str, owner=request.user) | \
            Income.objects.filter(date__istartswith=search_str, owner=request.user) | \
            Income.objects.filter(description__icontains=search_str, owner=request.user) | \
            Income.objects.filter(source__icontains=search_str, owner=request.user)
        data = incomes.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    incomes = Income.objects.filter(owner=request.user)
    paginator = Paginator(incomes, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'incomes': incomes,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'income/index.html', context)


@login_required(login_url='/authentication/login')
def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)
    elif request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        source = request.POST['source']
        income_data = request.POST['income_data']
        if not amount:
            messages.error(request, 'The amount is empty')
            return render(request, 'income/add_income.html', context)
        if not description:
            messages.error(request, 'The description is empty')
            return render(request, 'income/add_income.html', context)
        Income.objects.create(
            amount=amount,
            date=income_data,
            description=description,
            owner=request.user,
            source=source)
        messages.success(request, 'The income was successfully saved')
        return redirect('income')
    return render(request, 'income/add_income.html', context)


@login_required(login_url='/authentication/login')
def edit_income(request, income_id):
    income = Income.objects.get(pk=income_id)
    sources = Source.objects.all()
    context = {
        'income': income,
        'sources': sources,
    }
    if request.method == 'GET':
        return render(request, 'income/edit-income.html', context)
    elif request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        source = request.POST['source']
        income_data = request.POST['income_data']
        if not amount:
            messages.error(request, 'The amount is empty')
            return render(request, 'income/edit-income.html', context)
        if not description:
            messages.error(request, 'The description is empty')
            return render(request, 'income/edit-income.html', context)

        income.amount = amount
        income.date = income_data
        income.description = description
        income.owner = request.user
        income.source = source
        income.save()
        messages.success(request, 'The income was successfully updated')
        return redirect('income')


@login_required(login_url='/authentication/login')
def income_delete(request, income_id):
    income = Income.objects.get(pk=income_id)
    income.delete()
    messages.success(request, 'The income was successfully removed')
    return redirect('income')


@login_required(login_url='/authentication/login')
def income_category_summary(request):
    today = datetime.date.today()
    six_months_ago = today - datetime.timedelta(days=182)
    incomes = Income.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=today)
    source_list = list(set(map(lambda income: income.source, incomes)))

    def get_income_source_amount(source):
        amount = 0
        filter_query = incomes.filter(source=source)
        for item in filter_query:
            amount += item.amount
        return amount

    final_dct = {}
    for source in source_list:
        final_dct[source] = get_income_source_amount(source)
    return JsonResponse({'income_source_data': final_dct}, safe=False)


@login_required(login_url='/authentication/login')
def stats_view(request):
    return render(request, 'income/stats.html')


@login_required(login_url='/authentication/login')
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    current_date = datetime.datetime.now().date()
    formatted_date = current_date.strftime('%d %B %Y')
    response['Content-Disposition'] = f'attachment; filename=Income {formatted_date}.csv'
    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Source', 'Date'])
    incomes = Income.objects.filter(owner=request.user)
    for income in incomes:
        writer.writerow([income.amount, income.description, income.source, income.date])
    return response


@login_required(login_url='/authentication/login')
def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    current_date = datetime.datetime.now().date()
    formatted_date = current_date.strftime('%d %B %Y')
    response['Content-Disposition'] = f'attachment; filename=Expense {formatted_date}.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Incomes')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Amount', 'Description', 'Source', 'Date']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()
    rows = Income.objects.filter(owner=request.user).values_list('amount', 'description', 'source', 'date')
    for row in rows:
        row_num += 1
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    wb.save(response)
    return response
