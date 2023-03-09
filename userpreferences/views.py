from django.contrib import messages
from django.shortcuts import render
import os
import json
from django.conf import settings
from .models import UserPreference


def index(request):
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')
    """
    Функция os.path.join() принимает один или более аргументов, 
    каждый из которых представляет собой часть пути к файлу или директории, 
    и возвращает строку, которая содержит объединенный путь к файлу.
    BASE_DIR - то место, где находится manage.py
    Первый аргумент - это базовая директория проекта, а второй аргумент - это имя файла "currencies.json".
    """
    currency_data = []
    with open(file_path, 'r') as file:
        data = json.load(file)
        # data = dict
        for key, value in data.items():
            currency_data.append({
                'name': key,
                'value': value})
    #         name & value потому что таковы атрибуты в html тэга option

    exists = UserPreference.objects.filter(user=request.user).exists()
    # Проверка на то, есть ли у данного пользователя установленные предпочтения или нет
    user_preferences = None
    if exists:
        user_preferences = UserPreference.objects.get(user=request.user)
        # request.user - вернёт экземпляр авторизованного пользователя
    context = {
        'currencies': currency_data,
        'user_preferences': user_preferences
    }
    if request.method == 'GET':
        return render(request, 'preferences/index.html', context)
    elif request.method == 'POST':
        currency = request.POST['currency']
        # currency example: USD - United States Dollar
        # Забираем значение из select
        if exists:
            user_preferences.currency = currency
            user_preferences.save()
        else:
            UserPreference.objects.create(user=request.user, currency=currency)
        messages.success(request, 'Changes saved')
        return render(request, 'preferences/index.html', context)

