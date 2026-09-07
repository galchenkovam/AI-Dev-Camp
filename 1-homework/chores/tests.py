import uuid
from datetime import date

from django.db import connection
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Category, Chore, Household, HouseholdMember
from .scheduling import next_due_date


class AppConfigTest(TestCase):
	def test_app_is_installed(self):
		from django.apps import apps

		self.assertTrue(apps.is_installed("chores"))

	def test_database_connection_is_available(self):
		with connection.cursor() as cursor:
			cursor.execute("SELECT 1")
			self.assertEqual(cursor.fetchone()[0], 1)


class AuthenticationTest(TestCase):
	def test_user_can_register_with_hashed_password(self):
		response = self.client.post(
			reverse("register"),
			{"username": "alice", "password1": "A-strong-password-123", "password2": "A-strong-password-123"},
		)

		self.assertRedirects(response, reverse("home"))
		user = get_user_model().objects.get(username="alice")
		self.assertTrue(user.check_password("A-strong-password-123"))
		self.assertNotEqual(user.password, "A-strong-password-123")

	def test_duplicate_username_is_rejected(self):
		get_user_model().objects.create_user(username="alice", password="A-strong-password-123")

		response = self.client.post(
			reverse("register"),
			{"username": "alice", "password1": "Another-password-123", "password2": "Another-password-123"},
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "A user with that username already exists.")

	def test_registration_rejects_mismatched_passwords(self):
		response = self.client.post(
			reverse("register"),
			{"username": "alice", "password1": "A-strong-password-123", "password2": "Different-password-123"},
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "The two password fields")
		self.assertFalse(get_user_model().objects.filter(username="alice").exists())

	def test_registration_rejects_missing_required_fields_with_warning_popup(self):
		response = self.client.post(
			reverse("register"),
			{"username": "", "password1": "", "password2": ""},
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "This field is required.")
		self.assertContains(response, "window.alert")
		self.assertContains(response, "Please fix these problems")

	def test_registration_rejects_password_that_breaks_displayed_requirements(self):
		response = self.client.post(
			reverse("register"),
			{"username": "alice", "password1": "short", "password2": "short"},
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "This password is too short.")
		self.assertContains(response, "window.alert")
		self.assertFalse(get_user_model().objects.filter(username="alice").exists())

	def test_user_can_login_stay_authenticated_and_logout(self):
		get_user_model().objects.create_user(username="alice", password="A-strong-password-123")

		login_response = self.client.post(
			reverse("login"),
			{"username": "alice", "password": "A-strong-password-123"},
		)
		self.assertRedirects(login_response, reverse("home"))
		self.assertContains(self.client.get(reverse("home")), "Welcome, alice")

		logout_response = self.client.post(reverse("logout"))
		self.assertRedirects(logout_response, reverse("login"))
		self.assertRedirects(self.client.get(reverse("home")), f"{reverse('login')}?next={reverse('home')}")


