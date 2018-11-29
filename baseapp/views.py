from django.shortcuts import render, redirect, reverse
from .forms import PostCreateForm
from relation.models import *
from object.models import *
from object.numbers import *
from notice.models import *
from django.db.models import Q
from django.db import transaction
import uuid

from django.utils.timezone import now, timedelta

# Create your views here.





def note_all(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            try:
                with transaction.atomic():
                    notices_update = Notice.objects.filter(Q(user=request.user) & Q(checked=False)).update(
                        checked=True)
                    notice_count = request.user.noticecount
                    notice_count.count = 0
                    notice_count.save()
            except Exception as e:
                print(e)
                pass
            return render(request, 'baseapp/note_all.html')
        else:
            return redirect(reverse('baseapp:main_create_log_in'))





def register_url(request):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return redirect(reverse('baseapp:main_create_log_in'))
        return render(request, 'baseapp/register_url.html')


def update_url(request, uuid):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return redirect(reverse('baseapp:main_create_log_in'))
        sub_url_object = None
        try:
            sub_url_object = SubUrlObject.objects.get(uuid=uuid, user=request.user)
        except Exception as e:
            return redirect(reverse('baseapp:main_create_log_in'))
        return render(request, 'baseapp/update_url.html', {'id': uuid})


def user_profile(request, user_username):
    if request.method == "GET":
        if request.user.is_authenticated:
            user = None
            try:
                chosen_user = User.objects.get(userusername__username=user_username)
            except:
                return render(request, '404.html')
            if chosen_user is not None:
                bridging = None
                if Bridge.objects.filter(user=request.user, bridge=chosen_user).exists():
                    bridging = True

                return render(request, 'baseapp/user_profile.html', {'chosen_user': chosen_user, 'bridging': bridging})
        else:
            user = None
            try:
                chosen_user = User.objects.get(userusername__username=user_username)
            except:
                return render(request, '404.html')
            if chosen_user is not None:
                bridging = None
                return render(request, 'baseapp/user_profile.html',
                              {'chosen_user': chosen_user, 'bridging': bridging})


def suobj(request, uuid):
    if request.method == "GET":
        suobj = None
        try:
            suobj = SubUrlObject.objects.get(uuid=uuid)
        except:
            return render(request, '404.html')
        if suobj is not None:
            return render(request, 'baseapp/suobj.html', {'id': uuid})

        return render(request, '404.html')


def url(request, uuid):
    if request.method == "GET":
        url_object = None
        try:
            url_object = UrlObject.objects.get(uuid=uuid)
        except:
            return render(request, '404.html')
        if url_object is not None:
            return render(request, 'baseapp/url.html', {'url_object':url_object, 'id': uuid})

        return render(request, '404.html')




def explore_feed(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return render(request, 'baseapp/user_feed.html')
        else:
            return redirect(reverse('baseapp:main_create_log_in'))


def search_all(request):
    if request.method == "GET":
        q = request.GET.get('q', None)
        if q is None:
            q = ''
        word = q
        return render(request, 'baseapp/search_all.html', {'word': word})

# 브릿지 검색아래 제네럴 검색


def search_user(request):
    if request.method == "GET":
        q = request.GET.get('q', None)
        if q is None:
            q = ''
        word = q
        return render(request, 'baseapp/search_user.html', {'word': word})


def search_bridge(request):
    if request.method == "GET":
        q = request.GET.get('q', None)
        print(q)
        if q is None:
            q = ''
        word = q
        return render(request, 'baseapp/search_bridge.html', {'word': word})


def search_keyword(request):
    if request.method == "GET":
        q = request.GET.get('q', None)
        if q is None:
            q = ''
        word = q
        return render(request, 'baseapp/search_keyword.html', {'word': word})


def search_url(request):
    if request.method == "GET":
        q = request.GET.get('q', None)
        if q is None:
            q = ''
        word = q
        return render(request, 'baseapp/search_url.html', {'word': word})