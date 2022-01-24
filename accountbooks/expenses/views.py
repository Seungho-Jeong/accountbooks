import json

from json import JSONDecodeError

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from .models import Expense, DeletedExpense

from utils.decorators import login_decorator
from utils.validators import validate_expense
from utils.exceptions import PermissionException, DataTypeException, DataTooLongException, InvalidValueException


class ExpenseListView(View):
    """
    가계부 지출내역 리스트 뷰.

    유효한 인가 token 보유자에 한하여 본인이 작성한 지출내역을 출력한다.
    키워드(keyword), 날짜(date), 기간조회(due)를 할 수 있다.
    """

    @login_decorator
    def get(self, request):
        """
        리스트 뷰 함수.

        token decoding 값에 포함된 `user_id`와 매칭되는 지출 내역을 반환한다.
        인가 확인 동작은 `login_decorator`가 수행한다.

        쿼리 파마리터를 조합하여 키워드(keyword), 날짜(date), 기간조회(due)를 수행할 수 있다.

        parameter
        ---------
        request: nothing.
        query parameters
            keyword: str
            date: str (yyyy-mm-dd)
            start-date: str (yyyy-mm-dd)
            end-date: str (yyyy-mm-dd)

        returns
        -------
        JsonResponse: list of JSON
            id: int
            date: str (yyyy-mm-dd)
            title: str
            amount: int
            status code:
                200: success
                400: failure
                401: authorization error
                405: not allowed method
        """

        try:
            query = Q()
            queryset = Expense.objects.filter(user_id=request.user.id)
            keyword = request.GET.get('keyword', None)
            date = request.GET.get('date', None)
            due_stt = request.GET.get('start-date', None)
            due_end = request.GET.get('end-date', None)

            if keyword:
                query = Q(title__contains=keyword)
            if date:
                query = Q(date=date)
            if due_stt and due_end:
                if due_stt < due_end:
                    raise InvalidValueException(message="'end-date' must greater than 'start-date'.")
                query = Q(date__gte=due_stt) & Q(date__lte=due_end)

            expenses = queryset.filter(query)
            expenses = [expense for expense in expenses.values('id', 'date', 'title', 'amount')]
            return JsonResponse({"expenses": expenses}, status=200)

        except InvalidValueException as e:
            return JsonResponse({"error": e.message}, status=e.status)
        except ValidationError as e:
            return JsonResponse({"error": "%s" % e}, status=400)


class ExpenseNewView(View):
    """
    가계부 지출내역 신규등록 뷰.

    유효한 인가 token 보유자에 한하여 새 지출내역을 등록할 수 있다.
    """

    @login_decorator
    def post(self, request):
        """
        신규등록 뷰 함수.

        json 입력을 받아 유효한 값인 경우 db에 저장한다.
        입력값 유효성 검사는 `validators` 모듈에서 수행한다.

        parameters
        ----------
        request: JSON
            date: str (yyyy-mm-dd)
            title: str
            amount: int (positive)
            description: str

        returns
        -------
        JsonResponse: JSON
            message: str
            status code:
                201: success
                400: failure
                401: authorization error
                405: not allowed method
                413: data too long
        """

        try:
            data = json.loads(request.body)
            data = validate_expense(data)
            Expense.objects.create(user_id=request.user.id, title=data['title'], date=data['date'],
                                   amount=data['amount'], description=data['description'])
            return JsonResponse({"message": "new expense created successfully."}, status=201)
        except JSONDecodeError:
            return JsonResponse({"error": "invalid json."}, status=400)
        except DataTypeException as e:
            return JsonResponse({"error": e.message}, status=e.status)
        except DataTooLongException as e:
            return JsonResponse({"error": e.message}, status=e.status)
        except TypeError:
            return JsonResponse({"error": "date format must be 'yyyy-mm-dd'."}, status=400)
        except KeyError as e:
            return JsonResponse({"error": "%s is required." % e}, status=400)


