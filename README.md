# Flask User Form with MySQL RDS on AWS

This is a simple **Flask** application that runs on **Amazon Linux EC2** and connects to a **MySQL RDS** database.  
It provides a web form to collect **username**, **phone number**, and **place**, then stores the data in a MySQL table.

---

## Features
- Simple HTML form
- Stores user data in AWS RDS MySQL
- Runs on Amazon Linux 2023 EC2
- Minimal dependencies

---

## Project Structure
flaskapp/
│
├── app.py # Flask backend code
└── templates/
└── form.html # HTML form template

---

## Prerequisites
Before running the project, make sure you have:
- **AWS EC2 instance** running Amazon Linux 2023
- **AWS RDS MySQL instance** with a database and table created
- Security group rules allowing:
  - Port **5000** for Flask
  - MySQL Port **3306** between EC2 and RDS

---

## MySQL Setup
Run this in your MySQL RDS:
```sql
CREATE DATABASE mydb;
USE mydb;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    phone VARCHAR(20),
    place VARCHAR(100)
);
Installation on EC2
SSH into your EC2 and run:

# Update packages
sudo dnf update -y

# Install pip
sudo dnf install python3-pip -y

# Install dependencies
pip3 install flask pymysql

# Clone this repo
git clone https://github.com/Shreenivas123/FlaskApp-withDbConnect.git
cd FlaskApp-withDbConnect

# Edit RDS credentials in app.py
nano app.py
Running the App

# Foreground
python3 app.py

# Background
nohup python3 app.py &
Access the App
Visit:

http://<EC2_PUBLIC_IP>:5000
Example DB Config in app.py



DB_HOST = "your-rds-endpoint"
DB_USER = "admin"
DB_PASS = "yourpassword"
DB_NAME = "mydb"
Screenshot

# Multistage Docker build commands

docker build -t multibuildflask \
  -f ~/FlaskApp-withDbConnect/multistagedocker/Dockerfile \
  ~/FlaskApp-withDbConnect/


