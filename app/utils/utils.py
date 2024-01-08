from collections import OrderedDict
from rest_framework import status
from django.core.mail import EmailMessage
from typing import Dict, Union, List
from rest_framework.response import Response
import threading
from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 8

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "data": data,
            }
        )

    def get_link_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data if isinstance(data[0], dict) else dict(data)),
                ]
            )
        )


class ResponseManager:
    """Utility class that abstracts how we create a DRF response"""

    @staticmethod
    def handle_response(
        data: Union[Dict, List] = None, errors: Dict = None, status: int = 200, message: str = ""
    ) -> Response:
        if data is None:
            data = []
        if errors is None:
            errors = {}
        if errors:
            return Response({"errors": errors, "message": message}, status=status)
        return Response({"data": data, "message": message}, status=status)

    @staticmethod
    def handle_paginated_response(
        paginator_instance: PageNumberPagination = PageNumberPagination(), data=None
    ) -> Response:
        if data is None:
            data = {}
        return paginator_instance.get_paginated_response(data)

    @staticmethod
    def handle_dict_paginated_response(
        paginator_instance: PageNumberPagination = PageNumberPagination(), data=None
    ) -> Response:
        if data is None:
            data = {}
        return paginator_instance.get_link_paginated_response(data)

    @staticmethod
    def paginate_response(
        queryset, request, serializer_=None, page_size=10, paginator=CustomPagination
    ):
        paginator_instance = paginator()
        paginator_instance.page_size = page_size
        if not serializer_:
            return ResponseManager.handle_paginated_response(
                paginator_instance,
                paginator_instance.paginate_queryset(queryset, request),
            )
        return ResponseManager.handle_paginated_response(
            paginator_instance,
            serializer_(
                paginator_instance.paginate_queryset(queryset, request), many=True
            ).data,
        )

    @staticmethod
    def paginate_dict_response(
        result, request, page_size=10, paginator=CustomPagination
    ):
        paginator_instance = paginator()
        queryset = tuple(result.items())
        paginator_instance.page_size = page_size
        return ResponseManager.handle_dict_paginated_response(
            paginator_instance, paginator_instance.paginate_queryset(queryset, request)
        )

    @staticmethod
    def paginate_list_response(
        result, request, page_size=10, paginator=CustomPagination
    ):
        paginator_instance = paginator()
        queryset = result
        paginator_instance.page_size = page_size
        return ResponseManager.handle_dict_paginated_response(
            paginator_instance, paginator_instance.paginate_queryset(queryset, request)
        )

class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class EmailManager:
    """
    Utility class that abstracts how we send emails
    """
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], from_email='obedbalogun@gmail.com',
            to=[data['to_email']])
        email.content_subtype = "html"
        EmailThread(email).start()


class CustomResponseMixin:
    """
    A mixin for the generic serializer validation and request response
    """

    def response(self, response, data=None):
        return ResponseManager.handle_response(
            errors=response.get("error", None) or response.get("server_error", None),
            message=response.get("success", None),
            data=response.get("data", None) or data,
            status=response.get("status", None) or (status.HTTP_400_BAD_REQUEST if response.get("error", None)
                                                    else status.HTTP_200_OK if response.get("success", None)
            else status.HTTP_500_INTERNAL_SERVER_ERROR if response.get("server_error", None)
            else status.HTTP_201_CREATED),
        )

    def validate_serializer(self, serialized_data):
        if not serialized_data.is_valid():
            return ResponseManager.handle_response(
                errors=list(serialized_data.errors.items())[0][0] + " error",
                message="Payload is not valid",
                status=status.HTTP_400_BAD_REQUEST,
            )
        pass





