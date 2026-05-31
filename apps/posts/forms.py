from django import forms
from .models import Post, Reel, Story

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['caption', 'media_file', 'visibility', 'location']
        widgets = {
            'caption': forms.Textarea(attrs={'class': 'comic-input', 'placeholder': 'What\'s making you go yentroww today? 😯', 'rows': 4}),
            'media_file': forms.FileInput(attrs={'class': 'comic-input', 'accept': 'image/*,video/mp4,video/quicktime'}),
            'visibility': forms.Select(attrs={'class': 'comic-input'}),
            'location': forms.TextInput(attrs={'class': 'comic-input', 'placeholder': 'Optional location'}),
        }

class ReelForm(forms.ModelForm):
    class Meta:
        model = Reel
        fields = ['caption', 'video_file', 'visibility']
        widgets = {
            'caption': forms.Textarea(attrs={'class': 'comic-input', 'placeholder': 'Reel caption...', 'rows': 3}),
            'video_file': forms.FileInput(attrs={'class': 'comic-input', 'accept': 'video/mp4,video/quicktime'}),
            'visibility': forms.Select(attrs={'class': 'comic-input'}),
        }

class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['media_file']
        widgets = {
            'media_file': forms.FileInput(attrs={'class': 'comic-input', 'accept': 'image/*,video/mp4,video/quicktime'}),
        }
