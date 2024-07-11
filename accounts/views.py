from django.shortcuts import render, get_object_or_404
from rest_framework import views, generics, status,  viewsets
from rest_framework.response import Response
from .models import Follow, Profile as UserProfile, User
from .serializers import ProfileSerializer, UserSerializer, RegisterSerializer, ChangePasswordSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse

class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save(is_active=False)
        self.send_verification_email(user)

    def send_verification_email(self, user):
        mail_subject = 'Activate your account'
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = f"http://127.0.0.1:8000{reverse('activate', kwargs={'uidb64': uid, 'token': token})}"
        message = f"Hi {user.username},\n\n" \
                  f"Thanks for signing up! Please click the link below to verify your email address and activate your account:\n\n" \
                  f"{activation_link}\n\n" \
                  f"Best regards,\nYour Team"
        send_mail(mail_subject, message, 'noreply@dreamboard.onrender.com', [user.email])

        
        
class ActivateAPIView(views.APIView):

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'message': 'Account activated successfully!'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Activation link is invalid!'}, status=status.HTTP_400_BAD_REQUEST)
        
class LoginAPIView(views.APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
class LogoutAPIView(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = get_user_model()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, queryset=None):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            
            # Change the password
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()

            # Optionally, return a new JWT token
            refresh = RefreshToken.for_user(self.object)
            return Response({
                'message': 'Password changed successfully.',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetails(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def get_object(self):
        return self.request.user

class Profile(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer

class ProfileDetails(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer

class FollowersList(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        followers = Follow.objects.filter(followed_user=user)
        followers_users = [follow.follower for follow in followers]
        serializer = UserSerializer(followers_users, many=True)
        return Response(serializer.data)

class FollowingList(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        following = Follow.objects.filter(follower=user)
        following_users = [follow.followed_user for follow in following]
        serializer = UserSerializer(following_users, many=True)
        return Response(serializer.data)

class FollowUser(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, user_id):
        user_to_follow = get_object_or_404(User, pk=user_id)
        if Follow.objects.filter(follower=request.user, followed_user=user_to_follow).exists():
            return Response({'message': 'You are already following this user'}, status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.create(follower=request.user, followed_user=user_to_follow)
        return Response({'message': 'User followed successfully'}, status=status.HTTP_201_CREATED)

class UnfollowUser(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def delete(self, request, user_id):
        user_to_unfollow = get_object_or_404(User, pk=user_id)
        follow = get_object_or_404(Follow, follower=request.user, followed_user=user_to_unfollow)
        follow.delete()
        return Response({'message': 'User unfollowed successfully'}, status=status.HTTP_204_NO_CONTENT)

class FollowersCount(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        followers_count = user.followers.count()
        return Response({'followers_count': followers_count}, status=status.HTTP_200_OK)
    
class FollingCount(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        following_count = user.following.count()
        return Response({'following_count': following_count}, status=status.HTTP_200_OK)
    
