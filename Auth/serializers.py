from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError


class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)


    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'password1', 'password2', 'role', 'address', 'age', 'phone']
        read_only_fields = ("id",)

    def validate(self, attrs):
        password1 = attrs.get('password1')
        password2 = attrs.get('password2')
        email = attrs.get('email')

        if password1 != password2:
            raise serializers.ValidationError('Parollar mos emas')
        if password1 is None and password2 is None:
            raise serializers.ValidationError('Parollar toliq kiritilmagan')
        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Bu email allaqachon ro‘yxatdan o‘tgan."})

        try:
            validate_password(password1)
        except DjangoValidationError as e:
            raise serializers.ValidationError({'error': list(e.messages)})

        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password1')
        validated_data.pop('password2', None)
        user = CustomUser.objects.create_user(password=password, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError('Iltimos, username va password kiriting')

        user = authenticate(username=username, password=password)

        # Birinchi user mavjudligini tekshirish kerak
        if not user:
            raise serializers.ValidationError("Ushbu foydalanuvchi ro'yxatdan o'tmagan yoki login/parol noto'g'ri")

        if not user.is_active:
            raise serializers.ValidationError('Foydalanuvchi faol emas')

        # Faqat user mavjud bo'lsa role tekshiramiz
        user_role = user.role
        if not user_role:
            raise serializers.ValidationError("Admin sizga hali role bermagan")

        attrs['user'] = user
        attrs['role'] = user_role
        return attrs


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'address', 'age', 'phone']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            instance.save()
        return instance


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context.get('request').user
        if not user.check_password(value):
            raise serializers.ValidationError("Eski parol noto'g'ri")
        return value

    def validate_new_password(self, value):
        user = self.context.get('request').user
        try:
            validate_password(value, user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def save(self, **kwargs):
        user = self.context.get('request').user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyResetCodeSerializer(serializers.Serializer):
    code = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        p = attrs.get('password')
        cp = attrs.get('confirm_password')

        if p != cp:
            raise serializers.ValidationError("Parollar mos emas")
        try:
            validate_password(p)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password":list(e.messages)})
        return attrs

