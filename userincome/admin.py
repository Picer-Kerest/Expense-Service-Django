from django.contrib import admin
from .models import Source, Income


class IncomeAdmin(admin.ModelAdmin):
    list_display = ('amount', 'description', 'owner', 'source', 'date', )
    search_field = ('description', 'owner', 'source', )


admin.site.register(Source)
admin.site.register(Income, IncomeAdmin)

