import random
from django.core.cache import cache


def generate_otp():
    return str(random.randint(100000, 999999))


def set_otp_cache(phone_number, code, ttl=120):
    cache.set(f"otp:{phone_number}", code, timeout=ttl)


def get_otp_cache(phone_number):
    return cache.get(f"otp:{phone_number}")


def delete_otp_cache(phone_number):
    cache.delete(f"otp:{phone_number}")


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    return (
        x_forwarded_for.split(",")[0]
        if x_forwarded_for
        else request.META.get("REMOTE_ADDR")
    )


def is_blocked_by_ip(ip, scope="sms", limit=3):
    key = f"{scope}-fail:{ip}"
    return cache.get(key, 0) >= limit


def register_ip_failure(ip, scope="sms", limit=3, block_duration=3600):
    key = f"{scope}-fail:{ip}"
    attempts = cache.get(key, 0) + 1
    cache.set(key, attempts, timeout=block_duration if attempts >= limit else 300)


def reset_ip_failure(ip, scope="sms"):
    cache.delete(f"{scope}-fail:{ip}")


def is_blocked_by_phone_and_ip(phone, ip, scope="otp", limit=3):
    key = f"{scope}-fail:{phone}:{ip}"
    return cache.get(key, 0) >= limit


def register_phone_ip_failure(phone, ip, scope="otp", limit=3, block_duration=3600):
    key = f"{scope}-fail:{phone}:{ip}"
    attempts = cache.get(key, 0) + 1
    cache.set(key, attempts, timeout=block_duration if attempts >= limit else 300)


def reset_phone_ip_failure(phone, ip, scope="otp"):
    cache.delete(f"{scope}-fail:{phone}:{ip}")
