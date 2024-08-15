# Ensure pip is installed
python -m ensurepip --upgrade

# Upgrade pip
python -m pip install --upgrade pip

# Install the Python dependencies
pip install nextcord
pip install apscheduler
pip install python-dotenv
pip install pytz
pip install dateparser
pip install peewee
pip install psycopg2-binary

# Optional: Install development tools
pip install black
pip install flake8
pip install pytest

Write-Output "All dependencies have been installed successfully!"
