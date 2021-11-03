release: pip install pycryptodome && pip uninstall crypto && python manage.py makemigrations && python manage.py migrate
web: gunicorn elearning.wsgi --log-file -