from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name='expenses'),
    path('add-expense/', views.add_expense, name='add-expense'),
    path('edit-expense/<int:expense_id>/', views.edit_expense, name='edit-expense'),
    path('expense-delete/<int:expense_id>/', views.expense_delete, name='expense-delete'),
    path('search-expense/', csrf_exempt(views.search_expenses), name='search-expense'),
    path('expense-category-summary/', csrf_exempt(views.expense_category_summary), name='expense-category-summary'),
    path('stats/', views.stats_view, name='stats'),
    path('export-csv/', views.export_csv, name='export-csv'),
    path('export-excel/', views.export_excel, name='export-excel'),
]

