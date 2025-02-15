import random
from django.core.mail import send_mail
from .models import CustomUser, OTPCode
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_backends
from django.contrib import messages
from rest_framework.views import APIView
from .forms import RegisterForm, LoginForm, VerifyOTPForm
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from django.urls import reverse
User = get_user_model()
token_generator = PasswordResetTokenGenerator()

class RegisterView(APIView):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'authentication/register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password1')
            confirm_password = request.POST.get('password2')

            if password != confirm_password:
                messages.error(request, "Passwords do not match!")
                return render(request, 'authentication/register.html', {'form': form})

            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, "Email is already registered!")
                return render(request, 'authentication/register.html', {'form': form})
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                username=email.split('@')[0]
            )
            user.role = request.POST.get('role')
            user.save()
            if user:
                otp_instance, created = OTPCode.objects.get_or_create(user=user)
                otp_instance.code = f"{random.randint(100000, 999999)}"
                otp_instance.created_at = now()
                otp_instance.save()
                #print('it is otp_code=', otp_instance.code)
                send_mail(
                    "Ваш OTP-код",
                    f"Ваш код подтверждения: {otp_instance.code}",
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )

                request.session["email"] = email  # Store email in session

                messages.success(request, "OTP-код отправлен на вашу почту.")
                return redirect("otp_verification")

        return render(request, "authentication/otp_verification.html")


class verify_otp_view(APIView):
    """Отображает форму подтверждения OTP и выполняет аутентификацию."""

    def get(self, request):
        form = VerifyOTPForm(request.POST)
        return render(request, 'authentication/otp_verification.html', {'form': form})

    def post(self, request):
        form = VerifyOTPForm(request.POST)
        email = request.session.get("email")
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            messages.error(request, "Пользователь с таким email не найден.")
            return render(request, "authentication/otp_verification.html", {"form": form})

            # Assign the correct backend
        backend = get_backends()[0]  # Use the first configured backend
        user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
        otp = OTPCode.objects.filter(user=user).first()
        if request.method == "POST":
            code = request.POST.get("otp")
            if not otp or not otp.is_valid() or otp.code != code:
                messages.error(request, "Неверный или просроченный код.")
                return render(request, "authentication/otp_verification.html", {"form": form})

            user.is_verified = True
            user.save()
            login(request, user)  # Log in the user

            messages.success(request, "Вы успешно вошли!")
            return redirect("home")


class ResendOTPView(APIView):
    def post(self, request):
        # Extract the email from the session
        email = request.session.get("email")
        if not email:
            messages.error(request, "Email not found in session.")
            return redirect("otp_verification")

        # Check if the user exists
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            messages.error(request, "User not found.")
            return redirect("otp_verification")

        # Check if an OTP already exists
        otp_instance = OTPCode.objects.filter(user=user).first()

        # Optional: Cooldown logic to prevent spamming
        if otp_instance and (now() - otp_instance.created_at).total_seconds() < 60:
            messages.error(request, "Please wait before resending OTP.")
            return redirect("otp_verification")

        # Generate a new OTP
        new_otp = f"{random.randint(100000, 999999)}"

        # Update or create the OTP record
        if otp_instance:
            otp_instance.code = new_otp
            otp_instance.created_at = now()
            otp_instance.save()
        else:
            OTPCode.objects.create(user=user, code=new_otp)

        # Send the OTP via email
        send_mail(
            "Ваш новый OTP-код",
            f"Ваш код подтверждения: {new_otp}",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        messages.success(request, "A new OTP has been sent to your email.")
        return redirect("otp_verification")

class LoginView(APIView):
    def get(self, request):
        form = LoginForm()
        return render(request, 'authentication/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            if user is not None:
                if not user.is_verified:
                    messages.error(request, "Please verify your account before logging in.")
                    return redirect("otp_verification")
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('home')
            else:
                messages.error(request, "Invalid email or password. Please try again.")

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

        return render(request, 'authentication/login.html', {'form': form})


class PasswordResetView(APIView):
    def get(self, request):
        return render(request, 'authentication/password_reset.html')

    def post(self, request):
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()

        if user:
            # Generate token and encode user ID
            token = token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Create password reset URL
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )

            # Send email
            send_mail(
                "Password Reset Request",
                f"Click the link below to reset your password:\n{reset_url}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            messages.success(request, "A password reset link has been sent to your email.")
            return redirect('login')

        messages.error(request, "Email not found.")
        return render(request, 'authentication/password_reset.html')


class PasswordResetConfirmView(APIView):
    def get(self, request, uidb64, token):
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if token_generator.check_token(user, token):
                return render(request, 'authentication/password_reset_confirm.html',
                              {'valid_link': True, 'uidb64': uidb64, 'token': token})
            else:
                messages.error(request, "Invalid or expired password reset token.")
                return render(request, 'authentication/password_reset_confirm.html', {'valid_link': False})

        except Exception as e:
            messages.error(request, "Invalid link.")
            return render(request, 'authentication/password_reset_confirm.html', {'valid_link': False})

    def post(self, request, uidb64, token):
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if token_generator.check_token(user, token):
                new_password = request.POST.get('new_password')
                confirm_password = request.POST.get('confirm_password')

                if new_password != confirm_password:
                    messages.error(request, "Passwords do not match.")
                    return render(request, 'authentication/password_reset_confirm.html',
                                  {'valid_link': True, 'uidb64': uidb64, 'token': token})

                user.set_password(new_password)
                user.save()
                print('it is new_password =', new_password,'it is confirm_password =', confirm_password)
                messages.success(request, "Your password has been successfully reset!")
                return redirect('login')

        except Exception as e:
            messages.error(request, "Something went wrong.")
            return redirect('password_reset')

        return redirect('password_reset')
@login_required
def home_view(request):
    return render(request, 'authentication/home.html')


class LogoutView(APIView):
    def get(self, request):
        logout(request)
        return redirect('login')