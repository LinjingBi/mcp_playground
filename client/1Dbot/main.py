"""
1. start with input()
2. prompt to LLM has 4 parts:
    - context
    - tool description
    - question
    - tool response(if any)
3. if LLM needs tool, should return a json strictly following the format:
    {tools: [{"name": "tool_name", "input": "input_json"}]}

4. if no tool needed, just return a json with:
    {"answer": "answer", "context": "a short summary of previous context and new answer"}


input -> client -> LLM -> client -> (server -> client -> LLM -> client) -> output
"""




