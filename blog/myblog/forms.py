from django import forms
from django.contrib.auth.models import User

from .models import Post, PostPoint


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                        'id': 'nameInput'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={"class": "form-control",
                                                           "id": "exampleInputEmail1",
                                                           "aria-describedby": "emailHelp"
                                                           }))
    to = forms.EmailField(widget=forms.TextInput(attrs={"class": "form-control",
                                                        "id": "emailTo"}))
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control",
                                                                           "id": "comments",
                                                                           "rows": "3"}))


class CommentForm(forms.Form):
    name = forms.CharField(max_length=25, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                        'id': 'nameInput'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={"class": "form-control",
                                                           "id": "exampleInputEmail1",
                                                           "aria-describedby": "emailHelp"
                                                           }))
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control",
                                                                           "id": "comments",
                                                                           "rows": "3"}))


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        "id": "inputLogin",
        " class": "form-control",
        " placeholder": "Логин",
    }))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            "type": "password",
            "id": "inputPassword",
            "class": "form-control",
            "placeholder": "Пароль"
        }))


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'short_description', 'image', 'tags')


class PostPointForm(forms.ModelForm):
    class Meta:
        model = PostPoint
        fields = ('post_header', 'post_point_text', 'post_images')


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(max_length=40, widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('first_name', 'last_name',
                  'username', 'email', 'password')


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name',
                  'username', 'email')
