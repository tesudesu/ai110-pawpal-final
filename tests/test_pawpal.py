import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


def test_mark_complete_changes_status():
    task = Task(title="Walk dog", duration_minutes=30, priority="high")
    assert task.status == "incomplete"
    task.mark_complete()
    assert task.status == "complete"


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task(title="Feed Buddy", duration_minutes=10, priority="medium"))
    assert len(pet.tasks) == 1


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_by_duration_shortest_first():
    """Tasks are returned in ascending duration order (chronological by length)."""
    owner = Owner(name="Alex", time_available_minutes=120)
    scheduler = Scheduler(owner)
    scheduler.add_task(Task(title="Long walk", duration_minutes=60, priority="low"))
    scheduler.add_task(Task(title="Quick feed", duration_minutes=10, priority="low"))
    scheduler.add_task(Task(title="Grooming", duration_minutes=30, priority="low"))

    result = scheduler.sort_by_duration()

    assert [t.duration_minutes for t in result] == [10, 30, 60]


def test_sort_by_duration_longest_first():
    """Passing reverse=True returns tasks longest-first."""
    owner = Owner(name="Alex", time_available_minutes=120)
    scheduler = Scheduler(owner)
    scheduler.add_task(Task(title="Long walk", duration_minutes=60, priority="low"))
    scheduler.add_task(Task(title="Quick feed", duration_minutes=10, priority="low"))

    result = scheduler.sort_by_duration(reverse=True)

    assert result[0].duration_minutes == 60
    assert result[-1].duration_minutes == 10


def test_generate_plan_orders_by_priority():
    """generate_plan schedules high-priority tasks before low-priority ones."""
    owner = Owner(name="Alex", time_available_minutes=60)
    scheduler = Scheduler(owner)
    scheduler.add_task(Task(title="Low task", duration_minutes=20, priority="low"))
    scheduler.add_task(Task(title="High task", duration_minutes=20, priority="high"))
    scheduler.add_task(Task(title="Med task", duration_minutes=20, priority="medium"))

    plan = scheduler.generate_plan()

    priorities = [t.priority for t in plan]
    assert priorities == ["high", "medium", "low"]


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

def test_daily_recurrence_creates_next_day_task():
    """Completing a daily task returns a new task due the following day."""
    today = date.today()
    task = Task(
        title="Morning walk",
        duration_minutes=30,
        priority="high",
        recurrence="daily",
        due_date=today,
    )

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.title == task.title
    assert next_task.recurrence == "daily"
    assert next_task.status == "incomplete"


def test_weekly_recurrence_creates_next_week_task():
    """Completing a weekly task returns a new task due seven days later."""
    today = date.today()
    task = Task(
        title="Bath time",
        duration_minutes=45,
        priority="medium",
        recurrence="weekly",
        due_date=today,
    )

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=7)


def test_non_recurring_task_returns_none():
    """mark_complete returns None for tasks with no recurrence."""
    task = Task(title="One-time vet visit", duration_minutes=60, priority="high")
    next_task = task.mark_complete()
    assert next_task is None


def test_complete_task_appends_next_occurrence_to_scheduler():
    """Scheduler.complete_task appends the next occurrence to its task list."""
    today = date.today()
    owner = Owner(name="Alex", time_available_minutes=120)
    scheduler = Scheduler(owner)
    task = Task(
        title="Feed cat",
        duration_minutes=10,
        priority="high",
        recurrence="daily",
        due_date=today,
    )
    scheduler.add_task(task)

    scheduler.complete_task(task)

    assert len(scheduler.tasks) == 2
    next_task = scheduler.tasks[1]
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.status == "incomplete"


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_flags_overlapping_tasks():
    """Two tasks whose time windows overlap produce a warning."""
    owner = Owner(name="Alex", time_available_minutes=120)
    scheduler = Scheduler(owner)
    task_a = Task(title="Buddy: walk", duration_minutes=60, priority="high", start_time=480)   # 8:00–9:00
    task_b = Task(title="Buddy: feed", duration_minutes=30, priority="high", start_time=510)   # 8:30–9:00

    warnings = scheduler.detect_conflicts([task_a, task_b])

    assert len(warnings) == 1
    assert "WARNING" in warnings[0]
    assert "Buddy: walk" in warnings[0]
    assert "Buddy: feed" in warnings[0]


def test_detect_conflicts_no_warning_for_sequential_tasks():
    """Tasks that run back-to-back (not overlapping) produce no warnings."""
    owner = Owner(name="Alex", time_available_minutes=120)
    scheduler = Scheduler(owner)
    task_a = Task(title="Buddy: walk", duration_minutes=30, priority="high", start_time=480)   # 8:00–8:30
    task_b = Task(title="Buddy: feed", duration_minutes=30, priority="high", start_time=510)   # 8:30–9:00

    warnings = scheduler.detect_conflicts([task_a, task_b])

    assert warnings == []


def test_detect_conflicts_task_contained_within_another():
    """A task fully inside another's window is still flagged as a conflict."""
    owner = Owner(name="Alex", time_available_minutes=120)
    scheduler = Scheduler(owner)
    task_a = Task(title="Buddy: groom", duration_minutes=120, priority="low", start_time=480)  # 8:00–10:00
    task_b = Task(title="Buddy: feed", duration_minutes=15, priority="high", start_time=510)   # 8:30–8:45

    warnings = scheduler.detect_conflicts([task_a, task_b])

    assert len(warnings) == 1


