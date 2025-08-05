import os
import boto3

class MediaClient:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("S3_SECRET_KEY")
        )
        self.bucket = os.getenv("S3_BUCKET")
        self.prefix = os.getenv("S3_OUTPUT_PREFIX", "")

    def upload_image(self, filename, data):
        s3_key = f"{self.prefix}{filename}"
        self.s3.upload_fileobj(data, self.bucket, s3_key)
        return f"https://{self.bucket}.s3.amazonaws.com/{s3_key}"
