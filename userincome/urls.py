from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name='income'),
    path('add-income/', views.add_income, name='add-income'),
    path('edit-income/<int:income_id>/', views.edit_income, name='edit-income'),
    path('income-delete/<int:income_id>/', views.income_delete, name='income-delete'),
    path('search-income/', csrf_exempt(views.search_incomes), name='search-income'),
    path('income-category-summary/', csrf_exempt(views.income_category_summary), name='income-category-summary'),
    path('stats-income/', views.stats_view, name='stats-income'),
    path('export-csv-income/', views.export_csv, name='export-csv-income'),
    path('export-excel-income/', views.export_excel, name='export-excel-income'),
]

