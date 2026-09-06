# Backlog

## 1. Set up empty Django project with passing test
Goal: Establish the base project skeleton and verify the environment is working.
Description: Create the initial Django project and app structure, add the minimum configuration, and write a simple test that confirms the app loads and the test runner passes. This task should leave the project in a clean starting state for the next tasks without introducing feature logic.

## 2. Build authentication and household foundation
Goal: Allow users to register, sign in, and join a shared household.
Description: Set up the user auth flow, the household model, and the membership relationship between users and households. This task also includes creating a household and joining through a shared invite link so the core household structure is ready before chores are added.

## 3. Create chore data model and category system
Goal: Define the shared data needed for chores, recurrence, and category organization.
Description: Add the category and chore models with fields for title, description, due date, priority, estimated time, recurrence, points, and status. This task should also include the default values and validation rules that keep chore creation consistent across the app.

## 4. Build chore CRUD and assignment workflow
Goal: Enable household members to create, edit, delete, and assign chores.
Description: Implement the forms, views, and templates needed to manage chores, including manual assignment and the user-facing list of household tasks. This task is focused on the create/edit/delete workflow and the assignment logic, without completion tracking yet.

## 5. Add chore completion and points tracking
Goal: Record completed chores and update each member’s score.
Description: Implement the completion flow so a member can mark a task done, store the completing user and timestamp, and award points to the correct household member. This task also includes the basic score display needed to review household progress.

## 6. Add list, calendar, and filtering views
Goal: Let users review chores across the household in a practical layout.
Description: Build the list and calendar views, then add basic filters for status, category, assignee, and priority. This task should focus on the household dashboard experience and the main browsing flows.

## 7. Add recurring chores and reminder scaffolding
Goal: Support repeated chores and prepare reminder behavior for upcoming deadlines.
Description: Add the recurring schedule logic for daily, weekly, and monthly patterns and create the reminder model needed for in-app notifications. This task combines the scheduling piece and the reminder foundation so both can be tested together without moving into full email or push infrastructure.

## 8. Finalize responsive UX and regression checks
Goal: Make the MVP usable and ensure the main flows work end to end.
Description: Improve the mobile-friendly layout, add clear validation and unauthorized-access messaging, and run the final regression checks for registration, household sharing, chore management, completion, and household views. This task wraps up the project so it is ready for demo and handoff.
