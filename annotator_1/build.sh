# Build command
pip install -r requirements.txt && mkdir -p db && python manage.py migrate --run-syncdb

# Start command
# python manage.py runserver 0.0.0.0:8000
