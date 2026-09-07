# Shared Household Chores Tool

## 1. Product Scope

Build a responsive, mobile-friendly web app for any type of household: families, couples, roommates, or other shared living arrangements.

The app helps household members create, organize, assign, complete, and score shared chores.

## 2. Decisions From Brainstorming

- **Audience:** Any household arrangement.
- **Household access:** Members join through a shared household link.
- **Accounts:** Users create simple accounts with a username and password.
- **Permissions:** All members have equal permissions.
- **Assignment:** Support manual assignment, automatic rotation, and member-claimed chores.
- **Schedules:** Each chore can be one-time or recurring.
- **Chore details:** Name, description, due date, repeat schedule, category, priority, and estimated time.
- **Completion:** Record the member who completed the chore and award points.
- **Reminders:** Support optional chore reminders and automatic reminders before deadlines.
- **Views:** Provide both list and calendar views, with the calendar supporting month navigation and clear due-date placement.
- **Categories:** Include visual category labels. Start with Kitchen, Laundry, Cleaning, and Other; allow members to create custom categories.
- **Storage:** Use a shared online database so multiple members and devices see the same data.
- **Platform:** Responsive web app with a mobile-friendly layout.

## 3. MVP Features

The minimum viable version must support:

1. Create and manage chores.
2. Assign chores to household members.
3. Mark chores as complete and record who completed them.
4. Award and display points for completed chores.

The MVP should also include the agreed supporting behavior:

- Create or join a household using a shared link.
- Register and sign in with username and password.
- Set one-time or recurring schedules.
- Organize chores by visual category.
- View chores in a list and on a calendar.
- Set due dates, priority, and estimated time.

## 4. Core User Flows

### Create a household

1. A user creates an account.
2. The user creates a household.
3. The app generates a shareable invite link.
4. Other users create accounts and join through the link.

### Create and assign a chore

1. A member opens the chore form.
2. The member enters the chore name and details.
3. The member selects a category, priority, due date, and schedule.
4. The member assigns the chore, enables member claiming, or selects automatic rotation.
5. The chore appears for the household.

### Complete a chore

1. A member opens an assigned or available chore.
2. The member marks it complete.
3. The app records the member and completion time.
4. The app awards the configured points.
5. The chore is shown as completed and the member's score is updated.

### Review household progress

1. A member opens the list or calendar view.
2. The member filters chores by status, category, assignee, or priority.
3. The member can see upcoming, overdue, and completed chores.
4. The member can view each member's accumulated points.

## 5. Suggested Data Model

- **User:** id, username, password hash, created date.
- **Household:** id, name, invite token, created by, created date.
- **HouseholdMember:** household id, user id, joined date.
- **Category:** id, household id, name, color, icon.
- **Chore:** id, household id, title, description, category id, priority, estimated minutes, due date, recurrence, assignment mode, points, status, created by.
- **ChoreAssignment:** chore id, user id, assignment date, status.
- **Completion:** chore id, user id, completed date, points awarded.
- **Reminder:** chore id, user id, reminder time, enabled.

For recurring chores, store a chore template and create or calculate the current occurrence. Keep the first implementation simple by supporting daily, weekly, and monthly recurrence.

## 6. Practical Defaults

These choices were not explicitly fixed during brainstorming:

- Use four priority levels: Low, Medium, High, and Urgent.
- Use three chore statuses: To do, In progress, and Done.
- Give each chore a default value of 10 points; allow the creator to change it.
- Treat overdue chores as still open until completed.
- Use a household-specific invite token rather than a public searchable household directory.
- Let any member create chores, categories, assignments, and reminders because all members have equal permissions.
- Prevent duplicate usernames.
- Store passwords as hashes; never store plain-text passwords.
- Make reminders in-app first. Email or push notifications are optional future work.
- Use accessible color plus text or icons for categories so color is not the only indicator.

## 7. Out of Scope for This Homework

- Social login.
- Payments or subscriptions.
- Admin-only roles.
- Public household discovery.
- Chat or comments.
- Photo proof of completion.
- Complex reward redemption.
- Email and push notification infrastructure.
- Native iOS or Android apps.
- Advanced analytics and export tools.
- Multi-household switching for one account, unless it is easy to support.

## 8. Acceptance Criteria

The homework is complete when:

- A user can register and sign in.
- A user can create a household and share its invite link.
- Another user can join the household through the link.
- Household data is shared between members and persists in the database.
- Members can create, edit, assign, and delete chores.
- A chore can be configured as one-time or recurring.
- Chores show their category, due date, priority, assignee, and estimated time.
- Members can mark chores complete and the app records who completed them.
- Completing a chore updates the member's points.
- Chores can be viewed in both list and calendar layouts.
- Categories are visually distinguishable and custom categories can be created.
- The main workflows are usable on both desktop and mobile screen sizes.
- Invalid forms and unauthorized access produce clear error messages.

## 9. Recommended Implementation Order

1. Set up the responsive web app and database connection.
2. Implement registration and sign-in.
3. Implement household creation, invite links, and joining.
4. Implement chore creation and management.
5. Implement assignment and completion tracking.
6. Implement points and member progress.
7. Add categories, filters, and visual labels.
8. Add list and calendar views.
9. Add recurring chores and reminders.
10. Test the main workflows on desktop and mobile layouts.
