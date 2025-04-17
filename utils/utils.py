import secrets
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


def generate_otp():
    return ''.join(secrets.choice('0123456789') for _ in range(6))


def set_otp_cache(phone_number, code, ttl=120):
    cache.set(f"otp:{phone_number}", code, timeout=ttl)
    logger.info(f"OTP set for {phone_number}")


def get_otp_cache(phone_number):
    return cache.get(f"otp:{phone_number}")


def delete_otp_cache(phone_number):
    cache.delete(f"otp:{phone_number}")
    logger.info(f"OTP cache cleared for {phone_number}")


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    ip = x_forwarded_for.split(",")[0] if x_forwarded_for else request.META.get("REMOTE_ADDR")
    logger.debug(f"Client IP: {ip}")
    return ip


def send_sms(phone, code):
    try:
        # sms_service(phone, code) 
        print(f"OTP code for {phone}: {code}")
        logger.info(f"SMS sent to {phone}: {code}")
        return True
    except Exception as e:
        logger.error(f"SMS sending failed for {phone}: {e}")
        return False