from app.core.config import settings


class OSSConfigError(RuntimeError):
    pass


def validate_oss_config() -> None:
    if not settings.oss_endpoint or not settings.oss_bucket:
        raise OSSConfigError("OSS not configured. Set OSS_ENDPOINT and OSS_BUCKET in environment.")


# Placeholder for future signed upload URL implementation.
def build_public_url(object_key: str) -> str:
    validate_oss_config()
    return f"https://{settings.oss_bucket}.{settings.oss_endpoint}/{object_key}"
