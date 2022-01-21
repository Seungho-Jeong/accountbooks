import re

import jwt
import bcrypt

import my_settings

from .exceptions import InvalidValueException, DataTooLongException, DataTypeException

# 이메일 정규식 검사 패턴
# alphanumeric@alphanumeric.alphanumeric
EMAIL_REGEX_PATTERN = "^[a-zA-Z0-9]([-_\.]?[a-zA-Z0-9])*@[a-zA-Z0-9]([-_\.]?[a-zA-Z0-9])*\.[a-zA-Z]{2,}$"

# 패스워드 정규식 검사 패턴
# 8자 이상, alphanumeric + 특수기호
PASSWORD_REGEX_PATTERN = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"


def validate_email(email):
    """
    이메일 유효성 검사 함수.

    자료형(type)･길이(length)･형식(format)을 검사한다.

    parameters
    ----------
    email: str

    returns
    -------
    email: str
    """

    if validate_datatype(data=email, field='email'):
        if validate_length(data=email, field='email'):
            if re.match(EMAIL_REGEX_PATTERN, email):
                return email
            raise InvalidValueException(message="invalid email address.")


def validate_password(password):
    """
    패스워드 유효성 검사 함수.

    자료형(type)･크기(length)･형식(format)을 검사한다.

    parameters
    ----------
    password: str

    returns
    -------
    password: str
    """

    if validate_datatype(data=password, field='password'):
        if validate_length(data=password, field='password'):
            if re.match(PASSWORD_REGEX_PATTERN, password):
                return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            raise InvalidValueException(message="passwords must be at least 8 characters long and "
                                                "contain alphanumeric characters and special characters.")


def validate_expense(data):
    """
    지출내역 입력값 유효성 검사 함수.

    자료형(type)･크기(length)･형식(format)을 검사한다.

    parameters
    ----------
    data: dict (JSON)

    returns
    -------
    data: dict
    """

    for key, value in data.items():
        if validate_datatype(data=value, field=key):
            if validate_length(data=value, field=key):
                return data


def validate_datatype(data, field):
    """
    유효성 검사 하위 함수. (자료형 검사)

    parameters
    ----------
    data: dynamic (str OR int)
    field: str

    return
    ------
    True: bool
    """

    type_dict = {'email': str, 'password': str, 'title': str,
                 'date': str, 'amount': int, 'description': str}
    if type(data) != type_dict[field]:
        raise DataTypeException(message="%s datatype must be %s." % (field, type_dict[field]))
    return True


def validate_length(data, field):
    """
    유효성 검사 하위 함수. (데이터 크기 검사)

    Parameters
    ----------
    data: dynamic (str OR int)
    field: str

    Returns
    -------
    True: bool
    """

    length_dict = {'email': 60, 'password': 24, 'title': 255, 'description': 255}
    if field == 'amount' or field == 'date':
        return True
    if len(data) > length_dict[field]:
        raise DataTooLongException(message="'%s' too long. (max: %d)" % (field, length_dict[field]))
    return True


def check_password(password, saved_password, user_id):
    """
    패스워드 비교 함수.

    입력받은 로그인 패스워드와 저장된 패스워드를 비교한다.

    Parameters
    ----------
    password: str
    saved_password: str
    user_id: int

    Returns
    -------
    token: str (jwt token)
    """

    if bcrypt.checkpw(password.encode('utf-8'), saved_password.encode('utf-8')):
        token = jwt.encode(payload={'user_id': user_id}, key=my_settings.SECRET_KEY, algorithm=my_settings.ALGORITHM)
        return token
    raise InvalidValueException(message="invalid 'email' or 'password'.")
