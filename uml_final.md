# PawPal+ Final UML Class Diagram

```mermaid
classDiagram
    class Owner {
        +name: str
        +daily_time_available: int
        +preferences: dict
        +pets: list~Pet~
        +update_preferences(preferences)
        +can_fit_task(duration_minutes) bool
        +add_pet(pet)
        +remove_pet(pet_name)
        +get_pets() list
    }

    class Pet {
        +name: str
        +species: str
        +age: int
        +notes: str
        +tasks: list~CareTask~
        +add_task(task)
        +remove_task(task_title)
        +get_tasks() list
    }

    class CareTask {
        +title: str
        +category: str
        +duration_minutes: int
        +priority: str
        +time: str
        +preferred_time: str
        +required: bool
        +completed: bool
        +frequency: str
        +due_date: date
        +is_high_priority() bool
        +matches_preferences(preferences) bool
        +mark_complete()
        +create_next_occurrence(base_date) CareTask
    }

    class Scheduler {
        +start_hour: int
        +start_minutes: int
        +generate_plan(owner, pet, tasks) DailyPlan
        +rank_tasks(tasks) list
        +select_tasks(tasks, time_available) list
        +explain_choice(task, owner) str
        +sort_tasks_by_time(tasks) list
        +filter_tasks(owner, completed, pet_name) list
        +mark_task_complete(pet, task_title, completed_on) CareTask
        +detect_time_conflicts(owner) list
        -_minutes_to_time(minutes) str
    }

    class DailyPlan {
        +date: str
        +available_minutes: int
        +items: list~PlanItem~
        +skipped_tasks: list~CareTask~
        +add_item(item)
        +remaining_minutes() int
        +get_summary() str
        +is_valid_plan() bool
        +get_all_tasks_considered() list
    }

    class PlanItem {
        +task: CareTask
        +start_time: str
        +end_time: str
        +reason: str
        +format_for_display() str
    }

    Owner "1" *-- "0..*" Pet : owns
    Pet "1" *-- "0..*" CareTask : has
    Scheduler ..> Owner : reads constraints
    Scheduler ..> Pet : reads tasks / marks complete
    Scheduler ..> CareTask : ranks / selects / recurs
    Scheduler --> DailyPlan : creates
    DailyPlan "1" *-- "0..*" PlanItem : contains
    DailyPlan "0..*" --> "0..*" CareTask : skipped
    PlanItem --> CareTask : references
```

## What changed from the initial diagram

| Class | Changes |
|---|---|
| `Owner` | Added `pets` field (the 1-to-many relationship is now a **composition**, not just an association). Added `add_pet`, `remove_pet`, `get_pets`. |
| `CareTask` | Added `time`, `completed`, `frequency`, `due_date` fields to support scheduling, completion tracking, and recurrence. Added `mark_complete` and `create_next_occurrence`. |
| `Pet` | Added `tasks` field explicitly — the 1-to-many to `CareTask` is now a **composition** inside `Pet`, not just an association arrow. |
| `Scheduler` | Added `start_hour` / `start_minutes` instance fields. Added `sort_tasks_by_time`, `filter_tasks`, `mark_task_complete`, `detect_time_conflicts`, and private `_minutes_to_time`. |
| `DailyPlan` | Added `is_valid_plan` (invariant check) and `get_all_tasks_considered` (scheduled + skipped combined). |
| Relationships | `Owner → Pet` upgraded from association to **composition** (`*--`). `Pet → CareTask` upgraded from association to **composition**. Added explicit `DailyPlan → CareTask` skipped arrow. |
