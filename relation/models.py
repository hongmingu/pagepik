from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings
from authapp.models import *


class Bridge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='is_bridging')
    bridge = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='is_bridged')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "ok: %s, bridge: %s" % (self.pk, self.pk)

    class Meta:
        unique_together = ('user', 'bridge',)


class BridgingCount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "bridging Count of: %s" % self.pk


class BridgerCount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "bridger Count of: %s" % self.pk
'''

class Blocking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocking')
    blocking = models.ForeignKey(User, on_delete=models.CASCADE, related_name='on_blocking')

    def __str__(self):
        return "Whose Blocking: %s, blocked user: %s" % (self.user.userusername.username,
                                                  self.blocking.userusername.username)

    class Meta:
        unique_together = ('user', 'blocking',)

# 전체 검색 결과에서 만약 블락ed가 없으면 유저 하나 당 blockuser에서 체크해야한다. 그러나 블락ed가 있으면 거기에 있는 유저는 빼고 검색결과 보여주면 된다.
class BlockingCount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "Blocking Count of: %s" % self.user.userusername.username



class Blocked(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked')
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name='in_blocked_list')

    def __str__(self):
        return "Whose Blocked: %s, blocked by user: %s" % (self.user.userusername.username,
                                                  self.blocking.userusername.username)

    class Meta:
        unique_together = ('user', 'blocked',)

# 전체 검색 결과에서 만약 블락ed가 없으면 유저 하나 당 blockuser에서 체크해야한다. 그러나 블락ed가 있으면 거기에 있는 유저는 빼고 검색결과 보여주면 된다.
class BlockedCount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "Blocked Count of: %s" % self.user.userusername.username

'''
