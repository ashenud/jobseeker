FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml /app/
RUN pip install --no-cache-dir -e .[dev]
COPY . /app
EXPOSE 8000
CMD ["uvicorn", "job_agent.web.app:create_app", "--factory", "--host", "127.0.0.1", "--port", "8000"]
