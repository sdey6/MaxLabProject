from pathlib import Path

from moviepy.audio.io.AudioFileClip import AudioFileClip
import speech_recognition as sr
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

class TranscribeUtility:
    r = sr.Recognizer()

    def __init__(self, room_id, user_id):
        self._room_id = room_id
        self._user_id = user_id
        self._base_dir = "D:/maxlab_project/meeting_recordings/"

    def create_room_folder(self):
        Path(self._base_dir + self._room_id).mkdir(parents=True, exist_ok=True)

    def save_file(self, video_file):
        default_storage.save(f"{self._base_dir}/{self._room_id}/recording_{self._user_id}.webm", ContentFile(video_file.read()))
        # video_file.save(f"{self._base_dir}/{self._room_id}/recording_{self._user_id}.webm")

    def extract_audio(self):
        audioclip = AudioFileClip(f"{self._base_dir}/{self._room_id}/recording_{self._user_id}.webm")
        audioclip.write_audiofile(f"{self._base_dir}/{self._room_id}/extracted_{self._user_id}.wav")
        return f"{self._base_dir}/{self._room_id}/extracted_{self._user_id}.wav"

    def transcribe_file(self, path):
        try:
            with sr.AudioFile(path) as source:
                audio = self.r.record(source)
            a = self.r.recognize_google(audio)
            with open(f"{self._base_dir}/{self._room_id}/transcription_{self._user_id}.txt", "w") as f:
                f.write(str(a))
        except sr.UnknownValueError as e:
            print("unable to recognize")

