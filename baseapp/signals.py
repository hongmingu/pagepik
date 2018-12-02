from django.db.models.signals import post_save, post_delete, pre_save
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
        if instance.user == instance.follow:
            return
        try:
            with transaction.atomic():
                notice = Notice.objects.create(user=instance.follow, kind=BRIDGE)
                notice_bridge = NoticeBridge.objects.create(notice=notice, bridge=instance)
                notice_count = instance.bridge.noticecount
                notice_count.count = F('count') + 1
                notice_count.save()

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
        if instance.notice:
            try:
                with transaction.atomic():
                    if instance.notice.checked is False:
                        notice_count = instance.notice.user.noticecount
                        notice_count.count = F('count') - 1
                        notice_count.save()

                        bridging_count = instance.user.bridgingcount
                        bridging_count.count = F('count') - 1
                        bridging_count.save()

                        bridger_count = instance.bridge.bridgercount
                        bridger_count.count = F('count') - 1
                        bridger_count.save()

                    instance.notice.delete()
            except Exception as e:
                print(e)
                pass
    except:
        pass


@receiver(post_delete, sender=NoticeBridge)
def deleted_notice_bridge(sender, instance, **kwargs):
    try:
        if instance.notice:
            try:
                with transaction.atomic():
                    if instance.notice.checked is False:
                        notice_count = instance.notice.user.noticecount
                        notice_count.count = F('count') - 1
                        notice_count.save()
                    instance.notice.delete()
            except Exception as e:
                print(e)
                pass
    except:
        pass


# ----------------------------------------------------------------------------------
# notice post_chat_rest_like


@receiver(post_save, sender=SubUrlObjectSubKeyword)
def created_sub_keyword(sender, instance, created, **kwargs):
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

        except Exception as e:
            print(e)
            pass


@receiver(post_delete, sender=SubUrlObjectSubKeyword)
def deleted_sub_keyword(sender, instance, **kwargs):
    try:
        with transaction.atomic():
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

                # 이거 놓치지말고 down_count 랑 up_count 도 0 될 때 다 지운다.
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
            if url_keyword.register_count == 0 and url_keyword.up_count == 0 and url_keyword.down_count == 0:
                url_keyword.delete()
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
            if url_keyword.register_count == 0 and url_keyword.up_count == 0 and url_keyword.down_count == 0:
                url_keyword.delete()
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


@receiver(post_delete, sender=UrlKeywordDown)
def deleted_keyword_down(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            url_keyword = instance.url_keyword
            url_keyword.down_count = F('down_count') - 1
            url_keyword.save()
            if url_keyword.register_count == 0 and url_keyword.up_count == 0 and url_keyword.down_count == 0:
                url_keyword.delete()
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
            sub_raw_keywords_exist = SubRawKeyword.objects.filter(sub_keyword=sub_keyword).exists()

            if not sub_raw_keywords_exist:
                sub_keyword.delete()

    except Exception as e:
        print(e)
        pass
