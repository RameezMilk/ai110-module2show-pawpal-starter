"""Demo script — verifies PawPal+ logic in the terminal before touching Streamlit."""

from datetime import date
from pawpal_system import Pet, Task, Owner, Schedule

# --- Setup ---
owner = Owner(name="Jordan", available_minutes=90)

mochi = Pet(name="Mochi", species="dog")
whiskers = Pet(name="Whiskers", species="cat")

owner.add_pet(mochi)
owner.add_pet(whiskers)

today = date.today()

# Add tasks for Mochi
mochi.add_task(Task(title="Morning walk", duration_minutes=30, priority="high", scheduled_date=today))
mochi.add_task(Task(title="Flea medication", duration_minutes=5, priority="high", scheduled_date=today))
mochi.add_task(Task(title="Grooming session", duration_minutes=45, priority="low", scheduled_date=today))

# Add tasks for Whiskers
whiskers.add_task(Task(title="Feeding", duration_minutes=10, priority="high", scheduled_date=today))
whiskers.add_task(Task(title="Play / enrichment", duration_minutes=20, priority="medium", scheduled_date=today))

# --- Generate and display the schedule ---
schedule = Schedule(date=today, owner=owner)
schedule.generate_plan()

print(schedule.explain_plan())
print()

# Show what didn't make the cut
all_today = owner.get_tasks_for_date(today)
skipped = [t for t in all_today if t not in schedule.tasks]
if skipped:
    print("Skipped (not enough time):")
    for t in skipped:
        print(f"  - {t.title} ({t.duration_minutes} min, {t.priority})")
