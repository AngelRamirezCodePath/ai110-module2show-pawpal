# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The three core actions a user should be able to perform in PawPal+ are:

1. **Enter owner and pet information** — The user provides basic context about themselves and their pet (name, species, breed, age, and any relevant constraints like time available per day). This seeds the system with the data it needs to personalize every plan.

2. **Add and manage care tasks** — The user creates, edits, or removes individual care tasks (such as walks, feedings, medication, or grooming), specifying at minimum a duration and a priority level for each task. This builds the task list that the scheduler works from.

3. **Generate a daily care plan** — The user triggers the scheduler to produce a prioritized, time-blocked daily schedule based on their available time and the tasks they have defined. The app displays the resulting plan and explains why tasks were ordered or excluded the way they were.

The initial UML design includes five classes organized into two layers: pure data containers and logic/composite classes.

**Data classes (use Python `@dataclass`):**

- **`Pet`** — holds the pet's profile (name, species, breed, age, special needs, medical conditions). Its only responsibility is describing the subject of care; it has no scheduling awareness.
- **`Owner`** — holds the owner's name, daily available hours, and task preferences. It answers one question for the scheduler: "how much time do I have, and in what order do I prefer things?"
- **`Task`** — represents a single care action (walk, feeding, medication, etc.) with a duration, priority level (HIGH/MEDIUM/LOW), frequency, and optional time-window preference. It knows only about itself — whether it is critical, recurring, or constrained to a time of day.

**Logic/composite classes:**

- **`DailyPlan`** — the output object. It holds an ordered list of `(Task, start_time)` tuples for one day, tracks total time used, detects scheduling conflicts, and formats the plan for display. It owns the schedule once built but does not decide what goes into it.
- **`Scheduler`** — the brain of the system. It takes a `Pet`, an `Owner`, and a list of `Task`s as inputs, then produces a `DailyPlan` by sorting tasks by priority, filtering out tasks that exceed the available time budget, and assigning start times respecting each task's time-window preference. It also generates a plain-English explanation of every scheduling decision made.

**b. Design changes**

Yes, the design changed in five ways after reviewing the initial skeleton for missing relationships and logic bottlenecks.

1. **`Task` gained an optional `pet` reference.** The original design had tasks stored globally on the `Scheduler`, with no way to know which pet a task belonged to. Adding `pet: Optional[Pet]` to `Task` lets the scheduler filter tasks by pet when planning for multiple animals, and prevents a medication task for one pet from accidentally appearing in another pet's plan.

2. **`Scheduler` changed from holding one `Pet` to a list of `Pet`s.** The UML showed a 1-to-many relationship between `Owner` and `Pet`, but the original `Scheduler.__init__` only accepted a single pet. Switching to `pets: list` makes the scheduler consistent with that relationship and avoids needing a separate scheduler instance per pet.

3. **`DailyPlan` gained an `Owner` reference.** Without it, `has_conflicts()` and `validate_plan()` had no way to check the plan against the owner's available time budget without passing the owner in as an extra argument every time. Storing it on the plan keeps validation self-contained.

4. **`fit_tasks_into_timeline()` was split into `assign_time_windows()` and `pack_into_slots()`.** The original single method was responsible for both grouping tasks by time-of-day preference and assigning concrete start times — two distinct concerns that would have made the method difficult to test and debug independently. Splitting them keeps each method focused on one job.

5. **`filter_tasks()` now returns a `(kept, dropped)` tuple instead of just the kept list.** `explain_plan()` needs to report on tasks that were excluded and the reason they were skipped. Without the dropped list, that information was silently lost after filtering, making the explanation incomplete.

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