class ExpenseDetailView(View):
    """
    가계부 지출내역 상세 뷰.

    유효한 인가 token 보유자에 한하여 본인이 작성한 지출 상세내역을
    조회(get)･수정(put)･삭제(delete) 할 수 있다.
    """

    @login_decorator
    def get(self, request, expense_id):
        """
        상세조회 뷰 함수.

        지출내역 id(expense_id)를 path parameter로 한다.
        token decoding 값에 포함된 `user_id`와 매칭되는 경우에만 지출 내역을 반환한다.

        parameters
        ----------
        request: nothing.
        expense_id: int

        returns
        -------
        JsonResponse: JSON
            id: int
            owner_id: int
            date: str (yyyy-mm-dd)
            title: str
            amount: int (positive)
            description: str
            created_at: datetime
            updated_at: datetime
            status code:
                200: success
                400: failure
                401: authorization error
                403: permission error
                404: page not found
                405: not allowed method
        """

        try:
            expense = get_object_or_404(Expense, id=expense_id)
            if expense.user_id == request.user.id:
                expense = expense.get_expense(request)
                return JsonResponse({"expense": expense}, status=200)
            raise PermissionException
        except PermissionException as e:
            return JsonResponse({"error": e.message}, status=e.status)

    @login_decorator
    def put(self, request, expense_id):
        """
        수정 뷰 함수.

        지출내역 id(expense_id)를 path parameter로 한다.
        token decoding 값에 포함된 `user_id`와 매칭되는 경우에만 수정할 수 있다.

        parameters
        ----------
        request: JSON
            date: str (yyyy-mm-dd)
            title: str
            amount: int (positive)
            description: str
        expense_id: int

        returns
        -------
        JsonResponse: JSON
            message: str
            status code:
                200: success
                400: failure
                401: authorization error
                403: permission error
                404: page not found
                405: not allowed method
                413: data too long
            updated_at: datetime
        """

        try:
            expense = get_object_or_404(Expense, id=expense_id)
            if expense.user_id == request.user.id:
                data = json.loads(request.body)
                data = validate_expense(data)
                expense.edit_expense(data)
                return JsonResponse({"message": "'id: %d' modified successfully." % expense_id}, status=200)
            raise PermissionException
        except JSONDecodeError:
            return JsonResponse({"error": "invalid json."}, status=400)
        except PermissionException as e:
            return JsonResponse({"error": e.message}, status=e.status)
        except DataTypeException as e:
            return JsonResponse({"error": e.message}, status=e.status)
        except DataTooLongException as e:
            return JsonResponse({"error": e.message}, status=e.status)
        except TypeError:
            return JsonResponse({"error": "date format must be 'yyyy-mm-dd'."}, status=400)
        except KeyError as e:
            return JsonResponse({"error": "%s is required." % e}, status=400)

    @login_decorator
    def delete(self, request, expense_id):
        """
        삭제 뷰 함수.

        지출내역 id(expense_id)를 path parameter로 한다.
        token decoding 값에 포함된 `user_id`와 매칭되는 경우에만 삭제할 수 있다.
        삭제 시 백업 테이블(deleted_expenses)에 백업 후 삭제된다.

        parameters
        ----------
        request: nothing.
        expense_id: int

        returns
        -------
        message: str
        status_code:
            204: success (no content)
            401: authorization error
            403: permission error
            404: page not found
            405: not allowed method
        """

        try:
            expense = get_object_or_404(Expense, id=expense_id)
            if expense.user_id == request.user.id:
                with transaction.atomic():
                    d_expense = DeletedExpense(user_id=expense.user_id, title=expense.title,
                                               amount=expense.amount, description=expense.description,
                                               created_at=expense.created_at, updated_at=expense.updated_at)
                    d_expense.save()
                    expense.delete()
                    return JsonResponse({"message": "'id: %d' removed successfully." % expense_id}, status=204)
            raise PermissionException
        except PermissionException as e:
            return JsonResponse({"error": e.message}, status=e.status)


class DeletedExpenseListView(View):
    """
    삭제된 지출내역 리스트 뷰.

    유효한 인가 token 보유자에 한하여 본인이 삭제한 지출내역을 출력한다.
    """

    @login_decorator
    def get(self, request):
        """
        삭제 리스트 뷰 함수.

        token decoding 값에 포함된 `user_id`와 매칭되는 삭제된 지출 내역을 반환한다.
        인가 확인 동작은 `login_decorator`가 수행한다.

        parameters
        ----------
        request: nothing.

        returns
        -------
        JsonResponse: list of JSON
            id: int
            date: str(datetime)
            title: str
            amount: int
            status code:
                200: success
                400: failure
                401: authorization error
                405: not allowed method
        """

        d_expenses = DeletedExpense.objects.filter(user_id=request.user.id)
        d_expenses = [d_expense for d_expense in d_expenses.values('id', 'date', 'title', 'amount')]
        return JsonResponse({"deleted_expenses": d_expenses}, status=200)


class DeletedDetailView(View):
    """
    삭제된 지출내역 상세 뷰.

    유효한 인가 token 보유자에 한하여 본인이 삭제한 지출 상세내역을
    조회(get)･삭제(=복원, delete) 할 수 있다.
    """

    @login_decorator
    def get(self, request, d_expense_id):
        """
        삭제 상세조회 뷰 함수.

        지출내역 id(expense_id)를 path parameter로 한다.
        token decoding 값에 포함된 `user_id`와 매칭되는 경우에만 지출 내역을 반환한다.

        parameters
        ----------
        request: nothing.
        d_expense_id: int

        returns
        -------
        JsonResponse: JSON
            id: int
            owner_id: int
            date: str (yyyy-mm-dd)
            title: str
            amount: int (positive)
            description: str
            created_at: datetime
            updated_at: datetime
            deleted_at: datetime
            status code:
                200: success
                400: failure
                401: authorization error
                403: permission error
                404: page not found
                405: not allowed method
        """

        try:
            d_expense = get_object_or_404(DeletedExpense, id=d_expense_id)
            if d_expense.user_id == request.user.id:
                d_expense = d_expense.get_expense(request)
                return JsonResponse({"deleted_expense": d_expense}, status=200)
            raise PermissionException
        except PermissionException as e:
            return JsonResponse({"error": e.message}, status=e.status)

    @login_decorator
    def delete(self, request, d_expense_id):
        """
        삭제(=복원) 뷰 함수.

        지출내역 id(expense_id)를 path parameter로 한다.
        token decoding 값에 포함된 `user_id`와 매칭되는 경우에만 삭제할 수 있다.
        삭제 시 지출내역 테이블(expenses)에 복원 후 삭제된다.

        parameters
        ----------
        request: nothing.
        d_expense_id: int

        returns
        -------
        message: str
        status_code:
            204: success (no content)
            401: authorization error
            403: permission error
            404: page not found
            405: not allowed method
        """

        try:
            d_expense = get_object_or_404(DeletedExpense, id=d_expense_id)
            if d_expense.user_id == request.user.id:
                with transaction.atomic():
                    r_expense = Expense(user_id=d_expense.user_id, title=d_expense.title,
                                        amount=d_expense.amount, description=d_expense.description,
                                        created_at=d_expense.created_at, updated_at=d_expense.updated_at)
                    r_expense.save()
                    d_expense.delete()
                    return JsonResponse({"message": "'id: %d' recovered successfully." % d_expense_id}, status=204)
            raise PermissionException
        except PermissionException as e:
            return JsonResponse({"error": e.message}, status=e.status)
