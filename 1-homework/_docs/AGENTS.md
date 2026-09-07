Commands

- `uv sync` - install dependencies
- `uv run python manage.py test` - the whole suite
- `uv run python manage.py test chores.tests.AuthenticationTest` - one test class

Documents

- `_docs/plan.md` - product requirements and scope
- `_docs/tasks.md` - backlog of GitHub issues
- `_docs/process.md` - workflow and execution rules

Rules

- Work on one GitHub issue at a time.
- Read the task description and acceptance criteria before starting work.
- Commit regularly and only after a task is finished.
- Dependencies are added in `pyproject.toml`. Do not add one without
  asking.
- If a task affects the product direction, check `_docs/plan.md` before
  making changes.