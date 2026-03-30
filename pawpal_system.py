from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Owner:
    name: str
    daily_time_available: int
    preferences: dict[str, str] = field(default_factory=dict)

    def update_preferences(self, preferences: dict[str, str]) -> None:
        self.preferences.update(preferences)

    def can_fit_task(self, duration_minutes: int) -> bool:
        return duration_minutes <= self.daily_time_available


@dataclass
class CareTask:
    title: str
    category: str
    duration_minutes: int
    priority: str
    preferred_time: str = "anytime"
    required: bool = False

    def is_high_priority(self) -> bool:
        return self.priority.lower() == "high"

    def matches_preferences(self, preferences: dict[str, str]) -> bool:
        preferred_time = preferences.get("preferred_time")
        if preferred_time is None or self.preferred_time == "anytime":
            return True
        return self.preferred_time == preferred_time


@dataclass
class Pet:
    name: str
    species: str
    age: int = 0
    notes: str = ""
    tasks: list[CareTask] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        self.tasks.append(task)

    def remove_task(self, task_title: str) -> None:
        self.tasks = [task for task in self.tasks if task.title != task_title]

    def get_tasks(self) -> list[CareTask]:
        return list(self.tasks)


@dataclass
class PlanItem:
    task: CareTask
    start_time: str
    end_time: str
    reason: str

    def format_for_display(self) -> str:
        return f"{self.start_time}-{self.end_time}: {self.task.title} ({self.reason})"


@dataclass
class DailyPlan:
    date: str
    available_minutes: int
    items: list[PlanItem] = field(default_factory=list)
    skipped_tasks: list[CareTask] = field(default_factory=list)

    def add_item(self, item: PlanItem) -> None:
        self.items.append(item)

    def remaining_minutes(self) -> int:
        used_minutes = sum(item.task.duration_minutes for item in self.items)
        return self.available_minutes - used_minutes

    def get_summary(self) -> str:
        if not self.items:
            return "No tasks scheduled."
        return "\n".join(item.format_for_display() for item in self.items)


class Scheduler:
    def generate_plan(self, owner: Owner, pet: Pet, tasks: list[CareTask]) -> DailyPlan:
        raise NotImplementedError("Implement plan generation logic.")

    def rank_tasks(self, tasks: list[CareTask]) -> list[CareTask]:
        raise NotImplementedError("Implement task ranking logic.")

    def select_tasks(self, tasks: list[CareTask], time_available: int) -> list[CareTask]:
        raise NotImplementedError("Implement task selection logic.")

    def explain_choice(self, task: CareTask, owner: Owner) -> str:
        raise NotImplementedError("Implement explanation logic.")