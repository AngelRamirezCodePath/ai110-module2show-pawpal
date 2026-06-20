# Testing Playground

from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    # --- Owner ---
    owner = Owner(name="Alex", available_hours=2.0)  # 120 minutes per day

    # --- Pets ---
    biscuit = Pet(name="Biscuit", species="Dog", breed="Golden Retriever", age=3)
    luna    = Pet(name="Luna",    species="Cat", breed="Siamese",          age=5,
                  medical_conditions=["hyperthyroidism"])

    # --- Tasks for Biscuit ---
    walk      = Task("Morning walk",  30, "HIGH",   "DAILY",  time_window="morning",   pet=biscuit)
    feeding_b = Task("Feeding",       10, "HIGH",   "DAILY",  time_window="morning",   pet=biscuit)
    fetch     = Task("Fetch session", 20, "MEDIUM", "DAILY",  time_window="afternoon", pet=biscuit)

    # --- Tasks for Luna ---
    feeding_l = Task("Feeding",       10, "HIGH",   "DAILY",  time_window="morning",   pet=luna)
    medication = Task("Medication",    5, "HIGH",   "DAILY",  time_window="morning",   pet=luna)
    brushing   = Task("Brushing",     15, "MEDIUM", "WEEKLY", time_window="evening",   pet=luna)

    all_tasks = [walk, feeding_b, fetch, feeding_l, medication, brushing]

    # --- Scheduler ---
    scheduler = Scheduler(owner=owner, pets=[biscuit, luna], available_tasks=all_tasks)

    # --- Generate and print plans ---
    print("=" * 52)
    print("          TODAY'S SCHEDULE")
    print("=" * 52)

    for pet in [biscuit, luna]:
        plan = scheduler.generate_daily_plan(pet)
        print(plan.get_summary())
        print()


if __name__ == "__main__":
    main()
