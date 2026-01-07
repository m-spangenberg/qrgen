# Run the application
run:
    uv run python main.py

# Run tests
test:
    uv run pytest tests

# Prepare the virtual environment and install all dependencies (runtime + dev)
init:
    uv sync