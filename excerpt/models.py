from django.db import models
from django.utils import timezone


class Excerpt(models.Model):

    class Meta:
        db_table = 'excerpt'

    client_id = models.IntegerField(primary_key=True, null=False)
    domain = models.CharField(max_length=100, null=True)
    auth = models.CharField(max_length=500, null=True)
    type = models.CharField(max_length=100, null=True)
    identity = models.IntegerField(null=False)
    file_name = models.CharField(max_length=100, null=False)
    media_file = models.CharField(max_length=150, null=False)
    text = models.CharField(max_length=5000, null=False)
    # summary = models.CharField(max_length=5000, null=False)
    created_at = models.DateTimeField(default=timezone.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
    updated_at = models.DateTimeField(default=timezone.now().strftime("%Y-%m-%d %H:%M:%S.%f"))

    def __str__(self):
        return f"{self.client_id} {self.file_name} {self.created_at}"