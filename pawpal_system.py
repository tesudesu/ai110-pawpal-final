from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str         # "high" | "medium" | "low"
    category: str = "other"
    notes: str = ""

    @property
    def priority_value(self) -> int:
        pass

    def __str__(self) -> str:
        pass


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str          # "dog" | "cat" | "other"
    breed: Optional[str] = None
    age_years: Optional[float] = None

    def __str__(self) -> str:
        pass


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    name: str
    time_available_minutes: int
    pet: Optional[Pet] = None
    preferences: list[str] = field(default_factory=list)

    def has_time_for(self, _task: Task) -> bool:
        pass

    def consume_time(self, _minutes: int) -> None:
        pass


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner: Owner = owner
        self.tasks: list[Task] = []

    def add_task(self, _task: Task) -> None:
        pass

    def generate_plan(self) -> list[Task]:
        pass

    def explain_plan(self, _plan: list[Task]) -> str:
        pass
