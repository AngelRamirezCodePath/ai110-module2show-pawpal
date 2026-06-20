# Logic Layer where all backend classes live.

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Data classes — pure data containers, no scheduling logic
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    special_needs: list = field(default_factory=list)
    medical_conditions: list = field(default_factory=list)

    def get_info(self) -> str:
        """Return a human-readable pet profile summary."""
        pass

    def add_special_need(self, need: str) -> None:
        """Append a special need to the pet's list."""
        pass

    def requires_task(self, task_type: str) -> bool:
        """Return True if this pet needs the given task type."""
        pass


@dataclass
class Owner:
    name: str
    available_hours: float
    preferences: dict = field(default_factory=dict)
    contact_info: str = ""

    def set_availability(self, hours: float) -> None:
        """Update the owner's available hours for the day."""
        pass

    def update_preferences(self, prefs: dict) -> None:
        """Merge new preferences into the owner's preference dict."""
        pass

    def get_available_time(self) -> float:
        """Return total available hours."""
        pass


@dataclass
class Task:
    name: str
    duration: int          # minutes
    priority: str          # "HIGH", "MEDIUM", or "LOW"
    frequency: str         # "DAILY", "WEEKLY", "MONTHLY", "AS_NEEDED"
    description: str = ""
    time_window: str = ""  # "morning", "afternoon", "evening", or ""

    def get_duration(self) -> int:
        """Return task duration in minutes."""
        pass

    def is_critical(self) -> bool:
        """Return True if priority is HIGH."""
        pass

    def is_recurring(self, frequency: str) -> bool:
        """Return True if this task matches the given frequency."""
        pass

    def can_schedule_at(self, time: str) -> bool:
        """Return True if the task fits the given time-of-day slot."""
        pass


# ---------------------------------------------------------------------------
# Composite / logic classes — hold references to data classes
# ---------------------------------------------------------------------------

class DailyPlan:
    def __init__(self, date: str, pet: Pet):
        self.date: str = date
        self.pet: Pet = pet
        self.scheduled_tasks: list = []   # list of (Task, start_time_str) tuples
        self.total_time_used: int = 0     # minutes
        self.notes: str = ""

    def add_task(self, task: Task, start_time: str) -> None:
        """Add a task with its assigned start time to the schedule."""
        pass

    def remove_task(self, task: Task) -> None:
        """Remove a task from the schedule."""
        pass

    def get_tasks_ordered(self) -> list:
        """Return scheduled tasks sorted by start time."""
        pass

    def calculate_total_time(self) -> int:
        """Sum durations of all scheduled tasks and update total_time_used."""
        pass

    def has_conflicts(self) -> bool:
        """Return True if any two tasks have overlapping time slots."""
        pass

    def get_summary(self) -> str:
        """Return a formatted, human-readable daily schedule."""
        pass


class Scheduler:
    def __init__(self, pet: Pet, owner: Owner, available_tasks: Optional[list] = None):
        self.pet: Pet = pet
        self.owner: Owner = owner
        self.available_tasks: list = available_tasks or []

    def generate_daily_plan(self) -> DailyPlan:
        """Create and return a DailyPlan for today based on constraints."""
        pass

    def sort_tasks_by_priority(self) -> list:
        """Return available_tasks sorted HIGH → MEDIUM → LOW."""
        pass

    def filter_tasks(self, available_time: float) -> list:
        """Drop low-priority tasks that would exceed the time budget."""
        pass

    def fit_tasks_into_timeline(self, time_available: float) -> list:
        """Assign start times to tasks, respecting time_window preferences."""
        pass

    def validate_plan(self, plan: DailyPlan) -> bool:
        """Return True if the plan has no conflicts and fits within available time."""
        pass

    def explain_plan(self, plan: DailyPlan) -> str:
        """Return a plain-English explanation of why each task was included or skipped."""
        pass
