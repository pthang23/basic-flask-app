FROM python:3.10
#EXPOSE 5000
WORKDIR /app

RUN apt update

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["/bin/bash", "docker-entrypoint.sh"]
#CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:create_app()"]
#CMD ["flask", "run", "--host", "0.0.0.0"]