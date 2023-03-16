# Use an official Python
FROM python:latest

ENV APP_HOME=/home/user/app \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.3.2 \
    POETRY_HOME=/home/user/poetry \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

ENV PATH="$POETRY_HOME/bin:$PATH" \
    PYTHONPATH=$APP_HOME/:$PYTHONPATH


# Set the working directory to /app
WORKDIR /app

# Install modules
RUN pip install --upgrade pip
RUN curl -sSL https://install.python-poetry.org | python -

# Copy the pyproject.toml and poetry.lock files into the container at /app
COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --no-root

# Copy the rest of the application code into the container at /app
COPY . ./app

# Start the server
CMD ["python", "main.py"]

