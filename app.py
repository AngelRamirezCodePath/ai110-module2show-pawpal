import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.divider()

st.subheader("Owner & Pet Setup")
owner_name = st.text_input("Owner name", value="Jordan")
available_hours = st.number_input("Available hours today", min_value=0.5, max_value=24.0, value=4.0, step=0.5)
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

# Initialize Owner and Pet in session state so they survive reruns
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name, available_hours=available_hours)

if "pet" not in st.session_state:
    st.session_state.pet = Pet(name=pet_name, species=species, breed="unknown", age=1)

# Keep owner fields in sync if the user edits the inputs
st.session_state.owner.name = owner_name
st.session_state.owner.available_hours = available_hours
st.session_state.pet.name = pet_name
st.session_state.pet.species = species

st.markdown("### Tasks")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    new_task = Task(
        name=task_title,
        duration=int(duration),
        priority=priority.upper(),
        frequency="DAILY",
        pet=st.session_state.pet,
    )
    st.session_state.pet.add_task(new_task)

if st.session_state.pet.tasks:
    st.write("Current tasks:")
    st.table([
        {"title": t.name, "duration_minutes": t.duration, "priority": t.priority.lower()}
        for t in st.session_state.pet.tasks
    ])
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Mark Task Complete")

pending = [t for t in st.session_state.pet.tasks if not t.completed]
if pending:
    selected_name = st.selectbox(
        "Select a task to mark complete",
        options=[t.name for t in pending],
    )
    if st.button("Mark complete"):
        task_to_complete = next(t for t in pending if t.name == selected_name)
        temp_scheduler = Scheduler(
            owner=st.session_state.owner,
            pets=[st.session_state.pet],
            available_tasks=st.session_state.pet.tasks,
        )
        next_occ = temp_scheduler.complete_task(task_to_complete)
        if next_occ:
            freq_label = "tomorrow" if task_to_complete.frequency.upper() == "DAILY" else "next week"
            st.success(f'"{task_to_complete.name}" marked complete. Next occurrence scheduled for {freq_label}.')
        else:
            st.success(f'"{task_to_complete.name}" marked complete (no recurrence).')
        st.rerun()
else:
    st.info("No pending tasks to complete.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if not st.session_state.pet.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(
            owner=st.session_state.owner,
            pets=[st.session_state.pet],
            available_tasks=st.session_state.pet.tasks,
        )
        plan = scheduler.generate_daily_plan(st.session_state.pet)

        st.success("Schedule generated!")
        st.text(plan.get_summary())
        if plan.notes:
            st.info(plan.notes)
