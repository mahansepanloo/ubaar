from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .serializers import PhoneSerializer, OTPVerifySerializer, LoginSerializer, UserProfileSerializer
from utils.utils import generate_otp, set_otp_cache, get_otp_cache, delete_otp_cache, get_client_ip, send_sms
from .models import User, FailedLoginAttempt
import logging

logger = logging.getLogger(__name__)


class SendOTPView(APIView):
    def post(self, request):
        serializer = PhoneSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data["phone_number"]
        ip = get_client_ip(request)

        if FailedLoginAttempt.is_blocked_by_ip(ip, scope="otp"):
            logger.warning(f"Blocked OTP request from IP {ip}")
            return Response(
                {"detail": "Access temporarily blocked due to too many attempts."},
                status=status.HTTP_403_FORBIDDEN,
            )

        code = generate_otp()
        set_otp_cache(phone, code)
        if not send_sms(phone, code):
            return Response(
                {"detail": "Failed to send OTP. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({"detail": "OTP sent successfully."}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data["phone_number"]
        code = serializer.validated_data["code"]
        ip = get_client_ip(request)

        if FailedLoginAttempt.is_blocked_by_phone_and_ip(phone, ip, scope="otp"):
            logger.warning(f"Blocked OTP verification for {phone} from IP {ip}")
            return Response(
                {"detail": "Too many attempts. Try again later."},
                status=status.HTTP_403_FORBIDDEN,
            )

        real_code = get_otp_cache(phone)
        if not real_code or real_code != code:
            FailedLoginAttempt.register_failure(ip, phone, scope="otp")
            logger.warning(f"Invalid OTP for {phone} from IP {ip}")
            return Response(
                {"detail": "Invalid OTP code."}, status=status.HTTP_400_BAD_REQUEST
            )

        delete_otp_cache(phone)
        FailedLoginAttempt.reset_failure(ip, phone, scope="otp")

        user, created = User.objects.get_or_create(phone_number=phone)
        logger.info(f"User {phone} {'created' if created else 'logged in'} via OTP")

        return Response(
            {"detail": "OTP verified.", "new_user": created}, status=status.HTTP_200_OK
        )


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data["phone_number"]
        password = serializer.validated_data["password"]
        ip = get_client_ip(request)

        if FailedLoginAttempt.is_blocked_by_ip(ip, scope="login"):
            logger.warning(f"Blocked login attempt from IP {ip}")
            return Response(
                {"detail": "Access temporarily blocked due to too many attempts."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = authenticate(phone_number=phone, password=password)
        if user:
            FailedLoginAttempt.reset_failure(ip, scope="login")
            logger.info(f"User {phone} logged in successfully")
            return Response({"detail": "Login successful."}, status=status.HTTP_200_OK)
        else:
            FailedLoginAttempt.register_failure(ip, scope="login")
            logger.warning(f"Failed login attempt for {phone} from IP {ip}")
            return Response(
                {"detail": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST
            )


class CompleteProfileView(APIView):
    def post(self, request):
        serializer = UserProfileSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(phone_number=request.data.get("phone_number"))
        user.first_name = serializer.validated_data["first_name"]
        user.last_name = serializer.validated_data["last_name"]
        user.email = serializer.validated_data["email"]
        user.save()

        logger.info(f"Profile updated for {user.phone_number}")
        return Response({"detail": "Profile updated successfully."}, status=status.HTTP_200_OK)