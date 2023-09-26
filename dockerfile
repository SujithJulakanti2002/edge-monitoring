# Use the official Python image as the base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy your requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --trusted-host files.pythonhosted.org --trusted-host pypi.org --trusted-host pypi.python.org -r requirements.txt

# Copy your Python script and JSON file into the container
COPY log_processor_v2.py .
COPY keywords.json .

# Define the command to run your Python script
CMD ["python", "your_script.py"]
