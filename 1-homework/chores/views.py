import calendar
import secrets
import string
from datetime import date, timedelta

from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db.models import Prefetch
from django.utils import timezone
from django.http import Http404
from django.shortcuts import redirect, render

from .forms import CategoryForm, ChoreForm, HouseholdForm, HouseholdUserForm, ProfileForm, RegistrationForm
from .models import Category, Chore, Household, HouseholdMember, create_default_categories
from .scheduling import next_due_date


def register(request):
	if request.user.is_authenticated:
		return redirect("home")

	form = RegistrationForm(request.POST or None)
	if form.is_valid():
		user = form.save()
		login(request, user)
		return redirect("home")
	return render(request, "registration/register.html", {"form": form})


@login_required
def home(request):
	today = timezone.localdate()
	recent_cutoff = timezone.now() - timedelta(days=7)
	due_chores = Chore.objects.select_related("category", "assigned_to").filter(
		completed_at__isnull=True,
		due_date__isnull=False,
		due_date__lte=today,
	).order_by("due_date", "priority", "title")
	recently_completed = Chore.objects.select_related("category", "completed_by").filter(
		completed_at__gte=recent_cutoff,
		completed_at__isnull=False,
	).order_by("-completed_at", "title")
	households = Household.objects.filter(
		members__user=request.user,
	).prefetch_related(
		Prefetch("chores", queryset=due_chores, to_attr="due_chores"),
		Prefetch("chores", queryset=recently_completed, to_attr="recently_completed_chores"),
	).order_by("name")
	return render(request, "chores/home.html", {"households": households, "today": today})


@login_required
def profile(request):
	form = ProfileForm(request.POST or None, instance=request.user)
	if form.is_valid():
		form.save()
		messages.success(request, "Your profile has been updated.")
		return redirect("profile")
	return render(request, "registration/profile.html", {
		"form": form,
		"memberships": request.user.household_memberships.select_related("household"),
	})


@login_required
def password_change(request):
	form = PasswordChangeForm(request.user, request.POST or None)
	if form.is_valid():
		form.save()
		update_session_auth_hash(request, request.user)
		messages.success(request, "Your password has been changed.")
		return redirect("profile")
	return render(request, "registration/password_change.html", {"form": form})


@login_required
def create_household(request):
	form = HouseholdForm(request.POST or None)
	if form.is_valid():
		with transaction.atomic():
			household = form.save(commit=False)
			household.created_by = request.user
			household.save()
			HouseholdMember.objects.create(household=household, user=request.user)
			create_default_categories(household)
		return redirect("household-detail", household_id=household.id)
	return render(request, "chores/household_form.html", {"form": form})


@login_required
def household_detail(request, household_id):
	household = Household.objects.get(id=household_id)
	if not household.members.filter(user=request.user).exists():
		raise Http404
	return render(request, "chores/household_detail.html", {"household": household})


@login_required
def create_household_user(request, household_id):
	household = Household.objects.get(id=household_id)
	if household.created_by_id != request.user.id:
		raise Http404

	form = HouseholdUserForm(request.POST or None)
	if form.is_valid():
		password = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
		with transaction.atomic():
			try:
				with transaction.atomic():
					user = User.objects.create_user(username=form.cleaned_data["username"], password=password)
			except IntegrityError:
				if User.objects.filter(username=form.cleaned_data["username"]).exists():
					form.add_error("username", "A user with this username already exists.")
					return render(request, "chores/household_user_form.html", {"form": form, "household": household})
				raise
			HouseholdMember.objects.create(household=household, user=user)
		return render(request, "chores/household_user_created.html", {
			"household": household,
			"username": user.username,
			"password": password,
		})
	return render(request, "chores/household_user_form.html", {"form": form, "household": household})


@login_required
def join_household(request, invite_token):
	try:
		household = Household.objects.get(invite_token=invite_token)
	except Household.DoesNotExist as exc:
		raise Http404 from exc

	if request.method == "POST":
		HouseholdMember.objects.get_or_create(household=household, user=request.user)
		messages.success(request, f"You joined {household.name}.")
		return redirect("household-detail", household_id=household.id)

	return render(request, "chores/household_join.html", {"household": household})


@login_required
def create_category(request, household_id):
	household = Household.objects.get(id=household_id)
	if not household.members.filter(user=request.user).exists():
		raise Http404

	form = CategoryForm(request.POST or None)
	if form.is_valid():
		category = form.save(commit=False)
		category.household = household
		category.save()
		return redirect("household-detail", household_id=household.id)
	return render(request, "chores/category_form.html", {"form": form, "household": household})


def household_for_member(request, household_id):
	household = Household.objects.filter(id=household_id, members__user=request.user).first()
	if household is None:
		raise Http404
	return household


