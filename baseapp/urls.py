from django.urls import path, re_path
from authapp import views as authviews
from authapp import ajax_views as auth_ajax_views
from baseapp import ajax_views as base_ajax_views
from baseapp import views

app_name = 'baseapp'

urlpatterns = [

    re_path(r'^$', authviews.main_create_log_in, name='main_create_log_in'),
    re_path(r'^create/new/$', views.create_new, name='create_new'),
    re_path(r'^explore/feed/$', views.explore_feed, name='explore_feed'),
    re_path(r'^note/all/$', views.note_all, name='note_all'),
    re_path(r'^(?P<user_username>([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?))/$', views.user_profile, name='user_profile'),

    re_path(r'^post/update/(?P<uuid>([0-9a-f]{32}))/$', views.post_update, name='post_update'),
    re_path(r'^post/(?P<uuid>([0-9a-f]{32}))/$', views.post, name='post'),
    re_path(r'^search/all/$', views.search_all, name='search_all'),
    re_path(r'^search/user/$', views.search_user, name='search_user'),
    re_path(r'^search/post/$', views.search_post, name='search_post'),

    re_path(r'^re_settings/ajax/$', auth_ajax_views.re_settings, name='re_settings'),
    re_path(r'^re_settings/ajax/upload_user_photo/$', auth_ajax_views.upload_user_photo, name='re_upload_user_photo'),
    # re_path(r'^re/create/new/$', base_ajax_views.re_create_new, name='re_create_new'),

    re_path(r'^re/check/url/$', base_ajax_views.re_check_url,
            name='re_check_url'),
    re_path(r'^re/register/url/$', base_ajax_views.re_register_url,
            name='re_register_url'),
    # re_path(r'^email/key/send/$', views.email_key_send, name='email_key_send'),
    # re_path(r'^email/key/confirm/(?P<uid>([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?))/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        # views.email_key_confirm, name='email_key_confirm'),
    # re_path(r'^logout/$', views.log_out, name='log_out'),
    # re_path(r'^username/change/$', views.username_change, name='username_change'),
    # re_path(r'^password/change/$', views.password_change, name='password_change'),
    # re_path(r'^password/reset/$', views.password_reset, name='password_reset'),
    # re_path(r'^email/add/$', views.email_add, name='email_add'),
]
'''
    url(r'^create/$', views.main_create_log_in, name='create'),
'''