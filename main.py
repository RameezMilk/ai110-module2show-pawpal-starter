"""Demo script — exercises sorting, filtering, recurring tasks, and conflict detection."""

from datetime import date
from pawpal_system import Pet, Task, Owner, Schedule

# --- Setup ---
owner = Owner(name="Jordan", available_minutes=90)

mochi = Pet(name="Mochi", species="dog")
whiskers = Pet(name="Whiskers", species="cat")

owner.add_pet(mochi)
owner.add_pet(whiskers)

today = date.today()

# Add tasks OUT OF ORDER (different times) to test sorting
mochi.add_task(Task(title="Evening walk", duration_minutes=30, priority="medium",
                    scheduled_date=today, scheduled_time="18:00", frequency="daily"))
mochi.add_task(Task(title="Morning walk", duration_minutes=30, priority="high",
                    scheduled_date=today, scheduled_time="07:00", frequency="daily"))
mochi.add_task(Task(title="Flea medication", duration_minutes=5, priority="high",
                    scheduled_date=today, scheduled_time="08:00"))

# Whiskers tasks — one conflicts with Mochi's morning walk at 07:00
whiskers.add_task(Task(title="Feeding", duration_minutes=10, priority="high",
                       scheduled_date=today, scheduled_time="07:00", frequency="daily"))
whiskers.add_task(Task(title="Play / enrichment", duration_minutes=20, priority="low",
                       scheduled_date=today, scheduled_time="15:00"))

# --- Generate schedule (sorts + detects conflicts) ---
schedule = Schedule(date=today, owner=owner)
schedule.generate_plan()
print(schedule.explain_plan())

# --- Sorting by time ---
print("\n--- Sorted by time ---")
for t in schedule.sort_by_time():
    print(f"  {t.scheduled_time} — {t.title}")

# --- Filtering by pet ---
print("\n--- Mochi's tasks only ---")
for t in schedule.filter_by_pet("Mochi"):
    print(f"  {t.title} ({t.priority}, {t.frequency})")

# --- Filtering by status ---
print("\n--- Incomplete tasks ---")
for t in schedule.filter_by_status(completed=False):
    print(f"  {t.title}")

# --- Recurring task demo ---
print("\n--- Recurring task demo ---")
morning_walk = mochi.tasks[1]  # "Morning walk", daily
print(f"Completing '{morning_walk.title}' (scheduled {morning_walk.scheduled_date})...")
next_task = morning_walk.mark_complete()
if next_task:
    mochi.add_task(next_task)
    print(f"  → New occurrence created for {next_task.scheduled_date}")

# Verify: filter shows the completed one and the new pending one
print(f"  Completed tasks: {len(schedule.filter_by_status(completed=True))}")
print(f"  Pending tasks:   {len(schedule.filter_by_status(completed=False))}")
