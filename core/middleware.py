import logging

from django.conf import settings
from django.core import exceptions as django_exceptions
from rest_framework import status, exceptions as drf_exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler as default_exception_handler

from core.errors import UnexpectedCaseError

logger = logging.getLogger(__name__)


def custom_exceptions_handler(exc, context):
    response = default_exception_handler(exc, context)

    # Если ответ не сформировался стандартным обработчиком, создаем его вручную
    if response is None:
        response = Response(
            data={
                'error': {
                    'code': 'UNHANDLED_ERROR',
                    'message': "Unhandled error",
                    'details': {"msg": str(exc)},
                },
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(exc, drf_exceptions.ValidationError):
        response.data = {
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid input data',
                'details': exc.detail
            }
        }

    elif isinstance(exc, django_exceptions.ValidationError):
        response.data = {
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid input data',
                'details': exc.error_dict
            }
        }

    elif isinstance(exc, UnexpectedCaseError):
        response.data = {
            'error': {
                'code': 'UNEXPECTED_CASE',
                'message': 'Unexpected case in business logic',
                'details': {"msg": f'Возникла непредвиденная ошибка.'},
            }
        }

    return response


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
