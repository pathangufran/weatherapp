import logging
from django.shortcuts import render
from rest_framework import status
from accounts.models import AuthUser
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import IntegrityError
from common.throttling import RegisterThrottle,LoginThrottle,RefreshThrottle

logger = logging.getLogger(__name__)

class Register(APIView):

    throttle_classes = [RegisterThrottle]

    def post(self,request):

        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        address = request.data.get('address')
        
        if not username or not email or not password:
            return Response(
                {'error':'the above field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = AuthUser.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                address=address,
                password=make_password(password)
            )
            logger.info(
                f"user registration successful : {user.username}"
            )
            return Response(
                {
                'message':'User registration successful','user':user.id    
                },
                status=status.HTTP_201_CREATED
            )
        except IntegrityError as e:
            logger.error(e)
            return Response(
                {'error':'Database error'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception(e)
            return Response(
                {"error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    
class LogIn(APIView):

    throttle_classes = [LoginThrottle]

    def post(self,request):

        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'message':'username or password is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username,password=password)
        if not user:
            logger.warning(f'Invalid login attempt : {username}')
            return Response(
                {'error':'Invalid Credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            refresh = RefreshToken.for_user(user)
            logger.info(f'Login successful : {user.username}')
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user':{
                    'id':user.id,
                    'username':user.username,
                    'email':user.email
                }
            })
        except Exception as e:
            logger.exception(e)
            return Response(
                {"error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
class RefreshTokenView(APIView):

    throttle_classes = [RefreshThrottle]

    def post(self,request):

        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            refresh = RefreshToken(refresh_token)
            return Response(
                {'access':str(refresh.access_token)},
                status=status.HTTP_200_OK
            )
        
        except Exception:
            logging.warning('Invalid refresh token')
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
class LogOut(APIView):

    def post(self,request):

        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info(f'Logout successful : {request.user.username}')
            return Response(
                {"message": "Logout successful"},
                status=status.HTTP_200_OK,
            )
        except Exception:
            logger.warning('Invalid logout token')
            return Response(
                {"error": "Invalid refresh token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        