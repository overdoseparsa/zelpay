from .models import Profile, BaseUser
from django.http import  QueryDict , HttpResponseBadRequest
from django.contrib.auth import authenticate

def get_profile(user:BaseUser) -> Profile:
    return Profile.objects.get(user=user)

def loggin_user(pyload:QueryDict)-> BaseUser | None:
    """
    This is for loggin User with Email and password 
    pyload is {
        'email' ,
        'password'
    }
    """
    print('username loggin')
    user = authenticate(email=pyload.get('email') , password = pyload.get('password'))
    return user 