from rest_framework.views import exception_handler
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if hasattr(exc, 'default_code'):
            response.data = {
                'error': response.data.get('detail', str(exc)),
                'code': exc.default_code,
                'status': response.status_code
            }
        logger.warning(f'{context["request"].method} {context["request"].path} - {response.status_code}')

    return response
