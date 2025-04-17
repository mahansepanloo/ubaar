from rest_framework import serializers
import phonenumbers


def validate_phone_number(value):
    try:
        parsed = phonenumbers.parse(value, None)
        if phonenumbers.is_valid_number(parsed):
            return value
        raise serializers.ValidationError("Invalid phone number.")
    except phonenumbers.NumberParseException:
        raise serializers.ValidationError("Invalid phone number format.")


class PhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField(validators=[validate_phone_number])


class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField(validators=[validate_phone_number])
    code = serializers.CharField(min_length=6, max_length=6)


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(validators=[validate_phone_number])
    password = serializers.CharField()


class UserProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    email = serializers.EmailField(allow_blank=True)