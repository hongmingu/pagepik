import json
import urllib
from urllib.parse import urlparse

from PIL import Image
from io import BytesIO
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.timezone import now, timedelta
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

from authapp import options
from authapp import texts
from object.models import *
from .forms import PostProfilePhotoForm, PostChatPhotoForm
from relation.models import *
from notice.models import *
from .models import *
from django.contrib.auth import update_session_auth_hash
from django.utils.html import escape, _js_escapes, normalize_newlines
from object.numbers import *


# Create your models here.
# 좋아요 비공개 할 수 있게
# 챗스톡, 페이지픽, 임플린, 챗카부 순으로 만들자.


@ensure_csrf_cookie
def re_create_new_upload_photo(request):
    if request.method == "POST":
        if request.user.is_authenticated:

            if request.is_ajax():
                try:
                    post = Post.objects.get(uuid=request.POST['post_id'])
                except:
                    return JsonResponse({'res': 0})
                try:
                    post_profile = PostProfile.objects.get(post=post)
                except:
                    return JsonResponse({'res': 0})
                form = PostProfilePhotoForm(request.POST, request.FILES, instance=post_profile)
                if form.is_valid():

                    DJANGO_TYPE = request.FILES['file'].content_type

                    if DJANGO_TYPE == 'image/jpeg':
                        PIL_TYPE = 'jpeg'
                        FILE_EXTENSION = 'jpg'
                    elif DJANGO_TYPE == 'image/png':
                        PIL_TYPE = 'png'
                        FILE_EXTENSION = 'png'
                        # DJANGO_TYPE == 'image/gif
                    else:
                        return JsonResponse({'res': 0, 'message': texts.UNEXPECTED_ERROR})

                    from io import BytesIO
                    from PIL import Image
                    from django.core.files.uploadedfile import SimpleUploadedFile
                    import os
                    x = float(request.POST['x'])
                    y = float(request.POST['y'])
                    width = float(request.POST['width'])
                    height = float(request.POST['height'])
                    rotate = float(request.POST['rotate'])
                    # Open original photo which we want to thumbnail using PIL's Image
                    try:
                        with transaction.atomic():

                            image = Image.open(BytesIO(request.FILES['file'].read()))
                            image_modified = image.rotate(-1 * rotate, expand=True).crop((x, y, x + width, y + height))
                            # use our PIL Image object to create the thumbnail, which already
                            image = image_modified.resize((300, 300), Image.ANTIALIAS)

                            # Save the thumbnail
                            temp_handle = BytesIO()
                            image.save(temp_handle, PIL_TYPE, quality=90)
                            temp_handle.seek(0)

                            # Save image to a SimpleUploadedFile which can be saved into ImageField
                            # print(os.path.split(request.FILES['file'].name)[-1])
                            suf = SimpleUploadedFile(os.path.split(request.FILES['file'].name)[-1],
                                                     temp_handle.read(), content_type=DJANGO_TYPE)
                            # Save SimpleUploadedFile into image field
                            post_profile.file_300.save(
                                '%s.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
                                suf, save=True)

                            # request.FILES['file'].seek(0)
                            # image = Image.open(BytesIO(request.FILES['file'].read()))

                            # use our PIL Image object to create the thumbnail, which already
                            image = image_modified.resize((50, 50), Image.ANTIALIAS)

                            # Save the thumbnail
                            temp_handle = BytesIO()
                            image.save(temp_handle, PIL_TYPE, quality=90)
                            temp_handle.seek(0)

                            # Save image to a SimpleUploadedFile which can be saved into ImageField
                            # print(os.path.split(request.FILES['file'].name)[-1])
                            suf = SimpleUploadedFile(os.path.split(request.FILES['file'].name)[-1],
                                                     temp_handle.read(), content_type=DJANGO_TYPE)
                            # Save SimpleUploadedFile into image field
                            # print(os.path.splitext(suf.name)[0])
                            # user_photo.file_50.save(
                            #     '50_%s.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
                            #     suf, save=True)
                            post_profile.file_50.save(
                                '%s.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
                                suf, save=True)
                            return JsonResponse({'res': 1, 'url': post_profile.file_300.url})
                    except Exception:
                        return JsonResponse({'res': 0, 'message': texts.UNEXPECTED_ERROR})

            return JsonResponse({'res': 0, 'message': texts.UNEXPECTED_ERROR})


