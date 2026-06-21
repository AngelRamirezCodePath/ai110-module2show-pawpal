"""Streamlit UI for PawPal+ — daily pet-care scheduler."""
import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.divider()

st.subheader("Owner & Pet Setup")
owner_name = st.text_input("Owner name", value="Jordan")
available_hours = st.number_input(
    "Available hours today", min_value=0.5, max_value=24.0, value=4.0, step=0.5
)
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name, available_hours=available_hours)

if "pet" not in st.session_state:
    st.session_state.pet = Pet(name=pet_name, species=species, breed="unknown", age=1)

st.session_state.owner.name = owner_name
st.session_state.owner.available_hours = available_hours
st.session_state.pet.name = pet_name
st.session_state.pet.species = species

st.divider()

st.subheader("Add a Task")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["high", "medium", "low"])
with col4:
    time_window = st.selectbox("Time window", ["(any)", "morning", "afternoon", "evening"])

if st.button("Add task", type="primary"):
    new_task = Task(
        name=task_title,
        duration=int(duration),
        priority=priority.upper(),
        frequency="DAILY",
        time_window="" if time_window == "(any)" else time_window,
        pet=st.session_state.pet,
    )
    st.session_state.pet.add_task(new_task)
    st.success(f'Added "{task_title}" to the task list.')

st.divider()

# ── Task list — sorted by priority via Scheduler ──────────────────────────────
st.subheader("Current Tasks")

_temp_scheduler = Scheduler(
    owner=st.session_state.owner,
    pets=[st.session_state.pet],
    available_tasks=st.session_state.pet.tasks,
)

pending_tasks = _temp_scheduler.filter_tasks_by(
    st.session_state.pet.tasks, completed=False
)
completed_tasks = _temp_scheduler.filter_tasks_by(
    st.session_state.pet.tasks, completed=True
)

if pending_tasks:
    sorted_pending = _temp_scheduler.sort_tasks_by_priority(pending_tasks)
    st.markdown("**Pending** (sorted HIGH → MEDIUM → LOW)")
    st.table([
        {
            "Task": t.name,
            "Duration (min)": t.duration,
            "Priority": t.priority.capitalize(),
            "Time Window": t.time_window.capitalize() if t.time_window else "Any",
        }
        for t in sorted_pending
    ])
else:
    st.info("No pending tasks. Add one above.")

if completed_tasks:
    with st.expander(f"Completed tasks ({len(completed_tasks)})"):
        st.table([
            {
                "Task": t.name,
                "Duration (min)": t.duration,
                "Priority": t.priority.capitalize(),
            }
            for t in completed_tasks
        ])

st.divider()

# ── Mark complete ──────────────────────────────────────────────────────────────
st.subheader("Mark Task Complete")

if pending_tasks:
    selected_name = st.selectbox(
        "Select a task to mark complete",
        options=[t.name for t in pending_tasks],
    )
    if st.button("Mark complete"):
        task_to_complete = next(t for t in pending_tasks if t.name == selected_name)
        temp_scheduler = Scheduler(
            owner=st.session_state.owner,
            pets=[st.session_state.pet],
            available_tasks=st.session_state.pet.tasks,
        )
        next_occ = temp_scheduler.complete_task(task_to_complete)
        if next_occ:
            when = "tomorrow" if task_to_complete.frequency.upper() == "DAILY" else "next week"
            st.success(
                f'"{task_to_complete.name}" marked complete. '
                f"Next occurrence queued for {when}."
            )
        else:
            st.success(f'"{task_to_complete.name}" marked complete (no recurrence).')
        st.rerun()
else:
    st.info("No pending tasks to complete.")

st.divider()

# ── Generate schedule ──────────────────────────────────────────────────────────
st.subheader("Build Schedule")

if st.button("Generate schedule", type="primary"):
    if not st.session_state.pet.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(
            owner=st.session_state.owner,
            pets=[st.session_state.pet],
            available_tasks=st.session_state.pet.tasks,
        )
        plan = scheduler.generate_daily_plan(st.session_state.pet)

        # ── Conflict warnings ──────────────────────────────────────────────
        conflicts = scheduler.find_conflicts(plan)
        if conflicts:
            for w in conflicts:
                st.warning(w)
        else:
            st.success("No scheduling conflicts detected.")

        # ── Schedule table (tasks already sorted by sort_by_time inside plan) ──
        st.markdown(
            f"**Daily Plan for {plan.pet.name} ({plan.pet.species.capitalize()}) — {plan.date}**"
        )

        ordered = plan.get_tasks_ordered()
        if ordered:
            st.table([
                {
                    "Start": start,
                    "Task": task.name,
                    "Duration (min)": task.duration,
                    "Priority": task.priority.capitalize(),
                }
                for task, start in ordered
            ])

        # ── Time budget metrics ────────────────────────────────────────────
        budget_min = int(plan.owner.get_available_time() * 60)
        remaining = budget_min - plan.total_time_used
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Time used", f"{plan.total_time_used} min")
        col_b.metric("Available", f"{budget_min} min")
        col_c.metric("Remaining", f"{remaining} min")

        # ── Explanation note ───────────────────────────────────────────────
        if plan.notes:
            st.info(plan.notes)