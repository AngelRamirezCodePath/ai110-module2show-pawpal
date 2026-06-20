from pawpal_system import Pet, Task


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
