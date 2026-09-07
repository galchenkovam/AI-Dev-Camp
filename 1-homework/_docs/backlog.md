# Backlog

Before implementation, the PM must groom each task using [task-template.md](task-template.md) and the role guidance in [team/pm.md](team/pm.md). The groomed task must define its goal, acceptance criteria, out-of-scope work, and constraints.

## 1. Set up empty Django project with passing test and database connection
Goal: Establish the base project skeleton, connect it to the database, and verify the environment is working.
Description: Create the initial Django project and app structure, configure the database connection, add the minimum configuration, and write a simple test that confirms the app loads, the database connects, and the test runner passes. This task should leave the project in a clean starting state for the next tasks without introducing feature logic.

## 2. Implement user registration and authentication
Goal: Allow a user to create an account and sign in.
Description: Build the registration and sign-in forms, views, and templates. Store passwords as hashes, prevent duplicate usernames, and show clear validation errors for bad input. This task ends with a user who can register, log in, log out, and stay signed in across pages, but no household or chore functionality yet.

## 3. Implement household creation, invite links, and joining
Goal: Let a signed-in user create a household and let others join it through a shared link.
Description: Add the Household and HouseholdMember models, a create-household flow that generates a unique invite token, and a join flow that adds a new member when they follow the invite link. Restrict chore-related pages (built in later tasks) to members of the household. This task establishes the shared context that all chore features depend on.

## 4. Create chore and category data models
Goal: Define the shared data needed for chores and category organization.
Description: Add the Category and Chore models with fields for title, description, due date, priority, estimated time, recurrence, points, status, and assignment mode. Seed the default categories (Kitchen, Laundry, Cleaning, Other), support custom category creation, and add the validation rules and default values (e.g. 10 default points, four priority levels, three statuses) that keep chore creation consistent.

## 5. Build chore CRUD
Goal: Let household members create, view, edit, and delete chores.
Description: Implement the chore form, list template, and edit/delete flows. Chores should display their category, due date, priority, estimated time, and status. Assignment is stubbed to manual-only for this task; full assignment modes are handled next.

## 6. Build chore assignment workflow
Goal: Support all three assignment modes from the plan.
Description: Extend chore creation/editing so a chore can be manually assigned to a member, opened up for any member to claim, or set to rotate automatically among household members. Implement the rotation logic and the claim action, and reflect the current assignee (or "unclaimed") on the chore.

## 7. Add recurring chore scheduling
Goal: Support one-time and recurring chores.
Description: Implement daily, weekly, and monthly recurrence on top of the chore template, including the logic to calculate or generate the next occurrence. This task focuses on the scheduling logic itself so it is ready for the completion flow (task 8) to trigger it.

## 8. Add chore completion and points tracking
Goal: Record completed chores, update each member's score, and roll recurring chores to their next occurrence.
Description: Implement the completion flow so a member can mark a chore done, store the completing user and timestamp, and award points to the correct household member. If the chore is recurring, generate the next occurrence using the logic from task 7. Add the basic score display needed to review household progress.

## 9. Build chore list view with filtering
Goal: Let members browse household chores in a list, filtered to what they care about.
Description: Build the list view showing all household chores with their category, due date, priority, assignee, and status, and add filters for status, category, assignee, and priority. Ensure the layout works on both desktop and mobile widths.

## 10. Build chore calendar view
Goal: Let members see chores laid out by due date.
Description: Build a calendar view (month grid) that places chores on their due date, supports navigating between months, and links back to chore details. Ensure it degrades to a usable mobile layout.

## 11. Finalize responsive UX and regression checks
Goal: Make the MVP usable end to end and confirm the main flows work together.
Description: Polish the mobile-friendly layout across all pages, confirm validation and unauthorized-access messaging is clear throughout, and run final regression checks covering registration, household sharing, chore management, all three assignment modes, recurring chores, completion, points, and both views. This task wraps up the project so it is ready for demo and handoff.
