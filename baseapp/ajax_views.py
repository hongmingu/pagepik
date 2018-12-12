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
from relation.models import *
from notice.models import *
from .models import *
from django.contrib.auth import update_session_auth_hash
from django.utils.html import escape, _js_escapes, normalize_newlines
from object.numbers import *


# Create your models here.
# 좋아요 비공개 할 수 있게
# 챗스톡, 페이지픽, 임플린, 챗카부 순으로 만들자.

# ---------------------------------------------------------------------------------------------------------------------------


def url_without_scheme(url):
    if url.startswith('http://'):
        url = url.replace('http://', '', 1)
    elif url.startswith('https://'):
        url = url.replace('https://', '', 1)
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
    https_www = 'https://www.macawl.'
    https = 'https://macawl.'
    http_www = 'http://www.macawl.'
    http = 'http://macawl.'
    if url.startswith(https_www) or url.startswith(https) or url.startswith(http_www) or url.startswith(http):
        return True

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
    if o_count > 100:
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
                        return

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
                if len(keyword_list) == 0:
                    return JsonResponse({'res': 0})

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
                delete_list = request.POST.getlist('delete_list[]')

                if len(keyword_list) <= len(delete_list):
                    return JsonResponse({'res': 0})
                if len(keyword_list) == 0:
                    return JsonResponse({'res': 0})

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

            suobj_help = 'false'
            if request.user.is_authenticated:
                if SubUrlObjectHelp.objects.filter(user=request.user, sub_url_object=suobj).exists():
                    suobj_help = 'true'

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
                'suobj_help': suobj_help,
                'help_count': suobj.help_count
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

                                result = 'false'

                        except Exception as e:
                            print(e)
                            return JsonResponse({'res': 0})
                    else:
                        try:
                            with transaction.atomic():
                                bridge = Bridge.objects.create(bridge=chosen_user, user=request.user)

                                result = 'true'

                                # customers = Customer.objects.filter(scoops_ordered__gt=F('store_visits'))
                        except Exception as e:
                            print(e)
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

                step = 31
                next = None
                output = []
                if user is not None:
                    if next_id == '':
                        bridgings = Bridge.objects.filter(user=user).order_by('created')[:step]
                    else:
                        try:
                            last_bridging = Bridge.objects.get(bridge__username=next_id, user=user)
                        except:
                            return JsonResponse({'res': 0})
                        bridgings = Bridge.objects.filter(Q(user=user) & Q(pk__gte=last_bridging.pk)).order_by('created')[:step]
                    count = 0
                    for bridge in bridgings:
                        count = count+1
                        if count == step:
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
                step = 31
                next = None
                output = []
                if user is not None:
                    if next_id == '':
                        bridgers = Bridge.objects.filter(bridge=user).order_by('created')[:step]
                    else:
                        try:
                            last_bridger = Bridge.objects.get(bridge=user, user__username=next_id)
                        except Exception as e:
                            return JsonResponse({'res': 0})
                        bridgers = Bridge.objects.filter(Q(bridge=user) & Q(pk__gte=last_bridger.pk)).order_by('created')[:step]
                    count = 0
                    for bridge in bridgers:
                        count = count+1
                        if count == step:
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
def re_help_list(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                suobj_id = request.POST.get('suobj_id', None)
                next_id = request.POST.get('next_user_id', None)
                suobj = None
                try:
                    suobj = SubUrlObject.objects.get(uuid=suobj_id)
                except Exception as e:
                    return JsonResponse({'res': 0})
                step = 31

                next = None
                output = []
                if suobj is not None:
                    if next_id == '':
                        suobj_helps = SubUrlObjectHelp.objects.filter(sub_url_object=suobj).order_by('created')[:step]
                    else:
                        try:
                            last_suobj_help = SubUrlObjectHelp.objects.get(sub_url_object=suobj, user__username=next_id)
                        except:
                            return JsonResponse({'res': 0})
                        suobj_helps = SubUrlObjectHelp.objects.filter(Q(sub_url_object=suobj) & Q(pk__gte=last_suobj_help.pk)).order_by('created')[:step]
                    count = 0
                    for item in suobj_helps:
                        count = count+1
                        if count == step:
                            next = item.user.username
                            break
                        sub_output = {
                            'username': item.user.userusername.username,
                            'photo': item.user.userphoto.file_50_url(),
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
def re_suobj_help(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                suobj_id = request.POST.get('suobj_id', None)
                suobj = None
                try:
                    suobj = SubUrlObject.objects.get(uuid=suobj_id)
                except Exception as e:
                    return JsonResponse({'res': 0})
                suobj_help = None
                try:
                    suobj_help = SubUrlObjectHelp.objects.get(user=request.user, sub_url_object=suobj)
                except Exception as e:
                    pass
                if suobj_help is not None:
                    suobj_help.delete()
                    return JsonResponse({'res': 1, 'result': 'cancel'})
                else:
                    suobj_help = SubUrlObjectHelp.objects.create(user=request.user, sub_url_object=suobj)
                    return JsonResponse({'res': 1, 'result': 'help'})

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
            print(search_word)

            loc = None
            if not is_unable_url(search_word):
                loc = url_without_scheme(search_word)

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

            my_output = []
            if request.user.is_authenticated:
                if loc is None:
                    mys = SubUrlObject.objects.filter(
                        (Q(user=request.user))
                        & (Q(title__text__icontains=search_word)
                           | Q(suburlobjectsubkeyword__sub_keyword__keyword__text__icontains=search_word)
                           )).order_by(
                        '-created').distinct()[:10]
                else:
                    mys = SubUrlObject.objects.filter(
                        (Q(user=request.user))
                        & (Q(title__text__icontains=search_word)
                           | Q(suburlobjectsubkeyword__sub_keyword__keyword__text__icontains=search_word)
                           | Q(url_object__loc__icontains=loc))).order_by(
                        '-created').distinct()[:10]
            else:
                mys = SubUrlObject.objects.none()

            for my in mys:
                sub_raw_keywords = SubRawKeyword.objects.filter(sub_url_object=my).order_by('created')[:5]
                sub_raw_keywords_output = []
                for sub_raw_keyword in sub_raw_keywords:
                    sub_raw_keywords_output.append(sub_raw_keyword.text)
                sub_output = {
                    'username': request.user.userusername.username,
                    'id': my.uuid,
                    'title': my.title.text,
                    'url': my.url_object.get_url(),
                    'keyword_output': sub_raw_keywords_output
                }

                my_output.append(sub_output)
            suobj_output = []
            if request.user.is_authenticated:
                if loc is None:
                    suobjs = SubUrlObject.objects.filter(
                        (Q(user__is_bridged__user=request.user))
                        & (Q(user__userusername__username__icontains=search_word)
                           | Q(title__text__icontains=search_word)
                           | Q(suburlobjectsubkeyword__sub_keyword__keyword__text__icontains=search_word)
                           | Q(user__usertextname__name__icontains=search_word))).order_by(
                        '-created').distinct()[:10]
                else:
                    suobjs = SubUrlObject.objects.filter(
                        (Q(user__is_bridged__user=request.user))
                        & (Q(user__userusername__username__icontains=search_word)
                           | Q(title__text__icontains=search_word)
                           | Q(suburlobjectsubkeyword__sub_keyword__keyword__text__icontains=search_word)
                           | Q(user__usertextname__name__icontains=search_word)
                           | Q(url_object__loc__icontains=loc))).order_by(
                        '-created').distinct()[:10]
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
                    'title': suobj.title.text,
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
            if loc is None:
                url_objects = UrlObject.objects.filter(Q(urlkeyword__keyword__text__icontains=search_word)).order_by(
                    'urlkeyword__up_count')[:10]
            else:
                url_objects = UrlObject.objects.filter(
                    Q(urlkeyword__keyword__text__icontains=search_word) | Q(loc__icontains=loc)).order_by(
                    'urlkeyword__up_count')[:10]
            for url_object in url_objects:
                url_output.append(url_object.uuid)

            return JsonResponse({'res': 1,
                                 'user_output': user_output,
                                 'my_output': my_output,
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
def re_search_my(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                search_word = request.POST.get('search_word', None)
                end_id = request.POST.get('end_id', None)

                loc = None
                if not is_unable_url(search_word):
                    loc = url_without_scheme(search_word)

                step = 10
                sub_raw_keyword_step = 5

                if end_id == '':
                    if loc is None:
                        suobjs = SubUrlObject.objects.filter(
                            (Q(user=request.user)) &
                            (Q(title__text__icontains=search_word)
                             | Q(suburlobjectsubkeyword__sub_keyword__keyword__text__icontains=search_word)
                             )).order_by(
                            '-created').distinct()[:step]
                    else:
                        suobjs = SubUrlObject.objects.filter(
                            (Q(user=request.user)) &
                            (Q(title__text__icontains=search_word)
                             | Q(suburlobjectsubkeyword__sub_keyword__keyword__text__icontains=search_word)
                             | Q(url_object__loc__icontains=loc))).order_by(
                            '-created').distinct()[:step]
                else:
                    try:
                        end_suobjs = SubUrlObject.objects.get(uuid=end_id)
                    except Exception as e:
                        print(e)
                        return JsonResponse({'res': 0})
                    if loc is None:
                        suobjs = SubUrlObject.objects.filter(
                            ((Q(user=request.user)) &
                             (Q(title__text__icontains=search_word)
                             | Q(suburlobjectsubkeyword__sub_keyword__keyword__text__icontains=
                                 search_word)))
                            & Q(pk__lt=end_suobjs.pk)).order_by(
                            '-created').distinct()[:step]
                    else:
                        suobjs = SubUrlObject.objects.filter(
                            ((Q(user=request.user)) &
                             (Q(title__text__icontains=search_word)
                              | Q(suburlobjectsubkeyword__sub_keyword__keyword__text__icontains=
                                  search_word)
                              | Q(url_object__loc__icontains=loc)))
                            & Q(pk__lt=end_suobjs.pk)).order_by(
                            '-created').distinct()[:step]
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
                        'title': suobj.title.text,
                        'url': suobj.url_object.get_url(),
                        'keyword_output': sub_raw_keywords_output
                    }

                    output.append(sub_output)

                return JsonResponse({'res': 1,
                                     'output': output,
                                     'end': end})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_search_bridge(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                search_word = request.POST.get('search_word', None)
                end_id = request.POST.get('end_id', None)

                loc = None
                if not is_unable_url(search_word):
                    loc = url_without_scheme(search_word)

                step = 10
                sub_raw_keyword_step = 5

                if end_id == '':
                    if loc is None:

                        suobjs = SubUrlObject.objects.filter(
                            (Q(user__is_bridged__user=request.user)) &
                            (Q(user__userusername__username__icontains=search_word)
                             | Q(title__text__icontains=search_word)
                             | Q(suburlobjectsubkeyword__sub_keyword__keyword__text__icontains=search_word)
                             | Q(user__usertextname__name__icontains=search_word))).order_by(
                            '-created').distinct()[:step]
                    else:
                        suobjs = SubUrlObject.objects.filter(
                            (Q(user__is_bridged__user=request.user)) &
                            (Q(user__userusername__username__icontains=search_word)
                             | Q(title__text__icontains=search_word)
                             | Q(suburlobjectsubkeyword__sub_keyword__keyword__text__icontains=search_word)
                             | Q(user__usertextname__name__icontains=search_word)
                             | Q(url_object__loc__icontains=loc))).order_by(
                            '-created').distinct()[:step]
                else:
                    try:
                        end_suobjs = SubUrlObject.objects.get(uuid=end_id)
                    except Exception as e:
                        print(e)
                        return JsonResponse({'res': 0})
                    if loc is None:
                        suobjs = SubUrlObject.objects.filter(
                            ((Q(user__is_bridged__user=request.user)) &
                             (Q(user__userusername__username__icontains=search_word)
                             | Q(title__text__icontains=search_word)
                             | Q(suburlobjectsubkeyword__sub_keyword__keyword__text__icontains=
                                 search_word)
                             | Q(user__usertextname__name__icontains=search_word)))
                            & Q(pk__lt=end_suobjs.pk)).order_by(
                            '-created').distinct()[:step]
                    else:
                        suobjs = SubUrlObject.objects.filter(
                            ((Q(user__is_bridged__user=request.user)) &
                             (Q(user__userusername__username__icontains=search_word)
                              | Q(title__text__icontains=search_word)
                              | Q(suburlobjectsubkeyword__sub_keyword__keyword__text__icontains=
                                  search_word)
                              | Q(user__usertextname__name__icontains=search_word)
                              | Q(url_object__loc__icontains=loc)))
                            & Q(pk__lt=end_suobjs.pk)).order_by(
                            '-created').distinct()[:step]

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
                        'title': suobj.title.text,
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

            loc = None
            if not is_unable_url(search_word):
                loc = url_without_scheme(search_word)

            if loc is None:
                url_objects = UrlObject.objects.filter(Q(urlkeyword__keyword__text__icontains=search_word)).order_by(
                    'urlkeyword__up_count')[order:order + step]

            else:
                url_objects = UrlObject.objects.filter(
                    Q(urlkeyword__keyword__text__icontains=search_word)
                    | Q(loc__icontains=loc)).order_by('urlkeyword__up_count')[order:order + step]

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


@ensure_csrf_cookie
def re_note_all(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                end_id = request.POST.get('end_id', None)
                step = 30
                notices = None
                if end_id == '':
                    notices = Notice.objects.filter(Q(user=request.user)).order_by('-created').distinct()[:step]
                else:
                    end_notice = None
                    try:
                        end_notice = Notice.objects.get(uuid=end_id)
                    except Exception as e:
                        print(e)
                        return JsonResponse({'res': 0})
                    notices = Notice.objects.filter(Q(user=request.user) & Q(pk__lt=end_notice.pk)).order_by(
                        '-created').distinct()[:step]

                output = []
                count = 0
                end = None
                for notice in notices:
                    count = count + 1
                    if count == step:
                        end = notice.uuid
                    sub_output = {
                        'id': notice.uuid,
                        'created': notice.created,
                        'notice_kind': notice.kind,
                        'notice_value': notice.get_value(),
                    }

                    output.append(sub_output)

                return JsonResponse({'res': 1, 'output': output, 'end': end})

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


@ensure_csrf_cookie
def re_bridge_feed(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                end_id = request.POST.get('end_id', None)
                step = 20
                help_step = 20
                suobjs = None
                suobj_helps = None

                if end_id == '':
                    suobjs = SubUrlObject.objects.filter(Q(user__is_bridged__user=request.user)
                                                         ).order_by('-created').distinct()[:step]

                    suobj_helps = SubUrlObjectHelp.objects.filter(
                        Q(user__is_bridged__user=request.user)).exclude(Q(sub_url_object__user=request.user)).order_by(
                        '-created').distinct()[:help_step]
                else:
                    end_suobj = None
                    try:
                        end_suobj = SubUrlObject.objects.get(uuid=end_id)
                    except Exception as e:
                        print(e)
                        return JsonResponse({'res': 0})
                    suobjs = SubUrlObject.objects.filter((Q(user__is_bridged__user=request.user))
                                                         & Q(pk__lt=end_suobj.pk)).order_by(
                        '-created').distinct()[:step]

                    suobj_helps = SubUrlObjectHelp.objects.filter(
                        Q(user__is_bridged__user=request.user)
                        & Q(created__lt=end_suobj.created)).exclude(Q(sub_url_object__user=request.user)).order_by(
                        '-created').distinct()[:help_step]

                from itertools import chain
                from operator import attrgetter
                # ascending oreder
                result_list = sorted(
                    chain(suobjs, suobj_helps),
                    key=attrgetter('created'))

                output = []
                for item in result_list:
                    kind = ''
                    identity = ''
                    username = ''

                    if str(item).startswith('suobj'):
                        kind = 'suobj'
                        identity = item.uuid
                        username = item.user.userusername.username

                    elif str(item).startswith('help'):
                        kind = 'help'
                        identity = item.sub_url_object.uuid
                        username = item.user.userusername.username

                    sub_output = {
                        'obj_type': kind,
                        'id': identity,
                        'username': username

                    }
                    output.append(sub_output)

                count = 0
                end = None
                for item in suobjs:
                    count = count + 1
                    if count == step:
                        end = item.uuid

                return JsonResponse({'res': 1, 'output': output, 'end': end})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_home(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                end_id = request.POST.get('end_id', None)
                step = 20
                suobjs = None
                suobj_help = SubUrlObject.objects.exclude(
                    suburlobjecthelp__user__is_bridged__user=request.user).order_by(
                    '-created').distinct('sub_url_object')[:10]

                import random

                # filter_q = Q()
                # for sub_keyword in sub_keyword_sample:
                #     filter_q = filter_q | Q(suburlobjectsubkeyword__sub_keyword__keyword__text=sub_keyword.keyword.text)
                # suobj_qs1 = SubUrlObject.objects.filter(filter_q).order_by('-created')[:step]
                # sub_keyword_order = random.randint(0, sub_keyword_count-1)

                sub_keywords = SubKeyword.objects.filter(user=request.user)
                sub_keyword_count = sub_keywords.count()
                keyword_count = 0
                sub_keyword_list = []
                while keyword_count < 3:
                    keyword_count = keyword_count + 1
                    if sub_keyword_count < 2:
                        if sub_keyword_count == 1:
                            sub_keyword_order = 0
                        else:
                            keyword_count = 3
                            break
                    else:
                        sub_keyword_order = random.randint(0, sub_keyword_count - 1)
                    sub_keyword = sub_keywords[sub_keyword_order]
                    sub_keyword_list.append(sub_keyword.keyword.text)

                sub_keyword_list = sorted(set(sub_keyword_list), key=lambda x: sub_keyword_list.index(x))
                qs1_list = []
                for item in sub_keyword_list:
                    suobj_obj = None
                    if end_id=='':
                        suobj_obj = SubUrlObject.objects.filter(
                            Q(suburlobjectsubkeyword__sub_keyword__keyword__text=item)).exclude(
                            Q(user=request.user) | Q(user__is_bridged__user=request.user)
                        ).first()
                    else:
                        try:
                            end_suobj = SubUrlObject.objects.get(uuid=end_id)
                        except Exception as e:
                            print(e)
                            return JsonResponse({'res': 0})
                        suobj_obj = SubUrlObject.objects.filter(
                            Q(suburlobjectsubkeyword__sub_keyword__keyword__text=item)
                            & Q(created__lt=end_suobj.created)).exclude(
                            Q(user=request.user) | Q(user__is_bridged__user=request.user)
                        ).first()
                    if suobj_obj is not None:
                        sub_output = {
                            'id': suobj_obj.uuid,
                            'obj_type': 'keyword',
                            'keyword': item,
                            'created': suobj_obj.created
                        }
                        qs1_list.append(sub_output)


                qs2_list = []
                suobj_qs2 = None
                if end_id == '':
                    suobj_qs2 = SubUrlObject.objects.filter(
                        Q(suburlobjecthelp__isnull=False)).exclude(
                        Q(suburlobjecthelp__user__is_bridged__user=request.user)
                        | Q(user__is_bridged__user=request.user)
                        | Q(user=request.user)
                        | Q(suburlobjecthelp__user=request.user)).order_by(
                        '-suburlobjecthelp__created', '-created').distinct()[:step]

                else:
                    try:
                        end_suobj = SubUrlObject.objects.get(uuid=end_id)
                    except Exception as e:
                        print(e)
                        return JsonResponse({'res': 0})

                    suobj_qs2 = SubUrlObject.objects.filter(
                        Q(suburlobjecthelp__isnull=False)
                        & Q(suburlobjecthelp__created__lt=end_suobj.suburlobjecthelp_set.last().created)).exclude(
                        Q(suburlobjecthelp__user__is_bridged__user=request.user)
                        | Q(user__is_bridged__user=request.user)
                        | Q(user=request.user)
                        | Q(suburlobjecthelp__user=request.user)).order_by(
                        '-suburlobjecthelp__created', '-created').distinct()[:step]
                end = None
                if suobj_qs2 is not None:
                    count = 0
                    for item in suobj_qs2:
                        if count == step:
                            end = item.uuid
                        sub_qs = SubUrlObjectHelp.objects.filter(sub_url_object=item)
                        sub_count = sub_qs.count()

                        if sub_count < 2:
                            if sub_count == 1:
                                sub_order = 0
                            else:
                                break
                        else:
                            sub_order = random.randint(0, sub_keyword_count - 1)

                        sub_order = random.randint(0, sub_count-1)
                        sub_user = sub_qs[sub_order]

                        sub_output = {
                            'id': item.uuid,
                            'obj_type': 'help',
                            'username': sub_user.user.userusername.username,
                            'created': item.created
                        }
                        qs2_list.append(sub_output)

                from itertools import chain
                from operator import attrgetter
                from operator import itemgetter
                # ascending oreder
                output = sorted(
                    chain(qs1_list, qs2_list),
                    key=itemgetter('created'))

                return JsonResponse({'res': 1, 'output': output, 'end': end})

        return JsonResponse({'res': 2})

@ensure_csrf_cookie
def re_user_search_suobj(request):
    if request.method == "POST":
        if request.is_ajax():
            search_word = request.POST.get('search_word', None)
            end_id = request.POST.get('end_id', None)

            user_id = request.POST.get('user_id', None)

            try:
                user = User.objects.get(username=user_id)
            except Exception as e:
                return JsonResponse({'res': 0})

            loc = None
            if not is_unable_url(search_word):
                loc = url_without_scheme(search_word)

            step = 10
            sub_raw_keyword_step = 5

            if request.user.is_authenticated:
                if end_id == '':
                    if loc is None:

                        suobjs = SubUrlObject.objects.filter(
                            (Q(user=user)) &
                            (Q(title__text__icontains=search_word)
                             | Q(suburlobjectsubkeyword__sub_keyword__keyword__text__icontains=search_word))).order_by(
                            '-created').distinct()[:step]
                    else:
                        suobjs = SubUrlObject.objects.filter(
                            (Q(user=user)) &
                            (Q(title__text__icontains=search_word)
                             | Q(suburlobjectsubkeyword__sub_keyword__keyword__text__icontains=search_word)
                             | Q(url_object__loc__icontains=loc))).order_by(
                            '-created').distinct()[:step]
                else:
                    try:
                        end_suobjs = SubUrlObject.objects.get(uuid=end_id)
                    except Exception as e:
                        print(e)
                        return JsonResponse({'res': 0})
                    if loc is None:
                        suobjs = SubUrlObject.objects.filter(
                            ((Q(user=user)) &
                             (Q(title__text__icontains=search_word)
                             | Q(suburlobjectsubkeyword__sub_keyword__keyword__text__icontains=
                                 search_word)))
                            & Q(pk__lt=end_suobjs.pk)).order_by(
                            '-created').distinct()[:step]
                    else:
                        suobjs = SubUrlObject.objects.filter(
                            ((Q(user=user)) &
                             (Q(title__text__icontains=search_word)
                              | Q(suburlobjectsubkeyword__sub_keyword__keyword__text__icontains=
                                  search_word)
                              | Q(url_object__loc__icontains=loc)))
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
                    'title': suobj.title.text,
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
def re_user_search_keyword(request):
    if request.method == "POST":
        if request.is_ajax():
            search_word = request.POST.get('search_word', None)
            order = request.POST.get('order', None)

            user_id = request.POST.get('user_id', None)

            try:
                user = User.objects.get(username=user_id)
            except Exception as e:
                return JsonResponse({'res': 0})

            order = int(order)
            step = 10

            from django.db.models.functions import Length

            keywords = Keyword.objects.filter(Q(subkeyword__user=user)
                                              & Q(text__icontains=search_word)).order_by(
                Length('text').asc())[order:order + step]

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