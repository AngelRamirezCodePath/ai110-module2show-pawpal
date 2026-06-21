from pawpal_system import Pet, Task, Owner, Scheduler, DailyPlan
import datetime


def test_mark_complete_changes_status():
    """mark_complete() should flip completed from False to True."""
    task = Task(name="Morning walk", duration=30, priority="HIGH", frequency="DAILY")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its tasks list by one."""
    pet = Pet(name="Biscuit", species="Dog", breed="Golden Retriever", age=3)
    task = Task(name="Feeding", duration=10, priority="HIGH", frequency="DAILY")
    assert len(pet.tasks) == 0
    pet.add_task(task)
    assert len(pet.tasks) == 1


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """sort_by_time should order (Task, 'HH:MM') tuples by wall-clock time."""
    owner = Owner(name="Alex", available_hours=3.0)
    scheduler = Scheduler(owner=owner)

    task_a = Task(name="Evening walk",  duration=20, priority="LOW",    frequency="DAILY")
    task_b = Task(name="Morning meds",  duration=5,  priority="HIGH",   frequency="DAILY")
    task_c = Task(name="Afternoon play", duration=15, priority="MEDIUM", frequency="DAILY")

    unordered = [(task_a, "18:00"), (task_b, "08:00"), (task_c, "12:00")]
    result = scheduler.sort_by_time(unordered)

    assert [start for _, start in result] == ["08:00", "12:00", "18:00"]


def test_generate_daily_plan_tasks_in_chronological_order():
    """generate_daily_plan should produce a plan whose scheduled_tasks are in time order."""
    owner = Owner(name="Alex", available_hours=3.0)
    pet   = Pet(name="Rex", species="Dog", breed="Lab", age=2)

    tasks = [
        Task("Evening walk",   20, "LOW",    "DAILY", time_window="evening",   pet=pet),
        Task("Morning feeding", 10, "HIGH",   "DAILY", time_window="morning",   pet=pet),
        Task("Afternoon play",  15, "MEDIUM", "DAILY", time_window="afternoon", pet=pet),
    ]
    scheduler = Scheduler(owner=owner, pets=[pet], available_tasks=tasks)
    plan = scheduler.generate_daily_plan(pet)

    start_times = [start for _, start in plan.scheduled_tasks]
    assert start_times == sorted(
        start_times,
        key=lambda s: tuple(map(int, s.split(":"))),
    ), f"Tasks not in chronological order: {start_times}"


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

def test_complete_daily_task_creates_new_pending_task():
    """Completing a DAILY task should append a new uncompleted task to available_tasks."""
    owner = Owner(name="Alex", available_hours=2.0)
    pet   = Pet(name="Biscuit", species="Dog", breed="Golden Retriever", age=3)
    task  = Task(name="Morning walk", duration=30, priority="HIGH", frequency="DAILY", pet=pet)

    scheduler = Scheduler(owner=owner, pets=[pet], available_tasks=[task])
    next_task = scheduler.complete_task(task)

    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.name == task.name
    assert next_task.frequency == "DAILY"
    assert next_task in scheduler.available_tasks


def test_complete_monthly_task_creates_no_recurrence():
    """Completing a MONTHLY task should return None and not grow available_tasks."""
    owner = Owner(name="Alex", available_hours=2.0)
    pet   = Pet(name="Luna", species="Cat", breed="Siamese", age=5)
    task  = Task(name="Vet checkup", duration=60, priority="HIGH", frequency="MONTHLY", pet=pet)

    scheduler = Scheduler(owner=owner, pets=[pet], available_tasks=[task])
    result = scheduler.complete_task(task)

    assert result is None
    assert len(scheduler.available_tasks) == 1  # no new task appended


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_find_conflicts_flags_overlapping_tasks():
    """find_conflicts should return a warning when two tasks share overlapping time slots."""
    owner = Owner(name="Sam", available_hours=3.0)
    pet   = Pet(name="Rex", species="Dog", breed="Lab", age=2)
    today = datetime.date.today().isoformat()

    plan = DailyPlan(date=today, pet=pet, owner=owner)
    plan.add_task(Task("Morning walk", 30, "HIGH", "DAILY", pet=pet), "08:00")
    plan.add_task(Task("Feeding",      10, "HIGH", "DAILY", pet=pet), "08:00")  # overlaps walk

    scheduler = Scheduler(owner=owner)
    warnings = scheduler.find_conflicts(plan)

    assert len(warnings) >= 1
    assert any("WARNING" in w for w in warnings)


def test_find_conflicts_no_false_positive_for_back_to_back():
    """Back-to-back tasks (A ends exactly when B starts) must NOT be flagged."""
    owner = Owner(name="Sam", available_hours=3.0)
    pet   = Pet(name="Rex", species="Dog", breed="Lab", age=2)
    today = datetime.date.today().isoformat()

    plan = DailyPlan(date=today, pet=pet, owner=owner)
    plan.add_task(Task("Morning walk", 30, "HIGH", "DAILY", pet=pet), "08:00")  # ends 08:30
    plan.add_task(Task("Feeding",      10, "HIGH", "DAILY", pet=pet), "08:30")  # starts 08:30

    scheduler = Scheduler(owner=owner)
    warnings = scheduler.find_conflicts(plan)

    assert warnings == [], f"Unexpected conflict warnings: {warnings}"


def test_find_conflicts_detects_cross_pet_overlap():
    """find_conflicts should catch overlapping tasks across two different pets' plans."""
    owner = Owner(name="Sam", available_hours=3.0)
    dog   = Pet(name="Rex",   species="Dog", breed="Lab",   age=2)
    cat   = Pet(name="Mochi", species="Cat", breed="Tabby", age=4)
    today = datetime.date.today().isoformat()

    rex_plan   = DailyPlan(date=today, pet=dog, owner=owner)
    mochi_plan = DailyPlan(date=today, pet=cat, owner=owner)
    rex_plan.add_task(  Task("Vet visit", 60, "HIGH", "AS_NEEDED", pet=dog), "09:00")  # ends 10:00
    mochi_plan.add_task(Task("Grooming",  45, "HIGH", "MONTHLY",   pet=cat), "09:30")  # ends 10:15

    scheduler = Scheduler(owner=owner)
    warnings = scheduler.find_conflicts(rex_plan, mochi_plan)

    assert len(warnings) >= 1
