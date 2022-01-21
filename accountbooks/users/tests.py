import json

import bcrypt

from django.test import TestCase, Client

from .models import User


class UserTest(TestCase):
    """
    유저 앱 테스트 클래스.
    """

    def setUp(self):
        """Mock 데이터 세팅."""

        User.objects.create(email='test1@example.com',
                            password=bcrypt.hashpw('abc135!!'.encode('utf-8'), bcrypt.gensalt()).decode())

    def tearDown(self):
        """Mock 데이터 클린업."""

        User.objects.all().delete()

    def test_signup_success(self):
        """
        sign-up: success case.
        """

        client = Client()
        request_data = {
            'email'   : 'test2@example.com',
            'password': 'abc135!!'
        }
        response = client.post('/user/sign-up/', json.dumps(request_data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"message": "sign-up success."})

    def test_signup_duplicate_email(self):
        """
        sign-up: failure case 1.

        이메일 중복 오류.
        """

        client = Client()
        request_data = {
            'email'   : 'test1@example.com',
            'password': 'abc135!!'
        }
        response = client.post('/user/sign-up/', json.dumps(request_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "'test1@example.com' is already."})

    def test_signup_invalid_email_first(self):
        """
        sign-up: failure case 2.

        이메일 형식 오류.
        이메일에 `@`가 누락된 경우.
        """

        client = Client()
        request_data = {
            'email'   : 'test2email.com',
            'password': 'abc135!!'
        }
        response = client.post('/user/sign-up/', json.dumps(request_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "invalid email address."})

    def test_signup_invalid_email_second(self):
        """
        sign-up: failure case 3.

        이메일 형식 오류.
        이메일 도메인에 `.`이 누락된 경우.
        """

        client = Client()
        request_data = {
            'email'   : 'test2@emailcom',
            'password': 'abc135!!'
        }
        response = client.post('/user/sign-up/', json.dumps(request_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "invalid email address."})

    def test_signup_invalid_password_first(self):
        """
        sign-up: failure case 4.

        패스워드 형식 오류.
        패스워드가 8자 미만인 경우.
        """

        client = Client()
        request_data = {
            'email'   : 'test2@email.com',
            'password': 'abc135!'
        }
        response = client.post('/user/sign-up/', json.dumps(request_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "passwords must be at least 8 characters long and "
                                                    "contain alphanumeric characters and special characters."})

    def test_signup_invalid_password_second(self):
        """
        sign-up: failure case 5.

        패스워드 형식 오류.
        패스워드가 alphanumeric 으로만 구성된 경우.
        """

        client = Client()
        request_data = {
            'email'   : 'test2@email.com',
            'password': 'abc13579'
        }
        response = client.post('/user/sign-up/', json.dumps(request_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "passwords must be at least 8 characters long and "
                                                    "contain alphanumeric characters and special characters."})

    def test_signup_key_error_email(self):
        """
        sign-up: failure case 6.

        이메일 키 에러.
        """

        client = Client()
        request_data = {
            'mail'    : 'test1@example.com',
            'password': 'abc135!!'
        }
        response = client.post('/user/sign-up/', json.dumps(request_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "'email' is required."})

    def test_signup_key_error_password(self):
        """
        sign-up: failure case 7.

        패스워드 키 에러.
        """

        client = Client()
        request_data = {
            'email': 'test2@example.com',
            'pw'   : 'abc135!!'
        }
        response = client.post('/user/sign-up/', json.dumps(request_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "'password' is required."})

    def test_signup_type_error_email(self):
        """
        sign-up: failure case 8.

        이메일 타입 에러.
        """

        client = Client()
        request_data = {
            'email'   : 123,
            'password': 'abc135!!'
        }
        response = client.post('/user/sign-up/', json.dumps(request_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "email datatype must be <class 'str'>."})

    def test_signup_type_error_password(self):
        """
        sign-up: failure case 9.

        패스워드 타입 에러.
        """

        client = Client()
        request_data = {
            'email'   : 'test2@example.com',
            'password': True
        }
        response = client.post('/user/sign-up/', json.dumps(request_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "password datatype must be <class 'str'>."})

    def test_signup_data_too_long_email(self):
        """
        sign-up: failure case 10.

        이메일 허용 데이터 크기(60자) 초과.
        """

        client = Client()
        request_data = {
            'email'   : '01234567890123456789012345678901234567890123456789@example.com',
            'password': 'abc135!!'
        }
        response = client.post('/user/sign-up/', json.dumps(request_data), content_type='application/json')
        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.json(), {"error": "'email' too long. (max: 60)"})

    def test_signup_data_too_long_password(self):
        """
        sign-up: failure case 11.

        패스워드 허용 데이터 크기(24자) 초과.
        """

        client = Client()
        request_data = {
            'email'   : 'test2@example.com',
            'password': '0123456789abcdefghij!!!!!'
        }
        response = client.post('/user/sign-up/', json.dumps(request_data), content_type='application/json')
        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.json(), {"error": "'password' too long. (max: 24)"})

    def test_sign_in_success(self):
        """
        sign-in: success case.
        """

        client = Client()
        request_data = {
            'email'   : 'test1@example.com',
            'password': 'abc135!!'
        }
        response = client.post('/user/sign-in/', json.dumps(request_data), content_type='application/json')
        token = response.json()['Authorization']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "sign-in success.", "Authorization": "%s" % token})

    def test_sign_in_does_not_exist(self):
        """
        sign-in: failure case 1.

        없는 계정 오류.
        비밀번호 무작위 대입 및 rainbow 테이블 공격 방어를 위하여,
        패스워드 입력 오류와 동일한 메시지 적용.
        """

        client = Client()
        request_data = {
            'email'   : 'test2@example.com',
            'password': 'abc135!!'
        }
        response = client.post('/user/sign-in/', json.dumps(request_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "invalid 'email' or 'password'."})

    def test_sign_in_invalid_password(self):
        """
        sign-in: failure case 2.

        잘못된 비밀번호.
        """

        client = Client()
        request_data = {
            'email'   : 'test2@example.com',
            'password': 'abc135!!'
        }
        response = client.post('/user/sign-in/', json.dumps(request_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "invalid 'email' or 'password'."})
