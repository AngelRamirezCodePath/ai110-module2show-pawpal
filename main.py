"""Testing playground for PawPal+ scheduling, sorting, and filtering."""

import datetime
from pawpal_system import Owner, Pet, Task, Scheduler, DailyPlan


def _build_scheduler() -> tuple:
    """Return (scheduler, all_tasks, biscuit, luna) pre-loaded with out-of-order tasks."""
    owner   = Owner(name="Alex", available_hours=2.0)
    biscuit = Pet(name="Biscuit", species="Dog", breed="Golden Retriever", age=3)
    luna    = Pet(name="Luna",    species="Cat", breed="Siamese", age=5,
                  medical_conditions=["hyperthyroidism"])

    # Tasks added OUT OF ORDER intentionally to test sort_by_time
    all_tasks = [
        Task("Fetch session", 20, "MEDIUM", "DAILY",  time_window="afternoon", pet=biscuit),
        Task("Morning walk",  30, "HIGH",   "DAILY",  time_window="morning",   pet=biscuit),
        Task("Feeding",       10, "HIGH",   "DAILY",  time_window="morning",   pet=biscuit),
        Task("Brushing",      15, "MEDIUM", "WEEKLY", time_window="evening",   pet=luna),
        Task("Feeding",       10, "HIGH",   "DAILY",  time_window="morning",   pet=luna),
        Task("Medication",     5, "HIGH",   "DAILY",  time_window="morning",   pet=luna),
    ]

    # Mark some tasks complete before scheduling to demo the filter
    all_tasks[1].mark_complete()   # Morning walk
    all_tasks[5].mark_complete()   # Medication

    scheduler = Scheduler(owner=owner, pets=[biscuit, luna], available_tasks=all_tasks)
    return scheduler, all_tasks, biscuit, luna


def main():
    """Demonstrate sort_by_time, filter_tasks_by, and complete_task."""
    scheduler, all_tasks, biscuit, luna = _build_scheduler()

    # -----------------------------------------------------------------------
    # 1. Generate and print plans (uses sort_by_time internally)
    # -----------------------------------------------------------------------
    print("=" * 52)
    print("          TODAY'S SCHEDULE  (sort_by_time)")
    print("=" * 52)
    for pet in [biscuit, luna]:
        print(scheduler.generate_daily_plan(pet).get_summary())
        print()

    # -----------------------------------------------------------------------
    # 2. Filter by pet name
    # -----------------------------------------------------------------------
    print("=" * 52)
    print("     FILTER: tasks belonging to Biscuit")
    print("=" * 52)
    for t in scheduler.filter_tasks_by(all_tasks, pet_name="Biscuit"):
        status = "done" if t.completed else "pending"
        print(f"  [{status}] {t.name} ({t.duration} min, {t.priority})")
    print()

    # -----------------------------------------------------------------------
    # 3. Filter by completion status
    # -----------------------------------------------------------------------
    print("=" * 52)
    print("     FILTER: completed tasks (all pets)")
    print("=" * 52)
    for t in scheduler.filter_tasks_by(all_tasks, completed=True):
        print(f"  [done]    {t.name} — {t.pet.name if t.pet else 'no pet'}")
    print()

    print("=" * 52)
    print("     FILTER: pending tasks (all pets)")
    print("=" * 52)
    for t in scheduler.filter_tasks_by(all_tasks, completed=False):
        print(f"  [pending] {t.name} — {t.pet.name if t.pet else 'no pet'}")
    print()

    # -----------------------------------------------------------------------
    # 4. Combine both filters: pending tasks for Luna only
    # -----------------------------------------------------------------------
    print("=" * 52)
    print("     FILTER: pending tasks for Luna only")
    print("=" * 52)
    for t in scheduler.filter_tasks_by(all_tasks, pet_name="Luna", completed=False):
        print(f"  [pending] {t.name} ({t.duration} min, {t.priority})")
    print()

    # -----------------------------------------------------------------------
    # 5. complete_task — auto-recurrence demo
    # -----------------------------------------------------------------------
    print("=" * 52)
    print("     AUTO-RECURRENCE: complete_task()")
    print("=" * 52)
    for task in [all_tasks[2], all_tasks[3]]:   # Feeding (biscuit), Brushing (luna)
        next_occ = scheduler.complete_task(task)
        if next_occ:
            label = "tomorrow" if task.frequency.upper() == "DAILY" else "next week"
            print(f"  Completed : {task.name} ({task.pet.name}) [{task.frequency}]")
            print(f"  Scheduled : {next_occ.name} for {label} (pending={not next_occ.completed})")
        else:
            print(f"  Completed : {task.name} — no recurrence (frequency={task.frequency})")
    print()

    print("  Pending tasks after auto-recurrence:")
    for t in scheduler.filter_tasks_by(all_tasks, completed=False):
        print(f"    [pending] {t.name} — {t.pet.name if t.pet else 'no pet'} [{t.frequency}]")

    # -----------------------------------------------------------------------
    # 6. find_conflicts — conflict detection demo
    # -----------------------------------------------------------------------
    print()
    print("=" * 52)
    print("     CONFLICT DETECTION: find_conflicts()")
    print("=" * 52)

    owner2  = Owner(name="Sam", available_hours=3.0)
    dog     = Pet(name="Rex",   species="Dog", breed="Labrador", age=2)
    cat     = Pet(name="Mochi", species="Cat", breed="Tabby",    age=4)
    today   = datetime.date.today().isoformat()

    # Same-pet plan: two tasks manually placed at the same start time (08:00)
    same_pet_plan = DailyPlan(date=today, pet=dog, owner=owner2)
    same_pet_plan.add_task(Task("Morning walk", 30, "HIGH",   "DAILY", pet=dog), "08:00")
    same_pet_plan.add_task(Task("Feeding",      10, "HIGH",   "DAILY", pet=dog), "08:00")  # overlaps walk

    print("  -- Same-pet conflicts (Rex) --")
    same_warnings = scheduler.find_conflicts(same_pet_plan)
    if same_warnings:
        for w in same_warnings:
            print(f"  {w}")
    else:
        print("  No conflicts found.")

    print()

    # Cross-pet plans: Rex and Mochi both scheduled at 08:00 — same owner, same time slot
    rex_plan   = DailyPlan(date=today, pet=dog,  owner=owner2)
    mochi_plan = DailyPlan(date=today, pet=cat,  owner=owner2)
    rex_plan.add_task(  Task("Vet visit",  60, "HIGH", "AS_NEEDED", pet=dog),  "09:00")
    mochi_plan.add_task(Task("Grooming",   45, "HIGH", "MONTHLY",   pet=cat),  "09:30")  # overlaps vet visit

    print("  -- Cross-pet conflicts (Rex + Mochi) --")
    cross_warnings = scheduler.find_conflicts(rex_plan, mochi_plan)
    if cross_warnings:
        for w in cross_warnings:
            print(f"  {w}")
    else:
        print("  No conflicts found.")

    print()

    # Clean plan — should produce no warnings
    clean_plan = DailyPlan(date=today, pet=dog, owner=owner2)
    clean_plan.add_task(Task("Morning walk", 30, "HIGH", "DAILY", pet=dog), "08:00")
    clean_plan.add_task(Task("Feeding",      10, "HIGH", "DAILY", pet=dog), "08:30")  # starts after walk ends

    print("  -- Clean plan (no conflicts expected) --")
    clean_warnings = scheduler.find_conflicts(clean_plan)
    if clean_warnings:
        for w in clean_warnings:
            print(f"  {w}")
    else:
        print("  No conflicts found.")


if __name__ == "__main__":
    main()
