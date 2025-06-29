export FLASK_SECRET_KEY="$(python3 -c 'import os; print(os.urandom(24))')"
venv/bin/python index.py