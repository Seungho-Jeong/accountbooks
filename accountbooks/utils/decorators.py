import jwt
import my_settings

from django.http import JsonResponse
from users.models import User
from utils.exceptions import UnauthorizedException


def login_decorator(func):
    """
    인가(Authorization) 함수.

    Authorization 헤더 값(jwt token)의 유효성을 검증한다.
    """

    def wrapper(self, request, *args, **kwargs):
        try:
            if not request.headers.get('Authorization'):
                raise UnauthorizedException
            access_token = request.headers.get('Authorization')
            payload = jwt.decode(jwt=access_token, key=my_settings.SECRET_KEY, algorithms=my_settings.ALGORITHM)
            user = User.objects.get(id=payload['user_id'])
            request.user = user
        except UnauthorizedException as e:
            return JsonResponse({"error": e.message}, status=e.status)
        except jwt.exceptions.DecodeError:
            return JsonResponse({"error": "invalid token."}, status=400)
        return func(self, request, *args, **kwargs)
    return wrapper
