import json

from json import JSONDecodeError

from django.views import View
from django.http import JsonResponse

from utils.validators import validate_email, validate_password, check_password
from utils.exceptions import InvalidValueException, DataTooLongException, DataTypeException, DuplicationException
from .models import User


class SignupView(View):
    """
    회원가입 뷰.

    비밀번호는 validators 모듈로 암호화(Hashing) 후 저장한다.
    """

    def post(self, request):
        """
        회원가입 뷰 함수.

        post method만 허용하며 다른 Method request 시 405 에러 반환한다.
        입력 값(이메일･비밀번호)에 대한 유효성 검사는 validators 모듈로 수행한다.

        Parameters
        ----------
        request: JSON
            email: str
            password: str

        Returns
        -------
        JsonResponse: JSON
            message: str
            status code:
                201: success
                400: failure
                405: not allowed method
                413: data too long
        """

        try:
            data = json.loads(request.body)
            if User.objects.filter(email=data['email']).exists():
                raise DuplicationException(message="'%s' is already." % data['email'])

            email = validate_email(data['email'])
            hashed_password = validate_password(data['password'])
            User.objects.create(email=email, password=hashed_password)
            return JsonResponse({"message": "sign-up success."}, status=201)

        except InvalidValueException as e:
            return JsonResponse({"error": "%s" % e.message}, status=e.status)
        except JSONDecodeError:
            return JsonResponse({"error": "invalid json."}, status=400)
        except DuplicationException as e:
            return JsonResponse({"error": e.message}, status=e.status)
        except DataTooLongException as e:
            return JsonResponse({"error": e.message}, status=e.status)
        except DataTypeException as e:
            return JsonResponse({"error": e.message}, status=e.status)
        except KeyError as e:
            return JsonResponse({"error": "%s is required." % e}, status=400)


class SigninView(View):
    """
    로그인 뷰.

    성공적으로 로그인하면 인가 헤더용 token을 반환한다.
    """

    def post(self, request):
        """
        로그인 뷰 함수.

        입력 값에 대한 유효성 검증 로직은 `validators` 모듈이 수행한다.
        결과 값으로 jwt token 문자열이 반환된다.

        Parameters
        ----------
        request: JSON
            email: str
            password: str

        Returns
        -------
        JsonResponse: JSON
            message: str
            status code:
                200: success
                400: failure
                405: not allowed method
                413: data too long
        """

        try:
            data  = json.loads(request.body)
            user  = User.objects.get(email=data['email'])
            token = check_password(data['password'], user.password, user.id)
            return JsonResponse({"message": "sign-in success.", "Authorization": "%s" % token}, status=200)

        except InvalidValueException as e:
            return JsonResponse({"error": e.message}, status=e.status)
        except User.DoesNotExist:
            return JsonResponse({"error": "invalid 'email' or 'password'."}, status=400)
        except JSONDecodeError:
            return JsonResponse({"error": "invalid json."}, status=400)
        except DataTooLongException as e:
            return JsonResponse({"error": e.message}, status=e.status)
        except AttributeError:
            return JsonResponse({"error": "invalid data type. (email: str, password: str)"}, status=400)
        except KeyError as e:
            return JsonResponse({"error": "%s is required." % e}, status=400)
