from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ("email", "password1", "password2", "role")

    def clean_email(self):
        """Validate that the email is unique"""
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class RequestOTPForm(forms.Form):
    email = forms.EmailField()

class VerifyOTPForm(forms.Form):
    email = forms.EmailField(widget=forms.HiddenInput())
    otp_code = forms.CharField(max_length=6)

class ResendOTPForm(forms.Form):
    email = forms.EmailField(label="Email", required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email',
    }))

    def clean_email(self):
        email = self.cleaned_data.get("email")
        from .models import CustomUser  # Avoid circular imports
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("No user found with this email.")
        return email