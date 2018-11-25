from . import views
from django.conf.urls import url, include

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^dotest$', views.take_the_test, name='take_the_test'),
    url(r'^answer_response$', views.answer_response, name='answer_response'),
    url(r'^close_session$', views.close_test, name='close_test'),
    url(r'^result_test$', views.result_test, name='result_test'),
#     url(r'^(?P<pk>\d+)/delete', views.BlogDelete, name='blog_delete'),
#
#login
    url(r'^register', views.user_register, name='user_register'),
    url(r'^login', views.user_login, name='user_login'),
    url(r'^logout', views.user_logout, name='user_logout'),
    url(r'^profile', views.user_profile, name='user_profile'),
]
