FROM python:3.13
WORKDIR /app
COPY pyproject.toml .
COPY poetry.lock .
RUN pip install poetry
RUN poetry install --no-root
COPY api.py .
COPY lib lib
COPY setup.cfg .
CMD ["poetry", "run", "uvicorn", "api:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]
