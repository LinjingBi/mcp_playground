# 1Dbot(v1) – a chatbot that lives in the terminal :)  

### Highly inspired by the simple-chatbot from MCP python-sdk.


## It can
- Chat with LLM(qwen-qwq-32b on [groqcloud](https://console.groq.com/docs/models))
- Save short memory to local(provided by self-developed MCP server under `mcp_playground/server/filesystem`). Triggered by prompt like "save current chat to local".
- Load short memory to current chat. Provided at the beginning of each chat.
- Fetch online url(provided by MCP server [mcp-server-fetch](https://mcp.so/server/fetch/modelcontextprotocol)) Triggered by prompt like "fetch this url https://google.com for me".


## How to
### Install

- Prerequisite
    - python >=3.11
    - uv
    - edit server_config.json for MCP servers

- Cmd
```shell
uv venv && source .venv/bin/activate && uv pip install -e .
```

### Run
```shell
source .venv/bin/activate
python main.py
```

## Why not build into a binary
v1 is only a prototype of something bigger, so I like to have source code ready to edit anytime :)