# 이건 포스트의 프로필 이미지를 지우기 위함.
@ensure_csrf_cookie
def re_create_new_remove_photo(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                if request.POST.get('command', None) == 'remove_photo':
                    post_id = request.POST.get('post_id', None)
                    try:
                        post = Post.objects.get(pk=post_id)
                    except:
                        return JsonResponse({'res': 0})
                    try:
                        post_profile = PostProfile.objects.get(post=post)
                    except:
                        return JsonResponse({'res': 0})
                    post_profile.file_50 = None
                    post_profile.file_300 = None
                    post_profile.save()
                    return JsonResponse({'res': 1})
                elif request.POST.get('whose', None) == 'other':
                    pass

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_create_new_text(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_id = request.POST.get('post_id', None)
                try:
                    post = Post.objects.get(uuid=post_id)
                except:
                    return JsonResponse({'res': 0})

                try:
                    post_chat_last = PostChat.objects.filter(post=post).last()

                except PostChat.DoesNotExist:
                    return JsonResponse({'res': 0})

                you_say = False
                if request.POST.get('you_say', None) == 'you':
                    you_say = True
                post_chat = PostChat.objects.create(post=post, kind=POSTCHAT_TEXT, before=post_chat_last,
                                                    you_say=you_say, uuid=uuid.uuid4().hex)
                post_chat_text = PostChatText.objects.create(post_chat=post_chat, text=request.POST.get('text', None))
                return JsonResponse({'res': 1, 'content': post_chat.get_value()})

        return JsonResponse({'res': 2})


'''

@ensure_csrf_cookie
def re_create_new_text(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_id = request.POST.get('post_id', None)
                try:
                    post = Post.objects.last()
                except:
                    return JsonResponse({'res': 0})
                print('got post: ' + str(post))
                try:
                    post_chat_create = PostChat.objects.create(post=post, kind=POSTCHAT_TEXT, before=None, you_say=True, uuid=uuid.uuid4().hex)
                    print('post chat has been created')
                except Exception as e:
                    print('if it has exception: ' + str(e))
                print('just created post chat: ' + str(post_chat_create.pk))

                try:
                    post_chat_last = PostChat.objects.last()
                    print('any made post chat?: ' + str(post_chat_last.pk))

                except PostChat.DoesNotExist:
                    print('has error on getting post_chat_last')
                print('has no error on getting post_chat_last')
                you_say = False
                if request.POST.get('you_say', None) == 'you':
                    you_say = True
                print(request.POST.get('text', None))
                post_chat = PostChat.objects.create(kind=POSTCHAT_TEXT, before=post_chat_last, you_say=you_say, uuid=uuid.uuid4().hex)
                post_chat_text = PostChatText.objects.create(post_chat=post_chat, text=request.POST.get('text', None))
                return JsonResponse({'res': 1, 'content': post_chat.get_value()})

        return JsonResponse({'res': 2})'''


# 2018-07-28 해야 할 일: postchatphoto 업로드 테스트.


@ensure_csrf_cookie
def re_create_new_chat_photo(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_id = request.POST['post_id']
                try:
                    post = Post.objects.get(uuid=post_id)
                except:
                    return JsonResponse({'res': 0})
                try:
                    post_chat_last = PostChat.objects.filter(post=post).last()
                except PostChat.DoesNotExist:
                    return JsonResponse({'res': 0})
                form = PostChatPhotoForm(request.POST, request.FILES)
                if form.is_valid():
                    you_say = True
                    if request.POST.get('you_say', None) == 'someone':
                        you_say = False
                    post_chat = PostChat.objects.create(kind=POSTCHAT_PHOTO, post=post, before=post_chat_last,
                                                        you_say=you_say, uuid=uuid.uuid4().hex)
                    post_chat_photo = PostChatPhoto.objects.create(post_chat=post_chat)

                    DJANGO_TYPE = request.FILES['file'].content_type

                    if DJANGO_TYPE == 'image/jpeg':
                        PIL_TYPE = 'jpeg'
                        FILE_EXTENSION = 'jpg'
                    elif DJANGO_TYPE == 'image/png':
                        PIL_TYPE = 'png'
                        FILE_EXTENSION = 'png'
                        # DJANGO_TYPE == 'image/gif
                    else:
                        return JsonResponse({'res': 0, 'message': texts.UNEXPECTED_ERROR})

                    from io import BytesIO
                    from PIL import Image
                    from django.core.files.uploadedfile import SimpleUploadedFile
                    import os
                    rotate = float(request.POST['rotate'])
                    # Open original photo which we want to thumbnail using PIL's Image

                    image = Image.open(BytesIO(request.FILES['file'].read()))
                    image = image.rotate(-1 * rotate, expand=True)
                    # use our PIL Image object to create the thumbnail, which already
                    # Save the thumbnail
                    temp_handle = BytesIO()
                    image.save(temp_handle, PIL_TYPE, quality=70)
                    temp_handle.seek(0)

                    # Save image to a SimpleUploadedFile which can be saved into ImageField
                    # print(os.path.split(request.FILES['file'].name)[-1])
                    suf = SimpleUploadedFile(os.path.split(request.FILES['file'].name)[-1],
                                             temp_handle.read(), content_type=DJANGO_TYPE)
                    # Save SimpleUploadedFile into image field
                    post_chat_photo.file.save(
                        '%s.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
                        suf, save=True)

                    # request.FILES['file'].seek(0)
                    # image = Image.open(BytesIO(request.FILES['file'].read()))

                    # use our PIL Image object to create the thumbnail, which already
                    return JsonResponse({'res': 1, 'content': post_chat.get_value()})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_post_update(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_id = request.POST.get('post_id', None)

                try:
                    post = Post.objects.get(uuid=post_id)
                except Exception as e:
                    print(e)
                    return JsonResponse({'res': 0})
                # 여기서 None 이 나오진 않고 기껏해야 빈 문자열이 오는 것이다.
                open = request.POST.get('open', None)
                title_command = request.POST.get('title_command', None)
                desc_command = request.POST.get('desc_command', None)
                title_add = None
                desc_add = None
                if open == 'open':
                    post.is_open = True
                elif open == 'close':
                    post.is_open = False
                if title_command == 'removed':
                    post.title = None
                elif title_command == 'add':
                    title_add = request.POST.get('title', None)
                    title_add = title_add.strip()
                    post.title = title_add
                if desc_command == 'removed':
                    post.description = None
                elif desc_command == 'add':
                    desc_add = request.POST.get('description', None)
                    desc_add = desc_add.strip()
                    post.description = desc_add
                post.save()
                return JsonResponse({'res': 1})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_post_update_profile_name(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_id = request.POST.get('post_id', None)
                name = request.POST.get('name', None)
                name = name.strip()
                post = None
                try:
                    post = Post.objects.get(uuid=post_id)
                except Exception as e:
                    print(e)
                    return JsonResponse({'res': 0})
                if post is not None:
                    try:
                        post_profile = PostProfile.objects.get(post=post)
                    except Exception as e:
                        print(e)
                        return JsonResponse({'res': 0})
                    if post_profile is not None:
                        post_profile.name = name
                        post_profile.save()

                return JsonResponse({'res': 1})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_post_chat_remove(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_chat_id = request.POST.get('post_chat_id', None)
                try:
                    post_chat = PostChat.objects.get(uuid=post_chat_id)
                except:
                    return JsonResponse({'res': 0})
                post_chat.delete()
                return JsonResponse({'res': 1})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_post_chat_modify_populate(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_id = request.POST.get('post_id', None)
                try:
                    post = Post.objects.get(uuid=post_id)
                except:
                    return JsonResponse({'res': 0})
                post_chat_set = post.postchat_set.all().order_by('-created')[:20]
                from django.core import serializers
                post_chat_set = serializers.serialize('python', post_chat_set)
                actual_data = [PostChat.objects.get(pk=item['pk']).get_value() for item in post_chat_set]
                output = json.dumps(actual_data)
                return JsonResponse({'res': 1, 'set': output})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_post_chat_more_load(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_id = request.POST.get('post_id', None)
                post_chat_id = request.POST.get('post_chat_id', None)

                try:
                    post = Post.objects.get(uuid=post_id)
                except:
                    return JsonResponse({'res': 0})
                from django.db.models import Q
                standard_post_chat = PostChat.objects.get(uuid=post_chat_id)
                post_chat_set = PostChat.objects.filter(
                    Q(post=post) & Q(created__lt=standard_post_chat.created)).order_by('-created')[:10]
                from django.core import serializers
                post_chat_set = serializers.serialize('python', post_chat_set)
                actual_data = [PostChat.objects.get(pk=item['pk']).get_value() for item in post_chat_set]
                output = json.dumps(actual_data)
                return JsonResponse({'res': 1, 'set': output})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_home_feed(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                last_id = request.POST.get('last_id', None)
                posts = None
                if last_id == '':
                    posts = Post.objects.filter(
                        (Q(user__is_followed__user=request.user) | Q(post_follow__user=request.user)) & Q(
                            is_open=True)).order_by('-post_chat_created').distinct()[:30]
                else:
                    last_post = None
                    try:
                        last_post = Post.objects.get(uuid=last_id)
                    except Exception as e:
                        print(e)
                        return JsonResponse({'res': 0})

                    posts = Post.objects.filter(
                        (Q(user__is_followed__user=request.user) | Q(post_follow__user=request.user)) & Q(
                            is_open=True) & Q(post_chat_created__lte=last_post.post_chat_created)).exclude(
                        pk=last_post.pk).order_by('-post_chat_created').distinct()[:30]

                ################################
                output = []
                count = 0
                last = None
                post_follow = None
                for post in posts:
                    count = count + 1
                    if count == 30:
                        last = post.uuid
                    post_follow = True
                    if Follow.objects.filter(user=request.user, follow=post.user).exists():
                        post_follow = False
                    sub_output = {
                        'id': post.uuid,
                        'created': post.created,
                        'post_follow': post_follow
                    }

                    output.append(sub_output)

                return JsonResponse({'res': 1, 'set': output, 'last': last})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_comment_add(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_id = request.POST.get('post_id', None)
                text = request.POST.get('comment', None)
                try:
                    post = Post.objects.get(uuid=post_id)
                    # post = Post.objects.last()

                except:
                    return JsonResponse({'res': 0})
                try:
                    with transaction.atomic():
                        post_comment = PostComment.objects.create(post=post, user=request.user, uuid=uuid.uuid4().hex,
                                                                  text=text)
                        from django.db.models import F
                        post_comment_count = post.postcommentcount
                        post_comment_count.count = F('count') + 1
                        post_comment_count.save()
                        # customers = Customer.objects.filter(scoops_ordered__gt=F('store_visits'))
                except Exception:
                    return JsonResponse({'res': 0})

                output = []
                sub_output = {}
                if post_comment is not None:
                    sub_output = {
                        'comment_user_id': post_comment.user.username,
                        'comment_username': post_comment.user.userusername.username,
                        'comment_text': escape(post_comment.text),
                        'comment_created': post_comment.created,
                        'comment_uuid': post_comment.uuid,
                    }
                output.append(sub_output)
                return JsonResponse({'res': 1, 'set': output})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_comment_delete(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                comment_id = request.POST.get('comment_id', None)
                post_id = request.POST.get('post_id', None)
                try:
                    # post = Post.objects.last()
                    post = Post.objects.get(uuid=post_id)
                except:
                    return JsonResponse({'res': 0})

                try:
                    comment = PostComment.objects.get(uuid=comment_id, user=request.user)
                except:
                    try:
                        comment = PostComment.objects.get(uuid=comment_id, post=post, post__user=request.user)
                    except:
                        return JsonResponse({'res': 0})

                try:
                    with transaction.atomic():
                        comment.delete()
                        from django.db.models import F
                        post_comment_count = post.postcommentcount
                        post_comment_count.count = F('count') - 1
                        post_comment_count.save()
                except Exception:
                    return JsonResponse({'res': 0})
                return JsonResponse({'res': 1})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_comment_more_load(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_id = request.POST.get('post_id', None)
                last_comment_id = request.POST.get('last_comment_id', None)

                try:
                    post = Post.objects.get(uuid=post_id)
                except Exception:
                    return JsonResponse({'res': 0})

                post_comment_last = PostComment.objects.get(uuid=last_comment_id)

                post_comments = PostComment.objects.filter(
                    Q(post=post) & Q(created__gt=post_comment_last.created)).order_by('created')[:20]

                post_comment_uuids = [post_comment.uuid for post_comment in post_comments]
                output = []

                post_comment_end = PostComment.objects.last()
                post_comment = None
                end = False
                if post_comments:
                    for item in post_comment_uuids:
                        try:
                            post_comment = PostComment.objects.get(uuid=item)
                        except:
                            pass
                        if post_comment is not None:
                            sub_output = {
                                'comment_user_id': post_comment.user.username,
                                'comment_username': post_comment.user.userusername.username,
                                'comment_text': escape(post_comment.text),
                                'comment_created': post_comment.created,
                                'comment_uuid': post_comment.uuid,
                            }
                            output.append(sub_output)
                            if post_comment.uuid == post_comment_end.uuid:
                                end = True
                else:
                    output = None
                    end = True
                return JsonResponse({'res': 1, 'set': output, 'end': end})
        else:
            post_id = request.POST.get('post_id', None)
            last_comment_id = request.POST.get('last_comment_id', None)

            try:
                post = Post.objects.get(uuid=post_id)
            except Exception:
                return JsonResponse({'res': 0})

            post_comment_last = PostComment.objects.get(uuid=last_comment_id)

            post_comments = PostComment.objects.filter(
                Q(post=post) & Q(created__gt=post_comment_last.created)).order_by('created')[:20]

            post_comment_uuids = [post_comment.uuid for post_comment in post_comments]
            output = []

            post_comment_end = PostComment.objects.last()
            post_comment = None
            end = False
            if post_comments:
                for item in post_comment_uuids:
                    try:
                        post_comment = PostComment.objects.get(uuid=item)
                    except:
                        pass
                    if post_comment is not None:
                        sub_output = {
                            'comment_user_id': post_comment.user.username,
                            'comment_username': post_comment.user.userusername.username,
                            'comment_text': escape(post_comment.text),
                            'comment_created': post_comment.created,
                            'comment_uuid': post_comment.uuid,
                        }
                        output.append(sub_output)
                        if post_comment.uuid == post_comment_end.uuid:
                            end = True
            else:
                output = None
                end = True
            return JsonResponse({'res': 1, 'set': output, 'end': end})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_post_like(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_id = request.POST.get('post_id', None)
                try:
                    # post = Post.objects.last()
                    post = Post.objects.get(uuid=post_id)
                except:
                    return JsonResponse({'res': 0})
                try:
                    post_like = PostLike.objects.get(post=post, user=request.user)
                except PostLike.DoesNotExist:
                    post_like = None

                liked = None
                if post_like is not None:
                    try:
                        with transaction.atomic():
                            post_like.delete()
                            from django.db.models import F
                            post_like_count = post.postlikecount
                            post_like_count.count = F('count') - 1
                            post_like_count.save()
                            liked = False
                            # customers = Customer.objects.filter(scoops_ordered__gt=F('store_visits'))
                    except Exception:
                        return JsonResponse({'res': 0})
                else:
                    try:
                        with transaction.atomic():
                            post_like = PostLike.objects.create(post=post, user=request.user)
                            from django.db.models import F
                            post_like_count = post.postlikecount
                            post_like_count.count = F('count') + 1
                            post_like_count.save()
                            liked = True
                            # customers = Customer.objects.filter(scoops_ordered__gt=F('store_visits'))
                    except Exception:
                        return JsonResponse({'res': 0})

                return JsonResponse({'res': 1, 'liked': liked})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_user_home_populate(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_id = request.POST.get('post_id', None)
                try:
                    post = Post.objects.get(uuid=post_id)
                except:
                    return JsonResponse({'res': 0})
                from django.db.models import Q
                name = post.user.usertextname.name
                profile_photo = post.user.userphoto.file_50_url()

                if post.has_another_profile:
                    name = post.postprofile.name
                    profile_photo = post.postprofile.file_50_url()
                you_liked = False
                if PostLike.objects.filter(user=request.user, post=post).exists():
                    you_liked = True
                post_chat_read = PostChatRead.objects.filter(post=post, user=request.user).last()
                post_chat = None
                post_chat_last_chat = None
                if post_chat_read is None:
                    try:
                        post_chat = PostChat.objects.filter(post=post).order_by('created')[1]
                    except IndexError:
                        post_chat_last_chat = {'kind': 'start'}
                    if post_chat is not None:
                        if post_chat.kind == POSTCHAT_TEXT:
                            post_chat_last_chat = {'kind': 'text', 'you_say': post_chat.you_say,
                                                   'text': escape(post_chat.postchattext.text)}
                        elif post_chat.kind == POSTCHAT_PHOTO:
                            post_chat_last_chat = {'kind': 'photo', 'you_say': post_chat.you_say,
                                                   'url': post_chat.postchatphoto.file.url}
                else:
                    if post_chat_read.post_chat.kind == POSTCHAT_START:
                        try:
                            post_chat = PostChat.objects.filter(post=post).order_by('created')[1]
                        except IndexError:
                            post_chat_last_chat = {'kind': 'start'}
                        if post_chat is not None:
                            if post_chat.kind == POSTCHAT_TEXT:
                                post_chat_last_chat = {'kind': 'text', 'you_say': post_chat.you_say,
                                                       'text': escape(post_chat.postchattext.text)}
                            elif post_chat.kind == POSTCHAT_PHOTO:
                                post_chat_last_chat = {'kind': 'photo', 'you_say': post_chat.you_say,
                                                       'url': post_chat.postchatphoto.file.url}
                    elif post_chat_read.post_chat.kind == POSTCHAT_TEXT:
                        post_chat = post_chat_read.post_chat
                        post_chat_last_chat = {'kind': 'text', 'you_say': post_chat.you_say,
                                               'text': escape(post_chat.postchattext.text)}
                    elif post_chat_read.post_chat.kind == POSTCHAT_PHOTO:
                        post_chat = post_chat_read.post_chat
                        post_chat_last_chat = {'kind': 'photo', 'you_say': post_chat.you_say,
                                               'url': post_chat.postchatphoto.file.url}

                new = True
                post_chat_last = PostChat.objects.filter(post=post).last()
                post_chat_read_last = PostChatRead.objects.filter(post=post, user=request.user).last()
                if post_chat_read_last is not None:
                    if post_chat_read_last.post_chat == post_chat_last:
                        new = False
                    else:
                        new = True

                user_follow = False
                if Follow.objects.filter(user=request.user, follow=post.user).exists():
                    user_follow = True

                post_follow = False
                if PostFollow.objects.filter(post=post, user=request.user).exists():
                    post_follow = True

                output = {'title': post.title,
                          'desc': post.description,
                          'username': post.user.userusername.username,
                          'user_id': post.user.username,
                          'name': name,
                          'photo': profile_photo,
                          'created': post.post_chat_created,
                          'last_chat': post_chat_last_chat,
                          'absolute_url': post.get_absolute_url(),
                          'id': post.uuid,
                          'like_count': post.postlikecount.count,
                          'you_liked': you_liked,
                          'comment_count': post.postcommentcount.count,
                          'three_comments': post.get_three_comments(),
                          'new': new,
                          'user_follow': user_follow,
                          'post_follow': post_follow,
                          'post_follow_count': post.postfollowcount.count,
                          }
                return JsonResponse({'res': 1, 'set': output})
        else:
            if request.is_ajax():
                post_id = request.POST.get('post_id', None)
                try:
                    post = Post.objects.get(uuid=post_id)
                except:
                    return JsonResponse({'res': 0})
                from django.db.models import Q
                name = post.user.usertextname.name
                profile_photo = post.user.userphoto.file_50_url()

                if post.has_another_profile:
                    name = post.postprofile.name
                    profile_photo = post.postprofile.file_50_url()
                you_liked = False
                post_chat_read = None
                post_chat = None
                post_chat_last_chat = None
                if post_chat_read is None:
                    try:
                        post_chat = PostChat.objects.filter(post=post).order_by('created')[1]
                    except IndexError:
                        post_chat_last_chat = {'kind': 'start'}
                    if post_chat is not None:
                        if post_chat.kind == POSTCHAT_TEXT:
                            post_chat_last_chat = {'kind': 'text', 'you_say': post_chat.you_say,
                                                   'text': escape(post_chat.postchattext.text)}
                        elif post_chat.kind == POSTCHAT_PHOTO:
                            post_chat_last_chat = {'kind': 'photo', 'you_say': post_chat.you_say,
                                                   'url': post_chat.postchatphoto.file.url}

                new = True

                user_follow = False

                post_follow = False

                output = {'title': post.title,
                          'desc': post.description,
                          'username': post.user.userusername.username,
                          'user_id': post.user.username,
                          'name': name,
                          'photo': profile_photo,
                          'created': post.created,
                          'last_chat': post_chat_last_chat,
                          'absolute_url': post.get_absolute_url(),
                          'id': post.uuid,
                          'like_count': post.postlikecount.count,
                          'you_liked': you_liked,
                          'comment_count': post.postcommentcount.count,
                          'three_comments': post.get_three_comments(),
                          'new': new,
                          'user_follow': user_follow,
                          'post_follow': post_follow,
                          'post_follow_count': post.postfollowcount.count,
                          }
                return JsonResponse({'res': 1, 'set': output})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_post_already_read(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_id = request.POST.get('post_id', None)
                try:
                    # post = Post.objects.last()
                    post = Post.objects.get(uuid=post_id)
                except:
                    return JsonResponse({'res': 0})

                try:
                    post_chat_reads = PostChatRead.objects.filter(post_chat__post=post, user=request.user).order_by(
                        '-created')[:20]
                except:
                    return JsonResponse({'res': 0})

                post_chats = [post_chat_read.post_chat for post_chat_read in post_chat_reads]
                output = []
                last_post_chat = None
                if post_chats:
                    first_check = True
                    for post_chat in post_chats:
                        try:
                            count = post_chat.postchatlikecount.count
                        except:
                            count = None
                        # 여기서 you_like 부터 시작해야한다.
                        you_like = False
                        if PostChatLike.objects.filter(user=request.user, post_chat=post_chat).exists():
                            you_like = True
                        sub_output = {
                            'id': post_chat.uuid,
                            'kind': post_chat_kind_converter(post_chat.kind),
                            'like_count': count,
                            'created': post_chat.created,
                            'you_say': post_chat.you_say,
                            'content': post_chat.get_raw_value(),
                            'rest_count': post_chat.postchatrestmessagecount.count,
                            'you_like': you_like
                        }

                        output.append(sub_output)

                        if first_check is True:
                            last_post_chat = post_chat
                        first_check = False

                else:
                    post_chats = PostChat.objects.filter(post=post).order_by('created')[:2]
                    for post_chat in post_chats:

                        try:
                            count = post_chat.postchatlikecount.count
                        except:
                            count = None
                        you_like = False
                        if PostChatLike.objects.filter(user=request.user, post_chat=post_chat).exists():
                            you_like = True
                        sub_output = {
                            'id': post_chat.uuid,
                            'kind': post_chat_kind_converter(post_chat.kind),
                            'like_count': count,
                            'created': post_chat.created,
                            'you_say': post_chat.you_say,
                            'content': post_chat.get_raw_value(),
                            'rest_count': post_chat.postchatrestmessagecount.count,
                            'you_like': you_like
                        }

                        output.insert(0, sub_output)

                        post_chat_read = PostChatRead.objects.create(post=post, post_chat=post_chat, user=request.user)
                        last_post_chat = post_chat

                next = None
                if last_post_chat is not None:

                    try:
                        post_chat_next = PostChat.objects.get(before=last_post_chat)
                    except PostChat.DoesNotExist:
                        post_chat_next = None
                    if post_chat_next is not None:
                        next = {
                            'kind': post_chat_kind_converter(post_chat_next.kind),
                            'content': post_chat_next.get_value(),
                        }

                return JsonResponse({'res': 1, 'set': output, 'next': next})

        else:
            if request.is_ajax():
                post_id = request.POST.get('post_id', None)
                try:
                    # post = Post.objects.last()
                    post = Post.objects.get(uuid=post_id)
                except:
                    return JsonResponse({'res': 0})
                output = []
                post_chats = PostChat.objects.filter(post=post).order_by('created')[:2]

                last_post_chat = None
                for post_chat in post_chats:

                    try:
                        count = post_chat.postchatlikecount.count
                    except:
                        count = None
                    you_like = False
                    sub_output = {
                        'id': post_chat.uuid,
                        'kind': post_chat_kind_converter(post_chat.kind),
                        'like_count': count,
                        'created': post_chat.created,
                        'you_say': post_chat.you_say,
                        'content': post_chat.get_raw_value(),
                        'rest_count': post_chat.postchatrestmessagecount.count,
                        'you_like': you_like
                    }

                    output.insert(0, sub_output)

                    last_post_chat = post_chat

                next = None
                if last_post_chat is not None:

                    try:
                        post_chat_next = PostChat.objects.get(before=last_post_chat)
                    except PostChat.DoesNotExist:
                        post_chat_next = None
                    if post_chat_next is not None:
                        next = {
                            'kind': post_chat_kind_converter(post_chat_next.kind),
                            'content': post_chat_next.get_value(),
                        }

                return JsonResponse({'res': 1, 'set': output, 'next': next})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_post_reading_more_load(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                last_id = request.POST.get('post_chat_before_id', None)
                post_id = request.POST.get('post_id', None)
                try:
                    last_post_chat = PostChat.objects.get(uuid=last_id)
                except:
                    return JsonResponse({'res': 0})

                post_chats = PostChat.objects.filter(Q(post__uuid=post_id) & Q(pk__lt=last_post_chat.pk)).order_by(
                    '-created')[:11]

                output = []
                if post_chats:
                    for post_chat in post_chats:
                        try:
                            count = post_chat.postchatlikecount.count
                        except:
                            count = None
                        # 여기서 you_like 부터 시작해야한다.
                        you_like = False
                        if PostChatLike.objects.filter(user=request.user, post_chat=post_chat).exists():
                            you_like = True
                        sub_output = {
                            'id': post_chat.uuid,
                            'kind': post_chat_kind_converter(post_chat.kind),
                            'like_count': count,
                            'created': post_chat.created,
                            'you_say': post_chat.you_say,
                            'content': post_chat.get_raw_value(),
                            'rest_count': post_chat.postchatrestmessagecount.count,
                            'you_like': you_like
                        }

                        output.append(sub_output)

                return JsonResponse({'res': 1, 'set': output})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_post_chat_next_load(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_chat_id = request.POST.get('post_chat_next_id', None)
                try:
                    post_chat = PostChat.objects.get(uuid=post_chat_id)
                except:
                    return JsonResponse({'res': 0})
                output = []
                next = None
                if post_chat is not None:
                    try:
                        count = post_chat.postchatlikecount.count
                    except:
                        count = None
                    you_like = False
                    if PostChatLike.objects.filter(user=request.user, post_chat=post_chat).exists():
                        you_like = True
                    sub_output = {
                        'id': post_chat.uuid,
                        'kind': post_chat_kind_converter(post_chat.kind),
                        'like_count': count,
                        'created': post_chat.created,
                        'you_say': post_chat.you_say,
                        'content': post_chat.get_raw_value(),
                        'rest_count': post_chat.postchatrestmessagecount.count,
                        'you_like': you_like
                    }
                    post_chat_read = PostChatRead.objects.create(post=post_chat.post, post_chat=post_chat,
                                                                 user=request.user)

                    output.append(sub_output)
                    try:
                        post_chat_next = PostChat.objects.get(before=post_chat)
                    except PostChat.DoesNotExist:
                        post_chat_next = None
                    if post_chat_next is not None:
                        next = {
                            'kind': post_chat_kind_converter(post_chat_next.kind),
                            'content': post_chat_next.get_value(),
                        }

                return JsonResponse({'res': 1, 'set': output, 'next': next})

        else:
            if request.is_ajax():
                post_chat_id = request.POST.get('post_chat_next_id', None)
                try:
                    post_chat = PostChat.objects.get(uuid=post_chat_id)
                except:
                    return JsonResponse({'res': 0})
                output = []
                next = None
                if post_chat is not None:
                    try:
                        count = post_chat.postchatlikecount.count
                    except:
                        count = None
                    you_like = False
                    sub_output = {
                        'id': post_chat.uuid,
                        'kind': post_chat_kind_converter(post_chat.kind),
                        'like_count': count,
                        'created': post_chat.created,
                        'you_say': post_chat.you_say,
                        'content': post_chat.get_raw_value(),
                        'rest_count': post_chat.postchatrestmessagecount.count,
                        'you_like': you_like
                    }

                    output.append(sub_output)
                    try:
                        post_chat_next = PostChat.objects.get(before=post_chat)
                    except PostChat.DoesNotExist:
                        post_chat_next = None
                    if post_chat_next is not None:
                        next = {
                            'kind': post_chat_kind_converter(post_chat_next.kind),
                            'content': post_chat_next.get_value(),
                        }

                return JsonResponse({'res': 1, 'set': output, 'next': next})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_post_chat_like(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_chat_id = request.POST.get('post_chat_id', None)
                try:
                    post_chat = PostChat.objects.get(uuid=post_chat_id)
                except PostChat.DoesNotExist as e:
                    print(e)
                    return JsonResponse({'res': 0})
                try:
                    post_chat_like = PostChatLike.objects.get(post_chat=post_chat, user=request.user)
                except PostChatLike.DoesNotExist:
                    post_chat_like = None

                liked = None
                if post_chat_like is not None:
                    try:
                        with transaction.atomic():
                            post_chat_like.delete()
                            from django.db.models import F
                            post_chat_like_count = post_chat.postchatlikecount
                            post_chat_like_count.count = F('count') - 1
                            post_chat_like_count.save()
                            liked = False
                            # customers = Customer.objects.filter(scoops_ordered__gt=F('store_visits'))
                    except Exception as e:
                        print(e)
                        return JsonResponse({'res': 0})
                else:
                    try:
                        with transaction.atomic():
                            post_chat_like = PostChatLike.objects.create(post_chat=post_chat, user=request.user)
                            from django.db.models import F
                            post_chat_like_count = post_chat.postchatlikecount
                            post_chat_like_count.count = F('count') + 1
                            post_chat_like_count.save()
                            liked = True
                            # customers = Customer.objects.filter(scoops_ordered__gt=F('store_visits'))
                    except Exception as e:
                        print(e)
                        return JsonResponse({'res': 0})

                return JsonResponse({'res': 1, 'liked': liked})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_post_chat_add_rest(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_chat_id = request.POST.get('post_chat_id', None)
                text = request.POST.get('text', None)
                post_chat = None
                try:
                    post_chat = PostChat.objects.get(uuid=post_chat_id)
                except:
                    return JsonResponse({'res': 0})
                post_chat_rest_message = None
                sub_output = None
                if post_chat is not None:
                    post_chat_rest_message = PostChatRestMessage.objects.create(text=text, user=request.user,
                                                                                uuid=uuid.uuid4().hex,
                                                                                post_chat=post_chat)

                    from django.db.models import F
                    post_chat_rest_message_count = post_chat.postchatrestmessagecount
                    post_chat_rest_message_count.count = F('count') + 1
                    post_chat_rest_message_count.save()

                if post_chat_rest_message is not None:
                    sub_output = {
                        'id': post_chat_rest_message.uuid,
                        'name': post_chat_rest_message.user.usertextname.name,
                        'user_id': post_chat_rest_message.user.username,
                        'created': post_chat_rest_message.created,
                        'text': post_chat_rest_message.text,
                        'photo': post_chat_rest_message.user.userphoto.file_50_url()
                    }
                return JsonResponse({'res': 1, 'set': sub_output})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_post_chat_rest_more_load(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_chat_id = request.POST.get('post_chat_id', None)
                last_id = request.POST.get('last_id', None)
                post_chat = None
                try:
                    post_chat = PostChat.objects.get(uuid=post_chat_id)
                except:
                    return JsonResponse({'res': 0})
                post_chat_rest_messages = None
                if last_id == '' and post_chat is not None:
                    post_chat_rest_messages = PostChatRestMessage.objects.filter(post_chat=post_chat).order_by(
                        'created')[:11]
                elif last_id != '' and post_chat is not None:
                    try:
                        last_post_chat_rest_message = PostChatRestMessage.objects.get(uuid=last_id)
                    except:
                        return JsonResponse({'res': 0})

                    post_chat_rest_messages = PostChatRestMessage.objects.filter(
                        Q(post_chat=post_chat) & Q(pk__gt=last_post_chat_rest_message.pk)).order_by('created')[:11]
                count = 0
                next = False
                output = []
                if post_chat_rest_messages is not None:
                    for post_chat_rest_message in post_chat_rest_messages:
                        count = count + 1
                        if count == 11:
                            next = True
                            break
                        you_like = False
                        if PostChatRestMessageLike.objects.filter(user=request.user,
                                                                  post_chat_rest_message=post_chat_rest_message).exists():
                            you_like = True
                        sub_output = {
                            'id': post_chat_rest_message.uuid,
                            'user_id': post_chat_rest_message.user.username,
                            'name': post_chat_rest_message.user.usertextname.name,
                            'username': post_chat_rest_message.user.userusername.username,
                            'text': post_chat_rest_message.text,
                            'created': post_chat_rest_message.created,
                            'like_count': post_chat_rest_message.postchatrestmessagelikecount.count,
                            'photo': post_chat_rest_message.user.userphoto.file_50_url(),
                            'you_like': you_like,
                        }
                        output.append(sub_output)

                return JsonResponse({'res': 1, 'set': output, 'rest_next': next})
        else:
            if request.is_ajax():
                post_chat_id = request.POST.get('post_chat_id', None)
                last_id = request.POST.get('last_id', None)
                post_chat = None
                try:
                    post_chat = PostChat.objects.get(uuid=post_chat_id)
                except:
                    return JsonResponse({'res': 0})
                post_chat_rest_messages = None
                if last_id == '' and post_chat is not None:
                    post_chat_rest_messages = PostChatRestMessage.objects.filter(post_chat=post_chat).order_by(
                        'created')[:11]
                elif last_id != '' and post_chat is not None:
                    try:
                        last_post_chat_rest_message = PostChatRestMessage.objects.get(uuid=last_id)
                    except:
                        return JsonResponse({'res': 0})

                    post_chat_rest_messages = PostChatRestMessage.objects.filter(
                        Q(post_chat=post_chat) & Q(pk__gt=last_post_chat_rest_message.pk)).order_by('created')[:11]
                count = 0
                next = False
                output = []
                if post_chat_rest_messages is not None:
                    for post_chat_rest_message in post_chat_rest_messages:
                        count = count + 1
                        if count == 11:
                            next = True
                            break
                        you_like = False
                        sub_output = {
                            'id': post_chat_rest_message.uuid,
                            'user_id': post_chat_rest_message.user.username,
                            'name': post_chat_rest_message.user.usertextname.name,
                            'username': post_chat_rest_message.user.userusername.username,
                            'text': post_chat_rest_message.text,
                            'created': post_chat_rest_message.created,
                            'like_count': post_chat_rest_message.postchatrestmessagelikecount.count,
                            'photo': post_chat_rest_message.user.userphoto.file_50_url(),
                            'you_like': you_like,
                        }
                        output.append(sub_output)

                return JsonResponse({'res': 1, 'set': output, 'rest_next': next})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_post_chat_rest_like(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                rest_id = request.POST.get('rest_id', None)
                try:
                    post_chat_rest_message = PostChatRestMessage.objects.get(uuid=rest_id)
                except:
                    return JsonResponse({'res': 0})
                try:
                    post_chat_rest_message_like = PostChatRestMessageLike.objects.get(
                        post_chat_rest_message=post_chat_rest_message, user=request.user)
                except PostChatRestMessageLike.DoesNotExist:
                    post_chat_rest_message_like = None

                liked = None
                if post_chat_rest_message_like is not None:
                    try:
                        with transaction.atomic():
                            post_chat_rest_message_like.delete()
                            from django.db.models import F
                            post_chat_rest_message_like_count = post_chat_rest_message.postchatrestmessagelikecount
                            post_chat_rest_message_like_count.count = F('count') - 1
                            post_chat_rest_message_like_count.save()
                            liked = False
                            # customers = Customer.objects.filter(scoops_ordered__gt=F('store_visits'))
                    except Exception:
                        return JsonResponse({'res': 0})
                else:
                    try:
                        with transaction.atomic():
                            post_chat_rest_message_like = PostChatRestMessageLike.objects.create(
                                post_chat_rest_message=post_chat_rest_message, user=request.user)
                            from django.db.models import F
                            post_chat_rest_message_like_count = post_chat_rest_message.postchatrestmessagelikecount
                            post_chat_rest_message_like_count.count = F('count') + 1
                            post_chat_rest_message_like_count.save()
                            liked = True
                            # customers = Customer.objects.filter(scoops_ordered__gt=F('store_visits'))
                    except Exception:
                        return JsonResponse({'res': 0})

                return JsonResponse({'res': 1, 'liked': liked})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_post_chat_rest_delete(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                rest_id = request.POST.get('rest_id', None)
                try:
                    rest_message = PostChatRestMessage.objects.get(uuid=rest_id)
                except PostChatRestMessage.DoesNotExist:
                    return JsonResponse({'res': 0})
                if rest_message is not None:
                    if rest_message.user == request.user or rest_message.post_chat.post.user == request.user:

                        try:
                            with transaction.atomic():
                                rest_message.delete()
                                from django.db.models import F
                                rest_count = rest_message.post_chat.postchatrestmessagecount
                                rest_count.count = F('count') - 1
                                rest_count.save()
                                # customers = Customer.objects.filter(scoops_ordered__gt=F('store_visits'))
                        except Exception:
                            return JsonResponse({'res': 0})
                        return JsonResponse({'res': 1, 'deleted': True})

                return JsonResponse({'res': 2})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_profile_follow(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                chosen_user_id = request.POST.get('user_id', None)
                chosen_user = None
                try:
                    chosen_user = User.objects.get(username=chosen_user_id)
                except User.DoesNotExist:
                    return JsonResponse({'res': 0})

                if chosen_user is not None:
                    # 어이없는 스스로 팔로우 방지
                    if chosen_user == request.user:
                        return JsonResponse({'res': 0})
                    follow = None
                    try:
                        follow = Follow.objects.get(follow=chosen_user, user=request.user)
                    except Follow.DoesNotExist:
                        pass
                    result = None
                    if follow is not None:
                        try:
                            with transaction.atomic():
                                follow.delete()

                                from django.db.models import F
                                following_count = request.user.followingcount
                                following_count.count = F('count') - 1
                                following_count.save()
                                follower_count = chosen_user.followercount
                                follower_count.count = F('count') - 1
                                follower_count.save()
                                result = False

                                # customers = Customer.objects.filter(scoops_ordered__gt=F('store_visits'))
                        except Exception:
                            return JsonResponse({'res': 0})
                    else:
                        try:
                            with transaction.atomic():
                                follow = Follow.objects.create(follow=chosen_user, user=request.user)
                                from django.db.models import F
                                following_count = request.user.followingcount
                                following_count.count = F('count') + 1
                                following_count.save()
                                follower_count = chosen_user.followercount
                                follower_count.count = F('count') + 1
                                follower_count.save()
                                result = True

                                # customers = Customer.objects.filter(scoops_ordered__gt=F('store_visits'))
                        except Exception:
                            return JsonResponse({'res': 0})
                    return JsonResponse({'res': 1, 'result': result})

                return JsonResponse({'res': 2})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_profile_following(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                user_id = request.POST.get('user_id', None)
                next_id = request.POST.get('next_id', None)
                user = None
                try:
                    user = User.objects.get(username=user_id)
                except User.DoesNotExist:
                    pass

                next = None
                output = []
                if user is not None:
                    if next_id == '':
                        followings = Follow.objects.filter(user=user).order_by('created')[:31]
                    else:
                        try:
                            last_following = Follow.objects.get(follow__username=next_id, user=user)
                        except:
                            return JsonResponse({'res': 0})
                        followings = Follow.objects.filter(Q(user=user) & Q(pk__gte=last_following.pk)).order_by(
                            'created')[:31]
                    count = 0
                    for follow in followings:
                        count = count + 1
                        if count == 31:
                            next = follow.follow.username
                            break
                        sub_output = {
                            'username': follow.follow.userusername.username,
                            'photo': follow.follow.userphoto.file_50_url(),
                        }
                        output.append(sub_output)

                return JsonResponse({'res': 1, 'set': output, 'next': next})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_profile_follower(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                user_id = request.POST.get('user_id', None)
                next_id = request.POST.get('next_id', None)
                user = None
                try:
                    user = User.objects.get(username=user_id)
                except User.DoesNotExist:
                    pass

                next = None
                output = []
                if user is not None:
                    if next_id == '':
                        followers = Follow.objects.filter(follow=user).order_by('created')[:31]
                    else:
                        try:

                            last_follower = Follow.objects.get(follow=user, user__username=next_id)
                        except:
                            return JsonResponse({'res': 0})
                        followers = Follow.objects.filter(Q(follow=user) & Q(pk__gte=last_follower.pk)).order_by(
                            'created')[:31]
                    count = 0
                    for follow in followers:
                        count = count + 1
                        if count == 31:
                            next = follow.user.username
                            break
                        sub_output = {
                            'username': follow.user.userusername.username,
                            'photo': follow.user.userphoto.file_50_url(),
                        }
                        output.append(sub_output)

                return JsonResponse({'res': 1, 'set': output, 'next': next})

        return JsonResponse({'res': 2})



@ensure_csrf_cookie
def re_profile_populate(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_id = request.POST.get('post_id', None)
                try:
                    post = Post.objects.get(uuid=post_id)
                except:
                    return JsonResponse({'res': 0})
                from django.db.models import Q
                name = post.user.usertextname.name
                profile_photo = post.user.userphoto.file_50_url()

                if post.has_another_profile:
                    name = post.postprofile.name
                    profile_photo = post.postprofile.file_50_url()
                you_liked = False
                if PostLike.objects.filter(user=request.user, post=post).exists():
                    you_liked = True
                post_chat_read = PostChatRead.objects.filter(post=post, user=request.user).last()
                post_chat = None
                post_chat_last_chat = None
                if post_chat_read is None:
                    try:
                        post_chat = PostChat.objects.filter(post=post).order_by('created')[1]
                    except IndexError:
                        post_chat_last_chat = {'kind': 'start'}
                    if post_chat is not None:
                        if post_chat.kind == POSTCHAT_TEXT:
                            post_chat_last_chat = {'kind': 'text', 'you_say': post_chat.you_say,
                                                   'text': escape(post_chat.postchattext.text)}
                        elif post_chat.kind == POSTCHAT_PHOTO:
                            post_chat_last_chat = {'kind': 'photo', 'you_say': post_chat.you_say,
                                                   'url': post_chat.postchatphoto.file.url}
                else:
                    if post_chat_read.post_chat.kind == POSTCHAT_START:
                        try:
                            post_chat = PostChat.objects.filter(post=post).order_by('created')[1]
                        except IndexError:
                            post_chat_last_chat = {'kind': 'start'}
                        if post_chat is not None:
                            if post_chat.kind == POSTCHAT_TEXT:
                                post_chat_last_chat = {'kind': 'text', 'you_say': post_chat.you_say,
                                                       'text': escape(post_chat.postchattext.text)}
                            elif post_chat.kind == POSTCHAT_PHOTO:
                                post_chat_last_chat = {'kind': 'photo', 'you_say': post_chat.you_say,
                                                       'url': post_chat.postchatphoto.file.url}
                    elif post_chat_read.post_chat.kind == POSTCHAT_TEXT:
                        post_chat = post_chat_read.post_chat
                        post_chat_last_chat = {'kind': 'text', 'you_say': post_chat.you_say,
                                               'text': escape(post_chat.postchattext.text)}
                    elif post_chat_read.post_chat.kind == POSTCHAT_PHOTO:
                        post_chat = post_chat_read.post_chat
                        post_chat_last_chat = {'kind': 'photo', 'you_say': post_chat.you_say,
                                               'url': post_chat.postchatphoto.file.url}

                new = True
                post_chat_last = PostChat.objects.filter(post=post).last()
                post_chat_read_last = PostChatRead.objects.filter(post=post, user=request.user).last()
                if post_chat_read_last is not None:
                    if post_chat_read_last.post_chat == post_chat_last:
                        new = False
                    else:
                        new = True

                user_follow = False
                if Follow.objects.filter(user=request.user, follow=post.user).exists():
                    user_follow = True

                post_follow = False
                if PostFollow.objects.filter(post=post, user=request.user).exists():
                    post_follow = True

                output = {'title': post.title,
                          'desc': post.description,
                          'username': post.user.userusername.username,
                          'user_id': post.user.username,
                          'name': name,
                          'photo': profile_photo,
                          'created': post.post_chat_created,
                          'last_chat': post_chat_last_chat,
                          'absolute_url': post.get_absolute_url(),
                          'id': post.uuid,
                          'like_count': post.postlikecount.count,
                          'you_liked': you_liked,
                          'comment_count': post.postcommentcount.count,
                          'three_comments': post.get_three_comments(),
                          'new': new,
                          'user_follow': user_follow,
                          'post_follow': post_follow,
                          'post_follow_count': post.postfollowcount.count,
                          }
                return JsonResponse({'res': 1, 'set': output})
        else:
            if request.is_ajax():
                post_id = request.POST.get('post_id', None)
                try:
                    post = Post.objects.get(uuid=post_id)
                except:
                    return JsonResponse({'res': 0})
                from django.db.models import Q
                name = post.user.usertextname.name
                profile_photo = post.user.userphoto.file_50_url()

                if post.has_another_profile:
                    name = post.postprofile.name
                    profile_photo = post.postprofile.file_50_url()
                you_liked = False
                post_chat_read = None
                post_chat = None
                post_chat_last_chat = None
                if post_chat_read is None:
                    try:
                        post_chat = PostChat.objects.filter(post=post).order_by('created')[1]
                    except IndexError:
                        post_chat_last_chat = {'kind': 'start'}
                    if post_chat is not None:
                        if post_chat.kind == POSTCHAT_TEXT:
                            post_chat_last_chat = {'kind': 'text', 'you_say': post_chat.you_say,
                                                   'text': escape(post_chat.postchattext.text)}
                        elif post_chat.kind == POSTCHAT_PHOTO:
                            post_chat_last_chat = {'kind': 'photo', 'you_say': post_chat.you_say,
                                                   'url': post_chat.postchatphoto.file.url}

                new = True

                user_follow = False

                post_follow = False

                output = {'title': post.title,
                          'desc': post.description,
                          'username': post.user.userusername.username,
                          'user_id': post.user.username,
                          'name': name,
                          'photo': profile_photo,
                          'created': post.created,
                          'last_chat': post_chat_last_chat,
                          'absolute_url': post.get_absolute_url(),
                          'id': post.uuid,
                          'like_count': post.postlikecount.count,
                          'you_liked': you_liked,
                          'comment_count': post.postcommentcount.count,
                          'three_comments': post.get_three_comments(),
                          'new': new,
                          'user_follow': user_follow,
                          'post_follow': post_follow,
                          'post_follow_count': post.postfollowcount.count,
                          }
                return JsonResponse({'res': 1, 'set': output})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_post_like_list(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_id = request.POST.get('post_id', None)
                next_id = request.POST.get('next_id', None)
                post = None
                try:
                    post = Post.objects.get(uuid=post_id)
                except:
                    return JsonResponse({'res': 1})

                next = None
                output = []
                if post is not None:
                    if next_id == '':
                        likes = PostLike.objects.filter(post=post).order_by('created')[:31]
                    else:
                        try:

                            last_like = PostLike.objects.get(post=post, user__username=next_id)
                        except:
                            return JsonResponse({'res': 0})
                        likes = PostLike.objects.filter(Q(post=post) & Q(pk__gte=last_like.pk)).order_by('created')[:31]
                    count = 0
                    for like in likes:
                        count = count + 1
                        if count == 31:
                            next = like.user.username
                            break
                        sub_output = {
                            'username': like.user.userusername.username,
                            'photo': like.user.userphoto.file_50_url(),
                        }
                        output.append(sub_output)

                return JsonResponse({'res': 1, 'set': output, 'next': next})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_post_chat_like_list(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_chat_id = request.POST.get('post_chat_id', None)
                next_id = request.POST.get('next_id', None)
                post_chat = None
                try:
                    post_chat = PostChat.objects.get(uuid=post_chat_id)
                except:
                    return JsonResponse({'res': 1})

                next = None
                output = []
                if post_chat is not None:
                    if next_id == '':
                        likes = PostChatLike.objects.filter(post_chat=post_chat).order_by('created')[:31]
                    else:
                        try:

                            last_like = PostChatLike.objects.get(post_chat=post_chat, user__username=next_id)
                        except:
                            return JsonResponse({'res': 0})
                        likes = PostChatLike.objects.filter(Q(post_chat=post_chat) & Q(pk__gte=last_like.pk)).order_by(
                            'created')[:31]
                    count = 0
                    for like in likes:
                        count = count + 1
                        if count == 31:
                            next = like.user.username
                            break
                        sub_output = {
                            'username': like.user.userusername.username,
                            'photo': like.user.userphoto.file_50_url(),
                        }
                        output.append(sub_output)

                return JsonResponse({'res': 1, 'set': output, 'next': next})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_post_chat_rest_like_list(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_chat_rest_id = request.POST.get('post_chat_rest_id', None)
                next_id = request.POST.get('next_id', None)
                post_chat_rest_message = None
                try:
                    post_chat_rest_message = PostChatRestMessage.objects.get(uuid=post_chat_rest_id)
                except:
                    return JsonResponse({'res': 0})

                next = None
                output = []
                if post_chat_rest_message is not None:
                    if next_id == '':
                        likes = PostChatRestMessageLike.objects.filter(
                            post_chat_rest_message=post_chat_rest_message).order_by('created')[:31]
                    else:
                        try:

                            last_like = PostChatRestMessageLike.objects.get(
                                post_chat_rest_message=post_chat_rest_message, user__username=next_id)
                        except:
                            return JsonResponse({'res': 0})
                        likes = PostChatRestMessageLike.objects.filter(
                            Q(post_chat_rest_message=post_chat_rest_message) & Q(pk__gte=last_like.pk)).order_by(
                            'created')[:31]
                    count = 0
                    for like in likes:
                        count = count + 1
                        if count == 31:
                            next = like.user.username
                            break
                        sub_output = {
                            'username': like.user.userusername.username,
                            'photo': like.user.userphoto.file_50_url(),
                        }
                        output.append(sub_output)

                return JsonResponse({'res': 1, 'set': output, 'next': next})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_post_follow(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_id = request.POST.get('post_id', None)
                post = None
                try:
                    post = Post.objects.get(uuid=post_id)
                except:
                    return JsonResponse({'res': 0})
                post_follow = None
                try:
                    post_follow = PostFollow.objects.get(post=post, user=request.user)
                except PostFollow.DoesNotExist:
                    post_follow = None

                follow = None
                if post_follow is not None:
                    try:
                        with transaction.atomic():
                            post_follow.delete()
                            from django.db.models import F
                            post_follow_count = post.postfollowcount
                            post_follow_count.count = F('count') - 1
                            post_follow_count.save()
                            follow = False
                            # customers = Customer.objects.filter(scoops_ordered__gt=F('store_visits'))
                    except Exception:
                        return JsonResponse({'res': 0})
                else:
                    try:
                        with transaction.atomic():
                            post_follow = PostFollow.objects.create(post=post, user=request.user)
                            from django.db.models import F
                            post_follow_count = post.postfollowcount
                            post_follow_count.count = F('count') + 1
                            post_follow_count.save()
                            follow = True
                            # customers = Customer.objects.filter(scoops_ordered__gt=F('store_visits'))
                    except Exception:
                        return JsonResponse({'res': 0})

                return JsonResponse({'res': 1, 'follow': follow})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_post_follow_list(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_id = request.POST.get('post_id', None)
                next_id = request.POST.get('next_id', None)
                post = None
                try:
                    post = Post.objects.get(uuid=post_id)
                except:
                    return JsonResponse({'res': 0})

                next = None
                output = []
                post_follows = None
                if post is not None:
                    if next_id == '':
                        post_follows = PostFollow.objects.filter(post=post).order_by('created')[:31]
                    else:
                        try:

                            last_post_follow = PostFollow.objects.get(post=post, user__username=next_id)
                        except:
                            return JsonResponse({'res': 0})
                        post_follows = PostFollow.objects.filter(
                            Q(post=post) & Q(pk__gte=last_post_follow.pk)).order_by('created')[:31]
                    count = 0
                    for post_follow in post_follows:
                        count = count + 1
                        if count == 31:
                            next = post_follow.user.username
                            break
                        sub_output = {
                            'username': post_follow.user.userusername.username,
                            'photo': post_follow.user.userphoto.file_50_url(),
                        }
                        output.append(sub_output)

                return JsonResponse({'res': 1, 'set': output, 'next': next})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_explore_feed(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                last_id = request.POST.get('last_id', None)
                posts = None
                if last_id == '':
                    posts = Post.objects.filter(
                        ~Q(user__is_followed__user=request.user) & Q(is_open=True) & ~Q(user=request.user)).exclude(
                        Q(post_follow__user=request.user)).order_by('-post_chat_created').distinct()[:20]
                else:
                    last_post = None
                    try:
                        last_post = Post.objects.get(uuid=last_id)
                    except Exception as e:
                        print(e)
                        return JsonResponse({'res': 0})
                    posts = Post.objects.filter(~Q(user__is_followed__user=request.user) & Q(is_open=True) & Q(
                        post_chat_created__lte=last_post.post_chat_created) & ~Q(user=request.user)).exclude(
                        Q(post_follow__user=request.user) | Q(uuid=last_id)).order_by('-post_chat_created').distinct()[
                            :20]

                # 여기서 posts 옵션 준다. 20개씩 줄 것이므로 21로 잡는다. #########
                # 여기서 포스트 팔로우 된 건 피드에 뜨지 않게 Q 설정해야한다 .
                ################################
                output = []
                count = 0
                last = None
                post_follow = None
                for post in posts:
                    count = count + 1
                    if count == 20:
                        last = post.uuid
                    sub_output = {
                        'id': post.uuid,
                    }

                    output.append(sub_output)

                return JsonResponse({'res': 1, 'set': output, 'last': last})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_note_all(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                next_id = request.POST.get('next_id', None)
                notices = None
                if next_id == '':
                    notices = Notice.objects.filter(Q(user=request.user)).order_by('-created').distinct()[:31]
                else:
                    next_notice = None
                    try:
                        next_notice = Notice.objects.get(uuid=next_id)
                    except Exception as e:
                        print(e)
                        return JsonResponse({'res': 0})
                    notices = Notice.objects.filter(Q(user=request.user) & Q(pk__lte=next_notice.pk)).order_by(
                        '-created').distinct()[:31]

                # 여기서 posts 옵션 준다. 20개씩 줄 것이므로 21로 잡는다. #########
                # 여기서 포스트 팔로우 된 건 피드에 뜨지 않게 Q 설정해야한다 .
                ################################
                output = []
                count = 0
                next = None
                for notice in notices:
                    count = count + 1
                    if count == 31:
                        next = notice.uuid
                        break
                    sub_output = {
                        'id': notice.uuid,
                        'created': notice.created,
                        'notice_kind': notice.kind,
                        'notice_value': notice.get_value(),
                    }

                    output.append(sub_output)

                return JsonResponse({'res': 1, 'set': output, 'next': next})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_nav_badge_populate(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                try:
                    notice_count = request.user.noticecount.count
                except Exception as e:
                    print(e)
                    return JsonResponse({'res': 0})

                return JsonResponse({'res': 1, 'notice_count': notice_count})

        return JsonResponse({'res': 2})


# ---------------------------------------------------------------------------------------------------------------------------


def url_without_scheme(url):
    if url.startswith('http://www.'):
        url = url.replace('http://www.', '', 1)
    elif url.startswith('http://'):
        url = url.replace('http://', '', 1)
    elif url.startswith('https://www.'):
        url = url.replace('https://www.', '', 1)
    elif url.startswith('https://'):
        url = url.replace('https://', '', 1)
    elif url.startswith('www.'):
        url = url.replace('www.', '', 1)
    else:
        pass
    return url


def get_redirected_url(url):
    import ssl
    context = ssl._create_unverified_context()
    result = None
    try:
        result = urllib.request.urlopen(url, context=context).geturl()
    except Exception as e:
        print(e)
    return result


from threading import Lock

_lock = Lock()


def redirectTest(item):
    r = None
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        }
        try:
            r = requests.get(item, allow_redirects=False, headers=headers)
            # r = requests.head(item, allow_redirects=False, headers=headers)

        except Exception as e:
            print(e)
        if r is not None:
            if r.status_code == 301:
                print('301')
                return {'status': str(r.status_code), 'url': r.url, 'header_location': r.headers['Location']}
            elif r.status_code == 302:
                print('302')
                return {'status': str(r.status_code), 'url': r.url, 'header_location': r.headers['Location']}

                # 이 로케이션이 이상한 곳으로 갈 경우 그것도 테스트.
                # 301과 302는 다르다고 한다.
            elif r.status_code == 405:
                r = requests.get(item, allow_redirects=False, headers=headers)
                print('here')
                return {'status': str(r.status_code), 'url': r.url}
            else:
                return {'status': str(r.status_code), 'url': r.url}
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        pass
    return r


def is_unable_url(url):
    from urllib.parse import urlparse
    import re

    # from urlparse import urlparse  # Python 2
    if not (url.startswith('http://') or url.startswith('https://')):
        url = 'https://' + url

    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    re_match = None
    try:
        re_match = re.match(regex, url)
    except Exception as e:
        print(e)
    if re_match is None:
        return True
        # url 이 아닙니다.
    parsed_uri = urlparse(url)
    url_formatted = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    is_ip = ((url_without_scheme(url_formatted).strip().strip('/')).replace('.', '').replace(':', '')).isdigit()
    is_localhost = (
        (url_without_scheme(url_formatted).strip().strip('/')).replace('.', '').replace(':', '').lower().startswith(
            'localhost'))
    if is_ip or is_localhost:
        return True

    return False
    # localhost 랑 ip는 안 받는다.


def check_success_url(url, o_count, success_list, not_301_redirect_list, user):
    user = user
    if o_count > 30:
        return
    req = None
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }
    is_success = False
    count = 0
    if success_list is None:
        success_list = []
    if not_301_redirect_list is None:
        not_301_redirect_list = []

    while is_success is False:

        count = count + 1
        if count > 10:
            return

        url = url.strip()

        from furl import furl
        furl_obj = furl(url)
        furl_obj.path.normalize()

        url = furl_obj.remove(fragment=True).url
        # url = furl_obj.url

        try:
            req = requests.get(url, allow_redirects=False, headers=headers)
        except Exception as e:
            print('requests error: ' + str(e) + ' at: ' + url)
            return
        if req is not None:
            if req.status_code == 301:
                url = req.headers['Location']
                continue
            elif req.status_code == 302:
                url = req.headers['Location']
                not_301_redirect_list.append(url)
                # 이 로케이션이 이상한 곳으로 갈 경우 그것도 테스트.
                # 301과 302는 다르다고 한다.
                continue
            elif req.status_code == 200:
                discrete_url = None
                no_args_url = None
                import metadata_parser
                # 다음은 어이없게도 daum.net 입력시 301 redirect 가 없다.
                if not any(i.get('url') == req.url for i in success_list):
                    got_url = req.url

                    page = None
                    discrete_url = None

                    try:
                        page = metadata_parser.MetadataParser(url=got_url, search_head_only=False, url_headers=headers)
                    except Exception as e:
                        print(e)
                    no_args_url = furl_obj.remove(args=True, fragment=True).url
                    f = furl(got_url)

                    loc = got_url.replace(f.scheme + '://', '', 1)
                    title = page.get_metadatas('title', strategy=['page'])
                    title = title[0]

                    scheme = f.scheme

                    discrete_loc = None
                    discrete_scheme = None

                    if page is not None:
                        discrete_url = page.get_discrete_url()
                        f_discrete = furl(discrete_url)
                        discrete_loc = discrete_url.replace(f_discrete.scheme + '://', '', 1)
                        discrete_scheme = f_discrete.scheme

                    is_discrete = 'false'
                    if discrete_url == req.url:
                        is_discrete = 'true'

                    not_301_redirect = 'false'
                    if got_url in not_301_redirect_list:
                        not_301_redirect = 'true'

                    user_has_it = 'false'
                    sub_url_object = None
                    try:
                        sub_url_object = SubUrlObject.objects.get(user=user, url_object__loc=loc)
                    except Exception as e:
                        pass
                    if sub_url_object is not None:
                        user_has_it = sub_url_object.uuid
# ________________________________________________
# 이제 여기서 update_url 로 바로 넘어가게 하는 템플릿을 register_url에 만들어라.
                    sub_appender = {'url': got_url,
                                    'loc': loc,
                                    'title': title,
                                    'scheme': scheme,
                                    'is_discrete': is_discrete,
                                    'discrete_loc': discrete_loc,
                                    'discrete_scheme': discrete_scheme,
                                    'in_not_301': not_301_redirect,
                                    'user_has_it': user_has_it
                                    }
                    success_list.append(sub_appender)
                else:
                    return
                o_count = o_count + 1
                # discrete url 체크

                if discrete_url != req.url:
                    check_success_url(discrete_url, o_count, success_list, not_301_redirect_list, user)
                else:
                    pass
                if no_args_url != req.url:
                    check_success_url(no_args_url, o_count, success_list, not_301_redirect_list, user)
                else:
                    pass
                is_success = True
                continue
            else:
                try:
                    url = req.headers['Location']
                    not_301_redirect_list.append(url)

                    print(url)
                except Exception as e:
                    print(e)
                    return
                continue
    return


@ensure_csrf_cookie
def re_check_url(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                url = request.POST.get('url', None)

                if is_unable_url(url):
                    return JsonResponse({'res': 0, 'message': 'unable'})
                has_scheme = True
                if not (url.startswith('https://') or url.startswith('http://')):
                    has_scheme = False

                success_list = []
                not_301_redirect_list = []
                if has_scheme is False:
                    check_success_url('http://' + url, 0, success_list, not_301_redirect_list, request.user)
                    check_success_url('https://' + url, 0, success_list, not_301_redirect_list, request.user)
                else:
                    check_success_url(url, 0, success_list, not_301_redirect_list, request.user)
                return JsonResponse({'res': 1, 'output': success_list, 'init_url': url})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_register_url(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                discrete_loc = request.POST.get('discrete_loc', None)
                discrete_scheme = request.POST.get('discrete_scheme', None)
                in_not_301 = request.POST.get('in_not_301', None)
                is_discrete = request.POST.get('is_discrete', None)
                loc = request.POST.get('loc', None)
                scheme = request.POST.get('scheme', None)
                title_text = request.POST.get('title', None)
                url = request.POST.get('url', None)
                init_url = request.POST.get('init_url', None)
                if discrete_loc is None \
                        or discrete_scheme is None \
                        or in_not_301 is None \
                        or is_discrete is None \
                        or loc is None \
                        or scheme is None \
                        or title_text is None \
                        or url is None:
                    return JsonResponse({'res': 0})
                if discrete_loc == '' \
                        or discrete_scheme == '' \
                        or in_not_301 == '' \
                        or is_discrete == '' \
                        or loc == '' \
                        or scheme == '' \
                        or title_text == '' \
                        or url == '':
                    return JsonResponse({'res': 0})

                if in_not_301 == 'true':
                    in_not_301 = True
                else:
                    in_not_301 = False
                if is_discrete == 'true':
                    is_discrete = True
                else:
                    is_discrete = False

                keyword_list = request.POST.getlist('keyword_list[]')

                url_object = None
                try:
                    url_object = UrlObject.objects.get(loc=loc)
                except Exception as e:
                    pass

                if url_object is not None:
                    if scheme == 'http':
                        url_object.http = True
                        url_object.is_discrete = is_discrete
                        url_object.in_not_301 = in_not_301
                        url_object.discrete_loc = discrete_loc
                        url_object.save()
                    elif scheme == 'https':
                        url_object.https = True
                        url_object.is_discrete = is_discrete
                        url_object.in_not_301 = in_not_301
                        url_object.discrete_loc = discrete_loc
                        url_object.save()
                    title = None
                    try:
                        title = Title.objects.last()
                    except Exception as e:
                        pass
                    if title is not None:
                        if title.text != title_text:
                            title = Title.objects.create(text=title_text, url_object=url_object)
                    else:
                        title = Title.objects.create(text=title_text, url_object=url_object)

                    sub_url_object = None
                    try:
                        sub_url_object = SubUrlObject.objects.get(user=request.user, url_object=url_object)
                    except Exception as e:
                        pass
                    if sub_url_object is None:
                        sub_url_object = SubUrlObject.objects.create(user=request.user,
                                                                     title=title,
                                                                     url_object=url_object,
                                                                     uuid=uuid.uuid4().hex)


                else:
                    # url_object가 없다. 키워드고 뭐고 없음.
                    id = uuid.uuid4().hex
                    if scheme == 'http':
                        url_object = UrlObject.objects.create(loc=loc, http=True, https=False, is_discrete=is_discrete,
                                                              in_not_301=in_not_301, discrete_loc=discrete_loc, uuid=id)
                    elif scheme == 'https':
                        url_object = UrlObject.objects.create(loc=loc, http=False, https=True, is_discrete=is_discrete,
                                                              in_not_301=in_not_301, discrete_loc=discrete_loc, uuid=id)
                    title = Title.objects.create(text=title_text, url_object=url_object)
                    sub_url_object = SubUrlObject.objects.create(user=request.user,
                                                                 title=title,
                                                                 url_object=url_object,
                                                                 uuid=uuid.uuid4().hex)

                sub_url_object_initial_url = SubUrlObjectInitialUrl.objects.create(user=request.user,
                                                                                   url=init_url,
                                                                                   sub_url_object=sub_url_object)

                new_keyword_list = []
                for item in keyword_list:
                    new_keyword_list.append(item.strip())

                for item in new_keyword_list:
                    text = item.replace(" ", "")
                    keyword = Keyword.objects.get_or_create(text=text)

                    url_keyword = None
                    if UrlKeyword.objects.filter(url_object=url_object, keyword=keyword[0]).exists():
                        url_keyword = UrlKeyword.objects.get(url_object=url_object, keyword=keyword[0])
                    else:
                        url_keyword = UrlKeyword.objects.create(url_object=url_object,
                                                                keyword=keyword[0],
                                                                uuid=uuid.uuid4().hex)

                    sub_keyword = SubKeyword.objects.get_or_create(keyword=keyword[0],
                                                                   user=request.user)
                    sub_url_object_sub_keyword = SubUrlObjectSubKeyword.objects.get_or_create(sub_url_object=sub_url_object,
                                                                                              sub_keyword=sub_keyword[0])
                    sub_raw_keyword_count = SubRawKeywordCount.objects.get_or_create(sub_url_object=sub_url_object)
                    if sub_raw_keyword_count[0].count < 31:
                        sub_raw_keyword = SubRawKeyword.objects.get_or_create(text=item,
                                                                              sub_keyword=sub_keyword[0],
                                                                              sub_url_object=sub_url_object,
                                                                              user=request.user)
                return JsonResponse({'res': 1, 'id': sub_url_object.uuid})
        return JsonResponse({'res': 2})

@ensure_csrf_cookie
def re_update_url(request):
    if request.method == "POST":
        if request.user.is_authenticated:

            if request.is_ajax():
                id = request.POST.get('id', None)
                sub_url_object = None
                try:
                    sub_url_object = SubUrlObject.objects.get(uuid=id, user=request.user)
                except Exception as e:
                    return JsonResponse({'res': 0})
                sub_raw_keywords = SubRawKeyword.objects.filter(sub_url_object=sub_url_object).order_by('created')

                keyword_output = []
                for item in sub_raw_keywords:
                    keyword_output.append(item.text)

                url_object = sub_url_object.url_object
                title = sub_url_object.title.text

                url = None
                scheme = None
                if url_object.https is True:
                    scheme = 'https://'
                elif url_object.http is True:
                    scheme = 'http://'
                url = scheme + url_object.loc
                return JsonResponse({'res': 1, 'keyword_output': keyword_output, 'title': title, 'url': url})
        return JsonResponse({'res': 2})

@ensure_csrf_cookie
def re_refresh_url(request):
    if request.method == "POST":
        if request.user.is_authenticated:

            if request.is_ajax():
                url = request.POST.get('url', None)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
                }
                try:
                    req = requests.get(url, allow_redirects=False, headers=headers)
                except Exception as e:
                    print('requests error: ' + str(e) + ' at: ' + url)
                    return JsonResponse({'res': 0})
                import metadata_parser
                try:
                    page = metadata_parser.MetadataParser(url=url, search_head_only=False, url_headers=headers)
                except Exception as e:
                    print(e)
                    return JsonResponse({'res': 0})
                status_code = req.status_code
                title = page.get_metadatas('title', strategy=['page'])
                title = title[0]

                return JsonResponse({'res': 1, 'status_code': status_code, 'title': title})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_update_complete_url(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                id = request.POST.get('id', None)
                refresh = request.POST.get('refresh', None)
                sub_url_object = None
                try:
                    sub_url_object = SubUrlObject.objects.get(uuid=id)
                except Exception as e:
                    return JsonResponse({'res': 0})

                url_object = sub_url_object.url_object

                if refresh == 'true':
                    status_code = request.POST.get('status_code', None)
                    title_text = request.POST.get('title', None)
                    title = None
                    if title_text != url_object.title_set.last().text:
                        title = Title.objects.create(text=title_text,
                                                     url_object=url_object,
                                                     status_code=status_code)
                    else:
                        title = url_object.title_set.last()

                    if title is not None:
                        sub_url_object.title = title
                        sub_url_object.save()

                keyword_list = request.POST.getlist('keyword_list[]')

                new_keyword_list = []

                for item in keyword_list:
                    new_keyword_list.append(item.strip())

                for item in new_keyword_list:
                    text = item.replace(" ", "")
                    keyword = Keyword.objects.get_or_create(text=text)

                    url_keyword = None
                    if UrlKeyword.objects.filter(url_object=url_object, keyword=keyword[0]).exists():
                        url_keyword = UrlKeyword.objects.get(url_object=url_object, keyword=keyword[0])
                    else:
                        url_keyword = UrlKeyword.objects.create(url_object=url_object,
                                                                keyword=keyword[0],
                                                                uuid=uuid.uuid4().hex)

                    sub_keyword = SubKeyword.objects.get_or_create(keyword=keyword[0],
                                                                   user=request.user)
                    sub_url_object_sub_keyword = SubUrlObjectSubKeyword.objects.get_or_create(sub_url_object=sub_url_object,
                                                                                              sub_keyword=sub_keyword[0])
                    sub_raw_keyword_count = SubRawKeywordCount.objects.get_or_create(sub_url_object=sub_url_object)
                    if sub_raw_keyword_count[0].count < 31:
                        sub_raw_keyword = SubRawKeyword.objects.get_or_create(text=item,
                                                                              sub_keyword=sub_keyword[0],
                                                                              sub_url_object=sub_url_object,
                                                                              user=request.user)
                delete_list = request.POST.getlist('delete_list[]')
                new_delete_list = []
                for item in delete_list:
                    new_delete_list.append(item.strip())

                for item in new_delete_list:
                    text = item.replace(" ", "")
                    sub_raw_keyword = None
                    try:
                        sub_raw_keyword = SubRawKeyword.objects.get(text=item,
                                                                    sub_url_object=sub_url_object,
                                                                    user=request.user)
                    except Exception as e:
                        pass
                    if sub_raw_keyword is not None:
                        sub_raw_keyword.delete()
                return JsonResponse({'res': 1})
        return JsonResponse({'res': 2})

'''
print('accepted url: '+url)
print('redirected_url: '+redirected_url)
import re
regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)
try:
    print('re.match result: ' + re.match(regex, url))
except Exception as e:
    print(e)

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}


print('here')


# url_re = re.compile(r"https?://(www\.)?")

# dom_raw = url_re.sub('',
#                   url).replace(
#     " ", "").strip(
#     '/')

# dom = [dom_raw]
# print(dom)

def concatenate_url(url_item):
    scheme_list = ['http://www.', 'http://', 'https://www.', 'https://']
    for item in scheme_list:
        made_item = item + url_item
        #		print domTest
        redirectTest(made_item)

concatenate_url(url)
print('Done')
import metadata_parser

# 위에서 200이건 300이건 301이건 302 이건 뽑힌 것에서 메타데이터 파싱을 진행해야 한다.
# 티스토리 캐노니컬 주소 아닌 곳에서 어떻게 리스폰스가 오는지 확인하라. 그것도 200이면 그걸 고려해야하고
# 대표주소 아닐 경우 200 안 오면 그것을 고려해야 한다.
# moneycake.tistory.com/43 여기에 요청했을 시 왜 403인데도 제대로 작동하지 않는지 확인해봐야한다.
page = metadata_parser.MetadataParser(url=url, search_head_only=False, url_headers=headers)
print('-----------------')
print('discrete url: ' + page.get_discrete_url())
print('title :' + page.get_metadata('title'))
print('description: ' + page.get_metadata('description'))
# 사주포춘보고 타이틀, meta title, 그다음 meta description
print('title og: ' + page.get_metadatas('title', strategy=['og', ]))
print('title og, page, dc' + page.get_metadatas('title', strategy=['og', 'page', 'dc', ]))
print('----------get_redirect_url: ' + get_redirected_url(url))
'''


def test10(request):
    if request.method == 'POST':
        if request.is_ajax():
            ajax_url = request.POST.get('ajax_url', None)
            refresh_url = request.POST.get('refresh_url', None)

            '''

            a = 'http://www.cwi.nl:80/%7Eguido/Python.html'
            b = '/create/new/'
            c = 532
            d = u'dkakasdkjdjakdjadjfalskdjfalk'
            f1 = 'http://localhost'
            f2 = 'localhost:8000'
            print(re.match(regex, "http://www.example.com"))
            print(re.match(regex, "example.com"))
            print('-----')
            print(re.match(regex, a))
            print(re.match(regex, b))
            url = "https://goo.gl/7Gt5nQ"
            url2 = "http://f-st.co/THHI6hC"
            url_refresh_sample = "http://www.isthe.com/chongo/tech/comp/cgi/redirect.html"
            url_google = "http://google.com"
            redirect_url = get_redirected_url(url_refresh_sample)
            print(redirect_url)
            ssl._create_default_https_context = ssl._create_unverified_context
            html = urllib.request.urlopen(ajax_url)
            bs_object = BeautifulSoup(html.read(), "html.parser")
            bs_refresh = bs_object.find('link', attrs={'rel': 'canonical'})
            # bs_refresh = bs_object.find('meta', attrs={'http-equiv': 'Refresh'})

            print(bs_refresh)
            #refresh 랑 Refresh 구별해야함 그리고 smtp, ftp 그외 는 따로 분류할수도 있어야함.
            # bs_refresh_content = bs_refresh['content']
            # print(bs_refresh_content)
            # got_url = bs_refresh_content.partition('=')[2]
            # print(got_url)

            bs_pretty = bs_refresh.prettify()
            '''
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
            }

            try:
                r = requests.head('http://moneycake.tistory.com/43', allow_redirects=False, headers=headers)
                print(r.status_code)
            except requests.exceptions.RequestException as e:
                pass

            return JsonResponse({'success': 'yeah'})
    else:
        return render(request, 'testapp/test10.html')


import requests


def strip_scheme(url):
    parsed = urlparse(url)
    scheme = "%s://" % parsed.scheme
    return parsed.geturl().replace(scheme, '', 1)

# 301이면 어디로 가는지 확인하고 http랑 https 다 되면 https를 추천하는 방향으로.

# That's it!


# localhost, http:///change/new/, 이런거 확인. 그리고 줄임 주소 변경 여부 확인. get_current_url 이용

@ensure_csrf_cookie
def re_profile_suobj(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                chosen_user_id = request.POST.get('chosen_user_id', None)
                last_id = request.POST.get('last_suobj_id', None)
                user = None
                try:
                    user = User.objects.get(username=chosen_user_id)
                except Exception as e:
                    print(e)
                    return JsonResponse({'res': 0})
                suobjs = None

                if last_id == '':
                    suobjs = SubUrlObject.objects.filter(Q(user=user)).order_by('-created').distinct()[:20]
                else:
                    last_suojs = None
                    try:
                        last_suojs = SubUrlObject.objects.get(uuid=last_id)
                    except Exception as e:
                        print(e)

                        return JsonResponse({'res': 0})
                    if last_suojs is not None:
                        suobjs = SubUrlObject.objects.filter(
                            Q(user=user) & Q(pk_lt=last_suojs.pk)).order_by('-created').distinct()[:20]

                # 이제 리스트 만드는 코드가 필요하다. #########

                # filter(Q(post__uuid=post_id) & Q(pk__lt=last_post_chat.pk))
                ################################
                output = []
                count = 0
                last = None
                sub_output = None
                for suobj in suobjs:
                    count = count + 1
                    if count == 20:
                        last = suobj.uuid

                    sub_output = {
                        'id': suobj.uuid,
                    }

                    output.append(sub_output)

                return JsonResponse({'res': 1, 'output': output, 'last': last})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_suobj_populate(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                suobj_id = request.POST.get('suobj_id', None)
                suobj = None
                try:
                    suobj = SubUrlObject.objects.get(uuid=suobj_id)
                except Exception as e:
                    print(e)
                    return JsonResponse({'res': 0})
                ################################
                sub_raw_keywords = SubRawKeyword.objects.filter(sub_url_object=suobj)
                srk_output = []
                for sub_raw_keyword in sub_raw_keywords:
                    srk_output.append(sub_raw_keyword.text)

                output = {
                    'user_id': suobj.user.username,
                    'username': suobj.user.userusername.username,
                    'title': suobj.title.text,
                    'created': suobj.created,
                    'loc': suobj.url_object.loc,
                    'url': suobj.url_object.get_url(),
                    'srk_output': srk_output,
                    'url_id': suobj.url_object.uuid,
                    'suobj_id': suobj.uuid,
                }
                # {'user_id', 'username', 'gross(포스트의)', 'date(포스트의)', 'created', 'obj_id',
                #  ['comment_username', 'comment_text', 'comment_user_id', 'comment_created', 'comment_id']}

                return JsonResponse({'res': 1, 'output': output})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_bridge_add(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                chosen_user_id = request.POST.get('user_id', None)
                chosen_user = None
                try:
                    chosen_user = User.objects.get(username=chosen_user_id)
                except User.DoesNotExist:
                    return JsonResponse({'res': 0})

                if chosen_user is not None:
                    # 어이없는 스스로 팔로우 방지
                    if chosen_user == request.user:
                        return JsonResponse({'res': 0})
                    bridge = None
                    try:
                        bridge = Bridge.objects.get(bridge=chosen_user, user=request.user)
                    except Bridge.DoesNotExist:
                        pass
                    result = None
                    if bridge is not None:
                        try:
                            with transaction.atomic():
                                bridge.delete()

                                from django.db.models import F
                                bridging_count = request.user.bridgingcount
                                bridging_count.count = F('count') - 1
                                bridging_count.save()
                                bridger_count = chosen_user.bridgercount
                                bridger_count.count = F('count') - 1
                                bridger_count.save()
                                result = False

                                # customers = Customer.objects.filter(scoops_ordered__gt=F('store_visits'))
                        except Exception:
                            return JsonResponse({'res': 0})
                    else:
                        try:
                            with transaction.atomic():
                                bridge = Bridge.objects.create(bridge=chosen_user, user=request.user)
                                from django.db.models import F
                                bridging_count = request.user.bridgingcount
                                bridging_count.count = F('count') + 1
                                bridging_count.save()
                                bridger_count = chosen_user.bridgercount
                                bridger_count.count = F('count') + 1
                                bridger_count.save()
                                result = True

                                # customers = Customer.objects.filter(scoops_ordered__gt=F('store_visits'))
                        except Exception:
                            return JsonResponse({'res': 0})
                    return JsonResponse({'res': 1, 'result': result})

                return JsonResponse({'res': 2})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_bridging_list(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                user_id = request.POST.get('user_id', None)
                next_id = request.POST.get('next_user_id', None)
                user = None
                try:
                    user = User.objects.get(username=user_id)
                except User.DoesNotExist:
                    return JsonResponse({'res': 0})


                next = None
                output = []
                if user is not None:
                    if next_id == '':
                        bridgings = Bridge.objects.filter(user=user).order_by('created')[:31]
                    else:
                        try:
                            last_bridging = Bridge.objects.get(bridge__username=next_id, user=user)
                        except:
                            return JsonResponse({'res': 0})
                        bridgings = Bridge.objects.filter(Q(user=user) & Q(pk__gte=last_bridging.pk)).order_by('created')[:31]
                    count = 0
                    for bridge in bridgings:
                        count = count+1
                        if count == 31:
                            next = bridge.bridge.username
                            break
                        sub_output = {
                            'username': bridge.bridge.userusername.username,
                            'photo': bridge.bridge.userphoto.file_50_url(),
                        }
                        output.append(sub_output)

                return JsonResponse({'res': 1, 'output': output, 'next':next})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_bridger_list(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                user_id = request.POST.get('user_id', None)
                next_id = request.POST.get('next_user_id', None)
                user = None
                try:
                    user = User.objects.get(username=user_id)
                except User.DoesNotExist:
                    return JsonResponse({'res': 0})

                next = None
                output = []
                if user is not None:
                    if next_id == '':
                        bridgers = Bridge.objects.filter(bridge=user).order_by('created')[:31]
                    else:
                        try:
                            last_bridger = Bridge.objects.get(bridge=user, user__username=next_id)
                        except Exception as e:
                            return JsonResponse({'res': 0})
                        bridgers = Bridge.objects.filter(Q(bridge=user) & Q(pk__gte=last_bridger.pk)).order_by('created')[:31]
                    count = 0
                    for bridge in bridgers:
                        count = count+1
                        if count == 31:
                            next = bridge.user.username
                            break
                        sub_output = {
                            'username': bridge.user.userusername.username,
                            'photo': bridge.user.userphoto.file_50_url(),
                        }
                        output.append(sub_output)

                return JsonResponse({'res': 1, 'output': output, 'next': next})

        return JsonResponse({'res': 2})

@ensure_csrf_cookie
def re_url_populate(request):
    if request.method == "POST":
        if request.is_ajax():
            url_object_id = request.POST.get('url_id', None)
            url_object = None
            try:
                url_object = UrlObject.objects.get(uuid=url_object_id)
            except Exception as e:
                print(e)
                return JsonResponse({'res': 0})

            return JsonResponse({'res': 1, 'full_url': url_object.get_url(), 'title': url_object.title_set.last().text})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_url_keyword(request):
    if request.method == "POST":
        if request.is_ajax():
            url_id = request.POST.get('url_id', None)
            last_id = request.POST.get('last_id', None)
            url_object = None
            try:
                url_object = UrlObject.objects.get(uuid=url_id)
            except Exception as e:
                return JsonResponse({'res': 0})

            url_keywords = None
            if last_id == '':
                url_keywords = UrlKeyword.objects.filter(url_object=url_object).order_by('up_count')[:30]
            else:
                last_url_keyword = None
                try:
                    last_url_keyword = UrlKeyword.objects.get(uuid=last_id)
                except Exception as e:
                    return JsonResponse({'res': 0})
                url_keywords = UrlKeyword.objects.filter(
                    Q(url_object=url_object) & Q(up_count__lte=last_url_keyword.up_count)
                ).exclude(uuid=last_id).order_by('up_count')[:30]

            output = []
            count = 0
            last = None

            for url_keyword in url_keywords:
                count = count+1
                if count == 30:
                    last = url_keyword.uuid
                # 로그인된 상태
                register = 'false'
                if UrlKeywordRegister.objects.filter(user=request.user, url_keyword=url_keyword).exists():
                    register = 'true'

                up = 'false'
                if UrlKeywordUp.objects.filter(user=request.user, url_keyword=url_keyword).exists():
                    up = 'true'

                down = 'false'
                if UrlKeywordDown.objects.filter(user=request.user, url_keyword=url_keyword).exists():
                    down = 'true'
                sub_output = {
                    'keyword': url_keyword.keyword.text,
                    'keyword_id': url_keyword.uuid,
                    'reg_count': url_keyword.register_count,
                    'up_count': url_keyword.up_count,
                    'down_count': url_keyword.down_count,
                    'register': register,
                    'up': up,
                    'down': down
                }
                output.append(sub_output)

            return JsonResponse({'res': 1, 'output': output, 'last': last})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_url_keyword_up(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                url_keyword_id = request.POST.get('url_keyword_id', None)
                url_keyword = None
                try:
                    url_keyword = UrlKeyword.objects.get(uuid=url_keyword_id)
                except Exception as e:
                    return JsonResponse({'res': 0})
                url_keyword_up = None
                try:
                    url_keyword_up = UrlKeywordUp.objects.get(user=request.user, url_keyword=url_keyword)
                except Exception as e:
                    pass
                if url_keyword_up is not None:
                    url_keyword_up.delete()
                    return JsonResponse({'res': 1, 'result': 'cancel'})
                else:
                    url_keyword_up = UrlKeywordUp.objects.create(user=request.user, url_keyword=url_keyword)
                    return JsonResponse({'res': 1, 'result': 'up'})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_url_keyword_down(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                url_keyword_id = request.POST.get('url_keyword_id', None)
                url_keyword = None
                try:
                    url_keyword = UrlKeyword.objects.get(uuid=url_keyword_id)
                except Exception as e:
                    return JsonResponse({'res': 0})
                url_keyword_down = None
                try:
                    url_keyword_down = UrlKeywordDown.objects.get(user=request.user, url_keyword=url_keyword)
                except Exception as e:
                    pass
                if url_keyword_down is not None:
                    url_keyword_down.delete()
                    return JsonResponse({'res': 1, 'result': 'cancel'})
                else:
                    url_keyword_down = UrlKeywordDown.objects.create(user=request.user, url_keyword=url_keyword)
                    return JsonResponse({'res': 1, 'result': 'down'})

        return JsonResponse({'res': 2})

@ensure_csrf_cookie
def re_profile_suobj_delete(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                suobj_id = request.POST.get('suobj_id', None)
                suobj = None
                try:
                    suobj = SubUrlObject.objects.get(uuid=suobj_id, user=request.user)
                except Exception as e:
                    print(e)
                    return JsonResponse({'res': 0})
                if suobj is not None:
                    suobj.delete()

                return JsonResponse({'res': 1})

        return JsonResponse({'res': 2})



@ensure_csrf_cookie
def re_search_all(request):
    if request.method == "POST":
        if request.is_ajax():
            search_word = request.POST.get('search_word', None)

            user_output = []
            users = User.objects.filter(Q(userusername__username__icontains=search_word)
                                        | Q(usertextname__name__icontains=search_word)).order_by(
                '-userusername__created').distinct()[:10]

            for user in users:
                sub_output = {
                    'username': user.userusername.username,
                    'user_text_name': user.usertextname.name,
                }

                user_output.append(sub_output)

            suobj_output = []
            if request.user.is_authenticated:

                suobjs = SubUrlObject.objects.filter((Q(user__is_bridged__user=request.user) | Q(user=request.user)) &
                                                     (Q(user__userusername__username__icontains=search_word)
                                                     | Q(title__text__icontains=search_word)
                                                     | Q(suburlobjectsubkeyword__sub_keyword__keyword__text__icontains=
                                                         search_word)
                                                     | Q(user__usertextname__name__icontains=search_word))).order_by(
                    '-created').distinct()[:11]
            else:
                suobjs = SubUrlObject.objects.none()

            for suobj in suobjs:
                sub_raw_keywords = SubRawKeyword.objects.filter(sub_url_object=suobj).order_by('created')[:5]
                sub_raw_keywords_output = []
                for sub_raw_keyword in sub_raw_keywords:
                    sub_raw_keywords_output.append(sub_raw_keyword.text)
                sub_output = {
                    'username': suobj.user.userusername.username,
                    'id': suobj.uuid,
                    'url': suobj.url_object.get_url(),
                    'keyword_output': sub_raw_keywords_output
                }

                suobj_output.append(sub_output)

            keyword_output = []
            from django.db.models.functions import Length

            keywords = Keyword.objects.filter(text__icontains=search_word).order_by(Length('text').asc())[:10]
            for keyword in keywords:
                keyword_output.append(keyword.text)

            url_output = []
            url_objects = UrlObject.objects.filter(Q(urlkeyword__keyword__text__icontains=search_word)).order_by(
                'urlkeyword__up_count')[:10]
            for url_object in url_objects:
                url_output.append(url_object.uuid)

            return JsonResponse({'res': 1,
                                 'user_output': user_output,
                                 'bridge_output': suobj_output,
                                 'keyword_output': keyword_output,
                                 'url_output': url_output})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_search_user(request):
    if request.method == "POST":
        if request.is_ajax():
            search_word = request.POST.get('search_word', None)
            end_id = request.POST.get('end_id', None)
            step = 20
            if end_id == '':
                users = User.objects.filter(Q(userusername__username__icontains=search_word)
                                            | Q(usertextname__name__icontains=search_word)).order_by(
                    '-userusername__created').distinct()[:step]
            else:
                end_user = None
                try:
                    end_user = User.objects.get(username=end_id)
                except Exception as e:
                    print(e)
                    return JsonResponse({'res': 0})

                users = User.objects.filter((Q(userusername__username__icontains=search_word)
                                            | Q(usertextname__name__icontains=search_word))
                                            & Q(pk__lt=end_user.pk)).order_by(
                    '-userusername__created').distinct()[:step]
            output = []
            count = 0
            end = None
            for user in users:
                count = count + 1
                if count == step:
                    end = user.username
                sub_output = {
                    'username': user.userusername.username,
                    'user_photo': user.userphoto.file_50_url(),
                    'user_text_name': escape(user.usertextname.name),
                }

                output.append(sub_output)

            return JsonResponse({'res': 1,
                                 'output': output,
                                 'end': end})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_search_bridge(request):
    if request.method == "POST":
        if request.is_ajax():
            search_word = request.POST.get('search_word', None)
            end_id = request.POST.get('end_id', None)
            step = 10
            sub_raw_keyword_step = 5

            if request.user.is_authenticated:
                if end_id == '':

                    suobjs = SubUrlObject.objects.filter(
                        (Q(user__is_bridged__user=request.user) | Q(user=request.user)) &
                        (Q(user__userusername__username__icontains=search_word)
                         | Q(title__text__icontains=search_word)
                         | Q(suburlobjectsubkeyword__sub_keyword__keyword__text__icontains=search_word)
                         | Q(user__usertextname__name__icontains=search_word))).order_by(
                        '-created').distinct()[:step]
                else:
                    try:
                        end_suobjs = SubUrlObject.objects.get(uuid=end_id)
                    except Exception as e:
                        print(e)
                        return JsonResponse({'res': 0})
                    suobjs = SubUrlObject.objects.filter(
                        ((Q(user__is_bridged__user=request.user) | Q(user=request.user)) &
                         (Q(user__userusername__username__icontains=search_word)
                         | Q(title__text__icontains=search_word)
                         | Q(suburlobjectsubkeyword__sub_keyword__keyword__text__icontains=
                             search_word)
                         | Q(user__usertextname__name__icontains=search_word)))
                        & Q(pk__lt=end_suobjs.pk)).order_by(
                        '-created').distinct()[:step]
            else:
                suobjs = SubUrlObject.objects.none()

            output = []
            count = 0
            end = None
            for suobj in suobjs:
                count = count + 1
                if count == step:
                    end = suobj.uuid
                sub_raw_keywords = SubRawKeyword.objects.filter(
                    sub_url_object=suobj).order_by('created')[:sub_raw_keyword_step]
                sub_raw_keywords_output = []
                for sub_raw_keyword in sub_raw_keywords:
                    sub_raw_keywords_output.append(sub_raw_keyword.text)
                sub_output = {
                    'username': suobj.user.userusername.username,
                    'id': suobj.uuid,
                    'url': suobj.url_object.get_url(),
                    'keyword_output': sub_raw_keywords_output
                }

                output.append(sub_output)

            return JsonResponse({'res': 1,
                                 'output': output,
                                 'end': end})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_search_keyword(request):
    if request.method == "POST":
        if request.is_ajax():
            search_word = request.POST.get('search_word', None)
            order = request.POST.get('order', None)
            order = int(order)
            step = 10

            from django.db.models.functions import Length

            keywords = Keyword.objects.filter(
                text__icontains=search_word).order_by(Length('text').asc())[order:order + step]

            end = 'false'
            if keywords.count() < step:
                end = 'true'

            output = []

            for keyword in keywords:
                output.append(keyword.text)

            return JsonResponse({'res': 1,
                                 'output': output,
                                 'order': order + step,
                                 'end': end})

        return JsonResponse({'res': 2})

@ensure_csrf_cookie
def re_search_url(request):
    if request.method == "POST":
        if request.is_ajax():
            search_word = request.POST.get('search_word', None)
            order = request.POST.get('order', None)
            order = int(order)
            step = 10
            url_objects = UrlObject.objects.filter(Q(urlkeyword__keyword__text__icontains=search_word)).order_by(
                'urlkeyword__up_count')[order:order + step]

            end = 'false'
            if url_objects.count() < step:
                end = 'true'

            output = []
            for url_object in url_objects:
                output.append(url_object.uuid)

            return JsonResponse({'res': 1,
                                 'output': output,
                                 'order': order + step,
                                 'end': end})

        return JsonResponse({'res': 2})

