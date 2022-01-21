import datetime

from django.db import models

from users.models import User


class AbstractExpense(models.Model):
    """
    가계부 지출 객체를 정의하는 추상화 모델 클래스이다.
    각 모델 클래스는 본 추상화 클래스를 상속받는다.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    date = models.DateField(default=datetime.date.today())
    amount = models.PositiveIntegerField()
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_expense(self, request):
        """
        추상화 지출 모델 클래스의 상세내역 메서드이다.
        상세･삭제내용 조회 시 공통 사용되며 유사한 다른 용도로 사용할 수 있다.
        """

        return {
            'id'         : self.id,
            'owner_id'   : self.user_id,
            'date'       : self.date,
            'title'      : self.title,
            'amount'     : self.amount,
            'description': self.description,
            'created_at' : self.created_at,
            'updated_at' : self.updated_at
        }

    def edit_expense(self, request):
        """
        추상화 지출 모델 클래스의 Edit 메서드이다.
        생성･수정 시 공통적으로 사용되며 유사한 다른 용도로 사용할 수 있다.
        """

        self.date        = request['date'] if 'date' in request else self.date
        self.title       = request['title'] if 'title' in request else self.title
        self.amount      = request['amount'] if 'amount' in request else self.amount
        self.description = request['description'] if 'description' in request else self.description
        self.save()

    def __str__(self):
        return "%s %s" % (self.date, self.title)

    class Meta:
        abstract = True


class Expense(AbstractExpense):
    """
    활성화된 가계부 지출 객체를 정의하는 모델 클래스이다다.
    추상화 지출 모델 클래스를 상속받는다.
    """

    pass

    class Meta:
        db_table = 'expenses'


class DeletedExpense(AbstractExpense):
    """
    삭제된 가계부 지출 객체를 정의하는 모델 클래스이다.
    추상화 지출 모델 클래스를 상속받았지만 일부 `필드와 ``메서드를 Override 한다.
    ` created_at, updated_at, deleted_at
    `` get_expense
    """

    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(auto_now_add=True)

    def get_expense(self, request):
        return {
            'id'         : self.id,
            'owner_id'   : self.user_id,
            'date'       : self.date,
            'title'      : self.title,
            'amount'     : self.amount,
            'description': self.description,
            'created_at' : self.created_at,
            'updated_at' : self.updated_at,
            'deleted_at' : self.deleted_at
        }

    class Meta:
        db_table = 'deleted_expenses'
