from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class MovieRatingForm(forms.Form):
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Rating (1-5)'})
    )
    review = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your review...', 'rows': 4}),
        required=False
    )


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add form-control class to all fields
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        
        # Override help text to ensure English
        self.fields['username'].help_text = 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        self.fields['password1'].help_text = (
            'Your password must contain at least 8 characters, '
            'cannot be too similar to your other personal information, '
            'cannot be a commonly used password, and cannot be entirely numeric.'
        )
        self.fields['password2'].help_text = 'Enter the same password as before, for verification.'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
