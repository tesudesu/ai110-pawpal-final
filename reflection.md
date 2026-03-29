# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
The previous filter_tasks method uses two passes - one for filtering by status and another for filtering by pet_name. Claude suggested to combine these in one pass. 
- Why is that tradeoff reasonable for this scenario?
One pass is more efficient than two passes.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
The AI suggested to add a RECURRENCE_DAYS dictionary like RECURRENCE_DAYS = {"daily": 1, "weekly": 7} for the mark_complete method to avoid checking the self.recurrence string twice. I did not fully understand what the AI meant. 

- How did you evaluate or verify what the AI suggested?
I copied and pasted the AI's suggested fix back to the AI to ask it to explain. I also asked the AI what is the change in time complexity before and after the fix, which the AI stated there is no change except for improvements in readability and maintainability. The AI explained that if further time occurrences like "monthly" or "yearly" are added, then only the RECURRENCE_DAYS needs to be changed rather than changing the logic in the method. These explanation helped me better understand the reason behind the suggestion. 

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
