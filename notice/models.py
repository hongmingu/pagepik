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
SUB_URL_OBJECT_HELP = 1002
SUB_URL_OBJECT_COMMENT = 1003

KINDS_CHOICES = (
    (BRIDGE, "bridge"),
    (SUB_URL_OBJECT_HELP, "sub_url_object_help"),
    (SUB_URL_OBJECT_COMMENT, "sub_url_object_comment"),
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
        elif self.kind == SUB_URL_OBJECT_HELP:
            try:
                get_result = self.noticesuburlobjecthelp.sub_url_object_help
            except Exception as e:
                print(e)
                pass
            if get_result is not None:
                title = get_result.sub_url_object.title.text
                if len(title) > 10:
                    title = escape(title)[0:10] + '...'
                    title = escape(title)
                result = {'suobj_id': get_result.sub_url_object.uuid,
                          'username': get_result.user.userusername.username,
                          'user_photo': get_result.user.userphoto.file_50_url(),
                          'title': title}
            return result
        elif self.kind == SUB_URL_OBJECT_COMMENT:
            try:
                get_result = self.noticesuburlobjectcomment.sub_url_object_comment
            except Exception as e:
                print(e)
                pass
            if get_result is not None:
                comment_text = get_result.text
                if len(comment_text) > 10:
                    comment_text = escape(comment_text)[0:10] + '...'
                    comment_text = escape(comment_text)
                result = {'obj_id': get_result.sub_url_object.uuid,
                          'username': get_result.user.userusername.username,
                          'user_photo': get_result.user.userphoto.file_50_url(),
                          'comment_text': comment_text}
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


class NoticeSubUrlObjectHelp(models.Model):
    notice = models.OneToOneField(Notice, on_delete=models.CASCADE, null=True, blank=True)
    sub_url_object_help = models.ForeignKey(SubUrlObjectHelp, on_delete=models.CASCADE, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Notice_pk: %s, bridge_user: %s" % (self.notice.pk, self.sub_url_object_help.user.userusername.username)


class NoticeSubUrlObjectComment(models.Model):
    notice = models.OneToOneField(Notice, on_delete=models.CASCADE, null=True, blank=True)
    sub_url_object_comment = models.ForeignKey(SubUrlObjectComment, on_delete=models.CASCADE, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Notice_pk: %s, bridge_user: %s" % (self.notice.pk, self.sub_url_object_comment.user.userusername.username)