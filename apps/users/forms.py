from django import forms
from django.contrib.auth.models import User
from .models import Profile

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'comic-input', 'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'comic-input', 'placeholder': 'Confirm Password'}))

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'comic-input', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'comic-input', 'placeholder': 'Email'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'website', 'account_type']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'comic-input', 'rows': 3, 'placeholder': 'Tell us about yourself...'}),
            'website': forms.URLInput(attrs={'class': 'comic-input', 'placeholder': 'https://...'}),
            'account_type': forms.Select(attrs={'class': 'comic-input'}),
            'avatar': forms.FileInput(attrs={'class': 'comic-input', 'accept': 'image/*'})
        }
