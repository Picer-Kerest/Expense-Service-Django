import json
import threading
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages, auth
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_generator


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is invalid'}, status=400)
        # JsonResponse - то, что будет возвращено, если сделать запрос через postman
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'Sorry, this email already exists'}, status=409)
        return JsonResponse({'email_valid': True})


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            # isalnum метод строк, который проверяет, содержит ли строка только буквы и цифры
            return JsonResponse({'username_error': 'Username should only contain alphanumeric characters'}, status=400)
        # JsonResponse - то, что будет возвращено, если сделать запрос через postman
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'Sorry, this user already exists'}, status=409)
        return JsonResponse({'username_valid': True})


class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        context = {
            'fieldValues': request.POST
        }
        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, 'The password is too short')
                    return render(request, 'authentication/register.html', context)

                if len(email) == 0:
                    messages.error(request, 'Enter email')
                    return render(request, 'authentication/register.html', context)

                if len(username) == 0:
                    messages.error(request, 'Enter username')
                    return render(request, 'authentication/register.html', context)

                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                domain = get_current_site(request).domain
                link = reverse('activate', kwargs={
                    'uidb64': uidb64,
                    'token': token_generator.make_token(user)
                })
                email_subject = 'Activate your account'
                activate_url = 'http://' + domain + link
                email_body = f'Hi, {user.username}. Please use this link to verify your account\n{activate_url}'
                # Отправляем письмо на активацию аккаунта
                email = EmailMessage(
                    email_subject,
                    email_body,
                    'ailerdiskincsio@gmail.com',
                    [email],
                )
                # email.send(fail_silently=False)
                EmailThread(email).start()
                # fail_silently=False - если будет исключение, то всё упадёт
                messages.success(request, 'Account successfully created')
                return render(request, 'authentication/register.html', context)
        return render(request, 'authentication/register.html')


class VerificationView(View):
    def get(self, request, uidb64, token):
        """
        Проверяем соответствует ли ссылка пользователю, и если да, то даём право доступа
        """
        # Параметры, переданные в запросе
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            if not token_generator.check_token(user, token):
                """
                Проверяем, соответствует ли токен, предоставленный пользователем, 
                токену, хранящемуся в базе данных для этого пользователя. 
                Если токены не совпадают, значит пользователь не может быть авторизован, 
                и он будет перенаправлен на страницу входа
                """
                messages.error(request, 'Invalid account activation data')
                return redirect('login')
            if user.is_active:
                messages.success(request, 'Account already activated')
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request, 'Account successfully activated')
            return redirect('login')
        except Exception as ex:
            messages.info(request, f'Something went wrong..\nYou have an exception: {ex}')
            return redirect('login')


class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        context = {
            'fieldValues': request.POST
        }
        if username and password:
            user = auth.authenticate(username=username, password=password)
            if user:
                # Если is_active = false, то пользователь не проходит authenticate
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, f'Welcome, {user.username}, you are logged in.')
                    return redirect('expenses')
                messages.error(request, 'Account is not active, please check your email')
                return render(request, 'authentication/login.html')
            messages.error(request, 'Invalid credentials, try again')
            return render(request, 'authentication/login.html', context)
        messages.error(request, 'Please fill all fields')
        return render(request, 'authentication/login.html', context)


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')


class ResetEmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is invalid'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_valid': True})
        else:
            return JsonResponse({'email_error': 'There is no user with such an email'}, status=550)


class ResetPasswordView(View):
    def get(self, request):
        return render(request, 'authentication/reset-password.html')

    def post(self, request):
        # email гарантированно существует, потому что происходит валидация
        # следовательно пользователь с таким email гарантированно существует
        email = request.POST['email']
        user = User.objects.get(email=email)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        domain = get_current_site(request).domain
        link = reverse('set-new-password', kwargs={
            'uidb64': uidb64,
            'token': token_generator.make_token(user)
        })
        email_subject = 'Password Reset'
        reset_url = 'http://' + domain + link
        email_body = f'Hi, {user.username}. Please use this link to reset your password\n{reset_url}'
        # Отправляем письмо
        email = EmailMessage(
            email_subject,
            email_body,
            'ailerdiskincsio@gmail.com',
            [email],
        )
        # email.send(fail_silently=False)
        EmailThread(email).start()
        messages.success(request, 'We have sent you an email to reset your password')
        return render(request, 'authentication/reset-password.html')


class CompletePasswordResetView(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.error(request, 'The password recovery link is used or wrong, generate a new one')
                return render(request, 'authentication/reset-password.html')
            return render(request, 'authentication/set-new-password.html', context)
        except Exception as ex:
            messages.info(request, f'Something went wrong..\nYou have an exception: {ex}')
            return render(request, 'authentication/set-new-password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, "Password didn't match")
            return render(request, 'authentication/set-new-password.html', context)

        if len(password) < 6:
            messages.error(request, 'Password is too short')
            return render(request, 'authentication/set-new-password.html', context)
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password successfully reset')
            return redirect('login')
        except Exception as ex:
            messages.error(request, f'Something went wrong..\nYou have an exception: {ex}')
            return render(request, 'authentication/set-new-password.html', context)

