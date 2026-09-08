# Homework 1 Answers

## Completion Summary

All six homework questions have an answer supported by the project. The Django test suite passes with 49 tests. The application implements the main planned workflows, including authentication, household sharing, chore CRUD, assignments, recurring chores, completion and points, filtering, calendar views, and responsive-page checks. The selected coding agent and repository usage instructions are documented in the root [`README.md`](../README.md).

## Question 1: Select Your Coding Agent

**Answer:** GitHub Copilot.

The project was developed with GitHub Copilot as the coding agent.

## Question 2: Turn the Idea Into a Spec

**Answer:** The spec settled on these four MVP features:

1. Create and manage household chores.
2. Assign chores to household members.
3. Mark chores complete and record who completed them.
4. Award and display points for completed chores.

The supporting scope is documented in [`_docs/plan.md`](_docs/plan.md), including registration, household invite links, categories, recurring schedules, list and calendar views, due dates, priorities, and estimated time.

## Question 3: Django Project

**Answer:** `settings.py`.

The app is added to `INSTALLED_APPS` in [`config/settings.py`](config/settings.py).

## Question 4: Backlog

**Answer:** Task 1 is:

> Set up empty Django project with passing test and database connection.

Its goal is to establish the Django project and app skeleton, connect the database, and verify the environment with a passing smoke test. It is documented in [`_docs/backlog.md`](_docs/backlog.md).

## Question 5: First Version

**Answer:**

```text
uv run python manage.py runserver
```

The command uses Django's development server through the project's `manage.py` entry point.

## Question 6: Tests

**Answer:**

```text
uv run python manage.py test
```

Verification result: 49 tests ran successfully with `OK`.
