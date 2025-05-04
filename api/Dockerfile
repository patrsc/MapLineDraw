FROM python:3.13
WORKDIR /app
COPY pyproject.toml .
COPY poetry.lock .
RUN pip install poetry
RUN poetry install --no-root
COPY api.py .
COPY geo.py .
COPY globe.py .
COPY spline.py .
COPY themes.py .
COPY setup.cfg .
COPY util.py .
CMD ["poetry", "run", "uvicorn", "api:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]
