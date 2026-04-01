import streamlit as st
from datetime import date
from pawpal_system import Pet, Task, Owner, Schedule

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# --- Session state: keep the Owner alive across reruns ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Owner")

owner = st.session_state.owner

st.title("🐾 PawPal+")

# ── Owner info ──────────────────────────────────────────
with st.expander("Owner Settings", expanded=False):
    new_name = st.text_input("Your name", value=owner.name)
    available = st.number_input(
        "Available minutes today", min_value=10, max_value=480, value=owner.available_minutes
    )
    owner.name = new_name
    owner.available_minutes = available

# ── Add a Pet ───────────────────────────────────────────
st.subheader("Pets")

with st.form("add_pet_form"):
    col1, col2 = st.columns(2)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    add_pet = st.form_submit_button("Add pet")

if add_pet and pet_name:
    pet = Pet(name=pet_name, species=species)
    owner.add_pet(pet)
    st.success(f"Added {pet_name} the {species}!")

if owner.pets:
    for pet in owner.pets:
        st.write(f"- **{pet.name}** ({pet.species}) — {len(pet.tasks)} task(s)")
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ── Add a Task ──────────────────────────────────────────
st.subheader("Tasks")

if not owner.pets:
    st.info("Add a pet first before creating tasks.")
else:
    with st.form("add_task_form"):
        task_title = st.text_input("Task title", value="Morning walk")
        col1, col2, col3 = st.columns(3)
        with col1:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col2:
            priority = st.selectbox("Priority", ["high", "medium", "low"])
        with col3:
            pet_choice = st.selectbox("For which pet?", [p.name for p in owner.pets])
        scheduled = st.date_input("Scheduled date", value=date.today())
        add_task = st.form_submit_button("Add task")

    if add_task and task_title:
        task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            scheduled_date=scheduled,
        )
        # Find the matching pet and add the task to it
        target_pet = next(p for p in owner.pets if p.name == pet_choice)
        target_pet.add_task(task)
        st.success(f"Added '{task_title}' for {pet_choice}!")

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.write("All tasks:")
        for pet in owner.pets:
            for t in pet.tasks:
                status = "✅" if t.completed else "⬜"
                st.write(f"  {status} **{t.title}** — {t.duration_minutes} min, "
                         f"{t.priority}, {pet.name}, {t.scheduled_date}")
    else:
        st.info("No tasks yet.")

st.divider()

# ── Generate Schedule ───────────────────────────────────
st.subheader("Daily Schedule")

schedule_date = st.date_input("Plan for date", value=date.today(), key="schedule_date")

if st.button("Generate schedule"):
    schedule = Schedule(date=schedule_date, owner=owner)
    plan = schedule.generate_plan()

    if plan:
        st.markdown(f"```\n{schedule.explain_plan()}\n```")
    else:
        st.warning("No incomplete tasks found for this date.")
