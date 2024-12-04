from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Manufacture
from .serializers import ManufactureSerializer


class ManufactureDataTableAPIView(APIView):
    def get(self, request, *args, **kwargs):
        draw = request.GET.get("draw", 1)
        start = int(request.GET.get("start", 0))
        length = int(request.GET.get("length", 10))
        search_value = request.GET.get("search[value]", "")

        # Базовый queryset
        queryset = Manufacture.objects.all()

        # Фильтрация
        if search_value:
            queryset = queryset.filter(client__icontains=search_value)

        # Сортировка
        order_column_index = request.GET.get("order[0][column]")
        order_direction = request.GET.get("order[0][dir]")
        if order_column_index and order_direction:
            column_name = [
                "pk",
                "date_create",
                "client",
                "date_shipment",
                "count",
                "branding",
                "status",
                "comment",
            ][int(order_column_index)]
            if order_direction == "desc":
                column_name = f"-{column_name}"
            queryset = queryset.order_by(column_name)

        # Пагинация
        total_count = queryset.count()
        queryset = queryset[start : start + length]

        # Сериализация
        serializer = ManufactureSerializer(queryset, many=True)

        # Формирование ответа
        return Response(
            {
                "draw": int(draw),
                "recordsTotal": total_count,
                "recordsFiltered": total_count,
                "data": serializer.data,
            }
        )
