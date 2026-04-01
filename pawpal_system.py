"""PawPal+ Logic Layer — backend classes for the pet care planning assistant."""

from dataclasses import dataclass, field
from datetime import date

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    """A single pet care activity."""

    title: str
    duration_minutes: int
    priority: str  # "low", "medium", or "high"
    scheduled_date: date
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True


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
    """The scheduler — retrieves, prioritizes, and fits tasks into the owner's available time."""

    date: date
    owner: Owner
    tasks: list[Task] = field(default_factory=list)

    def generate_plan(self) -> list[Task]:
        """Build a daily plan sorted by priority, constrained by available minutes."""
        candidates = [
            t for t in self.owner.get_tasks_for_date(self.date) if not t.completed
        ]
        # Sort by priority (high first), then by duration (shorter first as tiebreaker)
        candidates.sort(key=lambda t: (PRIORITY_ORDER.get(t.priority, 99), t.duration_minutes))

        planned = []
        remaining = self.owner.available_minutes
        for task in candidates:
            if task.duration_minutes <= remaining:
                planned.append(task)
                remaining -= task.duration_minutes
        self.tasks = planned
        return planned

    def explain_plan(self) -> str:
        """Return a readable explanation of the daily plan."""
        if not self.tasks:
            return "No tasks scheduled for today."

        total = sum(t.duration_minutes for t in self.tasks)
        lines = [f"Schedule for {self.owner.name} on {self.date}"]
        lines.append(f"Total time: {total} min / {self.owner.available_minutes} min available\n")
        for i, task in enumerate(self.tasks, 1):
            pet_name = self._find_pet_for_task(task)
            lines.append(
                f"  {i}. [{task.priority.upper()}] {task.title} "
                f"({task.duration_minutes} min) — {pet_name}"
            )
        lines.append(f"\nHigh-priority tasks are scheduled first, "
                      f"fitting as many as possible within your available time.")
        return "\n".join(lines)

    def _find_pet_for_task(self, task: Task) -> str:
        """Find which pet a task belongs to."""
        for pet in self.owner.pets:
            if task in pet.tasks:
                return pet.name
        return "unknown"
