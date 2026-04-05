# DocuBot Model Card

This model card is a short reflection on your DocuBot system. Fill it out after you have implemented retrieval and experimented with all three modes:

1. Naive LLM over full docs  
2. Retrieval only  
3. RAG (retrieval plus LLM)

Use clear, honest descriptions. It is fine if your system is imperfect.

---

## 1. System Overview

**What is DocuBot trying to do?**  
Describe the overall goal in 2 to 3 sentences.

> _Your answer here._

**What inputs does DocuBot take?**  
For example: user question, docs in folder, environment variables.

> _Your answer here._

**What outputs does DocuBot produce?**

> _Your answer here._

---

## 2. Retrieval Design

**How does your retrieval system work?**  
Describe your choices for indexing and scoring.

- How do you turn documents into an index?
- How do you score relevance for a query?
- How do you choose top snippets?

> _Your answer here._

**What tradeoffs did you make?**  
For example: speed vs precision, simplicity vs accuracy.

> _Your answer here._

---

## 3. Use of the LLM (Gemini)

**When does DocuBot call the LLM and when does it not?**  
Briefly describe how each mode behaves.

- Naive LLM mode:
- Retrieval only mode:
- RAG mode:

> _Your answer here._

**What instructions do you give the LLM to keep it grounded?**  
Summarize the rules from your prompt. For example: only use snippets, say "I do not know" when needed, cite files.

> _Your answer here._

---

## 4. Experiments and Comparisons

Run the **same set of queries** in all three modes. Fill in the table with short notes.

You can reuse or adapt the queries from `dataset.py`.

| Query | Naive LLM: helpful or harmful? | Retrieval only: helpful or harmful? | RAG: helpful or harmful? | Notes |
|------|---------------------------------|--------------------------------------|---------------------------|-------|
| Example: Where is the auth token generated? | Harmful — confident but wrong. Listed OAuth, API Gateway, Node.js `jsonwebtoken`. Never mentioned `generate_access_token` in `auth_utils.py`. | Helpful — returned three real AUTH.md paragraphs including the correct function and env var. Hard to read as a direct answer. | Harmful — returned "I do not know based on the docs I have." Silent failure despite docs containing the answer. | RAG failure likely caused by query tokenization mismatch or empty chunk scoring. |
| Example: How do I connect to the database? | | | | |
| Example: Which endpoint lists all users? | | | | |
| Example: How does a client refresh an access token? | | | | |

**What patterns did you notice?**  

- **When does naive LLM look impressive but untrustworthy?** When the question is about something common (like auth tokens), the LLM produces a polished, well-structured answer drawn from its training data — but that answer describes general patterns, not this specific application. It never mentions `generate_access_token`, `auth_utils.py`, or `AUTH_SECRET_KEY` because it has no access to the docs. The output looks authoritative but could send a developer in the wrong direction.

- **When is retrieval only clearly better?** When accuracy matters more than readability. Retrieval only guarantees that every word shown came directly from the docs — no hallucination is possible. For verification tasks ("does the docs say X?") or when the user just needs a reference, it is more trustworthy than any LLM output.

- **When is RAG clearly better than both?** RAG should be better when retrieval finds the right chunks and the LLM synthesizes them into a readable, direct answer. In that case it combines the accuracy of retrieval with the readability of generation. However, RAG silently fails when retrieval returns nothing — making it appear the docs don't contain the answer when they do. That silent failure is the most dangerous outcome.

---

## 5. Failure Cases and Guardrails

**Describe at least two concrete failure cases you observed.**  
For each one, say:

- What was the question?  
- What did the system do?  
- What should have happened instead?

> _Failure case 1 here._

> _Failure case 2 here._

**When should DocuBot say “I do not know based on the docs I have”?**  
Give at least two specific situations.

> _Your answer here._

**What guardrails did you implement?**  
Examples: refusal rules, thresholds, limits on snippets, safe defaults.

> _Your answer here._

---

## 6. Limitations and Future Improvements

**Current limitations**  
List at least three limitations of your DocuBot system.

1. _Limitation 1_
2. _Limitation 2_
3. _Limitation 3_

**Future improvements**  
List two or three changes that would most improve reliability or usefulness.

1. _Improvement 1_
2. _Improvement 2_
3. _Improvement 3_

---

## 7. Responsible Use

**Where could this system cause real world harm if used carelessly?**  
Think about wrong answers, missing information, or over trusting the LLM.

> _Your answer here._

**What instructions would you give real developers who want to use DocuBot safely?**  
Write 2 to 4 short bullet points.

- _Guideline 1_
- _Guideline 2_
- _Guideline 3 (optional)_

---
