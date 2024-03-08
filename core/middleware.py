import logging

from django.http import JsonResponse
from rest_framework import status

from core.errors import LogicError

logger = logging.getLogger(__name__)


class DebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.error(request.META)
        response = self.get_response(request)
        logger.error(response.content)
        return response


class HandleLogicErrorsMiddleWare:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, LogicError):
            logger.error(request.META)
            return JsonResponse({'detail': str(exception)}, status=status.HTTP_400_BAD_REQUEST)
