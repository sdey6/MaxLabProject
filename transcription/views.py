from django.http.response import HttpResponseNotFound
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework import serializers
from rest_framework.parsers import JSONParser
from .models import Article
from .serializers import ArticleSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .transcribe_utility import TranscribeUtility
from  django.core.files import File,uploadedfile
from django.core.files.uploadedfile import InMemoryUploadedFile


# Create your views here.
@api_view(['POST'])
@csrf_exempt
def article_list(request):
    print(request)
    if request.method == 'POST':
         video_file = request.FILES['blob']  
         roomId = request.data['roomId']
         userId = request.data['userId']
         transcribe = TranscribeUtility(room_id=roomId, user_id=userId)
         transcribe.create_room_folder()
         transcribe.save_file(video_file=video_file)
         extracted_path = transcribe.extract_audio()
         transcribe.transcribe_file(extracted_path)
    return Response(data="video file saved",status=status.HTTP_201_CREATED)

@api_view(['GET','PUT','DELETE'])
@csrf_exempt
def article_detail(request,type,roomid):
   print(type)
   print(roomid)
   zip_file = open("D:\\maxlab_project\MaxLabProject\\transcription_app\\transcribe_utility.zip", 'rb')
   response = HttpResponse(zip_file, content_type='application/zip')
   response['Content-Disposition'] = 'attachment; filename="%s"' % 'foo.zip'
   response= HttpResponseNotFound("asdasd")
   return response 