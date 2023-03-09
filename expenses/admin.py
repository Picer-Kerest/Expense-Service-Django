from .models import Expense, Category
from django.contrib import admin


class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('amount', 'description', 'owner', 'category', 'date', )
    search_field = ('description', 'owner', 'category', )
    # list_per_page = 10


admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Category)
