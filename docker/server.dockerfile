FROM python:3.11-slim

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install -U --force-reinstall -r requirements.txt
EXPOSE $MCP_PORT
CMD ["python", "src/server.py"]
