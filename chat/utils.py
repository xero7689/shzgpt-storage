from rest_framework.serializers import ReturnDict


def build_response_content(data: ReturnDict, status: str, detail: str):
    return {
        'status': status,
        'detail': detail,
        'data': data
    }
