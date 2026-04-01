# PawPal+ Project Reflection

## 1. System Design

Three core actions a user should be able to perform in natural language:

1. The user should be able to see the tasks for that particular day
2. Be able to add a task or edit from an existing set of tasks
3. Add a pet with a designated owner

**a. Initial design**

UML should have a user with an arrow to a frontend component,
which represents the app's UI, and leaving that frontend component are
a series of arrows, each of which correspond to an action invoked
from different elements on the frontend. For example, clicking "add pet"
should call the Pet Management Service and enable adding a pet with
a designated owner, etc. (assuming service-oriented architecture)

Four classes, each with a clear responsibility:
- **Pet** — holds a name and species. Kept simple since the owner manages the relationship.
- **Task** — represents a single care task (title, duration, priority, scheduled date) and
  points to the Pet it's for. Uses a dataclass so we don't need boilerplate.
- **Owner** — the central hub. Holds a list of pets and tasks, and exposes add_pet(),
  add_task(), and get_tasks_for_date(). Also tracks available_minutes so the scheduler
  knows how much time the owner actually has in a day.
- **Schedule** — takes an owner and a date, then generate_plan() filters and orders
  the tasks by priority while staying within the owner's available time.
  explain_plan() gives a human-readable breakdown of why tasks were chosen and ordered.

**b. Design changes**

After reviewing the skeleton with AI, one overlap stood out: Owner had a
get_tasks_for_today() method, but Schedule.generate_plan() would also need
to filter tasks by date. Having both do the same filtering is redundant and
could lead to inconsistencies. So I removed get_tasks_for_today() and replaced
it with a more flexible get_tasks_for_date(target_date) on Owner — this way
Owner just does the lookup, and Schedule is the one that actually orders and
constrains the plan. Cleaner separation of concerns.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints: priority (high/medium/low), scheduled time
(HH:MM), and the owner's available minutes for the day. Priority matters most because
a busy pet owner needs to make sure the critical stuff (meds, feeding) happens even if
there's not enough time for everything. Time is the secondary sort so that tasks with
the same priority land in a natural chronological order. The available_minutes budget
keeps the plan realistic — no point scheduling 3 hours of tasks if the owner only has 90
minutes.

**b. Tradeoffs**

The conflict detection only checks for exact time matches — if two tasks are both at
"07:00" it flags a warning, but it doesn't check if a 30-minute task at 07:00 overlaps
with a task at 07:15. This is a reasonable tradeoff because for a pet care app, most
owners think in rough time blocks ("morning walk", "evening feeding") rather than
minute-level precision. Checking for exact collisions catches the most common mistake
(double-booking a slot) without overcomplicating the logic.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

20 tests total, covering happy paths and edge cases:
- Task completion and recurring task generation (daily creates tomorrow, weekly creates next week, one-time returns nothing)
- Adding tasks to a pet actually increases its task count
- Scheduler sorts by priority then time, stays within the time budget, and excludes completed tasks
- Filtering by pet name and completion status
- Conflict detection flags same-time tasks (within a pet and across different pets), and doesn't false-positive when times differ
- Edge cases: empty pets, empty owners, tasks on the wrong date, all tasks too big to fit

These tests matter because the scheduler has multiple interacting constraints — priority, time, budget, completion status. Without tests it would be easy to break one thing while fixing another.

**b. Confidence**

4 out of 5. The core logic is solid and the edge cases I can think of are covered. If I had more time I'd test overlap-based conflicts (a 30-min task at 07:00 vs a task at 07:15), what happens when two pets have the exact same name, and stress-testing with a large number of tasks to make sure sorting doesn't degrade.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
