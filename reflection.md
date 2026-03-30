# PawPal+ Project Reflection

## 1. System Design

- A user should be able to enter basic info about themselves and their pet.
- A user should be able to add and edit tasks with duration and priority.
- A user should be able to see a generated plan/schedule and the reasoning behind it.

**a. Initial design**

- My initial UML design focused on keeping the system small and centered on the scheduling problem. I used six main classes: `Owner`, `Pet`, `CareTask`, `Scheduler`, `DailyPlan`, and `PlanItem`.
- The goal was to separate input data from planning logic. `Owner`, `Pet`, and `CareTask` hold the core information entered by the user. `Scheduler` makes decisions based on constraints and priorities. `DailyPlan` represents the result for a single day, and `PlanItem` stores each scheduled task with timing and reasoning.
- I avoided extra classes like separate priority engines, rule objects, or inheritance trees because the project requirements do not justify that complexity yet.

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

- Yes, I made three key changes during the skeleton phase before implementation:

  1. **Added pets collection to Owner.** The UML showed Owner "1" → "1..*" Pet, but the Owner class had no way to hold pets. This would have forced the scheduler to receive owner and pet as separate, disconnected parameters. I added a `pets: list[Pet]` field and methods `add_pet()`, `remove_pet()`, and `get_pets()` to enforce the 1-to-many relationship properly.
  
  2. **Time validation and overflow handling in DailyPlan.** I realized `add_item()` was blindly appending tasks without checking if they fit in remaining time. I updated it to check `remaining_minutes()` and automatically move tasks that don't fit into `skipped_tasks`. This ensures the scheduler never overschedules a day.
  
  3. **Added plan validation method.** I created `is_valid_plan()` to verify two invariants: total scheduled time ≤ available time, and no required tasks are skipped. This gives the scheduler a way to check its own work and the UI a way to ensure the plan is sound before displaying it.

- Without Owner owning its pets, time overflow protection, and plan validation, the scheduler would have had to handle all these concerns itself, duplicating logic and making testing harder. Moving these checks into the data objects makes each class responsible for its own constraints.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- My scheduler considers five constraints:
  1. **Time availability** – All selected tasks must fit within the owner's `daily_time_available` (in minutes).
  2. **Task priority** – Tasks are ranked by priority level: required tasks first, then high/medium/low. Required tasks are always scheduled regardless of fit.
  3. **Owner preferences** – Tasks check `matches_preferences()` against owner preferences (e.g., preferred time of day), used in reasoning text but not as a hard filter.
  4. **Task recurrence** – Daily and weekly tasks auto-generate a next occurrence on completion using `timedelta`, so the scheduler always has an up-to-date task list without manual re-entry.
  5. **Time conflict detection** – `detect_time_conflicts()` scans tasks across all pets for shared `HH:MM` times and returns warning messages rather than crashing, allowing the owner to decide how to resolve overlaps.

- Time and priority are non-negotiable because the README explicitly requires them. Recurrence and conflict detection were added because a realistic daily care routine involves repeating tasks and a single owner managing multiple pets at once. Owner preferences remain soft constraints to keep the scheduler predictable and explainable.

**b. Tradeoffs**

- **Greedy selection over global optimization.** The scheduler ranks tasks by priority, then packs them into available time in order. This is predictable and testable, but not globally optimal. For example, two medium-priority tasks taking 50 minutes will be chosen over three low-priority tasks taking 45 minutes, even if fitting the low-priority tasks would complete more care goals. An optimal solver could find a better set, but at the cost of much greater complexity and harder-to-explain decisions.

- **Why this tradeoff is reasonable:** PawPal+ is a personal assistant where owner trust and transparency matter more than mathematical optimization. Greedy selection means the owner can always predict which tasks will be chosen, and the UI can explain every decision clearly. If requirements change to "maximize task count" or "balance variety across categories," this tradeoff would need revisiting.

