from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, logout, update_session_auth_hash, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import random

from .serializers import *

User = get_user_model()

# ------------------------
# SIGNUP
# ------------------------
class SignupView(APIView):
    @swagger_auto_schema(
        operation_summary="Ro‘yxatdan o‘tish",
        request_body=RegisterSerializer,
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Ro‘yxatdan o‘tish muvaffaqiyatli!",
                "user": RegisterSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ------------------------
# LOGIN
# ------------------------
class LoginView(APIView):
    @swagger_auto_schema(
        operation_summary="Tizimga kirish (login)",
        request_body=LoginSerializer,
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            role = serializer.validated_data['role']
            user = authenticate(username=username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "Tizimga muvaffaqiyatli kirdingiz!",
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                        "role": role
                    }
                })
            return Response({"error": "Login yoki parol noto‘g‘ri"}, status=400)
        return Response(serializer.errors, status=400)


# ------------------------
# LOGOUT
# ------------------------
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Tizimdan chiqish",
    )
    def post(self, request):
        logout(request)
        return Response({"message": "Tizimdan chiqdingiz"}, status=200)


# ------------------------
# PROFILE VIEW
# ------------------------
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Profilni ko‘rish",
    )
    def get(self, request):
        serializer = RegisterSerializer(request.user)
        return Response(serializer.data)


# ------------------------
# PROFILE UPDATE
# ------------------------
class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Profilni to‘liq yangilash (PUT)",
        request_body=ProfileUpdateSerializer,
    )
    def put(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profil yangilandi!", "user": serializer.data})
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(
        operation_summary="Profilni qisman yangilash (PATCH)",
        request_body=ProfileUpdateSerializer,
    )
    def patch(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profil yangilandi!", "user": serializer.data})
        return Response(serializer.errors, status=400)


# ------------------------
# PASSWORD CHANGE
# ------------------------
class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Parolni o‘zgartirish",
        request_body=PasswordChangeSerializer,
    )
    def put(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            update_session_auth_hash(request, user)
            return Response({"message": "Parol muvaffaqiyatli o‘zgartirildi!"})
        return Response(serializer.errors, status=400)


# ------------------------
# FORGOT PASSWORD
# ------------------------
class ForgotPasswordView(APIView):
    @swagger_auto_schema(
        operation_summary="Parolni tiklash uchun kod yuborish",
        request_body=ForgotPasswordSerializer,
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                code = str(random.randint(1000, 9999))
                request.session['reset_user_id'] = user.id
                request.session['reset_code'] = code
                print(f"Parolni tiklash kodi: {code}")
                return Response({"message": "Kod yuborildi (terminalda ko‘ring)."})
            return Response({"error": "Email topilmadi"}, status=404)
        return Response(serializer.errors, status=400)


# ------------------------
# VERIFY RESET CODE
# ------------------------
class VerifyResetCodeView(APIView):
    @swagger_auto_schema(
        operation_summary="Kod to‘g‘riligini tekshirish",
        request_body=VerifyResetCodeSerializer,
    )
    def post(self, request):
        serializer = VerifyResetCodeSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            saved_code = request.session.get('reset_code')
            if code == saved_code:
                return Response({"message": "Kod to‘g‘ri! Endi yangi parol kiriting."})
            return Response({"error": "Kod noto‘g‘ri"}, status=400)
        return Response(serializer.errors, status=400)


# ------------------------
# RESET PASSWORD
# ------------------------
class ResetPasswordView(APIView):
    @swagger_auto_schema(
        operation_summary="Yangi parolni o‘rnatish",
        request_body=ResetPasswordSerializer,
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            password = serializer.validated_data['password']
            user_id = request.session.get('reset_user_id')
            if not user_id:
                return Response({"error": "Sessiya muddati tugagan"}, status=400)
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({"error": "Foydalanuvchi topilmadi"}, status=404)

            user.set_password(password)
            user.save()

            request.session.pop('reset_user_id', None)
            request.session.pop('reset_code', None)

            return Response({"message": "Parol muvaffaqiyatli yangilandi! Endi login qiling."})
        return Response(serializer.errors, status=400)
