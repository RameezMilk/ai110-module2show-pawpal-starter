"""PawPal+ Logic Layer — backend classes for the pet care planning assistant."""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Pet:
    """Represents a pet with a name and species."""

    name: str
    species: str  # e.g. "dog", "cat", "other"


@dataclass
class Task:
    """Represents a pet care task (walk, feeding, meds, etc.)."""

    title: str
    duration_minutes: int
    priority: str  # "low", "medium", or "high"
    scheduled_date: date
    pet: Pet


@dataclass
class Owner:
    """Represents the pet owner who manages pets and tasks."""

    name: str
    available_minutes: int = 120  # minutes available per day
    pets: list[Pet] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list."""
        pass

    def add_task(self, task: Task) -> None:
        """Add a care task."""
        pass

    def get_tasks_for_date(self, target_date: date) -> list[Task]:
        """Return tasks scheduled for a given date."""
        pass


@dataclass
class Schedule:
    """Generates and holds a daily plan of tasks for an owner."""

    date: date
    owner: Owner
    tasks: list[Task] = field(default_factory=list)

    def generate_plan(self) -> list[Task]:
        """Build an ordered daily plan based on constraints and priorities."""
        pass

    def explain_plan(self) -> str:
        """Return a human-readable explanation of why tasks were ordered this way."""
        pass
