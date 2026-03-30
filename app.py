import streamlit as st

from pawpal_system import CareTask, Owner, Pet, Scheduler

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

st.subheader("Quick Demo Inputs")
owner_name = st.text_input("Owner name", value="Jordan")
daily_time_available = st.number_input(
    "Daily time available (minutes)",
    min_value=15,
    max_value=720,
    value=120,
)
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

# Initialize long-lived app objects once per browser session.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", daily_time_available=120)

if "pet" not in st.session_state:
    st.session_state.pet = Pet(name="Mochi", species="dog")
    st.session_state.owner.add_pet(st.session_state.pet)

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

# Keep session objects synced with current input widget values.
st.session_state.owner.name = owner_name
st.session_state.owner.daily_time_available = int(daily_time_available)
st.session_state.pet.name = pet_name
st.session_state.pet.species = species

st.markdown("### Tasks")
st.caption("Add tasks to your current pet using your backend class methods.")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    task_time = st.text_input("Time (HH:MM)", value="09:00")
with col5:
    required = st.checkbox("Required", value=False)

if st.button("Add task"):
    task = CareTask(
        title=task_title,
        category="general",
        duration_minutes=int(duration),
        priority=priority,
        time=task_time,
        required=required,
    )
    st.session_state.pet.add_task(task)
    st.success(f"Added **{task_title}** to {st.session_state.pet.name} at {task_time}.")

pet_tasks = st.session_state.pet.get_tasks()
if pet_tasks:
    scheduler = st.session_state.scheduler
    sorted_tasks = scheduler.sort_tasks_by_time(pet_tasks)

    st.write(f"**{st.session_state.pet.name}'s tasks** (sorted by time):")
    _priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    st.table(
        [
            {
                "time": task.time,
                "task": task.title,
                "duration (min)": task.duration_minutes,
                "priority": _priority_icon.get(task.priority, "") + " " + task.priority,
                "required": "✅" if task.required else "",
            }
            for task in sorted_tasks
        ]
    )

    # Conflict detection — show one banner per conflict found.
    conflicts = scheduler.detect_time_conflicts(st.session_state.owner)
    if conflicts:
        st.markdown("**⚠️ Scheduling conflicts detected:**")
        for warning in conflicts:
            st.warning(warning)
    else:
        st.success("No time conflicts found.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate a schedule using the Scheduler backend class.")

if st.button("Generate schedule"):
    tasks = st.session_state.pet.get_tasks()
    if not tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        st.session_state.generated_plan = st.session_state.scheduler.generate_plan(
            owner=st.session_state.owner,
            pet=st.session_state.pet,
            tasks=tasks,
        )

if "generated_plan" in st.session_state:
    plan = st.session_state.generated_plan
    st.markdown("### Today's Schedule")

    time_used = plan.available_minutes - plan.remaining_minutes()
    time_total = plan.available_minutes
    utilization = time_used / time_total if time_total > 0 else 0

    if plan.items:
        st.success(f"Scheduled {len(plan.items)} task(s) for {st.session_state.pet.name}.")
        _priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        st.table(
            [
                {
                    "time slot": f"{item.start_time} – {item.end_time}",
                    "task": item.task.title,
                    "duration (min)": item.task.duration_minutes,
                    "priority": _priority_icon.get(item.task.priority, "") + " " + item.task.priority,
                    "why scheduled": item.reason,
                }
                for item in plan.items
            ]
        )
    else:
        st.info("No tasks were scheduled.")

    if plan.skipped_tasks:
        with st.expander(f"⚠️ {len(plan.skipped_tasks)} task(s) skipped — not enough time", expanded=True):
            st.warning(
                "The following tasks did not fit within the available time. "
                "Consider increasing your daily time or marking fewer tasks as optional."
            )
            st.table(
                [
                    {
                        "task": task.title,
                        "duration (min)": task.duration_minutes,
                        "priority": task.priority,
                    }
                    for task in plan.skipped_tasks
                ]
            )

    st.divider()
    st.caption(f"Time used: {time_used} / {time_total} minutes")
    st.progress(min(utilization, 1.0))
    if utilization >= 1.0:
        st.warning("You've used all available time. Required tasks may exceed the limit.")
    elif utilization >= 0.8:
        st.info("Your day is nearly full. There's little room for unplanned tasks.")
    else:
        st.success(f"{plan.remaining_minutes()} minutes still available today.")
