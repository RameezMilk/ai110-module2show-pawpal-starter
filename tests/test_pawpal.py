"""Tests for PawPal+ core logic."""

from datetime import date, timedelta
from pawpal_system import Pet, Task, Owner, Schedule


def _make_task(title="Walk", priority="medium", minutes=20, time="09:00", frequency="once"):
    return Task(
        title=title,
        duration_minutes=minutes,
        priority=priority,
        scheduled_date=date.today(),
        scheduled_time=time,
        frequency=frequency,
    )


# --- Task tests ---

def test_mark_complete_changes_status():
    task = _make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_recurring_daily_creates_next_task():
    task = _make_task("Walk", frequency="daily")
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.scheduled_date == date.today() + timedelta(days=1)
    assert next_task.completed is False
    assert next_task.frequency == "daily"


def test_recurring_weekly_creates_next_task():
    task = _make_task("Grooming", frequency="weekly")
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.scheduled_date == date.today() + timedelta(weeks=1)


def test_one_time_task_returns_none_on_complete():
    task = _make_task(frequency="once")
    assert task.mark_complete() is None


# --- Pet tests ---

def test_add_task_increases_count():
    pet = Pet(name="Mochi", species="dog")
    assert len(pet.tasks) == 0
    pet.add_task(_make_task("Walk"))
    assert len(pet.tasks) == 1
    pet.add_task(_make_task("Feed"))
    assert len(pet.tasks) == 2


# --- Schedule tests ---

def test_schedule_respects_priority_order():
    owner = Owner(name="Jordan", available_minutes=120)
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)

    pet.add_task(_make_task("Low task", priority="low", minutes=10))
    pet.add_task(_make_task("High task", priority="high", minutes=10))

    schedule = Schedule(date=date.today(), owner=owner)
    plan = schedule.generate_plan()

    assert plan[0].title == "High task"
    assert plan[1].title == "Low task"


def test_schedule_respects_time_limit():
    owner = Owner(name="Jordan", available_minutes=30)
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)

    pet.add_task(_make_task("Short", priority="high", minutes=15))
    pet.add_task(_make_task("Long", priority="high", minutes=20))

    schedule = Schedule(date=date.today(), owner=owner)
    plan = schedule.generate_plan()

    total = sum(t.duration_minutes for t in plan)
    assert total <= 30


def test_completed_tasks_excluded_from_plan():
    owner = Owner(name="Jordan", available_minutes=120)
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)

    task = _make_task("Done task", priority="high", minutes=10)
    task.mark_complete()
    pet.add_task(task)
    pet.add_task(_make_task("Pending task", priority="medium", minutes=10))

    schedule = Schedule(date=date.today(), owner=owner)
    plan = schedule.generate_plan()

    assert len(plan) == 1
    assert plan[0].title == "Pending task"


def test_sort_by_time():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)

    pet.add_task(_make_task("Late", time="18:00"))
    pet.add_task(_make_task("Early", time="07:00"))
    pet.add_task(_make_task("Mid", time="12:00"))

    schedule = Schedule(date=date.today(), owner=owner)
    schedule.generate_plan()
    sorted_tasks = schedule.sort_by_time()

    assert [t.title for t in sorted_tasks] == ["Early", "Mid", "Late"]


def test_filter_by_pet():
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    whiskers = Pet(name="Whiskers", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    mochi.add_task(_make_task("Walk"))
    mochi.add_task(_make_task("Meds"))
    whiskers.add_task(_make_task("Feed"))

    schedule = Schedule(date=date.today(), owner=owner)
    assert len(schedule.filter_by_pet("Mochi")) == 2
    assert len(schedule.filter_by_pet("Whiskers")) == 1


def test_filter_by_status():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)

    done = _make_task("Done")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(_make_task("Pending"))

    schedule = Schedule(date=date.today(), owner=owner)
    assert len(schedule.filter_by_status(completed=True)) == 1
    assert len(schedule.filter_by_status(completed=False)) == 1


def test_detect_conflicts():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)

    pet.add_task(_make_task("Walk", time="07:00"))
    pet.add_task(_make_task("Feed", time="07:00"))
    pet.add_task(_make_task("Meds", time="08:00"))

    schedule = Schedule(date=date.today(), owner=owner)
    schedule.generate_plan()

    assert len(schedule.warnings) == 1
    assert "07:00" in schedule.warnings[0]
