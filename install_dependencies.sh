# Ensure pip is installed
python -m ensurepip --upgrade

# Install the Python dependencies
pip install nextcord
pip install apscheduler
pip install python-dotenv
pip install pytz
pip install dateparser
pip install peewee
pip install psycopg2-binary
pip install black
pip install flake8
pip install pytest
pip install setuptools

Write-Output "All dependencies have been installed successfully!"
