# Reflections

### What are the limitations or biases in your system?

The big limitation about my system is that it only retrieves information from the database. If the information is not in the codebase, the AI will not answer. Whether relevant information can be retrieved from the database also depends on how well the semantic comparison works. 

### Could your AI be misused, and how would you prevent that?

My AI could be misused as a general Gemini chatbot. Users might ask it questions unrelated to pet care, costing API call fees. I am preventing this by making the AI only respond based on context retrieved from the database. If nothing is retrieved, then the AI will punt. This will discourage users from asking unrelated questions.

### What surprised you while testing your AI's reliability?

I was surprised that when I asked a meta question, like "how many information do you have about cats", the AI chatbot still answered well, like "I have information about grooming, outdoor safety, and litter box care for cats!"

### Describe your collaboration with AI during this project. Identify one instance when the AI gave a helpful suggestion and one instance where its suggestion was flawed or incorrect.

When starting the project, I asked the AI for ideas to implement RAG into this project, and the AI gave various ideas including the current idea to implement a chatbot that retrieves information from a database. I thought this was a good, simple idea that puts together what I have learned in this course.

The AI suggested outdated Gemini embedding and chat models, which caused the program to crash. I asked the AI to troubleshoot but the suggestions were not helpful - the program was still crashing. I finally researched the issue myself and found that the program was calling from an obsolete Gemini chat model. So I found that for things that may have changed recently, such as the chat model or embedding model, it is better for a human to verify.