# Logic Layer where all backend classes live.

from dataclasses import dataclass, field
from typing import Optional
import datetime


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
    tasks: list = field(default_factory=list)

    def add_task(self, task: "Task") -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def get_info(self) -> str:
        """Return a human-readable pet profile summary."""
        parts = [f"{self.name} ({self.breed} {self.species}, age {self.age})"]
        if self.medical_conditions:
            parts.append(f"Medical: {', '.join(self.medical_conditions)}")
        if self.special_needs:
            parts.append(f"Special needs: {', '.join(self.special_needs)}")
        return " | ".join(parts)

    def add_special_need(self, need: str) -> None:
        """Append a special need to the pet's list."""
        if need not in self.special_needs:
            self.special_needs.append(need)

    def requires_task(self, task_type: str) -> bool:
        """Return True if this pet needs the given task type."""
        return task_type.lower() in [n.lower() for n in self.special_needs]


@dataclass
class Owner:
    name: str
    available_hours: float
    preferences: dict = field(default_factory=dict)
    contact_info: str = ""

    def set_availability(self, hours: float) -> None:
        """Update the owner's available hours for the day."""
        self.available_hours = hours

    def update_preferences(self, prefs: dict) -> None:
        """Merge new preferences into the owner's preference dict."""
        self.preferences.update(prefs)

    def get_available_time(self) -> float:
        """Return total available hours."""
        return self.available_hours


@dataclass
class Task:
    name: str
    duration: int          # minutes
    priority: str          # "HIGH", "MEDIUM", or "LOW"
    frequency: str         # "DAILY", "WEEKLY", "MONTHLY", "AS_NEEDED"
    description: str = ""
    time_window: str = ""  # "morning", "afternoon", "evening", or ""
    completed: bool = False
    # Fix: tasks belong to a specific pet so the scheduler can filter by pet
    pet: Optional["Pet"] = field(default=None, repr=False)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def get_duration(self) -> int:
        """Return task duration in minutes."""
        return self.duration

    def is_critical(self) -> bool:
        """Return True if priority is HIGH."""
        return self.priority.upper() == "HIGH"

    def is_recurring(self, frequency: str) -> bool:
        """Return True if this task matches the given frequency."""
        return self.frequency.upper() == frequency.upper()

    def can_schedule_at(self, time: str) -> bool:
        """Return True if the task fits the given time-of-day slot."""
        return self.time_window == "" or self.time_window.lower() == time.lower()


# ---------------------------------------------------------------------------
# Composite / logic classes — hold references to data classes
# ---------------------------------------------------------------------------

# Window start times in minutes from midnight
_WINDOW_STARTS = {"morning": 8 * 60, "afternoon": 12 * 60, "evening": 18 * 60}
_PRIORITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


class DailyPlan:
    # Fix: store owner so the plan can self-validate against the time budget
    def __init__(self, date: str, pet: Pet, owner: Owner):
        self.date: str = date
        self.pet: Pet = pet
        self.owner: Owner = owner
        self.scheduled_tasks: list = []   # list of (Task, start_time_str) tuples
        self.total_time_used: int = 0     # minutes
        self.notes: str = ""

    def add_task(self, task: Task, start_time: str) -> None:
        """Add a task with its assigned start time to the schedule."""
        self.scheduled_tasks.append((task, start_time))
        self.total_time_used += task.duration

    def remove_task(self, task: Task) -> None:
        """Remove a task from the schedule."""
        self.scheduled_tasks = [(t, s) for t, s in self.scheduled_tasks if t is not task]
        self.total_time_used = self.calculate_total_time()

    def get_tasks_ordered(self) -> list:
        """Return scheduled tasks sorted by start time."""
        return sorted(self.scheduled_tasks, key=lambda item: tuple(map(int, item[1].split(":"))))

    def calculate_total_time(self) -> int:
        """Sum durations of all scheduled tasks and update total_time_used."""
        self.total_time_used = sum(t.duration for t, _ in self.scheduled_tasks)
        return self.total_time_used

    def has_conflicts(self) -> bool:
        """Return True if any two tasks have overlapping time slots."""
        def _to_minutes(s: str) -> int:
            h, m = map(int, s.split(":"))
            return h * 60 + m

        intervals = sorted(
            (_to_minutes(start), _to_minutes(start) + task.duration)
            for task, start in self.scheduled_tasks
        )
        for i in range(len(intervals) - 1):
            if intervals[i][1] > intervals[i + 1][0]:
                return True
        return False

    def get_summary(self) -> str:
        """Return a formatted, human-readable daily schedule."""
        lines = [f"Daily Plan for {self.pet.name} ({self.pet.species}) — {self.date}"]
        lines.append("-" * 52)
        for task, start in self.get_tasks_ordered():
            lines.append(f"  {start} — {task.name} ({task.duration} min) [{task.priority.lower()}]")
        lines.append("-" * 52)
        budget_min = int(self.owner.get_available_time() * 60)
        lines.append(f"Total: {self.total_time_used} min used / {budget_min} min available")
        if self.notes:
            lines.append("")
            lines.append(self.notes)
        return "\n".join(lines)


