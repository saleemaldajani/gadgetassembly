# Use the official Codespaces Python image
FROM mcr.microsoft.com/vscode/devcontainers/python:3.9

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip \
 && pip install -r /tmp/requirements.txt

# Expose Dash default port
EXPOSE 8050

# Launch the Dash app
CMD ["python", "app.py"]