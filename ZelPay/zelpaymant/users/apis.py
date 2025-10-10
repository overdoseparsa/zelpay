from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework import serializers

from django.core.validators import MinLengthValidator
from django.contrib.auth import authenticate
from .validators import number_validator, special_char_validator, letter_validator
from zelpaymant.users.models import BaseUser , Profile
from zelpaymant.api.mixins import ApiAuthMixin , ApiProcessMixin
from zelpaymant.users.selectors import get_profile , loggin_user
from zelpaymant.users.services import register 
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from drf_spectacular.utils import extend_schema

from time import process_time

class ProfileApi(ApiAuthMixin, APIView):

    class OutPutSerializer(serializers.ModelSerializer):
        class Meta:
            model = Profile 
            fields = ("bio", "posts_count", "subscriber_count", "subscription_count")
    # get here 
    @extend_schema(responses=OutPutSerializer)
    def get(self, request):
        start = process_time()
        query = get_profile(user=request.user)
        end = process_time()
        print("Time for get api" , (end-start)*100) 
        return Response(self.OutPutSerializer(query, context={"request":request}).data)

class LogginProfileApi(ApiProcessMixin , APIView):
    class InputSerializer(serializers.Serializer):
        email = serializers.CharField()
        password = serializers.CharField()
    class OutPutSerializer(serializers.ModelSerializer):

        token = serializers.SerializerMethodField("get_token")

        class Meta:
            model = BaseUser 
            fields = ("email", "token", "created_at", "updated_at")

        def get_token(self, user):
            data = dict()
            token_class = RefreshToken

            refresh = token_class.for_user(user)

            data["refresh"] = str(refresh)
            data["access"] = str(refresh.access_token)

            return data
    @property
    def logic(self):
        return loggin_user
    @extend_schema(request=InputSerializer, responses=OutPutSerializer)
    def post(self, request:Request ,*args,**kwargs)-> Response:
        return self.process_request(request ,*args,**kwargs) and self.process_response()
        

class RegisterApi(APIView):

    class InputRegisterSerializer(serializers.Serializer):
        email = serializers.EmailField(max_length=255)
        bio = serializers.CharField(max_length=1000, required=False)
        password = serializers.CharField(
                validators=[
                        number_validator,
                        letter_validator,
                        special_char_validator,
                        MinLengthValidator(limit_value=10)
                    ]
                )
        confirm_password = serializers.CharField(max_length=255)
        
        def validate_email(self, email):
            if BaseUser.objects.filter(email=email).exists():
                raise serializers.ValidationError("email Already Taken")
            return email

        def validate(self, data):
            if not data.get("password") or not data.get("confirm_password"):
                raise serializers.ValidationError("Please fill password and confirm password")
            
            if data.get("password") != data.get("confirm_password"):
                raise serializers.ValidationError("confirm password is not equal to password")
            return data


    class OutPutRegisterSerializer(serializers.ModelSerializer):

        token = serializers.SerializerMethodField("get_token")

        class Meta:
            model = BaseUser 
            fields = ("email", "token", "created_at", "updated_at")

        def get_token(self, user):
            data = dict()
            token_class = RefreshToken

            refresh = token_class.for_user(user)

            data["refresh"] = str(refresh)
            data["access"] = str(refresh.access_token)

            return data


    @extend_schema(request=InputRegisterSerializer, responses=OutPutRegisterSerializer)
    def post(self, request):
        start = process_time()
        serializer = self.InputRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = register(
                    email=serializer.validated_data.get("email"),
                    password=serializer.validated_data.get("password"),
                    bio=serializer.validated_data.get("bio"),
                    )
        except Exception as ex:
            return Response(
                    f"Database Error {ex}",
                    status=status.HTTP_400_BAD_REQUEST
                    )
        end = process_time()
        print('post_api from sever ', (end-start)*100)
        return Response(self.OutPutRegisterSerializer(user, context={"request":request}).data)

