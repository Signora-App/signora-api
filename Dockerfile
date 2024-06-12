# Use the official lightweight Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONBUFFERED True
ENV APP_HOME /app

# Set the working directory
WORKDIR $APP_HOME

# Copy the application files
COPY . ./

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose the port that the application will run on
EXPOSE 8080

# Use Gunicorn to run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "main:app"]
