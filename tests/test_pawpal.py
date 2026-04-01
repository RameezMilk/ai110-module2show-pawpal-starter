"""Tests for PawPal+ core logic."""

from datetime import date
from pawpal_system import Pet, Task, Owner, Schedule


def _make_task(title="Walk", priority="medium", minutes=20):
    return Task(
        title=title,
        duration_minutes=minutes,
        priority=priority,
        scheduled_date=date.today(),
    )


# --- Task tests ---

def test_mark_complete_changes_status():
    task = _make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


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
