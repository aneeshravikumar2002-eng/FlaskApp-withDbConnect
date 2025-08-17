#!/bin/bash
set -e

# Update package list
sudo yum update -y

# Install Python and pip if not present
sudo yum install -y python3 python3-pip

# (Optional) Install database client libraries
# sudo yum install -y postgresql-devel  # For PostgreSQL
# sudo yum install -y mysql-devel       # For MySQL

# Install Python dependencies
pip3 install --user -r requirements.txt

echo "Setup complete."
