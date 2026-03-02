# Prompt Engineering Best Practices

## **Group 1: Foundation - Understanding Prompt Structure**

*Start here: What makes up a prompt*

- **Anatomy of a good prompt:**
    - Task description: what the task is and the role/persona of the model
    - Context: background info, reference materials, or grounding data
    - Actual task: specific instructions or text to analyze
    - Output format: structure, length, and style specifications
- **Message roles in prompts:**
    - System prompts: include task descriptions, role-playing instructions, and general behavioral guidance
    - User prompts: the actual task, question, or content to process
- **Using delimiters effectively:**
    - Separate different parts of input using symbols like ###, """, or ``` to distinguish instructions from content
    - Makes prompts clearer and reduces ambiguity about what should be processed vs. what is instruction

---

## **Group 2: Clarity and Specificity**

*The most fundamental principle: being clear about what you want*

- **Be clear and specific:**
    - State exactly what you want the model to do, how to do it, and how to handle uncertainty
    - Unclear intent forces the model to make assumptions that may miss the goal
    - The more specific and detailed, the better the results
    - Include details about desired context, outcome, length, format, and style
- **Define requirements explicitly:**
    - Define scoring systems or output formats you expect
    - Eliminate assumptions by being precise
    - Specify constraints and requirements upfront
    - Avoid saying what NOT to do; instead, say what TO do
- **Provide sufficient context:**
    - Ground the model with background information so it can generate accurate, relevant responses instead of guessing
    - The more relevant the context to the task, the better the performance
- **Strategic placement of information:**
    - Models are better at processing instructions at the beginning and end of prompts
    - Place most important information in strategic positions

---

## **Group 3: Providing Reference Materials**

*Grounding responses in trusted sources*

- **Use reference text to reduce hallucinations:**
    - Include specific documents, excerpts, or trusted sources you want the AI to use
    - Anchors the model's response to factual information
    - Like giving a student notes for a test - helps answer with fewer fabrications
    - Particularly useful when accuracy is critical or information must be based on specific data
    - The closer your source material is to the final answer form, the less work the model needs to do

---

## **Group 4: Core Prompting Techniques**

*Different approaches for different task types*

- **Zero-shot prompting:**
    - No examples provided
    - Meant for straightforward tasks where the model's training provides sufficient context
    - Add format and constraints if required for more accuracy
- **Few-shot prompting:**
    - Provide 1-5 examples of how you want the model to respond
    - Use when you need specific formatting or when desired behavior is ambiguous from instructions alone
    - Helps establish tone and approach
    - Better models need fewer examples
    - For domain-specific or complex formatting tasks, several examples are better
- **Role prompting (Persona adoption):**
    - Assign a persona or area of expertise to the model
    - Influences style, perspective, and depth of responses
    - Useful for customer service, educational content, creative writing - whenever content or expertise matters
    - Example: "You are a senior data scientist" or "Act as an expert marketing consultant"
    - Provide criteria the model should meet in that role

---

## **Group 5: Advanced Reasoning Techniques**

*Getting the model to think through problems*

- **Chain of Thought (CoT) prompting:**
    - Ask the model to think step-by-step before providing an answer
    - Encourages systematic problem-solving
    - Has been shown to improve performance on complex reasoning tasks
    - Simply ask to "think step-by-step" or "show your reasoning"
    - Reduces hallucinations because the model must justify answers with explicit reasoning steps
    - You can specify exactly the steps to follow or provide examples of a reasoning process
    - Trade-off: increased latency and cost
- **Give the model time to "think":**
    - Models make more reasoning errors when trying to answer immediately
    - Allow the model to work out its solution before rushing to a conclusion
    - Use a sequence of queries to guide the reasoning process
    - Request intermediate steps or calculations before final answer

---

## **Group 6: Task Decomposition**

*Breaking complexity into manageable pieces*

- **Prompt chaining:**
    - Break large tasks into smaller, more manageable subtasks
    - Create a series of smaller prompts and chain them together
    - Example: classify intent first, then proceed to handle based on that intent
    - Allows you to monitor and optimize each step independently
    - Can use different models for each step and execute in parallel
- **Sequential processing:**
    - Decompose complex tasks into simpler, sequential steps
    - Ensure output of one step serves as input for the next
    - Instead of summarizing an entire document at once, break it into sections
    - Use intent classification to identify the most relevant instruction for each part
    - Summarize or filter previous conversation segments progressively

---

## **Group 7: Using External Tools**

*Compensating for model limitations*

- **Leverage external tools strategically:**
    - Use text retrieval systems for efficient knowledge retrieval
    - Use code execution engines for accurate calculations and math
    - Use embeddings-based search for finding relevant information
    - If a task can be done more reliably or efficiently by a tool, offload it
    - Examples: Code Interpreter for math, retrieval systems for document search
    - Get the best of both worlds: model intelligence + tool reliability

---

## **Group 8: Iteration and Testing**

*Continuous improvement through systematic evaluation*

- **Iterate and experiment:**
    - Refine prompts based on observed results rather than expecting perfection upfront
    - Start simple and add complexity gradually
    - Adjust wording, add context, or simplify based on output quality
    - Prompt engineering is both art and science - requires experimentation
- **Test changes systematically:**
    - A modification that works on a few examples may lead to worse overall performance
    - Test prompts thoroughly with varied and edge-case inputs to ensure reliability
    - Use evaluation frameworks to compare different prompt versions
    - Measure if changes actually improve performance on representative examples
- **Version control:**
    - Version prompts and evaluate them consistently
    - Track improvements and avoid regressions in the full system
    - Pin production applications to specific model snapshots for consistent behavior
    - Document what works and what doesn't

---

## **Group 9: Best Practices and Guardrails**

*Rules of thumb to follow*

- **Specify output format explicitly:**
    - Control structure, length, and style of responses
    - Especially important when outputs feed into downstream systems
    - Define the exact format needed upfront
- **Use examples strategically:**
    - Deploy examples to reduce ambiguity when instructions alone are insufficient
    - Don't overdo it - better models need fewer examples
    - Balance between providing guidance and overwhelming the model
- **Avoid overcomplicating prompts:**
    - Excessive instructions or examples can confuse rather than help
    - Keep prompts as simple as possible while being complete
    - Remove unnecessary complexity
- **Model-specific considerations:**
    - Better/newer models are easier to prompt and need less hand-holding
    - Reasoning models vs. GPT models require different approaches
    - Reasoning models work well with high-level guidance (like senior coworker)
    - GPT models benefit from very precise instructions (like junior coworker)
    - Model selection and temperature are key parameters to adjust