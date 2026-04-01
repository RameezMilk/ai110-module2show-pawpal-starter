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


# --- Edge cases ---

def test_pet_with_no_tasks_generates_empty_plan():
    owner = Owner(name="Jordan")
    owner.add_pet(Pet(name="Mochi", species="dog"))

    schedule = Schedule(date=date.today(), owner=owner)
    plan = schedule.generate_plan()

    assert plan == []
    assert schedule.explain_plan() == "No tasks scheduled for today."


def test_owner_with_no_pets_generates_empty_plan():
    owner = Owner(name="Jordan")
    schedule = Schedule(date=date.today(), owner=owner)
    assert schedule.generate_plan() == []


def test_tasks_on_wrong_date_excluded():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)

    tomorrow = date.today() + timedelta(days=1)
    pet.add_task(_make_task("Tomorrow task"))  # scheduled for today
    pet.add_task(Task(title="Future task", duration_minutes=10, priority="high",
                      scheduled_date=tomorrow))

    schedule = Schedule(date=tomorrow, owner=owner)
    plan = schedule.generate_plan()

    assert len(plan) == 1
    assert plan[0].title == "Future task"


def test_all_tasks_exceed_budget():
    owner = Owner(name="Jordan", available_minutes=10)
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)

    pet.add_task(_make_task("Big task", minutes=30))
    pet.add_task(_make_task("Bigger task", minutes=60))

    schedule = Schedule(date=date.today(), owner=owner)
    plan = schedule.generate_plan()

    assert plan == []


def test_conflict_across_different_pets():
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    whiskers = Pet(name="Whiskers", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    mochi.add_task(_make_task("Walk Mochi", time="07:00"))
    whiskers.add_task(_make_task("Feed Whiskers", time="07:00"))

    schedule = Schedule(date=date.today(), owner=owner)
    schedule.generate_plan()

    assert len(schedule.warnings) == 1
    assert "Walk Mochi" in schedule.warnings[0]
    assert "Feed Whiskers" in schedule.warnings[0]


def test_no_conflicts_when_times_differ():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)

    pet.add_task(_make_task("Walk", time="07:00"))
    pet.add_task(_make_task("Feed", time="08:00"))
    pet.add_task(_make_task("Meds", time="09:00"))

    schedule = Schedule(date=date.today(), owner=owner)
    schedule.generate_plan()

    assert schedule.warnings == []


def test_filter_by_nonexistent_pet_returns_empty():
    owner = Owner(name="Jordan")
    owner.add_pet(Pet(name="Mochi", species="dog"))

    schedule = Schedule(date=date.today(), owner=owner)
    assert schedule.filter_by_pet("Ghost") == []


def test_recurring_task_preserves_time_and_priority():
    task = _make_task("Walk", priority="high", time="07:30", frequency="daily")
    next_task = task.mark_complete()

    assert next_task.scheduled_time == "07:30"
    assert next_task.priority == "high"
    assert next_task.title == "Walk"
