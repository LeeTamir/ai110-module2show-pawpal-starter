# PawPal+ Project Reflection

## 1. System Design

- A user should be able to enter basic info about themselves and their pet.
- A user should be able to add and edit tasks with duration and priority.
- A user should be able to see a generated plan/schedule and the reasoning behind it.

**a. Initial design**

- My initial UML design focused on keeping the system small and centered on the scheduling problem. I used six main classes: `Owner`, `Pet`, `CareTask`, `Scheduler`, `DailyPlan`, and `PlanItem`.
- The goal was to separate input data from planning logic. `Owner`, `Pet`, and `CareTask` hold the core information entered by the user. `Scheduler` makes decisions based on constraints and priorities. `DailyPlan` represents the result for a single day, and `PlanItem` stores each scheduled task with timing and reasoning.
- I avoided extra classes like separate priority engines, rule objects, or inheritance trees because the project requirements do not justify that complexity yet.

```mermaid
classDiagram
		class Owner {
				+name: str
				+daily_time_available: int
				+preferences: dict
				+update_preferences(preferences)
				+can_fit_task(duration_minutes) bool
		}

		class Pet {
				+name: str
				+species: str
				+age: int
				+notes: str
				+add_task(task)
				+remove_task(task_title)
				+get_tasks() list
		}

		class CareTask {
				+title: str
				+category: str
				+duration_minutes: int
				+priority: str
				+preferred_time: str
				+required: bool
				+is_high_priority() bool
				+matches_preferences(preferences) bool
		}

		class Scheduler {
				+generate_plan(owner, pet, tasks) DailyPlan
				+rank_tasks(tasks) list
				+select_tasks(tasks, time_available) list
				+explain_choice(task, owner) str
		}

		class DailyPlan {
				+date: str
				+available_minutes: int
				+items: list
				+skipped_tasks: list
				+add_item(item)
				+remaining_minutes() int
				+get_summary() str
		}

		class PlanItem {
				+task: CareTask
				+start_time: str
				+end_time: str
				+reason: str
				+format_for_display() str
		}

		Owner "1" --> "1..*" Pet : cares for
		Pet "1" --> "0..*" CareTask : needs
		Scheduler ..> Owner : reads constraints
		Scheduler ..> Pet : reads pet info
		Scheduler ..> CareTask : ranks/selects
		Scheduler --> DailyPlan : creates
		DailyPlan "1" *-- "0..*" PlanItem : contains
		PlanItem --> CareTask : references
```

- `Owner`
	Holds the owner's available time and preferences. It only needs behavior related to constraints, not scheduling decisions.

- `Pet`
	Holds basic pet details and the set of tasks associated with that pet. This keeps pet-specific data separate from owner preferences.

- `CareTask`
	Represents one unit of care such as walking, feeding, medication, or grooming. It stores the attributes the README explicitly calls for, especially duration and priority.

- `Scheduler`
	Encapsulates the planning logic. This keeps decision-making in one place instead of scattering it across task or UI code.

- `DailyPlan`
	Stores the output of the scheduling process for one day. It gives the app a clean object to display in the UI and test in unit tests.

- `PlanItem`
	Represents a scheduled task in the final plan, including timing and explanation. I kept this class because the project requires both a plan and reasoning, and mixing that directly into `CareTask` would blur the difference between a task definition and a scheduled result.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
