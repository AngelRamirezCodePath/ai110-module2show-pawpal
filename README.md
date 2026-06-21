# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

```
====================================================
          TODAY'S SCHEDULE
====================================================
Daily Plan for Biscuit (Dog) — 2026-06-20
----------------------------------------------------
  08:00 — Morning walk (30 min) [high]
  08:30 — Feeding (10 min) [high]
  12:00 — Fetch session (20 min) [medium]
----------------------------------------------------
Total: 60 min used / 120 min available

Scheduled 3 task(s) using 60 of 120 available minutes.

Daily Plan for Luna (Cat) — 2026-06-20
----------------------------------------------------
  08:00 — Feeding (10 min) [high]
  08:10 — Medication (5 min) [high]
  18:00 — Brushing (15 min) [medium]
----------------------------------------------------
Total: 30 min used / 120 min available

Scheduled 3 task(s) using 30 of 120 available minutes.
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| **Priority sorting** | `Scheduler.sort_tasks_by_priority()` | Tasks are sorted HIGH → MEDIUM → LOW before time-fitting so the most important care always gets a slot first. |
| **Chronological sorting** | `Scheduler.sort_by_time()` | Uses `sorted()` with a lambda key that converts each `'HH:MM'` string to an `(hours, minutes)` int tuple, ensuring the schedule displays in wall-clock order regardless of insertion order. |
| **Filtering by pet or status** | `Scheduler.filter_tasks_by()` | Keyword-only `pet_name` and `completed` filters can be combined (AND logic). Used to list pending tasks, show per-pet workloads, or find what's already done. |
| **Budget filtering** | `Scheduler.filter_tasks()` | Walks the priority-sorted list and drops tasks that would exceed the owner's available-time budget; returns both kept and dropped lists so the plan can explain every exclusion. |
| **Conflict detection** | `Scheduler.find_conflicts()` | Accepts one or more `DailyPlan` objects and checks every task pair with the interval-overlap condition (`start_A < end_B and start_B < end_A`). Returns plain-English warning strings rather than raising — safe to call at any point without crashing the app. Detects same-pet and cross-pet overlaps. |
| **Recurring task auto-scheduling** | `Scheduler.complete_task()` | Marking a `DAILY` or `WEEKLY` task complete automatically appends an identical pending task to `available_tasks`, so it re-appears in the next generated plan. `MONTHLY` and `AS_NEEDED` tasks are completed without creating a recurrence. |
| **Time-window grouping** | `Scheduler.assign_time_windows()` | Tasks that declare a `time_window` preference (`morning`, `afternoon`, `evening`) are grouped into ordered buckets before slot assignment, so a fetch session never gets pushed to 08:01 ahead of an afternoon preference. |
| **Slot packing** | `Scheduler.pack_into_slots()` | A single advancing cursor starts at 08:00 and jumps forward to the window's canonical start time (08:00 / 12:00 / 18:00) whenever a windowed task needs it — preventing gaps from appearing in the wrong place. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
