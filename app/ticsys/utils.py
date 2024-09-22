from django.http.request import HttpRequest


def is_htmx(request: HttpRequest) -> bool:
    return request.headers.get("Hx-Request") == "true"
