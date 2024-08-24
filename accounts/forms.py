from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms

User = get_user_model()


class SignupForm(UserCreationForm):
    face_image = forms.ImageField(required=False, help_text='顔写真をアップロードしてください。')

    class Meta:
        model = User
        fields = ('username', 'face_image', )
