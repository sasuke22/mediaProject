from django.conf.urls import url
from .views import login_view, terms, about, privacy, dashboard, logout_view, contact_us, user_login, friendship,\
    create_account, user_staff_login, user_profile, information, user_update, users, notification, accept_friendship, chat


urlpatterns = [
    url(r'^$', login_view, name='login'),
    url(r'^logout/$', logout_view, name='logout'),

    url(r'^dashboard/$', dashboard, name='dashboard'),
    url(r'^informations/$', information, name='informations'),

    url(r'^users/in/$', user_login, name='user_login'),
    url(r'^users/$', users, name='users'),
    url(r'^users/staff/in/$', user_staff_login, name='user_staff_login'),

    url(r'^profile/(?P<pk>[0-9]+)/$', user_profile, name='profile'),
    url(r'^edit/profile/(?P<pk>[0-9]+)/$', user_update, name='edit_profile'),

    url(r'^notification/$', notification, name='notification'),

    url(r'^accept/friendship/(?P<id>[0-9]+)/$', accept_friendship, name='accept_friendship'),

    url(r'^chat/$', chat, name='chat'),

    url(r'^friendship/(?P<id_receiver>[0-9]+)/$', friendship, name='friendship'),
    url(r'^create/account/$', create_account, name='create_account'),

    url(r'^contact/us/$', contact_us, name='contact'),
    url(r'^terms/$', terms, name='terms'),
    url(r'^about/$', about, name='about'),
    url(r'^privacy/$', privacy, name='privacy'),
]
