from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings
from authapp.models import *
from .disposers import *
import uuid
from django.utils.html import escape, _js_escapes, normalize_newlines
from django.utils.timezone import now
# For Post Things
# 페이지픽에서 공개 비공개와 별개로 등록 비등록이 중요하다. 어차피 등록될 때 누가 등록했는지는 안 뜨게 했었다.
# booleanfield로 대충 하고 꼭 어쩔 수 없는 것만 textfield 로 한다. 보통 3가지 경우 나오는 것.
# private , public은 나중에 한다. 귀찮다.


# PostChat 이랑 PostComment 에 좋아요 구현, PostRest 는 보류. 안 하는 게 나을 것 같다. 아냐 하는 게 나을 것 같아.
# 글을 많이 쓰게 하는 것이 원칙인데 구현하면 제안을 많이 쓰게 할 수 있다. 그러나 구현하지 않는다면 제안이 줄기 때문에 독창적인 사람만
# 글을 쓰는 데에 스트레스를 덜 주게 된다. 그러나 독창적인 사람의 경우 남의 의견이 어떻든 상관하지 않을 수 있기 때문에 효과는 미미할
# 것으로 예상한다. 필요하다면 제안을 제한하거나 제안을 장막으로 가리는 등의 도움이 될 수 있다. 글을 많이 쓰고 활동하게 하는 것이
# 우선이다. 원칙과 우선순위. 우선순위와 원칙. 우선순위와 예외와 규칙.
# ----------------------------------------------------------------------------------------------------------------------

class UrlObject(models.Model):

    loc = models.TextField(max_length=2050, null=True, unique=True, blank=True, default=None)

    # 여기서 unique True 면 null값도 두 개 이상 넣을 수 없나?
    http = models.BooleanField(default=False)
    https = models.BooleanField(default=False)
    uuid = models.CharField(max_length=34, unique=True, null=True, default=None, blank=True)

    is_discrete = models.BooleanField(default=False)
    in_not_301 = models.BooleanField(default=False)
    discrete_loc = models.TextField(max_length=2050, null=True, unique=True, blank=True, default=None)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "URL: %s" % self.loc

    def get_url(self):
        scheme = ''
        if self.https:
            scheme = 'https://'
        elif self.http:
            scheme = 'http://'
        return scheme + self.loc


class Keyword(models.Model):
    text = models.TextField(max_length=2048, null=True, blank=True, unique=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "text: %s" % self.text


class UrlKeyword(models.Model):
    url_object = models.ForeignKey(UrlObject, on_delete=models.CASCADE, null=True, blank=True)
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE, null=True, blank=True)
    uuid = models.CharField(max_length=34, unique=True, null=True, default=None, blank=True)
    up_count = models.PositiveIntegerField(default=0)
    down_count = models.PositiveIntegerField(default=0)
    register_count = models.PositiveIntegerField(default=0)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "text: %s" % self.pk

    class Meta:
        unique_together = ('url_object', 'keyword',)


class UrlKeywordRegister(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    url_keyword = models.ForeignKey(UrlKeyword, on_delete=models.CASCADE, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "pk: %s" % self.pk

    class Meta:
        unique_together = ('user', 'url_keyword',)


class UrlKeywordUp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    url_keyword = models.ForeignKey(UrlKeyword, on_delete=models.CASCADE, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "pk: %s" % self.pk

    class Meta:
        unique_together = ('user', 'url_keyword',)


class UrlKeywordDown(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    url_keyword = models.ForeignKey(UrlKeyword, on_delete=models.CASCADE, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "pk: %s" % self.pk

    class Meta:
        unique_together = ('user', 'url_keyword',)


class Title(models.Model):
    url_object = models.ForeignKey(UrlObject, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField(max_length=1000, null=True, blank=True)
    status = models.CharField(max_length=20, null=True, default='200', blank=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)


class SubUrlObject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.ForeignKey(Title, on_delete=models.CASCADE, null=True, blank=True)
    url_object = models.ForeignKey(UrlObject, on_delete=models.CASCADE, null=True, blank=True)
    uuid = models.CharField(max_length=34, unique=True, null=True, default=None, blank=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "pk: %s" % self.pk

    class Meta:
        unique_together = ('user', 'url_object',)


class SubUrlObjectInitialUrl(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    sub_url_object = models.ForeignKey(SubUrlObject, on_delete=models.CASCADE, null=True, blank=True)
    url = models.TextField(max_length=2060, null=True, blank=True, default=None)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "pk: %s" % self.pk

    class Meta:
        unique_together = ('url', 'sub_url_object',)


class SubKeyword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "text: %s" % self.keyword.text

    class Meta:
        unique_together = ('user', 'keyword',)


class SubUrlObjectSubKeyword(models.Model):
    sub_url_object = models.ForeignKey(SubUrlObject, on_delete=models.CASCADE, null=True, blank=True)
    sub_keyword = models.ForeignKey(SubKeyword, on_delete=models.CASCADE, null=True, blank=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "pk: %s" % self.pk

    class Meta:
        unique_together = ('sub_url_object', 'sub_keyword',)


class SubRawKeyword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    sub_url_object = models.ForeignKey(SubUrlObject, on_delete=models.CASCADE, null=True, blank=True)
    sub_keyword = models.ForeignKey(SubKeyword, on_delete=models.CASCADE, null=True, blank=True)

    text = models.TextField(max_length=2048, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sub_url_object', 'text',)


class SubRawKeywordCount(models.Model):
    sub_url_object = models.OneToOneField(SubUrlObject, on_delete=models.CASCADE, null=True, blank=True)
    count = models.PositiveSmallIntegerField(default=0)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)