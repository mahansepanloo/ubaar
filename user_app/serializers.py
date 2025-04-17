from rest_framework import serializers


def validate_phone_number(value):
    if value.startswith("09") and len(value) == 11 and value.isdigit():
        return value
    if value.startswith("+98") and len(value) == 13 and value[1:].isdigit():
        return value
    raise serializers.ValidationError("Invalid phone number format.")


class PhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField(validators=[validate_phone_number])


class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField(validators=[validate_phone_number])
    code = serializers.CharField(min_length=6, max_length=6)
