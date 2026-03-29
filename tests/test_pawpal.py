import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
    task = Task(title="Walk dog", duration_minutes=30, priority="high")
    assert task.status == "incomplete"
    task.mark_complete()
    assert task.status == "complete"


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task(title="Feed Buddy", duration_minutes=10, priority="medium"))
    assert len(pet.tasks) == 1
