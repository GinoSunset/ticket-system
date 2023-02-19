import openpyxl
from openpyxl.styles import Font, Alignment, Color, PatternFill
from openpyxl.styles.borders import Border, Side
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell.cell import Cell

from collections import namedtuple

from django.db import models
from django.db.models import Q
from users.models import User
from tempfile import NamedTemporaryFile

from ticket.models import Ticket
from additionally.models import Dictionary

ALIGNMENT_DEFAULT = Alignment(horizontal="center", vertical="center", wrapText=False)
alignment_not_wrap = Alignment(horizontal="center", vertical="center", wrapText=False)
alignment_not_wrap_left = Alignment(
    horizontal="left", vertical="center", wrapText=False
)
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

row_style = StyleField(
    BORDER_DEFAULT, alignment_not_wrap_left, FONT_DEFAULT, None, None
)
row_style_bold = StyleField(
    BORDER_DEFAULT, alignment_not_wrap_left, font_bold, None, None
)
row_style_center = StyleField(
    BORDER_DEFAULT, ALIGNMENT_DEFAULT, FONT_DEFAULT, None, None
)
row_style_number = StyleField(BORDER_DEFAULT, ALIGNMENT_DEFAULT, FONT_DEFAULT, None, 1)


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
                Q(date_update__lte=self.end_date)
                | Q(completion_date__lte=self.end_date)
            )
            & Q(date_create__gte=self.start_date)
        )
        return tickets

    def create_report(self):
        tickets = self.get_tickets_to_report()
        self.create_excel_file(tickets)

    def create_excel_file(self, tickets):
        """
        Create excel file with tickets
        """

        wb = openpyxl.Workbook()
        ws: Worksheet = wb.active
        ws.title = "Отчет"
        ws.append(self.header_style(ws))
        for num, ticket in enumerate(tickets):
            values = [
                num + 1,
                ticket["sap_id"],
                ticket["shop_id"],
                ticket["address"],
                ticket["date_create"].date(),
                ticket["date_update"].date(),
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

        for num, value in enumerate(data):
            c = Cell(ws, column=num + 1, row=row_num, value=value)
            if num == number_row:
                self.set_style(c, ws, style=row_style_number)
            if num in (date_start, date_end):
                self.set_style(c, ws, style=row_style_center)
            elif num == sap_id:
                self.set_style(c, ws, style=row_style_bold)
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
            length = len(str(c.value)) + 4
            length = length if length > 10 else 10
            ws.column_dimensions[c.column_letter].width = length
