FROM python:3.11-slim

WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/requirements.txt
RUN pip install -U --force-reinstall -r requirements.txt
COPY ./src /app/src

RUN pyinstaller --onefile src/tool_server.py --name mcp_tool_server --paths src
RUN pyinstaller --onefile src/server.py \
    --name mcp_agent_server \
    --paths src \
    --hidden-import=tiktoken_ext \
    --hidden-import=tiktoken_ext.openai_public \
    --add-data "/usr/local/lib/python3.11/site-packages/llama_index/core/agent/react/templates:llama_index/core/agent/react/templates" \
    --add-data "/usr/local/lib/python3.11/site-packages/litellm/litellm_core_utils/tokenizers:litellm/litellm_core_utils/tokenizers"


RUN cp dist/mcp_tool_server /usr/local/bin/mcp_tool_server && \
    cp dist/mcp_agent_server /usr/local/bin/mcp_agent_server && \
    rm -rf build dist *.spec