class HouseholdTest(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(username="alice", password="A-strong-password-123")
		self.other_user = get_user_model().objects.create_user(username="bob", password="A-strong-password-123")
		self.client.force_login(self.user)

	def test_authenticated_user_can_create_household_and_becomes_member(self):
		response = self.client.post(reverse("household-create"), {"name": "Maple House"})

		household = Household.objects.get(name="Maple House")
		self.assertRedirects(response, reverse("household-detail", args=[household.id]))
		self.assertTrue(HouseholdMember.objects.filter(household=household, user=self.user).exists())
		self.assertEqual(len(str(household.invite_token)), 36)
		self.assertCountEqual(household.categories.values_list("name", flat=True), ["Kitchen", "Laundry", "Cleaning", "Other"])

	def test_anonymous_user_is_redirected_from_household_creation(self):
		self.client.logout()

		response = self.client.get(reverse("household-create"))

		self.assertRedirects(response, f"{reverse('login')}?next={reverse('household-create')}")

	def test_each_household_gets_a_unique_invite_token(self):
		first = Household.objects.create(name="First", created_by=self.user)
		second = Household.objects.create(name="Second", created_by=self.user)

		self.assertNotEqual(first.invite_token, second.invite_token)

	def test_authenticated_user_can_join_with_invite_and_repeated_join_is_idempotent(self):
		household = Household.objects.create(name="Maple House", created_by=self.user)
		self.client.force_login(self.other_user)

		join_url = reverse("household-join", args=[household.invite_token])
		self.assertContains(self.client.get(join_url), "Join Maple House")
		response = self.client.post(join_url)
		self.assertRedirects(response, reverse("household-detail", args=[household.id]))
		self.client.post(join_url)

		self.assertEqual(HouseholdMember.objects.filter(household=household, user=self.other_user).count(), 1)

	def test_non_member_cannot_view_household(self):
		household = Household.objects.create(name="Maple House", created_by=self.user)
		self.client.force_login(self.other_user)

		response = self.client.get(reverse("household-detail", args=[household.id]))

		self.assertEqual(response.status_code, 404)

	def test_invalid_invite_token_returns_not_found(self):
		response = self.client.get(reverse("household-join", args=[uuid.uuid4()]))

		self.assertEqual(response.status_code, 404)

	def test_member_can_create_custom_category(self):
		household = Household.objects.create(name="Maple House", created_by=self.user)
		HouseholdMember.objects.create(household=household, user=self.user)

		response = self.client.post(
			reverse("category-create", args=[household.id]),
			{"name": "Garden", "color": "#123456", "icon": "leaf"},
		)

		self.assertRedirects(response, reverse("household-detail", args=[household.id]))
		self.assertTrue(Category.objects.filter(household=household, name="Garden").exists())

	def test_non_member_cannot_create_category(self):
		household = Household.objects.create(name="Maple House", created_by=self.user)
		self.client.force_login(self.other_user)

		response = self.client.post(
			reverse("category-create", args=[household.id]),
			{"name": "Garden", "color": "#123456", "icon": "leaf"},
		)

		self.assertEqual(response.status_code, 404)
		self.assertFalse(Category.objects.filter(household=household, name="Garden").exists())

	def test_chore_defaults_and_supported_choices_are_explicit(self):
		household = Household.objects.create(name="Maple House", created_by=self.user)
		category = Category.objects.create(household=household, name="Kitchen")

		chore = Chore.objects.create(
			household=household,
			category=category,
			title="Wash dishes",
			created_by=self.user,
		)

		self.assertEqual(chore.points, 10)
		self.assertEqual(chore.priority, Chore.Priority.MEDIUM)
		self.assertEqual(chore.status, Chore.Status.TODO)
		self.assertEqual(chore.recurrence, Chore.Recurrence.NONE)
		self.assertEqual(chore.assignment_mode, Chore.AssignmentMode.MANUAL)
		self.assertEqual(len(Chore.Priority.choices), 4)
		self.assertEqual(len(Chore.Status.choices), 3)

	def test_chore_rejects_category_from_another_household(self):
		first_household = Household.objects.create(name="First", created_by=self.user)
		second_household = Household.objects.create(name="Second", created_by=self.user)
		category = Category.objects.create(household=second_household, name="Kitchen")
		chore = Chore(
			household=first_household,
			category=category,
			title="Wash dishes",
			created_by=self.user,
		)

		with self.assertRaisesMessage(ValidationError, "The category must belong to the chore's household."):
			chore.full_clean()


class ResponsiveUXTest(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(username="alice", password="A-strong-password-123")

	def test_core_pages_include_mobile_viewport_and_feedback_region(self):
		self.client.force_login(self.user)
		response = self.client.get(reverse("home"))
		self.assertContains(response, 'name="viewport"')
		self.assertContains(response, 'role="status"')

		self.client.logout()
		for url in (reverse("login"), reverse("register")):
			response = self.client.get(url)
			self.assertContains(response, 'name="viewport"')
			self.assertContains(response, 'role="status"')


class ChoreCrudTest(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(username="alice", password="A-strong-password-123")
		self.other_user = get_user_model().objects.create_user(username="bob", password="A-strong-password-123")
		self.household = Household.objects.create(name="Maple House", created_by=self.user)
		HouseholdMember.objects.create(household=self.household, user=self.user)
		self.category = Category.objects.create(household=self.household, name="Kitchen")
		self.client.force_login(self.user)

	def chore_data(self, title="Wash dishes"):
		return {
			"title": title,
			"description": "Clean the dishes",
			"category": self.category.id,
			"due_date": "2026-09-10",
			"priority": "high",
			"estimated_minutes": 20,
			"recurrence": "none",
			"points": 15,
			"status": "todo",
			"assignment_mode": "manual",
		}

	def test_member_can_create_view_edit_and_delete_chore(self):
		response = self.client.post(reverse("chore-create", args=[self.household.id]), self.chore_data())
		chore = Chore.objects.get(title="Wash dishes")

		self.assertRedirects(response, reverse("chore-detail", args=[self.household.id, chore.id]))
		self.assertContains(self.client.get(reverse("chore-list", args=[self.household.id])), "Wash dishes")
		detail = self.client.get(reverse("chore-detail", args=[self.household.id, chore.id]))
		self.assertContains(detail, "Kitchen")
		self.assertContains(detail, "--category-color: #6c757d")
		self.assertContains(detail, "High")
		self.assertContains(detail, "20 minutes")

		self.client.post(reverse("chore-edit", args=[self.household.id, chore.id]), self.chore_data("Clean counters"))
		chore.refresh_from_db()
		self.assertEqual(chore.title, "Clean counters")

		response = self.client.post(reverse("chore-delete", args=[self.household.id, chore.id]))
		self.assertRedirects(response, reverse("chore-list", args=[self.household.id]))
		self.assertFalse(Chore.objects.filter(id=chore.id).exists())

	def test_member_can_assign_chore_to_another_household_member(self):
		HouseholdMember.objects.create(household=self.household, user=self.other_user)

		response = self.client.post(
			reverse("chore-create", args=[self.household.id]),
			{**self.chore_data(), "assigned_to": self.other_user.id},
		)

		self.assertEqual(response.status_code, 302)
		self.assertEqual(Chore.objects.get(title="Wash dishes").assigned_to, self.other_user)

	def test_chore_form_rejects_category_from_another_household(self):
		other_household = Household.objects.create(name="Other House", created_by=self.other_user)
		other_category = Category.objects.create(household=other_household, name="Laundry")

		response = self.client.post(
			reverse("chore-create", args=[self.household.id]),
			{**self.chore_data(), "category": other_category.id},
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Select a valid choice")
		self.assertFalse(Chore.objects.filter(title="Wash dishes").exists())

	def test_non_member_cannot_access_chore_crud(self):
		chore = Chore.objects.create(
			household=self.household,
			category=self.category,
			title="Wash dishes",
			created_by=self.user,
			due_date=date(2026, 9, 10),
		)
		self.client.force_login(self.other_user)

		for url in (
			reverse("chore-list", args=[self.household.id]),
			reverse("chore-create", args=[self.household.id]),
			reverse("chore-detail", args=[self.household.id, chore.id]),
			reverse("chore-edit", args=[self.household.id, chore.id]),
			reverse("chore-delete", args=[self.household.id, chore.id]),
		):
			self.assertEqual(self.client.get(url).status_code, 404)

	def test_claimable_chore_can_be_claimed_only_once(self):
		chore = Chore.objects.create(
			household=self.household, category=self.category, title="Take bins out", created_by=self.user,
			assignment_mode=Chore.AssignmentMode.CLAIM,
		)
		self.client.post(reverse("chore-claim", args=[self.household.id, chore.id]))
		chore.refresh_from_db()
		self.assertEqual(chore.assigned_to, self.user)

		self.client.force_login(self.other_user)
		HouseholdMember.objects.create(household=self.household, user=self.other_user)
		self.client.post(reverse("chore-claim", args=[self.household.id, chore.id]))
		chore.refresh_from_db()
		self.assertEqual(chore.assigned_to, self.user)

	def test_claimable_chore_is_not_claimed_by_a_get_request(self):
		chore = Chore.objects.create(
			household=self.household, category=self.category, title="Take bins out", created_by=self.user,
			assignment_mode=Chore.AssignmentMode.CLAIM,
		)

		response = self.client.get(reverse("chore-claim", args=[self.household.id, chore.id]))

		self.assertRedirects(response, reverse("chore-detail", args=[self.household.id, chore.id]))
		chore.refresh_from_db()
		self.assertIsNone(chore.assigned_to)

	def test_rotation_assigns_members_in_join_order(self):
		HouseholdMember.objects.create(household=self.household, user=self.other_user)
		chore = Chore.objects.create(
			household=self.household, category=self.category, title="Mop floor", created_by=self.user,
			assignment_mode=Chore.AssignmentMode.ROTATION,
		)

		chore.assign_next_member()
		self.assertEqual(chore.assigned_to, self.user)
		chore.assign_next_member()
		self.assertEqual(chore.assigned_to, self.other_user)

	def test_rotation_chore_created_through_form_is_assigned_immediately(self):
		HouseholdMember.objects.create(household=self.household, user=self.other_user)

		response = self.client.post(
			reverse("chore-create", args=[self.household.id]),
			{**self.chore_data("Rotate bins"), "assignment_mode": Chore.AssignmentMode.ROTATION},
		)

		self.assertEqual(response.status_code, 302)
		self.assertEqual(Chore.objects.get(title="Rotate bins").assigned_to, self.user)


class SchedulingTest(TestCase):
	def test_one_time_chore_has_no_next_occurrence(self):
		self.assertIsNone(next_due_date(date(2026, 9, 7), Chore.Recurrence.NONE))

	def test_daily_and_weekly_recurrence(self):
		start = date(2026, 9, 7)
		self.assertEqual(next_due_date(start, Chore.Recurrence.DAILY), date(2026, 9, 8))
		self.assertEqual(next_due_date(start, Chore.Recurrence.WEEKLY), date(2026, 9, 14))

	def test_monthly_recurrence_handles_month_end(self):
		self.assertEqual(next_due_date(date(2026, 1, 31), Chore.Recurrence.MONTHLY), date(2026, 2, 28))
		self.assertEqual(next_due_date(date(2026, 12, 31), Chore.Recurrence.MONTHLY), date(2027, 1, 31))


class CompletionTest(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(username="alice", password="A-strong-password-123")
		self.household = Household.objects.create(name="Maple House", created_by=self.user)
		HouseholdMember.objects.create(household=self.household, user=self.user)
		self.category = Category.objects.create(household=self.household, name="Kitchen")
		self.chore = Chore.objects.create(
			household=self.household, category=self.category, title="Wash dishes", created_by=self.user,
			due_date=date(2026, 9, 7), points=25, recurrence=Chore.Recurrence.WEEKLY,
		)
		self.client.force_login(self.user)

	def test_completion_records_user_time_awards_points_once_and_creates_next_occurrence(self):
		url = reverse("chore-complete", args=[self.household.id, self.chore.id])
		response = self.client.post(url)

		self.assertRedirects(response, reverse("chore-detail", args=[self.household.id, self.chore.id]))
		self.chore.refresh_from_db()
		member = HouseholdMember.objects.get(household=self.household, user=self.user)
		self.assertEqual(self.chore.status, Chore.Status.DONE)
		self.assertEqual(self.chore.completed_by, self.user)
		self.assertIsNotNone(self.chore.completed_at)
		self.assertEqual(member.points, 25)
		self.assertTrue(Chore.objects.filter(title="Wash dishes", due_date=date(2026, 9, 14), completed_at__isnull=True).exists())

		self.client.post(url)
		member.refresh_from_db()
		self.assertEqual(member.points, 25)

	def test_completing_one_time_chore_does_not_create_another_chore(self):
		self.chore.recurrence = Chore.Recurrence.NONE
		self.chore.save(update_fields=("recurrence",))

		self.client.post(reverse("chore-complete", args=[self.household.id, self.chore.id]))

		self.assertEqual(Chore.objects.filter(title=self.chore.title).count(), 1)

	def test_recurring_claimable_chore_starts_unclaimed(self):
		self.chore.assignment_mode = Chore.AssignmentMode.CLAIM
		self.chore.assigned_to = self.user
		self.chore.save(update_fields=("assignment_mode", "assigned_to"))

		self.client.post(reverse("chore-complete", args=[self.household.id, self.chore.id]))

		next_chore = Chore.objects.get(title=self.chore.title, completed_at__isnull=True)
		self.assertIsNone(next_chore.assigned_to)

	def test_recurring_rotating_chore_moves_to_next_member(self):
		other_user = get_user_model().objects.create_user(username="bob", password="A-strong-password-123")
		HouseholdMember.objects.create(household=self.household, user=other_user)
		self.chore.assignment_mode = Chore.AssignmentMode.ROTATION
		self.chore.assigned_to = self.user
		self.chore.save(update_fields=("assignment_mode", "assigned_to"))

		self.client.post(reverse("chore-complete", args=[self.household.id, self.chore.id]))

		next_chore = Chore.objects.get(title=self.chore.title, completed_at__isnull=True)
		self.assertEqual(next_chore.assigned_to, other_user)


class ChoreFilterTest(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(username="alice", password="A-strong-password-123")
		self.other_user = get_user_model().objects.create_user(username="bob", password="A-strong-password-123")
		self.household = Household.objects.create(name="Maple House", created_by=self.user)
		HouseholdMember.objects.create(household=self.household, user=self.user)
		self.category = Category.objects.create(household=self.household, name="Kitchen")
		self.other_category = Category.objects.create(household=self.household, name="Laundry")
		self.first = Chore.objects.create(household=self.household, category=self.category, title="Wash dishes", created_by=self.user, priority="high")
		Chore.objects.create(household=self.household, category=self.other_category, title="Fold clothes", created_by=self.user, priority="low", status="done")
		self.client.force_login(self.user)

	def test_filters_can_be_combined(self):
		response = self.client.get(reverse("chore-list", args=[self.household.id]), {"category": self.category.id, "priority": "high", "status": "todo"})

		self.assertContains(response, "Wash dishes")
		self.assertNotContains(response, "Fold clothes")
		self.assertContains(response, f'<option value="{self.category.id}" selected>Kitchen</option>', html=True)
		self.assertContains(response, '<option value="high" selected>High</option>', html=True)

	def test_assignee_filter_returns_only_matching_chores(self):
		HouseholdMember.objects.create(household=self.household, user=self.other_user)
		self.first.assigned_to = self.other_user
		self.first.save(update_fields=("assigned_to",))
		other = Chore.objects.create(
			household=self.household, category=self.other_category, title="Empty bins", created_by=self.user,
			assigned_to=self.user,
		)

		response = self.client.get(
			reverse("chore-list", args=[self.household.id]), {"assigned_to": self.other_user.id}
		)

		self.assertContains(response, "Wash dishes")
		self.assertNotContains(response, other.title)


class CalendarTest(TestCase):
	def test_calendar_places_chore_and_navigates_months(self):
		user = get_user_model().objects.create_user(username="alice", password="A-strong-password-123")
		household = Household.objects.create(name="Maple House", created_by=user)
		HouseholdMember.objects.create(household=household, user=user)
		category = Category.objects.create(household=household, name="Kitchen")
		chore = Chore.objects.create(household=household, category=category, title="Wash dishes", created_by=user, due_date=date(2026, 9, 7))
		self.client.force_login(user)

		response = self.client.get(reverse("chore-calendar", args=[household.id]), {"year": 2026, "month": 9})

		self.assertContains(response, "September 2026")
		self.assertContains(response, reverse("chore-detail", args=[household.id, chore.id]))
		self.assertContains(response, "month=10")

	def test_calendar_december_navigation_includes_following_year(self):
		user = get_user_model().objects.create_user(username="alice", password="A-strong-password-123")
		household = Household.objects.create(name="Maple House", created_by=user)
		HouseholdMember.objects.create(household=household, user=user)
		self.client.force_login(user)

		response = self.client.get(reverse("chore-calendar", args=[household.id]), {"year": 2026, "month": 12})

		self.assertEqual(response.context["following"], date(2027, 1, 1))

	def test_calendar_shows_empty_state_when_month_has_no_chores(self):
		user = get_user_model().objects.create_user(username="alice", password="A-strong-password-123")
		household = Household.objects.create(name="Maple House", created_by=user)
		HouseholdMember.objects.create(household=household, user=user)
		self.client.force_login(user)

		response = self.client.get(reverse("chore-calendar", args=[household.id]), {"year": 2026, "month": 9})

		self.assertContains(response, "No chores are scheduled for this month.")

	def test_non_member_cannot_view_calendar(self):
		owner = get_user_model().objects.create_user(username="owner", password="A-strong-password-123")
		household = Household.objects.create(name="Maple House", created_by=owner)
		self.client.force_login(get_user_model().objects.create_user(username="visitor", password="A-strong-password-123"))

		response = self.client.get(reverse("chore-calendar", args=[household.id]))

		self.assertEqual(response.status_code, 404)

