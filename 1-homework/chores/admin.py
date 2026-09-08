from django.contrib import admin

from .models import Category, Chore, Household, HouseholdMember


admin.site.register(Household)
admin.site.register(HouseholdMember)
admin.site.register(Category)
admin.site.register(Chore)
