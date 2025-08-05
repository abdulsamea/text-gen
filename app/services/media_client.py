import boto3
from app.core.config import settings

session = boto3.session.Session()
s3 = session.client(
    's3',
    endpoint_url=settings.S3_ENDPOINT,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
)

def upload_file(file_path, bucket, key):
    s3.upload_file(file_path, bucket, key)
    return f"{settings.S3_ENDPOINT}/{bucket}/{key}"
