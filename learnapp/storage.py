import pyrebase
from decouple import config
import os
import re
from django.conf import settings
from .models import FileRef
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework import permissions, status
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.exceptions import PermissionDenied, ValidationError


# STORAGE
class FileStorageView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    # Configuration
    config = {
        "apiKey": config('fire_apiKey'),
        "authDomain": config('fire_authDomain'),
        "projectId": config('fire_projectId'),
        "storageBucket": config('fire_storageBucket'),
        "messagingSenderId": config('fire_messagingSenderId'),
        "appId": config('fire_appId'),
        "databaseURL": config('fire_databaseURL'),
    }
    firebase = pyrebase.initialize_app(config)
    storage = firebase.storage()
    db = firebase.database()

    # For Service Account (pyrebase bug)
    config['serviceAccount'] = os.path.join(settings.BASE_DIR, 'google-credentials.json')
    firebase_super = pyrebase.initialize_app(config)
    storage_super = firebase_super.storage()

    def get(self, request):
        try:
            files_type = request.query_params.get('type')
            print(files_type)
            if files_type == 'backgrounds':
                print('Yes BG')
                url_arr = self.static_files_getter()
                return Response({
                    "file": url_arr
                }, status=status.HTTP_200_OK)
            print('after OwO')
        except ValueError as e:
            print('First Exception')
            raise ValidationError(detail=e)
        except Exception:
            print('Second Exception')
            raise ValidationError(detail='Something went wrong.')

    def post(self, request):
        try:
            # Getting file
            file = request.FILES.get('file')

            # For images
            if bool(re.match('image/', file.content_type)) and file.size < 3000000:
                # # Using temp file path instead
                # file_key = self.db.generate_key()
                # default_storage.save(file_key, file)  # Temporarily storing it in default storage
                # # Saving to firebase storage
                # uploadedImage = self.storage.child(f"images/{file_key}").put(f"media/{file_key}")
                # uploadedImageURL = self.storage.child(f"images/{file_key}").get_url(uploadedImage['downloadTokens'])
                # default_storage.delete(file_key)  # deleting from temporary storage

                (file_name, file_url) = self.file_create_helper(file)
                # Create a entry in FileRef for later reference
                FileRef.objects.create(author=request.user, name=file_name, url=file_url)

                return Response({
                    "status": True,
                    "url": file_url
                }, status=status.HTTP_201_CREATED)
            else:
                raise ValueError('File should be image and less than 3MB.')
        except ValueError as e:
            raise ValidationError(detail=e)
        except Exception:
            raise ValidationError(detail='Something went wrong.')

    def delete(self, request):
        try:
            file_url = request.data['url']
            self.file_delete_helper(file_url)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except PermissionError as e:
            raise ValidationError(detail=e)
        except Exception as e:
            print(e)
            raise ValidationError(detail="Something went wrong.")

    def file_create_helper(self, file):
        if bool(re.match('image/', file.content_type)) and file.size < 3000000:
            file_key = self.db.generate_key()
            file_path = file.temporary_file_path()
            # Saving to firebase storage
            uploadedImage = self.storage.child(f"images/{file_key}").put(file_path)
            print(uploadedImage)
            uploadedImageURL = self.storage.child(f"images/{file_key}").get_url()
            return uploadedImage['name'], uploadedImageURL

    def file_delete_helper(self, url):
        bucket = self.storage_super.bucket
        file_ref = FileRef.objects.get(url=url)
        if file_ref.author == self.request.user:
            blob = bucket.blob(file_ref.name)
            blob.delete()
            file_ref.delete()
        else:
            raise PermissionError

    def static_files_getter(self):
        all_files = self.storage_super.child().list_files()
        url_arr = []
        for file in all_files:
            try:
                if bool(re.match('static/[\d]{1}', file.name)):
                    url_arr.append(self.storage_super.child(file.name).get_url())
            except Exception as e:
                print(url_arr, e)
                print('Static failed')
                raise ValueError("Couldn't fetch files.")
        print('Static run sucss')
        return url_arr
