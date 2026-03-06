from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import threading

from .models import User, Address
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    ChangePasswordSerializer, ForgotPasswordSerializer,
    ResetPasswordSerializer, AddressSerializer
)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def _send_email_async(subject, message, from_email, recipient_list):
    """Send email in a background thread so it never blocks the HTTP response."""
    def _send():
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=True,
            )
        except Exception:
            pass

    thread = threading.Thread(target=_send, daemon=True)
    thread.start()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Send verification email in background — does NOT block response
        token = user.verification_token
        verify_url = f"{settings.FRONTEND_URL}/verify-email/{token}"
        _send_email_async(
            subject='Verify your TRIVÉ account',
            message=f'Hi {user.first_name},\n\nPlease verify your email: {verify_url}\n\nThis link expires in 24 hours.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        tokens = get_tokens_for_user(user)
        return Response({
            'success': True,
            'message': 'Registration successful. Please verify your email.',
            'user': UserSerializer(user, context={'request': request}).data,
            'tokens': tokens,
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        tokens = get_tokens_for_user(user)
        return Response({
            'success': True,
            'message': 'Login successful.',
            'user': UserSerializer(user, context={'request': request}).data,
            'tokens': tokens,
        })


class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass
        return Response({'success': True, 'message': 'Logged out successfully.'})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def verify_email(request, token):
    try:
        user = User.objects.get(verification_token=token)
    except User.DoesNotExist:
        return Response({'success': False, 'message': 'Invalid verification token.'}, status=400)

    if user.is_verified:
        return Response({'success': True, 'message': 'Email already verified.'})

    if user.verification_token_expires < timezone.now():
        return Response({'success': False, 'message': 'Verification token expired.'}, status=400)

    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires = None
    user.save(update_fields=['is_verified', 'verification_token', 'verification_token_expires'])

    return Response({'success': True, 'message': 'Email verified successfully.'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def resend_verification(request):
    user = request.user
    if user.is_verified:
        return Response({'success': False, 'message': 'Email already verified.'}, status=400)
    user.generate_verification_token()
    token = user.verification_token
    verify_url = f"{settings.FRONTEND_URL}/verify-email/{token}"
    _send_email_async(
        subject='Verify your TRIVÉ account',
        message=f'Hi {user.first_name},\n\nPlease verify your email: {verify_url}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
    return Response({'success': True, 'message': 'Verification email sent.'})


class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            user.generate_reset_token()
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{user.reset_token}"
            _send_email_async(
                subject='Reset your TRIVÉ password',
                message=f'Hi {user.first_name},\n\nReset your password: {reset_url}\n\nThis link expires in 1 hour.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
        except User.DoesNotExist:
            pass  # Don't reveal if email exists
        return Response({'success': True, 'message': 'If this email exists, a reset link has been sent.'})


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user.set_password(serializer.validated_data['new_password'])
        user.reset_token = None
        user.reset_token_expires = None
        user.save(update_fields=['password', 'reset_token', 'reset_token_expires'])
        return Response({'success': True, 'message': 'Password reset successfully.'})


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'success': False, 'message': 'Current password is incorrect.'}, status=400)
        user.set_password(serializer.validated_data['new_password'])
        user.save(update_fields=['password'])
        return Response({'success': True, 'message': 'Password changed successfully.'})


class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def set_default_address(request, pk):
    try:
        address = Address.objects.get(pk=pk, user=request.user)
        address.is_default = True
        address.save()
        return Response({'success': True, 'message': 'Default address updated.'})
    except Address.DoesNotExist:
        return Response({'success': False, 'message': 'Address not found.'}, status=404)