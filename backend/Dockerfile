# select python image
FROM python:3.12

# Update package lists
RUN apt-get update && \
    apt-get -y upgrade

# Set the working directory in the container
WORKDIR /workspace

# Install pip
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 8080

# Run any command to initialize the container
CMD ["bash"]