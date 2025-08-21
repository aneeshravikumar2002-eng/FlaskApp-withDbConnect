# Flask User Form with MySQL RDS on AWS

A minimal Flask application that collects a username, phone number, and place
and stores the data in a MySQL table hosted on Amazon RDS. The app is intended
to run on an Amazon Linux EC2 instance.

## Features

- HTML form for user details
- Saves records to RDS MySQL and lists recent entries
- Minimal dependencies

## Project Structure

```
.
├── app.py               # Flask backend
├── templates/
│   └── form.html        # HTML form template
├── requirements.txt
├── Dockerfile
└── multistagedocker/
    └── Dockerfile       # Example multi‑stage build
```

## Prerequisites

- Amazon Linux 2023 EC2 instance
- MySQL database on AWS RDS with security group rules allowing:
  - Port **5000** for Flask
  - Port **3306** between EC2 and RDS

## MySQL Setup

Run the following on your RDS instance:

```sql
CREATE DATABASE mydb;
USE mydb;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    phone VARCHAR(20),
    place VARCHAR(100)
);
```

## EC2 Setup

```bash
# Update packages
sudo dnf update -y

# Install pip
sudo dnf install python3-pip -y

# Clone this repo
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# Install dependencies
pip3 install -r requirements.txt

# Edit RDS credentials in app.py
nano app.py

# Set Flask secret key (defaults to "change-me" if unset)
export SECRET_KEY="your-secret-key"
```

## Running the App

```bash
# Foreground
python3 app.py

# Background
nohup python3 app.py &
```

## Access the App

Visit `http://<EC2_PUBLIC_IP>:5000` in your browser.

## Example DB Configuration

```python
DB_HOST = "your-rds-endpoint"
DB_USER = "admin"
DB_PASS = "yourpassword"
DB_NAME = "mydb"
```

## Docker (optional)

Build a multi-stage image:

```bash
docker build -t multibuildflask \
  -f multistagedocker/Dockerfile \
  .
```

