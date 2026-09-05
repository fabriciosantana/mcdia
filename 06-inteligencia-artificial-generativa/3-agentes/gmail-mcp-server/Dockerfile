FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY main.py .

# FastMCP defaults to port 8000 in SSE mode
EXPOSE 8000

# The default behavior is to run in SSE mode for HTTP communication (e.g. with Dify)
# Command can be overridden to run without arguments for stdio mode
ENTRYPOINT ["python", "main.py"]
CMD ["sse"]
