# How the Chatbot Creates an Answer

The chatbot generates an answer by following these steps:

1. **Receive Input**:
   - The chatbot receives a request containing the user's input (`chat_input`), selector choices, and reasoning type.

2. **Generate Conversation ID**:
   - If no `conversation_id` is provided, a new one is generated using the `generate_conversation_id` utility.

3. **Load Chat History**:
   - The chatbot retrieves the conversation history for the given `user_id` and `conversation_id` using the `load_chat_history` function.

4. **Build RAG Chain**:
   - The `build_rag_chain` function is called to create a pipeline for retrieving context and generating a response. This chain includes:
     - **Context Retrieval**:
       - The `get_context` function retrieves relevant chunks of information from the vector store using the `retrieve_context` function.
     - **Prompt Template**:
       - A predefined prompt (`RAG_PROMPT_PDF`) is used to structure the input for the language model.
     - **Language Model**:
       - The `ChatOllama` model processes the input and generates a response.
     - **Output Parsing**:
       - The response is parsed into a string format using `StrOutputParser`.

5. **Invoke RAG Chain**:
   - The RAG chain is invoked with the input data (`selector_choices`, `chat_input`, and `reasoning_type`) to generate a response.

6. **Save Chat History**:
   - The chatbot appends the user's input and the generated response to the chat history and saves it using the `save_chat_history` function.

7. **Return Response**:
   - The chatbot returns a `ChatResponse` object containing:
     - The generated answer.
     - The updated chat history.
     - The conversation ID.

This process ensures that the chatbot provides contextually relevant and accurate answers based on the user's input and the available data.

```# How the Chatbot Creates an Answer

The chatbot generates an answer by following these steps:

1. **Receive Input**:
   - The chatbot receives a request containing the user's input (`chat_input`), selector choices, and reasoning type.

2. **Generate Conversation ID**:
   - If no `conversation_id` is provided, a new one is generated using the `generate_conversation_id` utility.

3. **Load Chat History**:
   - The chatbot retrieves the conversation history for the given `user_id` and `conversation_id` using the `load_chat_history` function.

4. **Build RAG Chain**:
   - The `build_rag_chain` function is called to create a pipeline for retrieving context and generating a response. This chain includes:
     - **Context Retrieval**:
       - The `get_context` function retrieves relevant chunks of information from the vector store using the `retrieve_context` function.
     - **Prompt Template**:
       - A predefined prompt (`RAG_PROMPT_PDF`) is used to structure the input for the language model.
     - **Language Model**:
       - The `ChatOllama` model processes the input and generates a response.
     - **Output Parsing**:
       - The response is parsed into a string format using `StrOutputParser`.

5. **Invoke RAG Chain**:
   - The RAG chain is invoked with the input data (`selector_choices`, `chat_input`, and `reasoning_type`) to generate a response.

6. **Save Chat History**:
   - The chatbot appends the user's input and the generated response to the chat history and saves it using the `save_chat_history` function.

7. **Return Response**:
   - The chatbot returns a `ChatResponse` object containing:
     - The generated answer.
     - The updated chat history.
     - The conversation ID.

This process ensures that the chatbot provides contextually relevant and accurate answers based on the user's input and the available data.
