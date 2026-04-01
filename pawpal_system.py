"""PawPal+ Logic Layer — backend classes for the pet care planning assistant."""

from dataclasses import dataclass, field
from datetime import date, timedelta

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    """A single pet care activity with time, priority, frequency, and completion tracking."""

    title: str
    duration_minutes: int
    priority: str  # "low", "medium", or "high"
    scheduled_date: date
    scheduled_time: str = "09:00"  # HH:MM format
    frequency: str = "once"  # "once", "daily", or "weekly"
    completed: bool = False

    def mark_complete(self) -> "Task | None":
        """Mark done. If recurring, returns a new Task for the next occurrence."""
        self.completed = True
        if self.frequency == "daily":
            return Task(
                title=self.title,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                scheduled_date=self.scheduled_date + timedelta(days=1),
                scheduled_time=self.scheduled_time,
                frequency=self.frequency,
            )
        elif self.frequency == "weekly":
            return Task(
                title=self.title,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                scheduled_date=self.scheduled_date + timedelta(weeks=1),
                scheduled_time=self.scheduled_time,
                frequency=self.frequency,
            )
        return None


@dataclass
class Pet:
    """A pet with a name, species, and its own task list."""

    name: str
    species: str  # "dog", "cat", "other"
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def get_tasks_for_date(self, target_date: date) -> list[Task]:
        """Return this pet's tasks for a given date."""
        return [t for t in self.tasks if t.scheduled_date == target_date]


@dataclass
class Owner:
    """Manages multiple pets and provides access to all their tasks."""

    name: str
    available_minutes: int = 120
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Retrieve every task across all pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def get_tasks_for_date(self, target_date: date) -> list[Task]:
        """Retrieve tasks across all pets for a given date."""
        return [task for pet in self.pets for task in pet.get_tasks_for_date(target_date)]


@dataclass
class Schedule:
    """The scheduler — sorts, filters, detects conflicts, and builds daily plans."""

    date: date
    owner: Owner
    tasks: list[Task] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def generate_plan(self) -> list[Task]:
        """Build a daily plan: filter incomplete tasks, sort by priority+time, fit within budget."""
        candidates = [
            t for t in self.owner.get_tasks_for_date(self.date) if not t.completed
        ]
        candidates.sort(key=lambda t: (PRIORITY_ORDER.get(t.priority, 99), t.scheduled_time))

        planned = []
        remaining = self.owner.available_minutes
        for task in candidates:
            if task.duration_minutes <= remaining:
                planned.append(task)
                remaining -= task.duration_minutes
        self.tasks = planned
        self.warnings = self.detect_conflicts(planned)
        return planned

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Sort tasks by their scheduled_time (HH:MM string comparison)."""
        target = tasks if tasks is not None else self.tasks
        return sorted(target, key=lambda t: t.scheduled_time)

    def filter_by_status(self, completed: bool, tasks: list[Task] | None = None) -> list[Task]:
        """Filter tasks by completion status."""
        target = tasks if tasks is not None else self.owner.get_all_tasks()
        return [t for t in target if t.completed == completed]

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Filter tasks belonging to a specific pet."""
        for pet in self.owner.pets:
            if pet.name == pet_name:
                return list(pet.tasks)
        return []

    def detect_conflicts(self, tasks: list[Task] | None = None) -> list[str]:
        """Detect tasks scheduled at the same time and return warning messages."""
        target = tasks if tasks is not None else self.tasks
        time_slots: dict[str, list[Task]] = {}
        for task in target:
            time_slots.setdefault(task.scheduled_time, []).append(task)

        warnings = []
        for time, group in time_slots.items():
            if len(group) > 1:
                names = ", ".join(f"'{t.title}'" for t in group)
                warnings.append(f"Conflict at {time}: {names} are all scheduled at the same time.")
        return warnings

    def explain_plan(self) -> str:
        """Return a readable explanation of the daily plan, including any warnings."""
        if not self.tasks:
            return "No tasks scheduled for today."

        total = sum(t.duration_minutes for t in self.tasks)
        lines = [f"Schedule for {self.owner.name} on {self.date}"]
        lines.append(f"Total time: {total} min / {self.owner.available_minutes} min available\n")

        for i, task in enumerate(self.tasks, 1):
            pet_name = self._find_pet_for_task(task)
            freq = f" [{task.frequency}]" if task.frequency != "once" else ""
            lines.append(
                f"  {i}. [{task.priority.upper()}] {task.scheduled_time} — {task.title} "
                f"({task.duration_minutes} min) — {pet_name}{freq}"
            )

        if self.warnings:
            lines.append("")
            for w in self.warnings:
                lines.append(f"  ⚠ {w}")

        lines.append(f"\nHigh-priority tasks first, then by scheduled time, "
                      f"fitting as many as possible within your available time.")
        return "\n".join(lines)

    def _find_pet_for_task(self, task: Task) -> str:
        """Find which pet a task belongs to."""
        for pet in self.owner.pets:
            if task in pet.tasks:
                return pet.name
        return "unknown"
