"""
Contains the LLM prompts
"""

# Context prompt for the application
system_message = """
You are a research assistant. You will help a user with questions
about their book notes and highlights contained in a knowledge base.
Provide accurate and concise information based only on the content in
the knowledge base. Do not make up information.
"""

query_decomposition_message = """
Given the user query below, convert the query into questions with multiple
variants that can be used to search for information in the knowledge base.

Generate a maximun of {max_variants} search queries, one on each line separated
with the newline character

User query: {user_query}
Generated queries:
"""

answer_message = """
Use the retrieved context to answer the question in a precise manner. Help
the user see the connections between the sources and the answer.

You can and should quote the context in your response. You may also choose
to paraphrase. In either case you should add the source id following the text
that links to the source text. The id should be marked with '```' at the
beginning and end e.g. ```cbbff85d-cf4b-4b2d-a497-8181d33d8be6```, and added
in the relevant place in the response.

If the context does not provide an answer then respond with a message
indicating that the answer could not be found.

## Examples
Question: What is the main cause of success?
Context:
id: cbbff85d-cf4b-4b2d-a497-8181d33d8be6
text: Success is due to hard work and discipline

id: cbbff85d-cf4b-4b2d-a497-0000033d8be6
text: Success is due to luck

id: aafff85d-cf4b-4b2d-a497-0000033d8bf2
text: Charlie was a big person

Response: There are varying reasons for success. Some say it's due to hard
work and discipline ```cbbff85d-cf4b-4b2d-a497-8181d33d8be6```, while others
believe it's due to luck ```cbbff85d-cf4b-4b2d-a497-0000033d8be6```.
---
Question: Who won the 2020 election?
Context: []
Response: I'm sorry, I couldn't find the answer to your question in your
notes and highlights.

Now it's your turn to answer the user's question.
Question: {question}
Context: {context}
Response:
"""
