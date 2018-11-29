from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings
from authapp.models import *
from object.models import *
from relation.models import *
import uuid
from django.utils.html import escape, _js_escapes, normalize_newlines

# For Post Things
# 페이지픽에서 공개 비공개와 별개로 등록 비등록이 중요하다. 어차피 등록될 때 누가 등록했는지는 안 뜨게 했었다.
# booleanfield로 대충 하고 꼭 어쩔 수 없는 것만 textfield 로 한다. 보통 3가지 경우 나오는 것.
# private , public은 나중에 한다. 귀찮다.

BRIDGE = 1001

KINDS_CHOICES = (
    (BRIDGE, "bridge"),
)


class Notice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    kind = models.PositiveSmallIntegerField(choices=KINDS_CHOICES, default=0)
    checked = models.BooleanField(default=False)
    uuid = models.CharField(max_length=34, unique=True, null=True, default=None)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Notice pk: %s, user: %s, kind: %s" % (self.pk, self.user.userusername.username, self.kind)

    def get_value(self):
        result = None
        get_result = None
        if self.kind == BRIDGE:
            try:
                get_result = self.noticebridge.bridge
            except Exception as e:
                print(e)
                pass
            if get_result is not None:
                result = {'username': get_result.user.userusername.username,
                          'user_photo': get_result.user.userphoto.file_50_url()}
            return result

        return None


class NoticeCount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    count = models.PositiveIntegerField(default=0)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "user: %s, count: %s" % (self.user, self.count)


class NoticeBridge(models.Model):
    notice = models.OneToOneField(Notice, on_delete=models.CASCADE, null=True, blank=True)
    bridge = models.ForeignKey(Bridge, on_delete=models.CASCADE, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Notice_pk: %s, bridge_user: %s" % (self.notice.pk, self.bridge.user.userusername.username)