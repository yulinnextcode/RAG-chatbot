FROM python:3.12-slim



# Set environment variables

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1



# # Install dependencies

# RUN apt-get update && apt-get install -y gcc libaio1

RUN apt-get update && apt-get install -y \
    gcc \
    libaio-dev \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    unzip \
    wget \
 && rm -rf /var/lib/apt/lists/*


# Install Oracle Instant Client
RUN wget https://download.oracle.com/otn_software/linux/instantclient/2350000/instantclient-basiclite-linux.x64-23.5.0.24.07.zip \
    && unzip instantclient-basiclite-linux.x64-23.5.0.24.07.zip \
    && rm instantclient-basiclite-linux.x64-23.5.0.24.07.zip \
    && mv instantclient_23_5 /opt/oracle


# Set up Oracle Instant Client environment variables
ENV LD_LIBRARY_PATH=/opt/oracle
ENV PATH=$PATH:/opt/oracle


# Create working directory

WORKDIR /app



# Copy requirements.txt

COPY requirements.txt /app/


# Install Python dependencies

RUN python -m pip cache purge

RUN pip3 install --upgrade pip && pip install --no-cache-dir -r requirements.txt

RUN python -m pip install cx_Oracle

# Copy the application code

COPY . /app/



# Expose the port the app runs on

EXPOSE 5000



# Run the application with Gunicorn

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

