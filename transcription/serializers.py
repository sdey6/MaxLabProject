from django.db.models import fields
from rest_framework import serializers
from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["room_id","experimenters_id","max_participants","folder_path"]
