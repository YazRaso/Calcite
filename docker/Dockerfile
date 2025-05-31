# Use the official Rasa base image
FROM rasa/rasa:3.6.20

# Define a base directory for our application code
ENV APP_BASE=/opt/rasa_project
# APP_HOME will be where the actual project files (the 'app' package) reside
ENV APP_HOME=${APP_BASE}/app

# Switch to root user to install system dependencies and create directories
USER root

# Create these directories
RUN mkdir -p ${APP_HOME}

# Set DEBIAN_FRONTEND to noninteractive to prevent apt-get from prompting
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies required by PySide6 and other packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libdbus-1-3 \
    libxcb1 \
    libxcb-glx0 \
    libx11-xcb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-shm0 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    libgl1-mesa-glx \
    libgl1-mesa-dev \
    libglu1-mesa \
    libglu1-mesa-dev \
    libfontconfig1 \
    libfreetype6 \
    libxrender1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    ldconfig

# Set PYTHONPATH to include the APP_BASE directory.
# This allows Python to find the 'app' package within APP_BASE.
ENV PYTHONPATH "${PYTHONPATH}:${APP_BASE}"

# Copy the current directory contents (your project) into the APP_HOME directory
# e.g., your project root becomes /opt/rasa_project/app/
COPY . ${APP_HOME}

# Set the working directory to APP_BASE.
# This is crucial for Python to correctly resolve 'app.core.books'
# and not confuse the 'app' package with 'app.py' within APP_HOME.
WORKDIR ${APP_BASE}

# Install custom Python dependencies for your actions
# The path to requirements.txt is now relative to WORKDIR (${APP_BASE})
# and needs to point into the copied 'app' directory.
RUN if [ -f "${APP_HOME}/bot/actions/requirements.txt" ]; then \
      echo "Found ${APP_HOME}/bot/actions/requirements.txt, installing dependencies..." && \
      pip install --no-cache-dir --upgrade pip && \
      pip install --no-cache-dir -r "${APP_HOME}/bot/actions/requirements.txt"; \
    else \
      echo "${APP_HOME}/bot/actions/requirements.txt not found, skipping pip install."; \
    fi

EXPOSE 5005
EXPOSE 5055