mkdir -p db
rm db/relevation.db

python manage.py migrate --run-syncdb
python manage.py runserver
