from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import PhoneSerializer, OTPVerifySerializer
from utils.utils import (
    generate_otp,
    set_otp_cache,
    get_otp_cache,
    delete_otp_cache,
    get_client_ip,
    is_blocked_by_ip,
    register_ip_failure,
    reset_ip_failure,
    is_blocked_by_phone_and_ip,
    register_phone_ip_failure,
    reset_phone_ip_failure,
)

User = get_user_model()


class SendOTPView(APIView):
    def post(self, request):
        serializer = PhoneSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data["phone_number"]
        ip = get_client_ip(request)

        if is_blocked_by_ip(ip, scope="sms"):
            return Response(
                {"detail": "Access temporarily blocked."},
                status=status.HTTP_403_FORBIDDEN,
            )

        code = generate_otp()
        set_otp_cache(phone, code)
        # sms_service(phone, code)   برای ارسال پیام
        print(f"OTP code for {phone}: {code}")

        return Response({"detail": "OTP sent successfully."}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data["phone_number"]
        code = serializer.validated_data["code"]
        ip = get_client_ip(request)

        if is_blocked_by_phone_and_ip(phone, ip, scope="otp"):
            return Response(
                {"detail": "Too many attempts. Try again later."},
                status=status.HTTP_403_FORBIDDEN,
            )

        real_code = get_otp_cache(phone)
        if real_code != code:
            register_phone_ip_failure(phone, ip, scope="otp")
            return Response(
                {"detail": "Invalid OTP code."}, status=status.HTTP_400_BAD_REQUEST
            )

        delete_otp_cache(phone)
        reset_phone_ip_failure(phone, ip, scope="otp")

        user, created = User.objects.get_or_create(phone_number=phone)

        return Response(
            {"detail": "OTP verified.", "new_user": created}, status=status.HTTP_200_OK
        )
