from tortoise.models import Model
from tortoise import fields
import uuid

class Job(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    prompt = fields.TextField()
    parameters = fields.JSONField()
    status = fields.CharField(max_length=50)
    media_url = fields.TextField(null=True)
    error = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
