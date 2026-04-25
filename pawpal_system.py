from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

PRIORITY_ORDER = {"high": 3, "medium": 2, "low": 1}


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str         # "high" | "medium" | "low"
    category: str = "other"
    notes: str = ""
    status: str = "incomplete"
    recurrence: str | None = None   # "daily" | "weekly" | None
    due_date: date | None = None
    start_time: int | None = None   # minutes from midnight, e.g. 480 = 8:00 AM
    completed_date: date | None = None

    @property
    def duration_hhmm(self) -> str:
        """Return duration as a 'HH:MM' formatted string."""
        return f"{self.duration_minutes // 60:02d}:{self.duration_minutes % 60:02d}"

    @property
    def priority_value(self) -> int:
        """Return the numeric priority level for sorting."""
        return PRIORITY_ORDER.get(self.priority, 0)

    def mark_complete(self) -> Task | None:
        """Set the task's status to complete. Returns a new Task for the next occurrence if recurring."""
        self.status = "complete"
        self.completed_date = date.today()
        if self.recurrence in ("daily", "weekly"):
            delta = timedelta(days=1 if self.recurrence == "daily" else 7)
            next_due = (self.due_date or date.today()) + delta
            return Task(
                title=self.title,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                category=self.category,
                notes=self.notes,
                recurrence=self.recurrence,
                due_date=next_due,
                start_time=self.start_time,
            )
        return None

    def __str__(self) -> str:
        """Return a short human-readable summary of the task."""
        due = f" due {self.due_date}" if self.due_date else ""
        return f"[{self.priority.upper()}] {self.title} ({self.duration_minutes} min){due}"


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str          # "dog" | "cat" | "other"
    breed: Optional[str] = None
    age_years: Optional[float] = None
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def __str__(self) -> str:
        """Return the pet's name and species."""
        return f"{self.name} ({self.species})"


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    name: str
    time_available_minutes: int
    pets: list[Pet] = field(default_factory=list)
    preferences: list[str] = field(default_factory=list)

    def has_time_for(self, task: Task) -> bool:
        """Return True if the task fits within the owner's remaining time."""
        return task.duration_minutes <= self.time_available_minutes

    def consume_time(self, minutes: int) -> None:
        """Deduct the given number of minutes from the owner's available time."""
        self.time_available_minutes = max(0, self.time_available_minutes - minutes)


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner) -> None:
        """Initialize the scheduler with an owner and an empty task list."""
        self.owner: Owner = owner
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task to the scheduler's queue."""
        self.tasks.append(task)

    def complete_task(self, task: Task) -> Task | None:
        """Mark a task complete and auto-schedule the next occurrence if recurring."""
        next_task = task.mark_complete()
        if next_task is not None:
            self.tasks.append(next_task)
        return next_task

    def filter_tasks(self, *, status: str | None = None, pet_name: str | None = None) -> list[Task]:
        """Return tasks filtered by completion status and/or pet name prefix."""
        return [
            t for t in self.tasks
            if (status is None or t.status == status)
            and (pet_name is None or t.title.startswith(pet_name + ":"))
        ]

    def sort_by_duration(self, reverse: bool = False) -> list[Task]:
        """Return tasks sorted by duration_minutes, shortest first by default."""
        return sorted(self.tasks, key=lambda t: t.duration_minutes, reverse=reverse)

    def detect_conflicts(self, plan: list[Task]) -> list[str]:
        """Return warning messages for any tasks in the plan with overlapping time windows."""
        timed = [t for t in plan if t.start_time is not None]
        warnings = []
        for i, a in enumerate(timed):
            for b in timed[i + 1:]:
                a_end = a.start_time + a.duration_minutes
                b_end = b.start_time + b.duration_minutes
                if a.start_time < b_end and b.start_time < a_end:
                    pet_a = a.title.split(":")[0]
                    pet_b = b.title.split(":")[0]
                    label = "same pet" if pet_a == pet_b else "different pets"
                    warnings.append(
                        f"WARNING: '{a.title}' and '{b.title}' overlap ({label})"
                    )
        return warnings

    def generate_plan(self) -> list[Task]:
        """Return a priority-sorted list of incomplete tasks that fit the owner's available time."""
        incomplete = [t for t in self.tasks if t.status == "incomplete"]
        sorted_tasks = sorted(incomplete, key=lambda t: t.priority_value, reverse=True)
        scheduled: list[Task] = []
        for task in sorted_tasks:
            if self.owner.has_time_for(task):
                scheduled.append(task)
                self.owner.consume_time(task.duration_minutes)
        return scheduled

    def explain_plan(self, plan: list[Task]) -> str:
        """Return a formatted string summarizing the scheduled tasks and remaining time."""
        if not plan:
            return "No tasks could be scheduled given the available time."
        lines = [f"=== Today's Schedule for {self.owner.name} ===\n"]
        for i, task in enumerate(plan, start=1):
            lines.append(f"  {i}. {task}")
            if task.notes:
                lines.append(f"     Note: {task.notes}")
        lines.append(f"\nTime remaining after scheduling: {self.owner.time_available_minutes} min")
        return "\n".join(lines)
