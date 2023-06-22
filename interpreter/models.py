from django.db import models
from users.models import User

class UserCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=100)
    date_submitted = models.DateTimeField(auto_now_add=True)
