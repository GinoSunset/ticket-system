# ticket-system

## RUN
### install requirements
```
pip install -r requirements.txt
```
### run app
```
python manage.py runserver
```
### run celery
run celery
```
celery -A ticsys worker -B -l info 
```
> Celery requires a solution to send and receive messages; usually this comes in the form of a separate service called a message broker.
    
    docker run -d -p 5672:5672 rabbitmq --name rabbitmq-ticsys
    
