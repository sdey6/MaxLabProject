from django.db import models

# Create your models here.

class Article(models.Model):
    room_id = models.CharField(max_length=100)
    experimenters_id= models.CharField(max_length=100)
    max_participants = models.IntegerField()
    folder_path = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"room_id : {self.room_id} exp_id: {self.experimenters_id}"