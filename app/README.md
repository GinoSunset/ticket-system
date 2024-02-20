# ticket-system

## RUN
### install requirements
```
pip install -r requirements.txt
```


1. Установите переменные окружения или напишите его в файле .env в корне проекта:
```bash
# env for db
    export POSTGRES_DB="helpdeskdb"
    export POSTGRES_USER="helpdesk_user"
    export POSTGRES_PASSWORD=""
    export POSTGRES_EXTRA_OPTS=-Z1 --schema=public --blobs
# env for db
    export POSTGRES_HOST=postgres
    export SCHEDULE=@daily
    export BACKUP_KEEP_DAYS=7
    export BACKUP_KEEP_WEEKS=4
    export BACKUP_KEEP_MONTHS=6
    export HEALTHCHECK_PORT=8080
# other    
    export SECRET_KEY="django-insecure-secret"
    export DATABASE_URL="sqlite:///db.sqlite3"
    export DJANGO_ALLOWED_HOSTS="localhost 127.0.0.1"
    export CSRF_TRUSTED_ORIGINS="http://*.127.0.0.1"
    export PROTOCOL="https"
    export EMAIL_HOST_PASSWORD="my-pass"
    export EMAIL_HOST="localhost"
    export EMAIL_PORT="25"
    export EMAIL_IMAP_HOST="user"
    export EMAIL_USE_SSL=on
    export EMAIL_IMAP_PORT="993"
    export EMAIL_IMAP_HOST="imap.yandex.ru"
    export SUBJECT_TO_TICKET="ticket,заявка"
    export PERIOD_CHECK_EMAIL="60"
    export RABBIT_HOST="localhost"
    export RABBIT_LOGIN="user"
    export RABBIT_PASSWORD="guest"
    export RABBIT_VHOST="myvhost"
    export MANAGER_EMAIL="manager@host.com"
    export REDIS_HOST="localhost"
    export REDIS_PORT="6379"
    export SENTRY_DSN="https://sentry.io/..."
    export APP_ENV_SENTRY="my_local"
    export TG_BOT_URL="https://t.me/heff_bot"
```    


# Переменные окружения

 `SECRET_KEY` - секретный ключ Django

 `DATABASE_URL` - URL базы данных

 `DJANGO_ALLOWED_HOSTS` - список допустимых хостов

 `CSRF_TRUSTED_ORIGINS` - список допустимых хостов для CSRF

 `PROTOCOL` - протокол (http/https)

 `EMAIL_HOST_PASSWORD` - пароль для подключения к SMTP серверу отправки писем

 `EMAIL_HOST` - имя SMTP сервера для отправки писем

 `EMAIL_PORT` - порт SMTP сервера для отправки писем

 `EMAIL_IMAP_HOST` - имя IMAP сервера для получения писем

 `EMAIL_USE_SSL` - использование SSL для подключения к SMTP серверу отправки писем (on/off)

 `EMAIL_IMAP_PORT` - порт IMAP сервера для получения писем

 `SUBJECT_TO_TICKET` - список тем в письмах, которые должны быть преобразованы в заявку
 `PERIOD_CHECK_EMAIL` - периодичность проверки 
 почты (в секундах)
 `RABBIT_HOST` - имя хоста RabbitMQ

 `RABBIT_LOGIN` - логин для подключения к RabbitMQ

 `RABBIT_PASSWORD` - пароль для подключения к RabbitMQ

 `RABBIT_VHOST` - имя виртуального хоста RabbitMQ

 `MANAGER_EMAIL` - адрес электронной почты 
менеджера системы

 `REDIS_HOST` - имя хоста Redis

 `REDIS_PORT` - порт Redis

 `SENTRY_DSN` - DSN для интеграции с Sentry

 `APP_ENV_SENTRY` - окружение в Sentry

 `TG_BOT_URL` - URL бота Telegram


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
    


## Users
### Customer
Заказчкик

К каждому заказчику создается дополнительный класс (Profile) с дополнительными полями
 - linked_operators - список операторов, которые могут работать с заказами этого заказчика
 - parser - парсер, который будет использоваться для парсинга email заказов этого заказчика
 - 

    
# Сервисы и инструменты

Django - фреймворк Python для веб-разработки

[PostgreSQL](https://www.postgresql.org/) - объектно-реляционная система управления базами данных

RabbitMQ - брокер 

[Celery](https://docs.celeryproject.org/en/stable/) - асинхронная задача для обработки заданий в фоновом режиме

[Redis](https://redis.io/) - документно-ориентированная система управления данными

[Sentry](https://sentry.io/) - платформа мониторинга ошибок

[Postgres-backup-local](https://github.com/prodrigestivill/docker-postgres-backup-local) - Резервное копирование PostgresSQL в локальную файловую систему с периодической ротацией резервных копий на основе schickling / postgres-backup-s3. Резервное копирование нескольких баз данных с одного хоста путем установки имен баз данных в POSTGRES_DB, разделенных запятыми или пробелами. 


 Telegram Bot API - API для создания ботов в Telegram



## Резервное копирование вручную
По умолчанию `prodrigestivill/postgres-backup-local` контейнер создает ежедневные резервные копии, но вы можете запустить резервное копирование вручную, выполнив /backup.sh.
Этот скрипт в качестве примера создает одну резервную копию от имени запущенного пользователя и сохраняет ее в рабочей папке.

```sh
docker run --rm -v "$PWD:/backups" -u "$(id -u):$(id -g)" -e POSTGRES_HOST=postgres -e POSTGRES_DB=dbname -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password  prodrigestivill/postgres-backup-local /backup.sh
```