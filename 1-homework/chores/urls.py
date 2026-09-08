from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("profile/password/", views.password_change, name="password-change"),
    path("households/create/", views.create_household, name="household-create"),
    path("households/<int:household_id>/", views.household_detail, name="household-detail"),
    path("households/<int:household_id>/members/create/", views.create_household_user, name="household-user-create"),
    path("households/<int:household_id>/categories/create/", views.create_category, name="category-create"),
    path("households/<int:household_id>/chores/", views.chore_list, name="chore-list"),
    path("households/<int:household_id>/calendar/", views.chore_calendar, name="chore-calendar"),
    path("households/<int:household_id>/chores/create/", views.chore_create, name="chore-create"),
    path("households/<int:household_id>/chores/<int:chore_id>/", views.chore_detail, name="chore-detail"),
    path("households/<int:household_id>/chores/<int:chore_id>/edit/", views.chore_edit, name="chore-edit"),
    path("households/<int:household_id>/chores/<int:chore_id>/delete/", views.chore_delete, name="chore-delete"),
    path("households/<int:household_id>/chores/<int:chore_id>/claim/", views.chore_claim, name="chore-claim"),
    path("households/<int:household_id>/chores/<int:chore_id>/complete/", views.chore_complete, name="chore-complete"),
    path("households/join/<uuid:invite_token>/", views.join_household, name="household-join"),
]
