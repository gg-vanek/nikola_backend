import logging

from django.http import JsonResponse
from rest_framework import status

from django.conf import settings
from core.errors import LogicError

logger = logging.getLogger(__name__)


class DebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.error("---------------------------------------------------------------------------")
        logger.error(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        logger.error(f"CORS_ALLOWED_ORIGINS: {settings.CORS_ALLOWED_ORIGINS}")
        logger.error(f"CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")

        logger.error(f"request.meta: {request.META}")
        response = self.get_response(request)
        try:
            logger.error(f"response.content {response.content}")
        except Exception as e:
            logger.error(f"no response.content")

        logger.error("---------------------------------------------------------------------------")
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