@login_required
def chore_list(request, household_id):
	household = household_for_member(request, household_id)
	chores = household.chores.select_related("category").all()
	filters = {
		"status": request.GET.get("status"),
		"category": request.GET.get("category"),
		"assigned_to": request.GET.get("assigned_to"),
		"priority": request.GET.get("priority"),
	}
	if filters["status"]:
		chores = chores.filter(status=filters["status"])
	if filters["category"]:
		chores = chores.filter(category_id=filters["category"])
	if filters["assigned_to"]:
		chores = chores.filter(assigned_to_id=filters["assigned_to"])
	if filters["priority"]:
		chores = chores.filter(priority=filters["priority"])
	return render(request, "chores/chore_list.html", {"household": household, "chores": chores, "filters": filters})


@login_required
def chore_create(request, household_id):
	household = household_for_member(request, household_id)
	form = ChoreForm(request.POST or None, household=household)
	if form.is_valid():
		chore = form.save(commit=False)
		chore.household = household
		chore.created_by = request.user
		chore.save()
		if chore.assignment_mode == Chore.AssignmentMode.ROTATION:
			chore.assign_next_member()
		return redirect("chore-detail", household_id=household.id, chore_id=chore.id)
	return render(request, "chores/chore_form.html", {"form": form, "household": household})


@login_required
def chore_detail(request, household_id, chore_id):
	household = household_for_member(request, household_id)
	chore = household.chores.select_related("category").get(id=chore_id)
	return render(request, "chores/chore_detail.html", {"household": household, "chore": chore})


@login_required
def chore_edit(request, household_id, chore_id):
	household = household_for_member(request, household_id)
	chore = household.chores.get(id=chore_id)
	form = ChoreForm(request.POST or None, instance=chore, household=household)
	if form.is_valid():
		form.save()
		return redirect("chore-detail", household_id=household.id, chore_id=chore.id)
	return render(request, "chores/chore_form.html", {"form": form, "household": household, "chore": chore})


@login_required
def chore_delete(request, household_id, chore_id):
	household = household_for_member(request, household_id)
	chore = household.chores.get(id=chore_id)
	if request.method == "POST":
		chore.delete()
		return redirect("chore-list", household_id=household.id)
	return render(request, "chores/chore_confirm_delete.html", {"household": household, "chore": chore})


@login_required
def chore_claim(request, household_id, chore_id):
	household = household_for_member(request, household_id)
	chore = household.chores.get(id=chore_id)
	if request.method == "POST" and chore.assignment_mode == Chore.AssignmentMode.CLAIM and chore.assigned_to_id is None:
		chore.assigned_to = request.user
		chore.save(update_fields=("assigned_to",))
	return redirect("chore-detail", household_id=household.id, chore_id=chore.id)


@login_required
def chore_complete(request, household_id, chore_id):
	household = household_for_member(request, household_id)
	with transaction.atomic():
		chore = household.chores.select_for_update().get(id=chore_id)
		if request.method == "POST" and chore.completed_at is None:
			chore.completed_by = request.user
			chore.completed_at = timezone.now()
			chore.status = Chore.Status.DONE
			chore.save(update_fields=("completed_by", "completed_at", "status"))
			member = HouseholdMember.objects.select_for_update().get(household=household, user=request.user)
			member.points += chore.points
			member.save(update_fields=("points",))
			next_date = next_due_date(chore.due_date, chore.recurrence)
			if next_date:
				next_chore = Chore.objects.create(
					household=household, category=chore.category, title=chore.title,
					description=chore.description, due_date=next_date, priority=chore.priority,
					estimated_minutes=chore.estimated_minutes, recurrence=chore.recurrence,
					points=chore.points, assignment_mode=chore.assignment_mode,
					assigned_to=chore.assigned_to if chore.assignment_mode in (Chore.AssignmentMode.MANUAL, Chore.AssignmentMode.ROTATION) else None,
					created_by=chore.created_by,
				)
				if next_chore.assignment_mode == Chore.AssignmentMode.ROTATION:
					next_chore.assign_next_member()
	return redirect("chore-detail", household_id=household.id, chore_id=chore.id)


@login_required
def chore_calendar(request, household_id):
	household = household_for_member(request, household_id)
	today = date.today()
	try:
		month = int(request.GET.get("month", today.month))
		year = int(request.GET.get("year", today.year))
		selected = date(year, month, 1)
	except (TypeError, ValueError):
		selected = date(today.year, today.month, 1)
	weeks = calendar.Calendar(firstweekday=6).monthdatescalendar(selected.year, selected.month)
	chores_by_date = {}
	for chore in household.chores.filter(
		due_date__isnull=False,
		due_date__year=selected.year,
		due_date__month=selected.month,
	).select_related("category"):
		chores_by_date.setdefault(chore.due_date, []).append(chore)
	weeks = [
		[
			{
				"day": day,
				"chores": chores_by_date.get(day, []),
				"in_month": day.month == selected.month,
			}
			for day in week
		]
		for week in weeks
	]
	previous = date(selected.year - (selected.month == 1), 12 if selected.month == 1 else selected.month - 1, 1)
	following = date(selected.year + (selected.month == 12), 1 if selected.month == 12 else selected.month + 1, 1)
	return render(request, "chores/chore_calendar.html", {
		"household": household,
		"selected": selected,
		"weeks": weeks,
		"chores_by_date": chores_by_date,
		"previous": previous,
		"following": following,
	})
