"""
tests/test_pawpal.py - Unit tests for PawPal+ core logic.

Tests verify critical behaviors:
- Task completion tracking
- Pet task management
- Basic scheduling constraints
"""

import pytest
from datetime import date, timedelta
from pawpal_system import Owner, Pet, CareTask, Scheduler


class TestTaskCompletion:
    """Tests for task completion status tracking."""

    def test_mark_complete_changes_status(self):
        """Verify that calling mark_complete() changes the task's completed status from False to True."""
        task = CareTask(
            title="Morning walk",
            category="exercise",
            duration_minutes=20,
            priority="high"
        )
        
        # Initially, task should not be completed
        assert task.completed is False
        
        # Mark the task as complete
        task.mark_complete()
        
        # Task should now be marked as completed
        assert task.completed is True


class TestTaskAddition:
    """Tests for adding and managing tasks on pets."""

    def test_add_task_increases_count(self):
        """Verify that adding a task to a pet increases that pet's task count."""
        pet = Pet(
            name="Mochi",
            species="dog",
            age=3
        )
        
        # Initially, pet should have no tasks
        assert len(pet.get_tasks()) == 0
        
        # Create and add a task
        task = CareTask(
            title="Feeding",
            category="feeding",
            duration_minutes=10,
            priority="high"
        )
        pet.add_task(task)
        
        # Pet's task count should now be 1
        assert len(pet.get_tasks()) == 1
        
        # Add a second task
        task2 = CareTask(
            title="Playtime",
            category="enrichment",
            duration_minutes=30,
            priority="medium"
        )
        pet.add_task(task2)
        
        # Pet's task count should now be 2
        assert len(pet.get_tasks()) == 2

    def test_add_multiple_tasks_maintains_list(self):
        """Verify that multiple tasks are correctly stored and retrievable."""
        pet = Pet(
            name="Luna",
            species="cat",
            age=5
        )
        
        tasks = [
            CareTask("Feeding", "feeding", 10, "high", required=True),
            CareTask("Litter cleaning", "hygiene", 5, "high", required=True),
            CareTask("Play", "enrichment", 15, "medium"),
        ]
        
        for task in tasks:
            pet.add_task(task)
        
        # Verify all tasks were added
        pet_tasks = pet.get_tasks()
        assert len(pet_tasks) == 3
        
        # Verify task titles match
        titles = [t.title for t in pet_tasks]
        assert titles == ["Feeding", "Litter cleaning", "Play"]


class TestRecurringTasks:
    """Tests for recurring task completion behavior."""

    def test_daily_completion_creates_task_due_tomorrow(self):
        """Verify daily completion auto-creates next task due the next day."""
        scheduler = Scheduler()
        pet = Pet(name="Mochi", species="dog")
        task = CareTask(
            title="Daily medication",
            category="medication",
            duration_minutes=5,
            priority="high",
            frequency="daily",
            due_date=date(2026, 3, 30),
        )
        pet.add_task(task)

        next_task = scheduler.mark_task_complete(
            pet=pet,
            task_title="Daily medication",
            completed_on=date(2026, 3, 30),
        )

        assert next_task is not None
        assert task.completed is True
        assert next_task.completed is False
        assert next_task.frequency == "daily"
        assert next_task.due_date == date(2026, 3, 31)
        assert len(pet.get_tasks()) == 2

    def test_weekly_completion_creates_task_due_in_seven_days(self):
        """Verify weekly completion auto-creates next task due in seven days."""
        scheduler = Scheduler()
        pet = Pet(name="Luna", species="cat")
        completion_day = date(2026, 3, 30)
        task = CareTask(
            title="Weekly grooming",
            category="grooming",
            duration_minutes=20,
            priority="medium",
            frequency="weekly",
            due_date=completion_day,
        )
        pet.add_task(task)

        next_task = scheduler.mark_task_complete(
            pet=pet,
            task_title="Weekly grooming",
            completed_on=completion_day,
        )

        assert next_task is not None
        assert task.completed is True
        assert next_task.frequency == "weekly"
        assert next_task.due_date == completion_day + timedelta(days=7)
        assert len(pet.get_tasks()) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