---

## 3. AI Collaboration

**a. How you used AI**

- I used Copilot in distinct ways across the project lifecycle, by designing the initial UML and class responsibilities, implementation support for method scaffolding and docstring completion, and debugging/refactoring support once tests exposed edge-case failures.
- The most effective Copilot features for building the scheduler were iterative code generation in chat for quickly drafting class methods in `Scheduler`, `DailyPlan`, and `CareTask`, targeted test generation for specific behaviors (recurrence, conflict detection, and edge cases), which helped me expand from a small starter suite to full coverage, and refactor suggestions that improved clarity and performance, especially replacing repeated scans with identity-set lookups in skipped-task detection.

**b. Judgment and verification**

- One suggestion I intentionally modified was the early overflow behavior in `DailyPlan.add_item()`. The logic treated any over-limit task the same and moved it to `skipped_tasks`, which also affected required tasks. I rejected that as-is and changed the rule to: only optional tasks can be skipped for time; required tasks must still be scheduled.
- I verified that decision with tests, not intuition. The edge-case test for required-over-limit tasks failed before the fix and passed after adding the `not item.task.required` guard. I also reran the full suite to ensure the fix did not break existing behavior.
- Using separate chat sessions for different phases kept the project organized and reduced context drift. I treated each session as a focused workstream:
  1. Design session for UML and class boundaries.
  2. Core implementation session for scheduler behavior and data model methods.
  3. Testing session for expanding coverage and validating edge cases.
  4. UI integration/documentation session for Streamlit wiring and README/reflection updates.
- This separation made it easier to ask narrower questions, compare decisions by phase, and avoid mixing architectural choices with UI polish or test-writing concerns.

---

## 4. Testing and Verification

**a. What you tested**

- I tested the scheduler and task model across both normal usage and edge conditions. The suite covers task completion state, task addition/removal behavior, recurrence logic, time sorting, behavior for empty lists, one-item lists, identical times, and unsorted input, conflict detection, happy-path scheduling, and edge-case scheduling.
- These tests were important because each one maps directly to a real user expectation. Required care should not disappear, recurring tasks should reappear automatically, and owners should be warned about overlaps before they execute a plan. The tests also protected against regressions while I added new features late in development.

**b. Confidence**

- I am highly confident in the backend scheduler logic because the final suite passes all 22 of my tests, including both happy paths and intentionally difficult edge cases. My confidence is strongest for deterministic logic in ranking, selection, recurrence, sorting, filtering, and conflict warning generation.
- If I had more time, the next edge cases I would test are input validation edge cases, large task sets, multi-day recurrence flows, UI-level integration tests, and impossible schedules.

---

## 5. Reflection

**a. What went well**

- I am most satisfied with the combination of clean class boundaries and strong test coverage. The model objects own their own constraints, `Scheduler` owns decision-making, and the final suite validates both happy paths and edge cases. That structure made later features (recurrence, filtering, conflict warnings) easier to add without rewriting the system.

**b. What you would improve**

- In another iteration, I would add automated UI/integration tests around `app.py` and strengthen user-facing validation for time input format (`HH:MM`) and impossible schedules (for example, required tasks that exceed available time). I would also consider adding a configurable optimization mode for users who want "maximize number of tasks" instead of strict priority-first behavior.

**c. Key takeaway**

- My biggest takeaway is what it means to be the lead architect when collaborating with powerful AI tools. AI can generate options quickly, but I am responsible for system boundaries, correctness criteria, and tradeoff decisions.
- In practice, being the lead architect meant defining clear class responsibilities before accepting generated code, deciding which rules are hard invariants (required tasks, plan validity) versus soft preferences, and using tests as the final authority when AI suggestions looked plausible but might violate design intent.
- While AI accelerated execution, architectural ownership stayed with me. The quality of the final system depended less on how much code AI produced and more on how consistently I reviewed, constrained, and verified it.
