from django.urls import path, re_path
from authapp import views as authviews
from authapp import ajax_views as auth_ajax_views
from baseapp import ajax_views as base_ajax_views
from baseapp import views
from django.views.generic import TemplateView
from baseapp.sitemaps import sitemaps
from django.contrib.sitemaps import views as sitemap_views
app_name = 'baseapp'

urlpatterns = [
    re_path(r'^robots\.txt$',
            TemplateView.as_view(template_name="others/robots.txt", content_type="text/plain"), name="robots"),
    path('a/sitemap.xml', sitemap_views.index, {'sitemaps': sitemaps, 'sitemap_url_name': 'baseapp:sitemaps'}),
    path('a/sitemap-<section>.xml', sitemap_views.sitemap, {'sitemaps': sitemaps},
         name='sitemaps'),
    re_path(r'^$', authviews.main_create_log_in, name='main_create_log_in'),

    re_path(r'^register/url/$', views.register_url, name='register_url'),
    re_path(r'^update/url/(?P<uuid>([0-9a-f]{32}))/$', views.update_url, name='update_url'),
    re_path(r'^object/(?P<uuid>([0-9a-f]{32}))/$', views.suobj, name='suobj'),
    re_path(r'^url/(?P<uuid>([0-9a-f]{32}))/$', views.url, name='url'),

    re_path(r'^(?P<user_username>([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?))/$',
            views.user_profile, name='user_profile'),

    re_path(r'^search/all/$', views.search_all, name='search_all'),
    re_path(r'^search/my/$', views.search_my, name='search_my'),
    re_path(r'^search/user/$', views.search_user, name='search_user'),
    re_path(r'^search/bridge/$', views.search_bridge, name='search_bridge'),
    re_path(r'^search/keyword/$', views.search_keyword, name='search_keyword'),
    re_path(r'^search/url/$', views.search_url, name='search_url'),

    re_path(r'^bridge/feed/$', views.bridge_feed, name='bridge_feed'),
    re_path(r'^note/all/$', views.note_all, name='note_all'),

    re_path(r'^(?P<user_username>([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?))/search/$',
            views.user_search, name='user_search'),
    # re_path(r'^note/all/$', views.note_all, name='note_all'),



    re_path(r'^re_settings/ajax/$', auth_ajax_views.re_settings, name='re_settings'),
    re_path(r'^re_settings/ajax/upload_user_photo/$', auth_ajax_views.upload_user_photo, name='re_upload_user_photo'),
    # re_path(r'^re/create/new/$', base_ajax_views.re_create_new, name='re_create_new'),

    re_path(r'^re/check/url/$', base_ajax_views.re_check_url,
            name='re_check_url'),
    re_path(r'^re/register/url/$', base_ajax_views.re_register_url,
            name='re_register_url'),
    re_path(r'^re/update/url/$', base_ajax_views.re_update_url,
            name='re_update_url'),
    re_path(r'^re/update/complete/url/$', base_ajax_views.re_update_complete_url,
            name='re_update_complete_url'),
    re_path(r'^re/refresh/url/$', base_ajax_views.re_refresh_url,
            name='re_refresh_url'),

    re_path(r'^re/profile/suobj/$', base_ajax_views.re_profile_suobj,
            name='re_profile_suobj'),
    re_path(r'^re/suobj/populate/$', base_ajax_views.re_suobj_populate,
            name='re_suobj_populate'),


    re_path(r'^re/bridge/add/$', base_ajax_views.re_bridge_add,
            name='re_bridge_add'),
    re_path(r'^re/bridging/list/$', base_ajax_views.re_bridging_list,
            name='re_bridging_list'),
    re_path(r'^re/bridger/list/$', base_ajax_views.re_bridger_list,
            name='re_bridger_list'),
    re_path(r'^re/help/list/$', base_ajax_views.re_help_list,
            name='re_help_list'),
    re_path(r'^re/url/populate/$', base_ajax_views.re_url_populate,
            name='re_url_populate'),

    re_path(r'^re/url/keyword/$', base_ajax_views.re_url_keyword,
            name='re_url_keyword'),

    re_path(r'^re/url/keyword/up/$', base_ajax_views.re_url_keyword_up,
            name='re_url_keyword_up'),
    re_path(r'^re/url/keyword/down/$', base_ajax_views.re_url_keyword_down,
            name='re_url_keyword_down'),

    re_path(r'^re/suobj/help/$', base_ajax_views.re_suobj_help,
            name='re_suobj_help'),

    re_path(r'^re/comment/add/$', base_ajax_views.re_comment_add,
            name='re_comment_add'),
    re_path(r'^re/comment/delete/$', base_ajax_views.re_comment_delete,
            name='re_comment_delete'),
    re_path(r'^re/comment/more/load/$', base_ajax_views.re_comment_more_load,
            name='re_comment_more_load'),

    re_path(r'^re/profile/suobj/delete/$', base_ajax_views.re_profile_suobj_delete,
            name='re_profile_suobj_delete'),

    re_path(r'^re/search/all/$', base_ajax_views.re_search_all,
            name='re_search_all'),
    re_path(r'^re/search/my/$', base_ajax_views.re_search_my,
            name='re_search_my'),

    re_path(r'^re/search/user/$', base_ajax_views.re_search_user,
            name='re_search_user'),
    re_path(r'^re/search/bridge/$', base_ajax_views.re_search_bridge,
            name='re_search_user'),
    re_path(r'^re/search/keyword/$', base_ajax_views.re_search_keyword,
            name='re_search_user'),
    re_path(r'^re/search/url/$', base_ajax_views.re_search_url,
            name='re_search_user'),

    re_path(r'^re/nav/badge/populate/$', base_ajax_views.re_nav_badge_populate,
            name='re_nav_badge_populate'),

    re_path(r'^re/note/all/$', base_ajax_views.re_note_all,
            name='re_note_all'),

    re_path(r'^re/bridge/feed/$', base_ajax_views.re_bridge_feed,
            name='re_bridge_feed'),
    re_path(r'^re/home/$', base_ajax_views.re_home,
            name='re_home'),

    re_path(r'^re/user/search/suobj/$', base_ajax_views.re_user_search_suobj,
            name='re_user_search_suobj'),
    re_path(r'^re/user/search/keyword/$', base_ajax_views.re_user_search_keyword,
            name='re_user_search_keyword'),
    # re_path(r'^re/follow/add/$', base_ajax_views.re_follow_add,
    #         name='re_follow_add'),
    # re_path(r'^re/following/list/$', base_ajax_views.re_following_list,
    #         name='re_following_list'),
    # re_path(r'^re/follower/list/$', base_ajax_views.re_follower_list,
    #         name='re_follower_list'),
    #
    # re_path(r'^re/profile/post/$', base_ajax_views.re_profile_post,
    #         name='re_profile_post'),
    # re_path(r'^re/post/populate/$', base_ajax_views.re_post_populate,
    #         name='re_post_populate'),
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