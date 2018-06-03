FROM python

COPY . /app
WORKDIR /app

RUN pip install pipenv && pipenv install --system --three --deploy

ENTRYPOINT ["gunicorn", "--reload", "-b", ":8000", "api:app"]