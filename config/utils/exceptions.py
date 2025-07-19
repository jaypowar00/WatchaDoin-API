from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    # Call REST framework's default handler first
    response = exception_handler(exc, context)
    if response is not None:
        return Response({
            'status': False,
            'message': str(exc.detail) if hasattr(exc, 'detail') else str(exc),
        })
    # If exception wasn't handled by DRF
    return Response({
        'status': False,
        'message': 'Unexpected error occurred',
    })
