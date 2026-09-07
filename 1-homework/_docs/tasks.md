# Implementation Tasks

These tasks are the issue-ready breakdown for the backlog. The PM must groom each task using [task-template.md](task-template.md) and [team/pm.md](team/pm.md) before implementation starts. Complete tasks in order; each task should be implemented and tested before the next one begins.

## 1. Set up empty Django project with passing test and database connection
**Goal:** Establish the base project skeleton, connect it to the database, and verify the environment is working.

**Scope:** Create the Django project and app structure, configure the database, add minimum settings, and add a smoke test for app loading and database connectivity. Do not add feature logic.

**Acceptance criteria:**
- The Django project and app start successfully.
- The configured database connection can be opened during a test.
- The test runner passes with the smoke test included.
- The repository is ready for the next task without placeholder feature behavior.

## 2. Implement user registration and authentication
**Goal:** Allow a user to create an account and sign in.

**Scope:** Build registration, sign-in, and sign-out forms, views, templates, and routes. Hash passwords, reject duplicate usernames, preserve sessions across pages, and show useful validation errors. Do not add household or chore behavior.

**Acceptance criteria:**
- A user can register with a unique username and password.
- Passwords are stored as hashes and never as plain text.
- Duplicate usernames and invalid input produce clear errors.
- A user can log in, remain authenticated across pages, and log out.

## 3. Implement household creation, invite links, and joining
**Goal:** Let a signed-in user create a household and let others join through a shared link.

**Scope:** Add Household and HouseholdMember models, migrations, household creation, unique invite-token generation, invite joining, and membership checks for future chore pages.

**Acceptance criteria:**
- An authenticated user can create a household.
- Each household has a unique shareable invite token or link.
- Another authenticated user can join through the invite link.
- Chore-related access is restricted to household members.

## 4. Create chore and category data models
**Goal:** Define the shared data needed for chores and category organization.

**Scope:** Add Category and Chore models, migrations, default categories (Kitchen, Laundry, Cleaning, Other), custom categories, and validation/defaults for title, description, due date, priority, estimated time, recurrence, points, status, and assignment mode.

**Acceptance criteria:**
- Chores belong to a household and category.
- The model supports four priority levels and three statuses.
- Points default to 10 and can be customized.
- Recurrence and assignment mode have explicit supported values.
- Default categories are available and members can create custom categories.

## 5. Build chore CRUD
**Goal:** Let household members create, view, edit, and delete chores.

**Scope:** Implement chore forms, routes, templates, and tests for create, detail/list, edit, and delete. Show category, due date, priority, estimated time, and status. Keep assignment manual-only for this task.

**Acceptance criteria:**
- A household member can create a valid chore.
- Members can view, edit, and delete chores in their household.
- Chore details display all required fields.
- Non-members cannot access chore CRUD actions.

## 6. Build chore assignment workflow
**Goal:** Support manual, member-claimed, and automatic-rotation assignments.

**Scope:** Extend chore creation and editing, add assignment persistence, implement claiming and rotation logic, and show the current assignee or "unclaimed" state.

**Acceptance criteria:**
- A chore can be assigned directly to a household member.
- A claimable chore can be claimed by an eligible member only once.
- A rotating chore selects members according to the defined rotation order.
- The UI shows the current assignee or an unclaimed state.

## 7. Add recurring chore scheduling
**Goal:** Support one-time and recurring chores.

**Scope:** Implement daily, weekly, and monthly recurrence on the chore template and logic to calculate or generate the next occurrence. Cover date boundaries with tests.

**Acceptance criteria:**
- One-time chores do not produce another occurrence.
- Daily, weekly, and monthly schedules calculate the expected next date.
- The scheduling logic is independently testable and ready for completion to call.

## 8. Add chore completion and points tracking
**Goal:** Record completion, update scores, and roll recurring chores forward.

**Scope:** Add completion action and persistence, record completing user and timestamp, award points, display member scores, and generate the next occurrence for recurring chores.

**Acceptance criteria:**
- An eligible member can mark a chore complete.
- Completion stores the user and completion timestamp.
- Points are awarded to the correct household member exactly once.
- Completing a recurring chore creates or calculates its next occurrence.
- Household members can see basic score totals.

## 9. Build chore list view with filtering
**Goal:** Let members browse household chores in a filtered list.

**Scope:** Build the list view and responsive template with filters for status, category, assignee, and priority. Include category, due date, priority, assignee, and status in each result.

**Acceptance criteria:**
- Members can view all household chores in a list.
- Each requested filter can be applied independently and in combination.
- Results contain only chores from the current household.
- The layout remains usable on desktop and mobile widths.

## 10. Build chore calendar view
**Goal:** Let members see chores laid out by due date.

**Scope:** Build a month-grid calendar, month navigation, due-date placement, and links from calendar entries to chore details.

**Acceptance criteria:**
- Chores appear on the correct due dates.
- Members can navigate to previous and next months.
- Calendar entries link to the corresponding chore detail.
- The view degrades to a usable mobile layout.

## 11. Finalize responsive UX and regression checks
**Goal:** Make the MVP usable end to end and confirm the main flows work together.

**Scope:** Polish responsive behavior, validation messaging, and unauthorized-access messaging across all pages. Run regression tests for registration, household sharing, CRUD, all assignment modes, recurrence, completion, points, list filters, and calendar navigation.

**Acceptance criteria:**
- Main workflows work end to end on desktop and mobile-sized layouts.
- Invalid forms and unauthorized requests provide clear feedback.
- Regression coverage includes every backlog feature and assignment mode.
- The application is ready for demo and handoff.
