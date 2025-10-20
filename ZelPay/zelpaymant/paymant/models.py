from django.db import models
from django.conf import settings
from zelpaymant.common.models import BaseModel

class ReTransmactions(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    Transmaction_data = models.JSONField()
    token_url = models.CharField(max_length=144)
    request_pyload= models.JSONField()
    is_verifyed  = models.BooleanField(default=False)
    authority = models.CharField(max_length=144)
    