from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

# --- Create pets ---
mochi = Pet(name="Mochi", species="dog", breed="Shiba Inu", age_years=3)
luna  = Pet(name="Luna",  species="cat", breed="Siamese",   age_years=5)

# --- Create owner with both pets ---
jordan = Owner(
    name="Jordan",
    time_available_minutes=90,
    pets=[mochi, luna],
    preferences=["morning walks", "no tasks after 9pm"],
)

# --- Create tasks (added out of order: low → medium → high) ---
today = date.today()
# start_time = minutes from midnight (e.g. 480 = 8:00 AM)
# feeding (8:00) and medication (8:05) overlap for different pets
# feeding (8:00) and morning_walk (8:00) overlap for the same pet
grooming     = Task(title=f"{mochi.name}: Brushing",       duration_minutes=15, priority="low",    category="grooming",    recurrence="weekly", due_date=today, start_time=540)
enrichment   = Task(title=f"{luna.name}: Puzzle feeder",   duration_minutes=20, priority="medium", category="enrichment",  start_time=600)
medication   = Task(title=f"{luna.name}: Flea medication", duration_minutes=5,  priority="high",   category="medication",  notes="Apply between shoulder blades", recurrence="weekly", due_date=today, start_time=485)
feeding      = Task(title=f"{mochi.name}: Breakfast",      duration_minutes=10, priority="high",   category="feeding",     recurrence="daily",  due_date=today, start_time=480)
morning_walk = Task(title=f"{mochi.name}: Morning walk",   duration_minutes=30, priority="high",   category="walk",        start_time=480)

# --- Schedule (added out of order) ---
scheduler = Scheduler(owner=jordan)
for task in [grooming, enrichment, medication, feeding, morning_walk]:
    scheduler.add_task(task)

# --- Sort by duration ---
print("=== Tasks Sorted by Duration (shortest first) ===")
for task in scheduler.sort_by_duration():
    print(f"  {task.duration_hhmm}  {task.title}")

print()

# --- Filter: all incomplete tasks ---
print("=== Filter: Incomplete Tasks ===")
for task in scheduler.filter_tasks(status="incomplete"):
    print(f"  {task}")

print()

# --- Filter: Mochi's tasks only ---
print("=== Filter: Mochi's Tasks ===")
for task in scheduler.filter_tasks(pet_name="Mochi"):
    print(f"  {task}")

print()

# --- Filter: Luna's tasks only ---
print("=== Filter: Luna's Tasks ===")
for task in scheduler.filter_tasks(pet_name="Luna"):
    print(f"  {task}")

print()

# --- Complete recurring tasks via scheduler ---
print("=== Completing Recurring Tasks ===")
for task in [feeding, medication, grooming]:
    next_task = scheduler.complete_task(task)
    recur_label = f"[{task.recurrence}]" if task.recurrence else "[one-time]"
    if next_task:
        print(f"  Completed: {task.title} {recur_label} → next occurrence queued")
    else:
        print(f"  Completed: {task.title} {recur_label} → no recurrence")

print()

# --- Show queue after completions ---
print("=== All Tasks After Completions ===")
for task in scheduler.tasks:
    recur_label = f"[{task.recurrence}]" if task.recurrence else ""
    print(f"  [{task.status}] {task.title} {recur_label}")

print()

# --- Generate plan and check for conflicts ---
plan = scheduler.generate_plan()
conflicts = scheduler.detect_conflicts(plan)
if conflicts:
    print("=== Conflict Detection ===")
    for warning in conflicts:
        print(f"  {warning}")
    print()

print(scheduler.explain_plan(plan))
