# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The scheduler in `pawpal_system.py` goes beyond a simple task list:

- **Priority + time sorting** — tasks are ordered by priority (high first), then by scheduled time (HH:MM) within each priority level.
- **Time budget** — the plan respects the owner's `available_minutes`, fitting as many tasks as possible without overcommitting.
- **Filtering** — filter tasks by pet name or completion status to quickly see what matters.
- **Recurring tasks** — daily and weekly tasks auto-generate a new occurrence when marked complete (using `timedelta`).
- **Conflict detection** — warns when multiple tasks are booked at the same time slot.

## Testing PawPal+

Run the test suite:

```bash
python -m pytest
```

The suite includes 20 tests covering:

- **Task basics** — completion status, recurring task generation (daily/weekly), one-time tasks returning no follow-up
- **Pet management** — adding tasks increases the pet's task count
- **Scheduling logic** — priority ordering, time budget constraints, excluding completed tasks, chronological sorting
- **Filtering** — by pet name, by completion status, nonexistent pet returns empty
- **Conflict detection** — same-time conflicts (same pet and cross-pet), no false positives when times differ
- **Edge cases** — pet with no tasks, owner with no pets, tasks on wrong date, all tasks exceeding budget

**Confidence Level: ⭐⭐⭐⭐ (4/5)** — happy paths and key edge cases are well covered. The main gap is overlap-based conflict detection (e.g., a 30-min task at 07:00 vs a task at 07:15) which we intentionally skip in favor of simplicity.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
