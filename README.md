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
python -m pytest

# Run with verbose output to see each test name:
python -m pytest -v

# Run with coverage:
python -m pytest --cov
```

The test suite in `tests/test_pawpal.py` covers the following behaviors:

| Test | What it verifies |
|------|-----------------|
| `test_mark_complete_changes_status` | `Task.mark_complete()` flips `completed` from `False` to `True` |
| `test_add_task_increases_pet_task_count` | `Pet.add_task()` appends the task and grows the list by one |
| `test_sort_by_time_returns_chronological_order` | `Scheduler.sort_by_time()` orders `(Task, 'HH:MM')` tuples by wall-clock time regardless of insertion order |
| `test_generate_daily_plan_tasks_in_chronological_order` | `generate_daily_plan()` produces a plan whose tasks appear in time order from morning → afternoon → evening |
| `test_complete_daily_task_creates_new_pending_task` | Completing a `DAILY` task returns a new uncompleted copy and adds it to `available_tasks` |
| `test_complete_monthly_task_creates_no_recurrence` | Completing a `MONTHLY` task returns `None` and does not grow `available_tasks` |
| `test_find_conflicts_flags_overlapping_tasks` | `find_conflicts()` emits a `WARNING` string when two tasks share overlapping time slots |
| `test_find_conflicts_no_false_positive_for_back_to_back` | Back-to-back tasks (A ends at 08:30, B starts at 08:30) are **not** flagged as a conflict |
| `test_find_conflicts_detects_cross_pet_overlap` | `find_conflicts()` catches overlapping tasks across two different pets' plans |

Sample test output:

```
(.venv) (base) angel@Angels-MacBook-Air-94 ai110-module2show-pawpal % python -m pytest -v 
========================================================================== test session starts ==========================================================================
platform darwin -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0 -- /Users/angel/Documents/TF Folder/ai110-module2show-pawpal/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/angel/Documents/TF Folder/ai110-module2show-pawpal
plugins: anyio-4.14.0
collected 9 items                                                                                                                                                       

tests/test_pawpal.py::test_mark_complete_changes_status PASSED                                                                                                    [ 11%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED                                                                                               [ 22%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED                                                                                        [ 33%]
tests/test_pawpal.py::test_generate_daily_plan_tasks_in_chronological_order PASSED                                                                                [ 44%]
tests/test_pawpal.py::test_complete_daily_task_creates_new_pending_task PASSED                                                                                    [ 55%]
tests/test_pawpal.py::test_complete_monthly_task_creates_no_recurrence PASSED                                                                                     [ 66%]
tests/test_pawpal.py::test_find_conflicts_flags_overlapping_tasks PASSED                                                                                          [ 77%]
tests/test_pawpal.py::test_find_conflicts_no_false_positive_for_back_to_back PASSED                                                                               [ 88%]
tests/test_pawpal.py::test_find_conflicts_detects_cross_pet_overlap PASSED                                                                                        [100%]

=========================================================================== 9 passed in 0.02s ===========================================================================
(.venv) (base) angel@Angels-MacBook-Air-94 ai110-module2show-pawpal % 
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
