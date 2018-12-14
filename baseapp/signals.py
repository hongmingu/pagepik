from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver
from object.models import *
from relation.models import *
from notice.models import *
from django.db import transaction
from django.db.models import F
from django.utils.timezone import now
from object.numbers import *

# notice bridge

@receiver(post_save, sender=Bridge)
def created_bridge(sender, instance, created, **kwargs):
    if created:

        try:
            with transaction.atomic():
                if not instance.user == instance.bridge:
                    notice = Notice.objects.create(user=instance.bridge, kind=BRIDGE, uuid=uuid.uuid4().hex)
                    notice_bridge = NoticeBridge.objects.create(notice=notice, bridge=instance)

                bridging_count = instance.user.bridgingcount
                bridging_count.count = F('count') + 1
                bridging_count.save()

                bridger_count = instance.bridge.bridgercount
                bridger_count.count = F('count') + 1
                bridger_count.save()

        except Exception as e:
            print(e)
            pass


@receiver(post_delete, sender=Bridge)
def deleted_bridge(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            bridging_count = instance.user.bridgingcount
            bridging_count.count = F('count') - 1
            bridging_count.save()

            bridger_count = instance.bridge.bridgercount
            bridger_count.count = F('count') - 1
            bridger_count.save()

    except Exception as e:
        print(e)
        pass


@receiver(post_delete, sender=NoticeBridge)
def deleted_notice_bridge(sender, instance, **kwargs):
    if instance.notice:
        try:
            with transaction.atomic():
                instance.notice.delete()
        except Exception as e:
            print(e)
            pass


# ----------------------------------------------------------------------------------
# notice post_chat_rest_like


@receiver(post_save, sender=SubUrlObjectSubKeyword)
def created_sub_url_object_sub_keyword(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():
                url_keyword = None
                try:
                    url_keyword = UrlKeyword.objects.get(url_object=instance.sub_url_object.url_object,
                                                         keyword=instance.sub_keyword.keyword)
                except Exception as e:
                    return
                url_keyword_register = UrlKeywordRegister.objects.get_or_create(url_keyword=url_keyword,
                                                                                user=instance.sub_keyword.user)

                sub_url_object_sub_keyword_start, created = SubUrlObjectSubKeywordStart.objects.get_or_create(
                    sub_url_object_sub_keyword=instance)
                if created:
                    sub_url_object_sub_keyword_start.up_count = url_keyword.up_count
                    sub_url_object_sub_keyword_start.down_count = url_keyword.down_count
                    sub_url_object_sub_keyword_start.register_count = url_keyword.register_count
                    sub_url_object_sub_keyword_start.save()
        except Exception as e:
            print(e)
            pass


@receiver(pre_delete, sender=SubUrlObjectSubKeyword)
def deleted_sub_url_object_sub_keyword(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            sub_url_object_sub_keyword_exist = SubUrlObjectSubKeyword.objects.filter(
                sub_keyword=instance.sub_keyword).exists()
            if not sub_url_object_sub_keyword_exist:
                sub_keyword = instance.sub_keyword
                sub_keyword.delete()
            url_keyword = None
            try:
                url_keyword = UrlKeyword.objects.get(url_object=instance.sub_url_object.url_object,
                                                     keyword=instance.sub_keyword.keyword)
            except Exception as e:
                return
            try:
                url_keyword_register = UrlKeywordRegister.objects.get(url_keyword=url_keyword,
                                                                      user=instance.sub_keyword.user)
            except Exception as e:
                return
            url_keyword_register.delete()

    except Exception as e:
        print(e)
        pass


# notice post_chat_rest_like
@receiver(post_save, sender=UrlKeywordRegister)
def created_keyword_register(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():
                url_keyword = instance.url_keyword
                url_keyword.register_count = F('register_count') + 1
                url_keyword.save()
        except Exception as e:
            print(e)
            pass


@receiver(post_delete, sender=UrlKeywordRegister)
def deleted_keyword_register(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            url_keyword = instance.url_keyword
            url_keyword.register_count = F('register_count') - 1
            url_keyword.save()
    except Exception as e:
        print(e)
        pass


# notice post_chat_rest_like
@receiver(post_save, sender=UrlKeywordUp)
def created_keyword_up(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():
                url_keyword = instance.url_keyword
                url_keyword.up_count = F('up_count') + 1
                url_keyword.save()

                url_keyword_down = None
                try:
                    url_keyword_down = UrlKeywordDown.objects.get(user=instance.user, url_keyword=url_keyword)
                except Exception as e:
                    pass
                if url_keyword_down is not None:
                    url_keyword_down.delete()

        except Exception as e:
            print(e)
            pass


@receiver(post_delete, sender=UrlKeywordUp)
def deleted_keyword_up(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            url_keyword = instance.url_keyword
            url_keyword.up_count = F('up_count') - 1
            url_keyword.save()
    except Exception as e:
        print(e)
        pass


# notice post_chat_rest_like
@receiver(post_save, sender=UrlKeywordDown)
def created_keyword_down(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():
                url_keyword = instance.url_keyword
                url_keyword.down_count = F('down_count') + 1
                url_keyword.save()

                url_keyword_up = None
                try:
                    url_keyword_up = UrlKeywordUp.objects.get(user=instance.user, url_keyword=url_keyword)
                except Exception as e:
                    pass
                if url_keyword_up is not None:
                    url_keyword_up.delete()
        except Exception as e:
            print(e)
            pass


@receiver(pre_delete, sender=UrlKeywordDown)
def deleted_keyword_down(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            url_keyword = instance.url_keyword
            url_keyword.down_count = F('down_count') - 1
            url_keyword.save()

    except Exception as e:
        print(e)
        pass

# -------------------------------------------


@receiver(post_save, sender=SubUrlObject)
def created_sub_url_object(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():
                sub_raw_keyword_count = SubRawKeywordCount.objects.create(sub_url_object=instance)
                suobj_comment_count = SubUrlObjectCommentCount.objects.create(sub_url_object=instance)
        except Exception as e:
            print(e)
            pass





@receiver(post_save, sender=SubRawKeyword)
def created_sub_raw_keyword(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():
                sub_raw_keyword_count = instance.sub_url_object.subrawkeywordcount
                sub_raw_keyword_count.count = F('count') + 1
                sub_raw_keyword_count.save()
        except Exception as e:
            print(e)
            pass


@receiver(post_delete, sender=SubRawKeyword)
def deleted_sub_raw_keyword(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            sub_raw_keyword_count = instance.sub_url_object.subrawkeywordcount
            sub_raw_keyword_count.count = F('count') - 1
            sub_raw_keyword_count.save()

            sub_keyword = instance.sub_keyword
            sub_url_object = instance.sub_url_object
            sub_raw_keywords_exist = SubRawKeyword.objects.filter(sub_keyword=sub_keyword,
                                                                  sub_url_object=sub_url_object,
                                                                  user=instance.user).exists()

            if not sub_raw_keywords_exist:
                sub_url_object_sub_keyword_delete = SubUrlObjectSubKeyword.objects.filter(sub_url_object=sub_url_object,
                                                                                          sub_keyword=sub_keyword
                                                                                          ).delete()

    except Exception as e:
        print(e)
        pass


@receiver(post_save, sender=SubUrlObjectHelp)
def created_sub_url_object_help(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():
                if not instance.user == instance.sub_url_object.user:
                    notice = Notice.objects.create(user=instance.sub_url_object.user, kind=SUB_URL_OBJECT_HELP, uuid=uuid.uuid4().hex)
                    notice_suobj = NoticeSubUrlObjectHelp.objects.create(notice=notice, sub_url_object_help=instance)

                sub_url_object = instance.sub_url_object
                sub_url_object.help_count = F('help_count') + 1
                sub_url_object.save()
        except Exception as e:
            print(e)
            pass


@receiver(post_delete, sender=SubUrlObjectHelp)
def deleted_sub_url_object_help(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            sub_url_object = instance.sub_url_object
            sub_url_object.help_count = F('help_count') - 1
            sub_url_object.save()
    except Exception as e:
        print(e)
        pass


@receiver(post_delete, sender=NoticeSubUrlObjectHelp)
def deleted_notice_sub_url_object_help(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            instance.notice.delete()
    except Exception as e:
        print(e)
        pass


# notice post_comment
@receiver(post_save, sender=SubUrlObjectComment)
def created_sub_url_object_comment(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():
                if not instance.user == instance.sub_url_object.user:
                    notice = Notice.objects.create(user=instance.sub_url_object.user,
                                                   kind=SUB_URL_OBJECT_COMMENT,
                                                   uuid=uuid.uuid4().hex)
                    notice_suobj_comment = NoticeSubUrlObjectComment.objects.create(notice=notice,
                                                                                    sub_url_object_comment=instance)

                suobj_comment_count = instance.sub_url_object.suburlobjectcommentcount
                suobj_comment_count.count = F('count') + 1
                suobj_comment_count.save()
        except Exception as e:
            print(e)
            pass


@receiver(post_delete, sender=SubUrlObjectComment)
def deleted_sub_url_object_comment(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            suobj_comment_count = instance.sub_url_object.suburlobjectcommentcount
            suobj_comment_count.count = F('count') - 1
            suobj_comment_count.save()
    except Exception as e:
        print(e)
        pass


@receiver(post_delete, sender=NoticeSubUrlObjectComment)
def deleted_notice_sub_url_object_comment(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            instance.notice.delete()
    except Exception:
        pass



@receiver(post_save, sender=Notice)
def created_notice(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():
                notice_count = instance.user.noticecount
                notice_count.count = F('count') + 1
                notice_count.save()
        except Exception as e:
            print(e)
            pass


@receiver(post_delete, sender=Notice)
def deleted_notice(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            if instance.checked is False:
                notice_count = instance.user.noticecount
                notice_count.count = F('count') - 1
                notice_count.save()
    except Exception as e:
        print(e)
        pass