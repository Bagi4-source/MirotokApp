import uuid
from datetime import date

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField


class TimeMixin(models.Model):
    update_time = models.DateTimeField(auto_now=True, verbose_name='Update time')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='Creation time')

    class Meta:
        abstract = True


class Codes(TimeMixin):
    phone = PhoneNumberField(null=False, blank=False, unique=True)
    code = models.CharField(verbose_name='Code', max_length=8)

    class Meta:
        verbose_name = 'Code'
        verbose_name_plural = 'Codes'


class Users(TimeMixin):
    CHOICES = (
        (1, 'Admin'),
        (0, 'Client')
    )

    number = models.CharField(verbose_name='Phone', max_length=30, null=False, blank=False, unique=True)
    subscription_end = models.DateField(verbose_name='Дата окончания подписки', default=date.today)
    role = models.IntegerField(verbose_name='Role', choices=CHOICES, default=0)

    class Meta:
        verbose_name = 'Login'
        verbose_name_plural = 'Logins'

    def __str__(self):
        return str(self.number)


class UserInfo(TimeMixin):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, verbose_name='User')
    name = models.CharField(verbose_name='Name', max_length=100)
    surname = models.CharField(verbose_name='Surname', max_length=100)

    height = models.FloatField(verbose_name='Height', validators=[MinValueValidator(0)])
    weight = models.FloatField(verbose_name='Weight', validators=[MinValueValidator(0)])
    age = models.IntegerField(verbose_name='Age', validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = 'User Info'
        verbose_name_plural = 'User Info'


class Token(TimeMixin):
    token = models.CharField(max_length=64, verbose_name='Token', unique=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, verbose_name='User')

    class Meta:
        verbose_name = 'Token'
        verbose_name_plural = 'Tokens'

    def __str__(self):
        return self.token


class Tariffs(TimeMixin):
    days = models.IntegerField(verbose_name='Duration (days)', validators=[MinValueValidator(0)])
    title = models.CharField(verbose_name='Title', max_length=128)
    description = models.CharField(verbose_name='Description', max_length=512, blank=True, null=True)
    price = models.IntegerField(verbose_name='Price', validators=[MinValueValidator(0)])
    currency = models.CharField(verbose_name='Currency', max_length=6)

    class Meta:
        verbose_name = 'Tariff'
        verbose_name_plural = 'Tariffs'

    def __str__(self):
        return self.title


class FBids(TimeMixin):
    token = models.ForeignKey(Token, on_delete=models.CASCADE, verbose_name='Token')
    fBid = models.CharField(verbose_name='FBid', max_length=512, unique=True)

    class Meta:
        verbose_name = 'FBid'
        verbose_name_plural = 'FBids'

    def __str__(self):
        return self.fBid


class Results(TimeMixin):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, verbose_name='User')
    percent = models.IntegerField(verbose_name='Result percent',
                                  validators=[MinValueValidator(-76), MaxValueValidator(152)])
    result = models.JSONField(blank=True, null=True, verbose_name='Result info')

    class Meta:
        verbose_name = 'Result'
        verbose_name_plural = 'Results'

    def __str__(self):
        return str(self.user)


class Bill(TimeMixin):
    user = models.ForeignKey(Users, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='User ID')
    product = models.ForeignKey(Tariffs, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Product')
    amount = models.IntegerField(verbose_name='Amount', validators=[MinValueValidator(0)])
    status = models.BooleanField(verbose_name='Status', default=False)

    class Meta:
        verbose_name = 'Bill'
        verbose_name_plural = 'Bills'


class Messages(TimeMixin):
    user = models.ForeignKey(Users, null=True, blank=True, on_delete=models.CASCADE, verbose_name='User ID')
    title = models.CharField(verbose_name='Title', max_length=100)
    text = models.CharField(verbose_name='Text', max_length=1000)
    private = models.BooleanField(verbose_name='Private', default=False)

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'


class Diary(TimeMixin):
    CHOICES = (
        (0, 'Здоровье'),
        (1, 'Финансы'),
        (2, 'Личностный рост'),
        (3, 'Семья'),
    )

    user = models.ForeignKey(Users, null=True, blank=True, on_delete=models.CASCADE, verbose_name='User ID')
    text = models.CharField(verbose_name='Text', max_length=1000)
    type = models.IntegerField(verbose_name='Type', choices=CHOICES)

    class Meta:
        verbose_name = 'Diary'
        verbose_name_plural = 'Diaries'