def test_detect_conflicts_no_start_time_skipped():
    """Tasks without a start_time are ignored by conflict detection."""
    owner = Owner(name="Alex", time_available_minutes=120)
    scheduler = Scheduler(owner)
    task_a = Task(title="Buddy: walk", duration_minutes=60, priority="high")           # no start_time
    task_b = Task(title="Buddy: feed", duration_minutes=30, priority="high")           # no start_time

    warnings = scheduler.detect_conflicts([task_a, task_b])

    assert warnings == []


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_generate_plan_skips_tasks_exceeding_time_budget():
    """Tasks that don't fit in remaining time are excluded from the plan."""
    owner = Owner(name="Alex", time_available_minutes=20)
    scheduler = Scheduler(owner)
    scheduler.add_task(Task(title="Long walk", duration_minutes=60, priority="high"))
    scheduler.add_task(Task(title="Quick feed", duration_minutes=10, priority="low"))

    plan = scheduler.generate_plan()

    assert len(plan) == 1
    assert plan[0].title == "Quick feed"


def test_generate_plan_empty_when_no_time():
    """generate_plan returns empty list when owner has zero time available."""
    owner = Owner(name="Alex", time_available_minutes=0)
    scheduler = Scheduler(owner)
    scheduler.add_task(Task(title="Walk", duration_minutes=30, priority="high"))

    plan = scheduler.generate_plan()

    assert plan == []


# ---------------------------------------------------------------------------
# filter_tasks
# ---------------------------------------------------------------------------

def test_filter_tasks_by_status_incomplete():
    owner = Owner(name="Alex", time_available_minutes=60)
    scheduler = Scheduler(owner)
    task_a = Task(title="Walk", duration_minutes=30, priority="high")
    task_b = Task(title="Feed", duration_minutes=10, priority="low")
    task_b.mark_complete()
    scheduler.add_task(task_a)
    scheduler.add_task(task_b)

    result = scheduler.filter_tasks(status="incomplete")

    assert result == [task_a]


def test_filter_tasks_by_status_complete():
    owner = Owner(name="Alex", time_available_minutes=60)
    scheduler = Scheduler(owner)
    task_a = Task(title="Walk", duration_minutes=30, priority="high")
    task_b = Task(title="Feed", duration_minutes=10, priority="low")
    task_b.mark_complete()
    scheduler.add_task(task_a)
    scheduler.add_task(task_b)

    result = scheduler.filter_tasks(status="complete")

    assert result == [task_b]


def test_filter_tasks_by_pet_name():
    owner = Owner(name="Alex", time_available_minutes=60)
    scheduler = Scheduler(owner)
    task_mochi = Task(title="Mochi: Walk", duration_minutes=30, priority="high")
    task_luna  = Task(title="Luna: Feed",  duration_minutes=10, priority="low")
    scheduler.add_task(task_mochi)
    scheduler.add_task(task_luna)

    result = scheduler.filter_tasks(pet_name="Mochi")

    assert result == [task_mochi]


def test_filter_tasks_by_pet_name_and_status():
    owner = Owner(name="Alex", time_available_minutes=60)
    scheduler = Scheduler(owner)
    task_a = Task(title="Mochi: Walk", duration_minutes=30, priority="high")
    task_b = Task(title="Mochi: Feed", duration_minutes=10, priority="low")
    task_b.mark_complete()
    scheduler.add_task(task_a)
    scheduler.add_task(task_b)

    result = scheduler.filter_tasks(pet_name="Mochi", status="incomplete")

    assert result == [task_a]


# ---------------------------------------------------------------------------
# Owner time management
# ---------------------------------------------------------------------------

def test_owner_has_time_for_returns_true_when_enough_time():
    owner = Owner(name="Alex", time_available_minutes=30)
    task = Task(title="Walk", duration_minutes=30, priority="high")
    assert owner.has_time_for(task) is True


def test_owner_has_time_for_returns_false_when_not_enough_time():
    owner = Owner(name="Alex", time_available_minutes=20)
    task = Task(title="Walk", duration_minutes=30, priority="high")
    assert owner.has_time_for(task) is False


def test_owner_consume_time_deducts_minutes():
    owner = Owner(name="Alex", time_available_minutes=60)
    owner.consume_time(20)
    assert owner.time_available_minutes == 40


def test_owner_consume_time_floors_at_zero():
    owner = Owner(name="Alex", time_available_minutes=10)
    owner.consume_time(999)
    assert owner.time_available_minutes == 0


# ---------------------------------------------------------------------------
# Task.duration_hhmm formatting
# ---------------------------------------------------------------------------

def test_duration_hhmm_formats_correctly():
    task = Task(title="Long session", duration_minutes=90, priority="low")
    assert task.duration_hhmm == "01:30"


def test_duration_hhmm_under_one_hour():
    task = Task(title="Quick check", duration_minutes=5, priority="low")
    assert task.duration_hhmm == "00:05"


# ---------------------------------------------------------------------------
# generate_plan excludes completed tasks
# ---------------------------------------------------------------------------

def test_generate_plan_excludes_completed_tasks():
    owner = Owner(name="Alex", time_available_minutes=120)
    scheduler = Scheduler(owner)
    done = Task(title="Already done", duration_minutes=10, priority="high")
    done.mark_complete()
    pending = Task(title="Still pending", duration_minutes=10, priority="low")
    scheduler.add_task(done)
    scheduler.add_task(pending)

    plan = scheduler.generate_plan()

    assert len(plan) == 1
    assert plan[0].title == "Still pending"
