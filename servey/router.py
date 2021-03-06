from . import views
from django.conf.urls import url, include

urlpatterns = [
    # client
    url(r'^$', views.index, name='index'),
    url(r'^dotest$', views.take_the_test, name='take_the_test'),
    url(r'^answer_response$', views.answer_response, name='answer_response'),
    url(r'^close_session$', views.close_test, name='close_test'),
    url(r'^result_test$', views.result_test, name='result_test'),
    url(r'^start_new_session$', views.start_new_session, name='start_new_session'),

    #user
    url(r'^register$', views.user_register, name='user_register'),
    url(r'^login$', views.user_login, name='user_login'),
    url(r'^logout$', views.user_logout, name='user_logout'),
    url(r'^me$', views.user_profile, name='user_profile'),
    url(r'^profile/(?P<user_pk>\d+)$', views.user_profile, name='user_profile'),

    # statistics
    url(r'^statistics$', views.result_session, name='statistics'),
    url(r'^result_session$', views.result_session, name="result_session"),
    url(r'^videos$', views.videos, name="videos"),
    url(r'^user_account$', views.user_account, name="user_account"),
    url(r'^video/(?P<video_pk>\d+)$', views.detail_video, name="detail_video"),
]
