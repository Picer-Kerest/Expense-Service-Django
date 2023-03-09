from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse


class LoginViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_login_page(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login.html')

    def test_login_success(self):
        data = {
            'username': 'testuser',
            'password': 'testpass'
        }
        response = self.client.post(self.login_url, data)
        self.assertRedirects(response, reverse('expenses'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_invalid_credentials(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, data)
        self.assertTemplateUsed(response, 'authentication/login.html')
        self.assertContains(response, 'Invalid credentials, try again')

    def test_login_missing_fields(self):
        data = {
            'username': '',
            'password': ''
        }
        response = self.client.post(self.login_url, data)
        self.assertTemplateUsed(response, 'authentication/login.html')
        self.assertContains(response, 'Please fill all fields')

