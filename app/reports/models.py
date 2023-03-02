import re
from collections import namedtuple
from tempfile import NamedTemporaryFile

import openpyxl
from additionally.models import Dictionary
from django.conf import settings
from django.db import models
from django.db.models import Q
from docxtpl import DocxTemplate
from openpyxl.cell.cell import Cell
from openpyxl.styles import Alignment, Color, Font, PatternFill
from openpyxl.styles.borders import Border, Side
from openpyxl.worksheet.worksheet import Worksheet
from ticket.models import Ticket
from users.models import User

ALIGNMENT_DEFAULT = Alignment(horizontal="center", vertical="center", wrapText=True)
alignment_not_wrap = Alignment(horizontal="center", vertical="center", wrapText=True)
alignment_wrap_left = Alignment(horizontal="left", vertical="center", wrapText=True)
font_bold = Font(size=14, bold=True)
FONT_DEFAULT = Font(size=14, bold=False)
color = Color(rgb="3aaacf")
BORDER_DEFAULT = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)

StyleField = namedtuple("StyleField", ["border", "alignment", "font", "fill", "length"])

style_title = StyleField(BORDER_DEFAULT, ALIGNMENT_DEFAULT, font_bold, None, None)
style_title_not_bold = StyleField(None, alignment_not_wrap, FONT_DEFAULT, None, None)

row_style = StyleField(BORDER_DEFAULT, alignment_wrap_left, FONT_DEFAULT, None, None)
row_style_bold = StyleField(BORDER_DEFAULT, alignment_wrap_left, font_bold, None, None)
row_style_center = StyleField(
    BORDER_DEFAULT, ALIGNMENT_DEFAULT, FONT_DEFAULT, None, None
)
row_style_number = StyleField(BORDER_DEFAULT, ALIGNMENT_DEFAULT, FONT_DEFAULT, None, 1)
row_style_comment = StyleField(
    BORDER_DEFAULT, alignment_wrap_left, FONT_DEFAULT, None, 60
)


class Report(models.Model):
    class Meta:
        verbose_name = "Отчет"
        verbose_name_plural = "Отчеты"
        ordering = ["-date_create"]

    date_create = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    creator = models.ForeignKey(
        User, verbose_name="Создатель", related_name="reports", on_delete=models.CASCADE
    )
    file = models.FileField(upload_to="reports/%Y/%m/", verbose_name="Отчет")

    def __str__(self):
        return f"{self.start_date}-{self.end_date} [{self.date_create}]"

    @property
    def file_name(self):
        return self.file.name.split("/")[-1]

    def get_tickets_to_report(self):
        status = Dictionary.get_status_ticket("done")
        tickets = Ticket.objects.filter(
            Q(status=status)
            & (
                Q(completion_date__date__lte=self.end_date)
                | Q(date_update__date__lte=self.end_date)
            )
            & Q(completion_date__date__gte=self.start_date)
        )
        return tickets

    def create_report(self):
        tickets = self.get_tickets_to_report()
        self.create_excel_file(tickets)

    def get_comments(self, ticket):
        comments = ticket.get_comments_for_report()
        comments_text = "\n------------\n".join(
            [
                f"[{comment.author}-{comment.date_create.strftime('%d-%m-%Y')}]\n{self.clean_text_from_html(comment.text)}"
                for comment in comments
            ]
        )

        return comments_text

    def clean_text_from_html(self, text):
        if "<div>" not in text:
            return text
        html_tag_pattern = re.compile(r"<[^>]+>")
        text_without_html = re.sub(html_tag_pattern, "", text)
        return f"<! удалены html теги !>{text_without_html}"

    def create_excel_file(self, tickets):
        """
        Create excel file with tickets
        """

        wb = openpyxl.Workbook()
        ws: Worksheet = wb.active
        ws.title = "Отчет"
        ws.append(self.header_style(ws))
        for num, ticket in enumerate(tickets):
            comments_text = self.get_comments(ticket)
            values = [
                num + 1,
                ticket.sap_id,
                ticket.shop_id,
                ticket.address,
                ticket.date_create.date(),
                ticket.date_update.date(),
                comments_text,
            ]
            ws.append(self.row_style(ws, num + 2, values))
        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            self.file.save(f"{self.start_date}-{self.end_date}.xlsx", tmp)

    def header_style(self, ws: Worksheet):
        headers = [
            " ",
            "№ Заявки ДМ",
            "Наименование Объекта",
            "Адрес Объекта (магазина «Детский мир»)",
            "Дата принятия в работу",
            "Дата закрытия заявки",
            "Комментарии",
        ]
        for header in headers:
            c = Cell(ws, column=headers.index(header) + 1, row=1, value=header)
            self.set_style(c, ws, style=style_title)
            # c.length = style_title.length

            yield c

    def row_style(self, ws: Worksheet, row_num, data):
        number_row = 0
        date_start = 4
        date_end = 5
        sap_id = 1
        comment = 6

        for num, value in enumerate(data):
            c = Cell(ws, column=num + 1, row=row_num, value=value)
            if num == number_row:
                self.set_style(c, ws, style=row_style_number)
            if num in (date_start, date_end):
                self.set_style(c, ws, style=row_style_center)
            elif num == sap_id:
                self.set_style(c, ws, style=row_style_bold)
            elif num == comment:
                self.set_style(c, ws, style=row_style_comment)
            else:
                self.set_style(c, ws, style=row_style)
            yield c

    def set_style(self, c, ws: Worksheet, style):
        if style.border:
            c.border = style.border
        if style.alignment:
            c.alignment = style.alignment
        if style.font:
            c.font = style.font
        if style.fill:
            c.fill = style.fill
        if style.length:
            ws.column_dimensions[c.column_letter].width = style.length
        else:
            length = len(str(c.value)) + 6
            length = length if length > 10 else 10
            ws.column_dimensions[c.column_letter].width = length


class Act(models.Model):
    class Meta:
        verbose_name = "Акт выполненных работ"
        verbose_name_plural = "Акты выполненных работ"

    ticket = models.OneToOneField(
        Ticket, verbose_name="Заявка", on_delete=models.CASCADE
    )

    date_create = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    file_doc_act = models.FileField(
        upload_to="secret/acts/%Y/%m/", verbose_name="Акт выполненных работ"
    )

    def create_act(self):
        template_dir = settings.BASE_DIR / "reports/templates/reports/act"
        template = template_dir / "act_DM.docx"
        doc = DocxTemplate(template)
        context = self.get_context()
        doc.render(context)
        with NamedTemporaryFile() as tmp:
            doc.save(tmp.name)
            self.file_doc_act.save(f"{self.ticket.pk}.docx", tmp)

    def __str__(self) -> str:
        return f"Акт {self.ticket}"

    def get_context(self):
        date_start = self.ticket.date_to_work or self.ticket.date_create
        date_str = self.get_str_date(date_start)
        context = {
            "ticket": self.ticket,
            "date": date_str,
            "org": self.ticket.customer.profile.company or " ",
        }
        return context

    def get_str_date(self, date):
        month = {
            1: "января",
            2: "февраля",
            3: "марта",
            4: "апреля",
            5: "мая",
            6: "июня",
            7: "июля",
            8: "августа",
            9: "сентября",
            10: "октября",
            11: "ноября",
            12: "декабря",
        }
        date_str = f"«{date.day}» {month[date.month]} {date.year}"
        return date_str
