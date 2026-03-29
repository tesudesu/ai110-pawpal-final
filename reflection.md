# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
My initial UML design consists of 4 classes: Scheduler, Pet, Task, and Owner. Scheduler flows to Pet, Task, and Owner. Pet also flows to Owner.

**b. Design changes**

- Did your design change during implementation?
Yes. 
- If yes, describe at least one change and why you made it.
Scheduler now flows to Owner and Task. Owner flows to Pet, which flows to Task. This design makes more sense because a Owner can have multiple Pets, and each Pet can have multiple Tasks. 

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
My schedule considers task start time and duration to detect conflicts. One can also sort tasks by completion status, duration, and pet. 
- How did you decide which constraints mattered most?
Conflict detection is probably one of the most important, as it is a core improvement to the app.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
The previous filter_tasks method uses two passes - one for filtering by status and another for filtering by pet_name. Claude suggested to combine these in one pass. 
- Why is that tradeoff reasonable for this scenario?
One pass is more efficient than two passes.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used Claude throughout the whole process, from designing the initial UML to developing the app to implementing tests.
- What kinds of prompts or questions were most helpful?
I asked Claude questions like, "what bugs do you see" and "can you suggest any other improvements" to touch up the initial code that it gave me. Claude suggested important fixes through these prompts. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
The AI suggested to add a RECURRENCE_DAYS dictionary like RECURRENCE_DAYS = {"daily": 1, "weekly": 7} for the mark_complete method to avoid checking the self.recurrence string twice. I did not fully understand what the AI meant. 

- How did you evaluate or verify what the AI suggested?
I copied and pasted the AI's suggested fix back to the AI to ask it to explain. I also asked the AI what is the change in time complexity before and after the fix, which the AI stated there is no change except for improvements in readability and maintainability. The AI explained that if further time occurrences like "monthly" or "yearly" are added, then only the RECURRENCE_DAYS needs to be changed rather than changing the logic in the method. The explanation helped me better understand the reason behind the suggestion. 

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
The tests implemented include tests to verify sorting (ascending by duration, descending by duration, and by priority), recurrence (next day/week, no next task created when task is not recurring, and adding a next task grows the scheduler by 1), conflict detection (warning when overlapping, no warning when not overlapping), and that tasks with durations longer than the avilable minutes are ignored.
- Why were these tests important?
These tests help verify that the methods work as intended.

**b. Confidence**

- How confident are you that your scheduler works correctly?
Based on the test results (all 15 tests passed), I am fairly confident (4 stars) in the system's reliability.
- What edge cases would you test next if you had more time?
I would add a test that filtering by a pet name with no tasks returns an empty list, rather than raising an error (suggested by Claude).

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I'm happy that the app overall makes sense. For example, once the user inputs their name and the available minutes, they are not able to change those information later, while they can add tasks for different pets. I'm happy that the task list shows the due date of each task, so when a recurring task is marked as complete and a new next task is automatically added, one can check the date of the new task to ensure it is not the same task as the completed one.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would implement the ability to sort tasks by date and time. I would also add the task times to the task list.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
The first code iteration it gave you is likely not the best. It is likely that one would need to ask follow-up questions like, "suggest bug fixes" or "clean up the code", to get better versions of the code.
