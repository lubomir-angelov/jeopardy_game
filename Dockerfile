# repo_root/Dockerfile

FROM python:3.13-slim

# Go non-root; set UID explicitly for K8S runAsNonRoot compatibility
RUN useradd --uid 10001 --create-home --shell /bin/bash appuser
USER 10001

# Create venv in user home and prepend PATH
RUN python -m venv /home/appuser/venv
ENV PATH="/home/appuser/venv/bin:${PATH}"

WORKDIR /home/appuser/app

# Install dependencies (requirements are inside repo_root/src/jeopardy_game/)
COPY --chown=10001:10001 requirements.txt /home/appuser/app/requirements.txt

RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install -r /home/appuser/app/requirements.txt

# Copy application package contents directly under /home/appuser/app
# After this, /home/appuser/app/jeopardy_game/... exists (no /home/appuser/app/src)
COPY --chown=10001:10001 src/ /home/appuser/app/

# Copy scripts (loader)
COPY --chown=10001:10001 scripts/ /home/appuser/app/scripts/

# Ensure imports work (jeopardy_game is directly under /home/appuser/app)
ENV PYTHONPATH="/home/appuser/app"

EXPOSE 8000

# Default command for API service; docker-compose can override for the loader service
CMD ["uvicorn", "jeopardy_game.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
