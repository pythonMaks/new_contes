from django.db import models


class Post(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()
   

    def __str__(self):
        return f'{self.name}<br>{self.content}'