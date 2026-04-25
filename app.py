import streamlit as st
from datetime import date
from pawpal_system import Task, Pet, Owner, Scheduler
from rag.retriever import retrieve
from rag.generator import answer

st.set_page_config(page_title="PawPal++", page_icon="🐾", layout="centered")
st.title("🐾 PawPal++")

# ---------------------------------------------------------------------------
# Session helpers
# ---------------------------------------------------------------------------

def get_scheduler() -> Scheduler | None:
    return st.session_state.get("scheduler")

def get_remaining_capacity() -> int:
    scheduler = get_scheduler()
    if scheduler is None:
        return st.session_state.get("original_time", 0)
    used = sum(t.duration_minutes for t in scheduler.tasks if t.status == "incomplete")
    return st.session_state.original_time - used

# ---------------------------------------------------------------------------
# Owner & Pet section
# ---------------------------------------------------------------------------

st.subheader("Owner & Pet")

session_active = "owner" in st.session_state
if session_active:
    st.caption(
        f"Session active for **{st.session_state.owner.name}** "
        f"({st.session_state.original_time} min). Owner settings are locked."
    )
    if st.button("Reset session"):
        for key in ["owner", "scheduler", "original_time", "plan"]:
            st.session_state.pop(key, None)
        st.rerun()
else:
    st.caption("Owner and time are locked after the first task is added.")

owner_name = st.text_input("Owner name", value="Jordan", disabled=session_active)
time_available = st.number_input(
    "Time available (minutes)", min_value=1, max_value=480, value=120, disabled=session_active
)
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

# ---------------------------------------------------------------------------
# Add task form
# ---------------------------------------------------------------------------

st.markdown("### Tasks")

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
    title = task_title.strip()
    if not title:
        st.error("Task title cannot be empty.")
    else:
        total_time = int(time_available if not session_active else st.session_state.original_time)
        existing = get_scheduler()
        capacity = total_time - (
            sum(t.duration_minutes for t in existing.tasks if t.status == "incomplete")
            if existing else 0
        )
        if int(duration) > capacity:
            st.warning(
                f"Task duration ({int(duration)} min) exceeds remaining capacity "
                f"({capacity} min of {total_time} min left). It will never be scheduled."
            )
        else:
            if not session_active:
                st.session_state.owner = Owner(name=owner_name, time_available_minutes=total_time)
                st.session_state.original_time = total_time
                st.session_state.scheduler = Scheduler(owner=st.session_state.owner)
            pet = Pet(name=pet_name, species=species)
            st.session_state.owner.pets.append(pet)
            task = Task(
                title=f"{pet_name}: {title}",
                duration_minutes=int(duration),
                priority=priority,
                start_time=int(start_hour) * 60 + int(start_minute),
                recurrence=None if recurrence == "None" else recurrence,
                due_date=date.today(),
            )
            pet.add_task(task)
            st.session_state.scheduler.add_task(task)
            st.session_state.pop("plan", None)
            st.success(f"Task '{title}' added!")

# ---------------------------------------------------------------------------
# Task list with sort / filter
# ---------------------------------------------------------------------------

st.divider()

fcol1, fcol2, fcol3 = st.columns(3)
with fcol1:
    sort_order = st.selectbox("Sort by duration", ["Shortest first", "Longest first"])
with fcol2:
    filter_pet = st.text_input("Filter by pet name (leave blank for all)")
with fcol3:
    filter_status = st.selectbox("Filter by status", ["All", "Incomplete", "Complete"])

scheduler = get_scheduler()
if scheduler:
    reverse = sort_order == "Longest first"
    status_arg = None if filter_status == "All" else filter_status.lower()

    if filter_pet.strip():
        tasks = scheduler.filter_tasks(pet_name=filter_pet.strip(), status=status_arg)
        tasks = sorted(tasks, key=lambda t: t.duration_minutes, reverse=reverse)
    else:
        tasks = scheduler.sort_by_duration(reverse=reverse)
        if status_arg:
            tasks = [t for t in tasks if t.status == status_arg]

    incomplete = [t for t in tasks if t.status == "incomplete"]
    complete = [t for t in tasks if t.status == "complete"]

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
                    next_task = scheduler.complete_task(t)
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

# ---------------------------------------------------------------------------
# Schedule generation
# ---------------------------------------------------------------------------

st.divider()
st.subheader("Build Schedule")
st.caption("Tasks are sorted by priority and scheduled to fit within the owner's available time.")

if st.button("Generate schedule"):
    if scheduler:
        st.session_state.owner.time_available_minutes = st.session_state.original_time
        st.session_state.plan = scheduler.generate_plan()
    else:
        st.warning("Add at least one task before generating a schedule.")

if "plan" in st.session_state and scheduler:
    plan = st.session_state.plan
    conflicts = scheduler.detect_conflicts(plan)
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
        st.warning(scheduler.explain_plan(plan))

# ---------------------------------------------------------------------------
# Ask PawPal chat
# ---------------------------------------------------------------------------

st.divider()
st.subheader("Ask PawPal")
st.caption("Ask anything about pet care — answers are pulled from a pet care knowledge base.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

query = st.chat_input("e.g. How often should I bathe my dog?")
if query:
    st.session_state.chat_history.append({"role": "user", "content": query})

    pet_ctx = ""
    if "owner" in st.session_state:
        pets = st.session_state.owner.pets
        if pets:
            pet_ctx = ", ".join(f"{p.name} ({p.species})" for p in pets)

    with st.spinner("Thinking..."):
        try:
            docs = retrieve(query)
            reply = answer(query, docs, pet_ctx)
        except Exception as e:
            reply = f"Sorry, something went wrong: {e}"

    st.session_state.chat_history.append({"role": "assistant", "content": reply})
    st.rerun()
