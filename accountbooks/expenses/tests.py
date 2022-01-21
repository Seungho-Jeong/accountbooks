import json

import bcrypt
import jwt

from django.test import TestCase, Client

import my_settings
from users.models import User
from .models import Expense, DeletedExpense


class ExpenseTest(TestCase):
    """
    가계부 지출내역 테스트 클래스.
    """

    def setUp(self):
        """Mock 데이터 세팅."""

        User.objects.create(id=1, email='test1@example.com',
                            password=bcrypt.hashpw('abc135!!'.encode('utf-8'), bcrypt.gensalt()).decode())

        Expense.objects.bulk_create(
            Expense(title='아파트관리비', date='2022-01-01', user_id=1, id=i,
                    amount=i * 1000000, description='활성화 테이블') for i in range(1, 3))

        self.client = Client()
        self.login_information = {
            'email'   : 'test1@example.com',
            'password': 'abc135!!'
        }
        self.login_response = self.client.post('/user/sign-in/', json.dumps(self.login_information),
                                               content_type='application/json')
        self.token = self.login_response.json()['Authorization']

    def tearDown(self):
        """Mock 데이터 클린업."""

        User.objects.all().delete()
        Expense.objects.all().delete()
        DeletedExpense.objects.all().delete()

    def test_get_expenses_success(self):
        """
        get_expense_list: success case.
        """

        header = {"HTTP_Authorization": self.token}
        response = self.client.get('/expenses/', **header)
        expenses = {
            "expenses": [
                {
                    "id": 1,
                    "date": "2022-01-01",
                    "title": "아파트관리비",
                    "amount": 1000000
                },
                {
                    "id": 2,
                    "date": "2022-01-01",
                    "title": "아파트관리비",
                    "amount": 2000000
                }
            ]
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expenses)

    def test_get_expenses_unauthorized(self):
        """
        get_expense_list: failure case 1.

        로그인 없이 접근.
        """

        header = {"HTTP_Authorization": ""}
        response = self.client.get('/expenses/', **header)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"error": "login required."})

    def test_create_expense_success(self):
        """
        create_expense: success case.
        """

        header = {"HTTP_Authorization": self.token, "content_type": "application/json"}
        data = {
            'title': 'test',
            'date': '2022-01-01',
            'amount': 10000000,
            'description': 'test message'
        }
        response = self.client.post('/expenses/new/', data, **header)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"message": "new expense created successfully."})

    def test_create_expense_unauthorized(self):
        """
        create_expense: failure case 1.

        Unauthorized.
        """

        header = {"HTTP_Authorization": "", "content_type": "application/json"}
        data = {
            'title': 'test',
            'date': '2022-01-01',
            'amount': 10000000,
            'description': 'test message'
        }
        response = self.client.post('/expenses/new/', data, **header)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"error": "login required."})

    def test_create_expense_type_error(self):
        """
        create_expense: failure case 2.

        데이터 타입 에러.
        """

        header = {"HTTP_Authorization": self.token, "content_type": "application/json"}
        data = {
            'title': 12345,
            'date': '2022-01-01',
            'amount': 10000000,
            'description': 'test message'
        }
        response = self.client.post('/expenses/new/', data, **header)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "title datatype must be <class 'str'>."})

    def test_create_expense_data_too_long(self):
        """
        create_expense: failure case 3.

        데이터 허용 크기 초과 에러.
        """

        header = {"HTTP_Authorization": self.token, "content_type": "application/json"}
        data = {
            'title': '012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789'
                     '012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789'
                     '012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789',
            'date': '2022-01-01',
            'amount': 10000000,
            'description': 'test message'
        }
        response = self.client.post('/expenses/new/', data, **header)
        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.json(), {"error": "'title' too long. (max: 255)"})

    def test_create_expense_key_error(self):
        """
        create_expense: failure case 4.

        키 에러.
        """

        header = {"HTTP_Authorization": self.token, "content_type": "application/json"}
        data = {
            'title': 'test',
            'date': '2022-01-01',
            'description': 'test message'
        }
        response = self.client.post('/expenses/new/', data, **header)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "'amount' is required."})

    def test_get_expense_success(self):
        """
        get_expense: success case.
        """

        expense = {
            "expense": {
                "id": 1,
                "owner_id": 1,
                "date": "2022-01-01",
                "title": "아파트관리비",
                "amount": 1000000,
                "description": "활성화 테이블",
                "created_at": "2022-01-18T07:51:14.414Z",
                "updated_at": "2022-01-18T09:36:54.147Z"
            }
        }

        header = {"HTTP_Authorization": self.token, "content_type": "application/json"}
        response = self.client.get('/expenses/1/', **header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expense)
