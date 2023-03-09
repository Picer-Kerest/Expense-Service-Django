from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Source, Income
from userpreferences.models import UserPreference
import json


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
    paginator = Paginator(incomes, 10)
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


def income_delete(request, income_id):
    income = Income.objects.get(pk=income_id)
    income.delete()
    messages.success(request, 'The income was successfully removed')
    return redirect('income')

