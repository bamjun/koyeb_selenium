# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install pip packages from requirements.txt
COPY requirements.txt .
RUN pip install --upgrade pip --root-user-action=ignore \
    && pip install --no-cache-dir -r requirements.txt --root-user-action=ignore

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
