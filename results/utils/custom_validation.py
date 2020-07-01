from rest_framework.exceptions import APIException
from rest_framework import status


class CustomValidation(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'

    def __init__(self, detail, field, status_code):
        if status_code is not None:
            self.status_code = status_code
        if field is not None:
            self.detail = {field: detail}
        else:
            self.detail = {'detail': self.default_detail}
