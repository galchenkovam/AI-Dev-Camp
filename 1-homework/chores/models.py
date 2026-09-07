import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MinValueValidator


class Household(models.Model):
	name = models.CharField(max_length=100)
	invite_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="households_created")
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name


class HouseholdMember(models.Model):
	household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="members")
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="household_memberships")
	joined_at = models.DateTimeField(auto_now_add=True)
	points = models.PositiveIntegerField(default=0)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=("household", "user"), name="unique_household_member"),
		]
		ordering = ("joined_at",)

	def __str__(self):
		return f"{self.user.username} in {self.household.name}"


DEFAULT_CATEGORIES = (
	("Kitchen", "#e76f51", "utensils"),
	("Laundry", "#2a9d8f", "shirt"),
	("Cleaning", "#457b9d", "sparkles"),
	("Other", "#6c757d", "ellipsis"),
)


class Category(models.Model):
	household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="categories")
	name = models.CharField(max_length=50)
	color = models.CharField(max_length=7, default="#6c757d")
	icon = models.CharField(max_length=30, blank=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=("household", "name"), name="unique_category_per_household"),
		]
		ordering = ("name",)

	def __str__(self):
		return self.name


class Chore(models.Model):
	class Priority(models.TextChoices):
		LOW = "low", "Low"
		MEDIUM = "medium", "Medium"
		HIGH = "high", "High"
		URGENT = "urgent", "Urgent"

	class Status(models.TextChoices):
		TODO = "todo", "To do"
		IN_PROGRESS = "in_progress", "In progress"
		DONE = "done", "Done"

	class Recurrence(models.TextChoices):
		NONE = "none", "One time"
		DAILY = "daily", "Daily"
		WEEKLY = "weekly", "Weekly"
		MONTHLY = "monthly", "Monthly"

	class AssignmentMode(models.TextChoices):
		MANUAL = "manual", "Manual"
		CLAIM = "claim", "Member claimed"
		ROTATION = "rotation", "Automatic rotation"

	household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="chores")
	category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="chores")
	title = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	due_date = models.DateField(null=True, blank=True)
	priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
	estimated_minutes = models.PositiveIntegerField(null=True, blank=True)
	recurrence = models.CharField(max_length=10, choices=Recurrence.choices, default=Recurrence.NONE)
	points = models.PositiveIntegerField(default=10, validators=[MinValueValidator(0)])
	status = models.CharField(max_length=12, choices=Status.choices, default=Status.TODO)
	assignment_mode = models.CharField(max_length=10, choices=AssignmentMode.choices, default=AssignmentMode.MANUAL)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chores_created")
	assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="chores_assigned")
	created_at = models.DateTimeField(auto_now_add=True)
	completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="chores_completed")
	completed_at = models.DateTimeField(null=True, blank=True)

	def clean(self):
		if self.category_id and self.household_id and self.category.household_id != self.household_id:
			raise ValidationError({"category": "The category must belong to the chore's household."})

	def __str__(self):
		return self.title

	def assign_next_member(self):
		members = list(self.household.members.select_related("user").order_by("joined_at"))
		if not members:
			self.assigned_to = None
		else:
			current_index = next((index for index, member in enumerate(members) if member.user_id == self.assigned_to_id), -1)
			self.assigned_to = members[(current_index + 1) % len(members)].user
		self.save(update_fields=("assigned_to",))


def create_default_categories(household):
	Category.objects.bulk_create(
		[
			Category(household=household, name=name, color=color, icon=icon)
			for name, color, icon in DEFAULT_CATEGORIES
		]
	)
