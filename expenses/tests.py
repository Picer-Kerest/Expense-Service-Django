import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Expense


class TestExpenseSearch(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', email='testuser@test.com', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.expense1 = Expense.objects.create(
            amount=100, date='2022-01-01', description='Expense 1', category='Category 1', owner=self.user)
        self.expense2 = Expense.objects.create(
            amount=200, date='2022-01-02', description='Expense 2', category='Category 2', owner=self.user)
        self.expense3 = Expense.objects.create(
            amount=300, date='2022-01-03', description='Expense 3', category='Category 3', owner=self.user)

    def test_expense_search_by_amount(self):
        search_data = {'searchText': '100'}
        response = self.client.post(reverse('search-expense'), json.dumps(search_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.expense1.description)

    def test_expense_search_by_date(self):
        search_data = {'searchText': '2022-01-02'}
        response = self.client.post(reverse('search-expense'), json.dumps(search_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.expense2.description)

    def test_expense_search_by_description(self):
        search_data = {'searchText': 'expense 3'}
        response = self.client.post(reverse('search-expense'), json.dumps(search_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.expense3.description)

    def test_expense_search_by_category(self):
        search_data = {'searchText': 'Category 2'}
        response = self.client.post(reverse('search-expense'), json.dumps(search_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.expense2.description)

    def test_expense_search_with_no_results(self):
        search_data = {'searchText': 'Category 4'}
        response = self.client.post(reverse('search-expense'), json.dumps(search_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), '[]')

