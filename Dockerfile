# Note: AI assistance was used to structure this Dockerfile.
# The base image selection, layer ordering, and entrypoint syntax were AI-assisted.
# The decision to containerize and what to run was made independently.

FROM python:3.12-slim

WORKDIR /app

# Install dependencies first so this layer is cached on code-only changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["pytest"]
CMD ["-v", "--tb=short", "tests/"]
