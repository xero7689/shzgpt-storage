from rest_framework.serializers import ReturnDict


def build_response_content(data: ReturnDict, status: str, detail: str):
    return {"status": status, "detail": detail, "data": data}


def mask_api_key(api_key: str) -> str:
    return api_key[:7] + "*" * 24 + api_key[-4:]
