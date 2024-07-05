flask db migrate
flask db upgrade

gunicorn --bind 0.0.0.0:80 "app:create_app()"