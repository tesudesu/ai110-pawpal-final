import streamlit as st
from datetime import date
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner & Pet")

if "owner" in st.session_state:
    st.caption(f"Session active for **{st.session_state.owner.name}** ({st.session_state.original_time} min). Owner settings are locked.")
    if st.button("Reset session"):
        for key in ["owner", "scheduler", "original_time", "plan"]:
            st.session_state.pop(key, None)
        st.rerun()
else:
    st.caption("This info is used to create your Owner and Pet objects when you add the first task.")

owner_name = st.text_input("Owner name", value="Jordan", disabled="owner" in st.session_state)
time_available = st.number_input("Time available (minutes)", min_value=1, max_value=480, value=120, disabled="owner" in st.session_state)
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Each task is added to both the pet's task list and the scheduler's queue.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5, col6 = st.columns(3)
with col4:
    start_hour = st.number_input("Start time (hour, 0–23)", min_value=0, max_value=23, value=8)
with col5:
    start_minute = st.number_input("Start time (minute)", min_value=0, max_value=59, value=0, step=5)
with col6:
    recurrence = st.selectbox("Recurrence", ["None", "daily", "weekly"])

if st.button("Add task"):
    if not task_title.strip():
        st.error("Task title cannot be empty.")
    else:
        if "owner" not in st.session_state:
            st.session_state.owner = Owner(name=owner_name, time_available_minutes=int(time_available))
            st.session_state.original_time = int(time_available)
            st.session_state.scheduler = Scheduler(owner=st.session_state.owner)
        # Always use the current pet name/species from the form
        current_pet = Pet(name=pet_name, species=species)
        st.session_state.owner.pets.append(current_pet)
        start_time_minutes = int(start_hour) * 60 + int(start_minute)
        task = Task(
            title=f"{pet_name}: {task_title.strip()}",
            duration_minutes=int(duration),
            priority=priority,
            start_time=start_time_minutes,
            recurrence=None if recurrence == "None" else recurrence,
            due_date=date.today(),
        )
        current_pet.add_task(task)
        st.session_state.scheduler.add_task(task)
        st.session_state.pop("plan", None)  # clear stale schedule
        st.success(f"Task '{task_title.strip()}' added!")

# Sort and filter controls
fcol1, fcol2, fcol3 = st.columns(3)
with fcol1:
    sort_order = st.selectbox("Sort by duration", ["Shortest first", "Longest first"])
with fcol2:
    filter_pet = st.text_input("Filter by pet name (leave blank for all)")
with fcol3:
    filter_status = st.selectbox("Filter by status", ["All", "Incomplete", "Complete"])

# Display current tasks using Scheduler.sort_by_duration() / filter_tasks()
if "scheduler" in st.session_state:
    reverse = sort_order == "Longest first"
    status_arg = None if filter_status == "All" else filter_status.lower()

    if filter_pet.strip():
        sorted_tasks = st.session_state.scheduler.filter_tasks(
            pet_name=filter_pet.strip(), status=status_arg
        )
        sorted_tasks = sorted(sorted_tasks, key=lambda t: t.duration_minutes, reverse=reverse)
    else:
        all_tasks = st.session_state.scheduler.sort_by_duration(reverse=reverse)
        sorted_tasks = [t for t in all_tasks if status_arg is None or t.status == status_arg]

    # sorted_tasks is already filtered by status_arg; split into display groups
    incomplete = [t for t in sorted_tasks if t.status == "incomplete"]
    complete = [t for t in sorted_tasks if t.status == "complete"]

    if incomplete:
        st.markdown("**Incomplete tasks**")
        for i, t in enumerate(incomplete):
            col_a, col_b = st.columns([4, 1])
            with col_a:
                recur_label = f" ({t.recurrence})" if t.recurrence else ""
                due_label = f" — due {t.due_date}" if t.due_date else ""
                st.write(f"**{t.title}** — {t.duration_hhmm} — {t.priority.capitalize()}{recur_label}{due_label}")
            with col_b:
                if st.button("Complete", key=f"complete_{i}_{t.title}"):
                    next_task = st.session_state.scheduler.complete_task(t)
                    if next_task:
                        st.success(f"Done! Next occurrence queued for {next_task.due_date}.")
                    else:
                        st.success("Task marked complete.")
                    st.rerun()

    if complete:
        st.markdown("**Completed tasks**")
        st.table([
            {
                "Task": t.title,
                "Duration": t.duration_hhmm,
                "Priority": t.priority.capitalize(),
                "Recurrence": t.recurrence or "—",
                "Completed": str(t.completed_date) if t.completed_date else "—",
            }
            for t in complete
        ])

    if not incomplete and not complete:
        st.info("No tasks match the current filters.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Tasks are sorted by priority and scheduled to fit within the owner's available time.")

if st.button("Generate schedule"):
    if "scheduler" in st.session_state:
        # Reset available time before each generation so repeated clicks don't drain it
        st.session_state.owner.time_available_minutes = st.session_state.original_time
        st.session_state.plan = st.session_state.scheduler.generate_plan()
    else:
        st.warning("Add at least one task before generating a schedule.")

if "plan" in st.session_state:
    plan = st.session_state.plan
    conflicts = st.session_state.scheduler.detect_conflicts(plan)
    if conflicts:
        st.warning(f"{len(conflicts)} scheduling conflict(s) detected:")
        for warning in conflicts:
            st.write(f"- {warning}")

    if plan:
        st.success(f"Scheduled {len(plan)} task(s) for {st.session_state.owner.name}")
        st.table([
            {
                "Task": t.title,
                "Duration": t.duration_hhmm,
                "Priority": t.priority.capitalize(),
                "Notes": t.notes or "—",
            }
            for t in plan
        ])
        st.caption(f"Time remaining after scheduling: {st.session_state.owner.time_available_minutes} min")
    else:
        st.warning(st.session_state.scheduler.explain_plan(plan))
