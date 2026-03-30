"""
tests/test_pawpal.py - Unit tests for PawPal+ core logic.

Tests verify critical behaviors:
- Task completion tracking
- Pet task management
- Sorting correctness
- Recurrence logic
- Conflict detection
- Scheduling happy paths and edge cases
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


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------

class TestSortingByTime:
    """Tests for sort_tasks_by_time chronological ordering."""

    def test_sorts_tasks_in_chronological_order(self):
        """Verify tasks entered out of order come back in HH:MM ascending order."""
        scheduler = Scheduler()
        tasks = [
            CareTask("Evening meds",  "medication",  5,  "high",   time="19:00"),
            CareTask("Morning walk",  "exercise",    20, "high",   time="07:30"),
            CareTask("Lunch feeding", "feeding",     10, "medium", time="12:00"),
            CareTask("Night check",   "hygiene",     5,  "low",    time="21:45"),
            CareTask("Mid-morning",   "enrichment",  15, "medium", time="10:15"),
        ]

        sorted_tasks = scheduler.sort_tasks_by_time(tasks)
        times = [t.time for t in sorted_tasks]

        assert times == ["07:30", "10:15", "12:00", "19:00", "21:45"]

    def test_sort_empty_list_returns_empty(self):
        """Verify sorting an empty list returns [] without raising (edge case E6)."""
        scheduler = Scheduler()
        assert scheduler.sort_tasks_by_time([]) == []

    def test_sort_single_task_returns_same_task(self):
        """Verify a single-task list is returned unchanged."""
        scheduler = Scheduler()
        task = CareTask("Feeding", "feeding", 10, "high", time="08:00")
        result = scheduler.sort_tasks_by_time([task])
        assert result == [task]

    def test_sort_tasks_with_identical_times_preserves_all(self):
        """Verify all tasks are present even when two share the same time."""
        scheduler = Scheduler()
        tasks = [
            CareTask("Walk",    "exercise", 20, "high",   time="08:00"),
            CareTask("Feeding", "feeding",  10, "high",   time="08:00"),
            CareTask("Play",    "enrichment", 15, "medium", time="10:00"),
        ]
        result = scheduler.sort_tasks_by_time(tasks)
        assert len(result) == 3
        assert result[-1].time == "10:00"


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

class TestConflictDetection:
    """Tests for detect_time_conflicts warning logic."""

    def test_no_conflicts_returns_empty_list(self):
        """Verify no warnings when all tasks have distinct times (happy path H5)."""
        scheduler = Scheduler()
        owner = Owner(name="Jordan", daily_time_available=120)
        pet = Pet(name="Mochi", species="dog")
        pet.add_task(CareTask("Walk",    "exercise", 20, "high",   time="07:30"))
        pet.add_task(CareTask("Feeding", "feeding",  10, "high",   time="12:00"))
        owner.add_pet(pet)

        assert scheduler.detect_time_conflicts(owner) == []

    def test_same_pet_same_time_triggers_warning(self):
        """Verify a warning is raised when two tasks on the same pet share a time (edge case E3)."""
        scheduler = Scheduler()
        owner = Owner(name="Jordan", daily_time_available=120)
        pet = Pet(name="Mochi", species="dog")
        pet.add_task(CareTask("Walk",    "exercise", 20, "high", time="08:00"))
        pet.add_task(CareTask("Feeding", "feeding",  10, "high", time="08:00"))
        owner.add_pet(pet)

        warnings = scheduler.detect_time_conflicts(owner)
        assert len(warnings) == 1
        assert "08:00" in warnings[0]
        assert "Mochi" in warnings[0]

    def test_cross_pet_same_time_triggers_warning(self):
        """Verify a cross-pet warning when two different pets have tasks at the same time."""
        scheduler = Scheduler()
        owner = Owner(name="Jordan", daily_time_available=120)

        dog = Pet(name="Mochi", species="dog")
        dog.add_task(CareTask("Walk",    "exercise", 20, "high", time="08:00"))

        cat = Pet(name="Luna", species="cat")
        cat.add_task(CareTask("Feeding", "feeding",  10, "high", time="08:00"))

        owner.add_pet(dog)
        owner.add_pet(cat)

        warnings = scheduler.detect_time_conflicts(owner)
        assert len(warnings) == 1
        assert "08:00" in warnings[0]
        assert "Mochi" in warnings[0]
        assert "Luna" in warnings[0]

    def test_no_pets_returns_empty_list(self):
        """Verify no crash or warnings when owner has no pets."""
        scheduler = Scheduler()
        owner = Owner(name="Jordan", daily_time_available=120)
        assert scheduler.detect_time_conflicts(owner) == []


# ---------------------------------------------------------------------------
# Scheduling happy paths
# ---------------------------------------------------------------------------

class TestSchedulingHappyPaths:
    """Tests for generate_plan expected/normal operation."""

    def _make_owner_and_pet(self, minutes=120):
        owner = Owner(name="Jordan", daily_time_available=minutes)
        pet = Pet(name="Mochi", species="dog")
        owner.add_pet(pet)
        return owner, pet

    def test_all_tasks_fit_nothing_skipped(self):
        """Verify all tasks appear in plan.items when they fit in available time (happy path H1)."""
        owner, pet = self._make_owner_and_pet(minutes=120)
        pet.add_task(CareTask("Walk",    "exercise",   20, "high"))
        pet.add_task(CareTask("Feeding", "feeding",    10, "high"))
        pet.add_task(CareTask("Play",    "enrichment", 30, "medium"))

        plan = Scheduler().generate_plan(owner, pet, pet.get_tasks())

        assert len(plan.items) == 3
        assert plan.skipped_tasks == []
        assert plan.is_valid_plan() is True

    def test_required_task_is_first_in_plan(self):
        """Verify required tasks are always scheduled first regardless of input order (happy path H3)."""
        owner, pet = self._make_owner_and_pet()
        pet.add_task(CareTask("Play",    "enrichment", 30, "medium"))
        pet.add_task(CareTask("Meds",    "medication", 5,  "high",  required=True))
        pet.add_task(CareTask("Feeding", "feeding",    10, "high"))

        plan = Scheduler().generate_plan(owner, pet, pet.get_tasks())

        assert plan.items[0].task.title == "Meds"

    def test_plan_times_start_at_scheduler_start_hour(self):
        """Verify the first scheduled item begins at the configured start hour."""
        owner, pet = self._make_owner_and_pet()
        pet.add_task(CareTask("Walk", "exercise", 20, "high"))

        plan = Scheduler(start_hour=9).generate_plan(owner, pet, pet.get_tasks())

        assert plan.items[0].start_time == "09:00"
        assert plan.items[0].end_time == "09:20"


# ---------------------------------------------------------------------------
# Scheduling edge cases
# ---------------------------------------------------------------------------

class TestSchedulingEdgeCases:
    """Tests for boundary and unusual scheduling conditions."""

    def _make_owner_and_pet(self, minutes=120):
        owner = Owner(name="Jordan", daily_time_available=minutes)
        pet = Pet(name="Mochi", species="dog")
        owner.add_pet(pet)
        return owner, pet

    def test_pet_with_no_tasks_returns_empty_plan(self):
        """Verify no crash and empty plan when pet has zero tasks (edge case E1)."""
        owner, pet = self._make_owner_and_pet()
        plan = Scheduler().generate_plan(owner, pet, [])

        assert plan.items == []
        assert plan.skipped_tasks == []
        assert plan.is_valid_plan() is True

    def test_optional_tasks_skipped_when_time_exceeded(self):
        """Verify optional tasks that don't fit go to skipped_tasks (edge case E2)."""
        owner, pet = self._make_owner_and_pet(minutes=25)
        required = CareTask("Meds",  "medication", 10, "high",   required=True)
        optional = CareTask("Walk",  "exercise",   20, "medium")
        pet.add_task(required)
        pet.add_task(optional)

        plan = Scheduler().generate_plan(owner, pet, pet.get_tasks())

        scheduled_titles = [i.task.title for i in plan.items]
        skipped_titles   = [t.title for t in plan.skipped_tasks]
        assert "Meds" in scheduled_titles
        assert "Walk" in skipped_titles

    def test_required_task_always_scheduled_even_over_time_limit(self):
        """Verify required tasks are never skipped even when they exceed available time (edge case E2)."""
        owner, pet = self._make_owner_and_pet(minutes=5)
        required = CareTask("Insulin shot", "medication", 10, "high", required=True)
        pet.add_task(required)

        plan = Scheduler().generate_plan(owner, pet, pet.get_tasks())

        assert any(i.task.title == "Insulin shot" for i in plan.items)
        assert required not in plan.skipped_tasks

    def test_once_task_completion_returns_none(self):
        """Verify mark_task_complete returns None for a non-recurring task (edge case E5)."""
        scheduler = Scheduler()
        pet = Pet(name="Mochi", species="dog")
        pet.add_task(CareTask("Bath", "grooming", 30, "low", frequency="once"))

        result = scheduler.mark_task_complete(pet, "Bath")

        assert result is None
        assert len(pet.get_tasks()) == 1

    def test_filter_tasks_nonexistent_pet_returns_empty(self):
        """Verify filter_tasks returns [] for an unknown pet name without raising (edge case E7)."""
        scheduler = Scheduler()
        owner = Owner(name="Jordan", daily_time_available=120)
        pet = Pet(name="Mochi", species="dog")
        pet.add_task(CareTask("Walk", "exercise", 20, "high"))
        owner.add_pet(pet)

        result = scheduler.filter_tasks(owner, pet_name="NoSuchPet")
        assert result == []

    def test_same_name_tasks_on_different_pets_scheduled_independently(self):
        """Verify two tasks named 'Feeding' on different pets are each scheduled (edge case E4)."""
        scheduler = Scheduler()
        owner = Owner(name="Jordan", daily_time_available=120)

        dog = Pet(name="Mochi", species="dog")
        dog.add_task(CareTask("Feeding", "feeding", 10, "high", required=True))

        cat = Pet(name="Luna", species="cat")
        cat.add_task(CareTask("Feeding", "feeding", 10, "high", required=True))

        owner.add_pet(dog)
        owner.add_pet(cat)

        dog_plan = scheduler.generate_plan(owner, dog, dog.get_tasks())
        cat_plan = scheduler.generate_plan(owner, cat, cat.get_tasks())

        assert len(dog_plan.items) == 1
        assert len(cat_plan.items) == 1
        assert dog_plan.items[0].task is not cat_plan.items[0].task


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
