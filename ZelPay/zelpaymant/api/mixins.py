from typing import Sequence, Type, TYPE_CHECKING

from importlib import import_module

from django.conf import settings

from django.contrib import auth

from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.authentication import BaseAuthentication
from rest_framework.status import HTTP_400_BAD_REQUEST , HTTP_200_OK
from rest_framework_simplejwt.authentication import JWTAuthentication 
from rest_framework.response import Response

def get_auth_header(headers):
    value = headers.get('Authorization')

    if not value:
        return None

    auth_type, auth_value = value.split()[:2]

    return auth_type, auth_value


if TYPE_CHECKING:
    # This is going to be resolved in the stub library
    # https://github.com/typeddjango/djangorestframework-stubs/
    from rest_framework.permissions import _PermissionClass

    PermissionClassesType = Sequence[_PermissionClass]
else:
    PermissionClassesType = Sequence[Type[BasePermission]]


class ApiAuthMixin:
    authentication_classes: Sequence[Type[BaseAuthentication]] = [
            JWTAuthentication,
    ]
    permission_classes: PermissionClassesType = (IsAuthenticated, )


class ApiProcessMixin:
    
    def process_request(self,request,*args,**kwargs):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        try :  
            self.response = self.logic(data)
            print('the process_request Response' ,self.response)
        except Exception as ex:
            return Response(
                    f"Error {ex}",
                    status=HTTP_400_BAD_REQUEST
                    )
        return True
    
    def process_response(self):
        assert hasattr(self ,'response') , 'must implement Process Request'
        response = self.OutPutSerializer(self.response)
        return Response(
            response.data , 
            status=HTTP_200_OK
        )