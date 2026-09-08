# Household Chores App

This Django app helps household members create, assign, complete, and score shared chores.

## Setup

From this directory, install the project dependencies and apply the database migrations:

```text
uv sync
uv run python manage.py migrate
```

Start the development server with:

```text
uv run python manage.py runserver
```

Run the test suite with:

```text
uv run python manage.py test
```

The project was developed with GitHub Copilot. Product scope, workflow rules, and backlog details are in [_docs/plan.md](_docs/plan.md), [_docs/process.md](_docs/process.md), and [_docs/backlog.md](_docs/backlog.md).
