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
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
