from django.db import models


class User(models.Model):
    """
    유저 모델을 정의하는 모델 클래스이다.
    이메일과 해싱된 비밀번호로 이루어진다.
    이메일은 고유(unique)하며 중복되지 않는다.
    """

    email = models.EmailField(max_length=60, unique=True)
    password = models.CharField(max_length=60)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'users'
