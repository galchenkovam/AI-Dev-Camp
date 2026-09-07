from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Category, Chore, Household


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")


class HouseholdForm(forms.ModelForm):
    class Meta:
        model = Household
        fields = ("name",)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "color", "icon")


class ChoreForm(forms.ModelForm):
    class Meta:
        model = Chore
        fields = (
            "title",
            "description",
            "category",
            "due_date",
            "priority",
            "estimated_minutes",
            "recurrence",
            "points",
            "status",
            "assignment_mode",
            "assigned_to",
        )
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, household, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = household.categories.all()
        self.fields["assigned_to"].queryset = User.objects.filter(household_memberships__household=household).distinct()
