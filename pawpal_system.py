from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Owner:
    name: str
    daily_time_available: int
    preferences: dict[str, str] = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def update_preferences(self, preferences: dict[str, str]) -> None:
        """Update owner preferences with new key-value pairs."""
        self.preferences.update(preferences)

    def can_fit_task(self, duration_minutes: int) -> bool:
        """Return whether a task duration fits the owner's daily time."""
        return duration_minutes <= self.daily_time_available

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove pets with a matching name from the owner's pet list."""
        self.pets = [pet for pet in self.pets if pet.name != pet_name]

    def get_pets(self) -> list[Pet]:
        """Return a copy of the owner's pets list."""
        return list(self.pets)


@dataclass
class CareTask:
    title: str
    category: str
    duration_minutes: int
    priority: str
    preferred_time: str = "anytime"
    required: bool = False
    completed: bool = False

    def is_high_priority(self) -> bool:
        """Return True when the task priority is high."""
        return self.priority.lower() == "high"

    def matches_preferences(self, preferences: dict[str, str]) -> bool:
        """Return whether the task matches owner time preferences."""
        preferred_time = preferences.get("preferred_time")
        if preferred_time is None or self.preferred_time == "anytime":
            return True
        return self.preferred_time == preferred_time

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        self.completed = True


@dataclass
class Pet:
    name: str
    species: str
    age: int = 0
    notes: str = ""
    tasks: list[CareTask] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task_title: str) -> None:
        """Remove tasks with a matching title from this pet."""
        self.tasks = [task for task in self.tasks if task.title != task_title]

    def get_tasks(self) -> list[CareTask]:
        """Return a copy of this pet's tasks."""
        return list(self.tasks)


@dataclass
class PlanItem:
    task: CareTask
    start_time: str
    end_time: str
    reason: str

    def format_for_display(self) -> str:
        """Return a human-readable schedule line for this plan item."""
        return f"{self.start_time}-{self.end_time}: {self.task.title} ({self.reason})"


@dataclass
class DailyPlan:
    date: str
    available_minutes: int
    items: list[PlanItem] = field(default_factory=list)
    skipped_tasks: list[CareTask] = field(default_factory=list)

    def add_item(self, item: PlanItem) -> None:
        """Add a plan item or move it to skipped tasks if it does not fit."""
        if item.task.duration_minutes > self.remaining_minutes():
            self.skipped_tasks.append(item.task)
            return
        self.items.append(item)

    def remaining_minutes(self) -> int:
        """Return remaining minutes after scheduled items are counted."""
        used_minutes = sum(item.task.duration_minutes for item in self.items)
        return self.available_minutes - used_minutes

    def get_summary(self) -> str:
        """Return a newline-joined summary of scheduled items."""
        if not self.items:
            return "No tasks scheduled."
        return "\n".join(item.format_for_display() for item in self.items)

    def is_valid_plan(self) -> bool:
        """Return True if the plan fits time and skips no required tasks."""
        total_time = sum(item.task.duration_minutes for item in self.items)
        if total_time > self.available_minutes:
            return False
        required_scheduled = {item.task.title for item in self.items if item.task.required}
        required_skipped = {task.title for task in self.skipped_tasks if task.required}
        if required_skipped:
            return False
        return True

    def get_all_tasks_considered(self) -> list[CareTask]:
        """Return all tasks that were either scheduled or skipped."""
        scheduled = [item.task for item in self.items]
        return scheduled + self.skipped_tasks


class Scheduler:
    def __init__(self, start_hour: int = 8):
        """Initialize the scheduler with a default start hour."""
        self.start_hour = start_hour
        self.start_minutes = start_hour * 60

    def generate_plan(self, owner: Owner, pet: Pet, tasks: list[CareTask]) -> DailyPlan:
        """Generate a daily plan from ranked tasks and owner constraints."""
        from datetime import datetime
        
        # Create a plan for today
        today = datetime.now().strftime("%Y-%m-%d")
        plan = DailyPlan(date=today, available_minutes=owner.daily_time_available)
        
        # Rank tasks by priority
        ranked_tasks = self.rank_tasks(tasks)
        selected_tasks = self.select_tasks(ranked_tasks, owner.daily_time_available)
        
        # Schedule selected tasks sequentially, starting at start_hour
        current_minutes = self.start_minutes
        
        for task in selected_tasks:
            start_time = self._minutes_to_time(current_minutes)
            end_time = self._minutes_to_time(current_minutes + task.duration_minutes)
            reason = self.explain_choice(task, owner)
            
            item = PlanItem(
                task=task,
                start_time=start_time,
                end_time=end_time,
                reason=reason
            )
            plan.add_item(item)
            current_minutes += task.duration_minutes
        
        # Any unscheduled tasks are collected in skipped_tasks by add_item overflow logic
        # Add tasks that didn't fit
        for task in tasks:
            if not any(item.task.title == task.title for item in plan.items) and task not in plan.skipped_tasks:
                plan.skipped_tasks.append(task)
        
        return plan

    def rank_tasks(self, tasks: list[CareTask]) -> list[CareTask]:
        """Rank tasks by required flag and priority from high to low."""
        # Define priority order
        priority_order = {"required": 0, "high": 1, "medium": 2, "low": 3}
        
        def sort_key(task: CareTask) -> tuple:
            # Required tasks sort first
            if task.required:
                return (0, 0)
            # Then by priority level
            priority_level = priority_order.get(task.priority.lower(), 4)
            return (1, priority_level)
        
        return sorted(tasks, key=sort_key)

    def select_tasks(self, tasks: list[CareTask], time_available: int) -> list[CareTask]:
        """Select tasks greedily in ranked order within available time."""
        selected = []
        time_used = 0
        
        for task in tasks:
            # Always include required tasks
            if task.required:
                selected.append(task)
                time_used += task.duration_minutes
            # For non-required tasks, only add if they fit
            elif time_used + task.duration_minutes <= time_available:
                selected.append(task)
                time_used += task.duration_minutes
        
        return selected

    def explain_choice(self, task: CareTask, owner: Owner) -> str:
        """Return a short reason string for a scheduling decision."""
        reasons = []
        
        if task.required:
            reasons.append("required")
        
        if task.is_high_priority():
            reasons.append("high priority")
        elif task.priority.lower() == "medium":
            reasons.append("medium priority")
        
        if task.matches_preferences(owner.preferences):
            preferred_time = owner.preferences.get("preferred_time")
            if preferred_time and task.preferred_time != "anytime":
                reasons.append(f"{preferred_time} preferred")
        
        return " | ".join(reasons) if reasons else "fits in schedule"

    def _minutes_to_time(self, minutes: int) -> str:
        """Convert minutes since midnight into HH:MM 24-hour format."""
        hours = (minutes // 60) % 24
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"