class Scheduler:
    # Fix: accept a list of pets so one Scheduler can plan for multiple pets
    def __init__(self, owner: Owner, pets: Optional[list] = None, available_tasks: Optional[list] = None):
        self.owner: Owner = owner
        self.pets: list = pets or []           # list[Pet]
        self.available_tasks: list = available_tasks or []  # list[Task]

    def generate_daily_plan(self, pet: Pet) -> DailyPlan:
        """Create and return a DailyPlan for the given pet based on owner constraints."""
        date = datetime.date.today().isoformat()
        plan = DailyPlan(date=date, pet=pet, owner=self.owner)

        # Only include tasks that belong to this pet or have no pet assignment
        pet_tasks = [t for t in self.available_tasks if t.pet is None or t.pet is pet]

        sorted_tasks = self.sort_tasks_by_priority(pet_tasks)
        kept, dropped = self.filter_tasks(sorted_tasks, self.owner.get_available_time())
        ordered = self.assign_time_windows(kept)
        scheduled = self.pack_into_slots(ordered, self.owner.get_available_time())

        for task, start_time in self.sort_by_time(scheduled):
            plan.add_task(task, start_time)

        plan.notes = self.explain_plan(plan, dropped)
        return plan

    def sort_tasks_by_priority(self, tasks: list) -> list:
        """Return tasks sorted HIGH → MEDIUM → LOW."""
        return sorted(tasks, key=lambda t: _PRIORITY_ORDER.get(t.priority.upper(), 99))

    def filter_tasks(self, tasks: list, available_time: float) -> tuple:
        """Return (kept, dropped) — drops tasks that exceed the time budget.

        Returning both lists lets explain_plan() report on what was excluded and why.
        Each entry in dropped is a (Task, reason_str) tuple.
        """
        budget_min = available_time * 60
        kept = []
        dropped = []
        time_used = 0

        for task in tasks:
            if time_used + task.duration <= budget_min:
                kept.append(task)
                time_used += task.duration
            else:
                dropped.append((task, "exceeds remaining time budget"))

        return kept, dropped

    # Fix: split the original fit_tasks_into_timeline into two focused methods
    def assign_time_windows(self, tasks: list) -> list:
        """Group tasks by their time_window preference (morning / afternoon / evening / any)."""
        buckets: dict = {"morning": [], "afternoon": [], "evening": [], "": []}
        for task in tasks:
            key = task.time_window.lower() if task.time_window.lower() in buckets else ""
            buckets[key].append(task)
        # Ordered: morning → afternoon → evening → unpreferred
        return buckets["morning"] + buckets["afternoon"] + buckets["evening"] + buckets[""]

    def pack_into_slots(self, tasks: list, time_available: float) -> list:
        """Assign concrete start times to tasks, respecting the grouped time windows."""
        # Single advancing cursor — windowed tasks jump to their window start if
        # the cursor hasn't reached it yet; otherwise they use the current cursor.
        # This prevents tasks with no preference from colliding with earlier windows.
        cursor = 8 * 60  # start at 08:00
        budget_min = time_available * 60
        time_used = 0
        result = []

        for task in tasks:
            if time_used + task.duration > budget_min:
                break
            window = task.time_window.lower()
            window_start = _WINDOW_STARTS.get(window)
            if window_start is not None and cursor < window_start:
                cursor = window_start

            start_str = f"{cursor // 60:02d}:{cursor % 60:02d}"
            result.append((task, start_str))
            cursor += task.duration
            time_used += task.duration

        return result

    def complete_task(self, task: Task) -> Optional[Task]:
        """Mark a task complete and automatically queue its next occurrence.

        Calls task.mark_complete(), then — for DAILY or WEEKLY tasks — creates
        an identical Task with completed=False and appends it to available_tasks
        so it will appear in the next generated plan. If available_tasks and
        task.pet.tasks are different list objects, the new task is added to both.

        MONTHLY and AS_NEEDED tasks are marked done but produce no recurrence
        because their schedule is not predictable on a fixed cadence.

        Args:
            task: The Task to complete. Must already be in available_tasks.

        Returns:
            The newly created next-occurrence Task, or None if no recurrence
            was scheduled (MONTHLY / AS_NEEDED frequency).
        """
        task.mark_complete()
        if task.frequency.upper() not in ("DAILY", "WEEKLY"):
            return None

        next_task = Task(
            name=task.name,
            duration=task.duration,
            priority=task.priority,
            frequency=task.frequency,
            description=task.description,
            time_window=task.time_window,
            pet=task.pet,
        )
        self.available_tasks.append(next_task)
        if task.pet is not None and self.available_tasks is not task.pet.tasks:
            task.pet.add_task(next_task)
        return next_task

    def filter_tasks_by(self, tasks: list, *, pet_name: str = None, completed: bool = None) -> list:
        """Return a subset of tasks matching the given criteria.

        Filters are applied with AND logic: a task must satisfy every supplied
        filter to be included. Both filters are keyword-only and optional —
        omit either to skip that check entirely.

        Args:
            tasks:      The flat list of Task objects to filter (e.g. available_tasks).
            pet_name:   Case-insensitive pet name to match against task.pet.name.
                        Tasks with no pet assigned (task.pet is None) are excluded
                        when this filter is active.
            completed:  Pass True to keep only completed tasks, False for pending only.

        Returns:
            A new list containing only the tasks that pass all active filters.
        """
        result = tasks
        if pet_name is not None:
            result = [t for t in result if t.pet is not None and t.pet.name.lower() == pet_name.lower()]
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        return result

    def sort_by_time(self, scheduled: list) -> list:
        """Return (Task, start_time_str) tuples sorted chronologically by start time.

        Uses a lambda as the sort key: each 'HH:MM' string is split on ':' and
        converted to a (hours, minutes) int tuple so Python's tuple comparison
        sorts by hour first, then minute. Zero-padded strings would sort correctly
        as plain strings too, but the numeric conversion makes the intent explicit
        and handles any non-padded inputs safely.

        Args:
            scheduled: list of (Task, 'HH:MM') tuples, in any order.

        Returns:
            A new sorted list; the original is not mutated.
        """
        return sorted(scheduled, key=lambda item: tuple(map(int, item[1].split(":"))))

    def find_conflicts(self, *plans: DailyPlan) -> list:
        """Return human-readable warning strings for every overlapping task pair.

        Strategy: all scheduled tasks from every supplied plan are flattened into
        a list of (task, start_min, end_min, pet_name) tuples. Every unique pair
        is then tested with the standard interval-overlap condition:
            start_A < end_B  AND  start_B < end_A
        This is O(n²) in the number of scheduled tasks — acceptable for the small
        daily task lists PawPal+ works with.

        Passing one plan checks for same-pet conflicts (two tasks for Rex at 08:00).
        Passing two or more plans checks cross-pet conflicts as well (Rex at 09:00
        and Mochi at 09:30 with a 60-min vet visit overlap).

        Never raises — a plan with zero scheduled tasks simply contributes nothing.

        Args:
            *plans: One or more DailyPlan objects to inspect.

        Returns:
            A list of warning strings, one per overlapping pair. Empty list means
            no conflicts were found.
        """
        def _to_min(s: str) -> int:
            h, m = map(int, s.split(":"))
            return h * 60 + m

        # Flatten all plans into (task, start_min, end_min, plan_label) tuples
        items = []
        for plan in plans:
            label = plan.pet.name
            for task, start_str in plan.scheduled_tasks:
                start = _to_min(start_str)
                items.append((task, start, start + task.duration, label))

        warnings = []
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                task_a, s_a, e_a, pet_a = items[i]
                task_b, s_b, e_b, pet_b = items[j]
                if s_a < e_b and s_b < e_a:
                    warnings.append(
                        f"WARNING: '{task_a.name}' ({pet_a}, "
                        f"{s_a // 60:02d}:{s_a % 60:02d}–{e_a // 60:02d}:{e_a % 60:02d}) "
                        f"overlaps '{task_b.name}' ({pet_b}, "
                        f"{s_b // 60:02d}:{s_b % 60:02d}–{e_b // 60:02d}:{e_b % 60:02d})"
                    )
        return warnings

    def validate_plan(self, plan: DailyPlan) -> bool:
        """Return True if the plan has no conflicts and fits within available time."""
        budget_min = plan.owner.get_available_time() * 60
        return not plan.has_conflicts() and plan.total_time_used <= budget_min

    def explain_plan(self, plan: DailyPlan, dropped: list) -> str:
        """Return a plain-English explanation of inclusions and exclusions.

        'dropped' is the second element of the tuple returned by filter_tasks().
        """
        budget_min = int(self.owner.get_available_time() * 60)
        lines = [
            f"Scheduled {len(plan.scheduled_tasks)} task(s) using "
            f"{plan.total_time_used} of {budget_min} available minutes."
        ]

        if dropped:
            lines.append(f"Skipped {len(dropped)} task(s) due to time constraints:")
            for task, reason in dropped:
                lines.append(f"  - {task.name} ({task.duration} min, {task.priority}): {reason}")

        return "\n".join(lines)
