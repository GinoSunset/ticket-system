from django.core.management.base import BaseCommand, CommandError

from ticket.handlers_itsm import get_url_one_task, get_with_auth_header, process_response, create_itsm_task


class Command(BaseCommand):
    help = "Создать ticket из ITSM по sys_id"

    def add_arguments(self, parser):
        parser.add_argument("itsm_id", help="ITSМ record sys_id")

    def handle(self, *args, **options):
        itsm_id = options["itsm_id"]
        url = get_url_one_task(itsm_id)
        try:
            response = get_with_auth_header(url)
            data = process_response(response)

            if isinstance(data, list):
                if not data:
                    self.stdout.write(self.style.ERROR(f"Нет данных для id {itsm_id}"))
                    return
                task = data[0]
            elif isinstance(data, dict):
                task = data
            else:
                self.stdout.write(self.style.ERROR("Неожиданный формат ответа от ITSM"))
                return

            created = create_itsm_task(task)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Ticket для {itsm_id} создан"))
            else:
                self.stdout.write(self.style.WARNING(f"Ticket для {itsm_id} уже существует или не создан"))
        except Exception as e:
            raise CommandError(f"Ошибка при получении/создании ticket: {e}")
