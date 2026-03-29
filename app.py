import streamlit as st
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
st.caption("This info is used to create your Owner and Pet objects when you add the first task.")
owner_name = st.text_input("Owner name", value="Jordan")
time_available = st.number_input("Time available (minutes)", min_value=1, max_value=480, value=120)
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Each task is added to both the pet's task list and the scheduler's queue.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    if "owner" not in st.session_state:
        st.session_state.owner = Owner(name=owner_name, time_available_minutes=int(time_available))
        st.session_state.pet = Pet(name=pet_name, species=species)
        st.session_state.scheduler = Scheduler(owner=st.session_state.owner)
    task = Task(title=task_title, duration_minutes=int(duration), priority=priority)
    st.session_state.pet.add_task(task)
    st.session_state.scheduler.add_task(task)
    st.session_state.tasks.append(str(task))

if st.session_state.tasks:
    st.write("Current tasks:")
    for t in st.session_state.tasks:
        st.write(t)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Tasks are sorted by priority and scheduled to fit within the owner's available time.")

if st.button("Generate schedule"):
    if "scheduler" in st.session_state:
        plan = st.session_state.scheduler.generate_plan()
        st.text(st.session_state.scheduler.explain_plan(plan))
    else:
        st.warning("Add at least one task before generating a schedule.")
