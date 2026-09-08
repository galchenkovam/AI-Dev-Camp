# AI-Dev-Camp

## Homework 1

This project is a Django web application for managing shared household chores.

The coding agent used for this homework was **GitHub Copilot**.

Project documentation:

- [Product plan](1-homework/_docs/plan.md)
- [Backlog](1-homework/_docs/backlog.md)
- [Homework answers](1-homework/answers.md)

### Run locally

```text
cd 1-homework
uv run python manage.py runserver
```

### Run tests

```text
cd 1-homework
uv run python manage.py test
```

## Demo path

1. Register a user and sign in.
2. Create a household and share its invite link.
3. Join the household with a second user.
4. Create chores with categories, due dates, priorities, recurrence, and points.
5. Exercise manual assignment, member claiming, and automatic rotation.
6. Complete a chore and verify the completion record and member score.
7. Review chores with list filters, then open the calendar and navigate between months.

The regression command completes with 60 passing tests in a clean Django test database. No known failures remain for the MVP workflows.

