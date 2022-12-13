from typing import Dict
from rest_framework.response import Response


class ResponseManager:
    """Utility class that abstracts how we create a DRF response"""

    @staticmethod
    def handle_response(
            data: Dict = None, errors: Dict = None, status: int = 200, message: str = ""
    ) -> Response:
        if data is None:
            data = {}
        if errors is None:
            errors = {}
        if errors:
            return Response({"errors": errors, "message": message}, status=status)
        return Response({"data": data, "message": message}, status=status)
