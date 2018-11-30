from . import views
from django.conf.urls import url, include

urlpatterns = [
    # client
    url(r'^$', views.index, name='index'),
    url(r'^dotest$', views.take_the_test, name='take_the_test'),
    url(r'^answer_response$', views.answer_response, name='answer_response'),
    url(r'^close_session$', views.close_test, name='close_test'),
    url(r'^result_test$', views.result_test, name='result_test'),
    url(r'^start_new_session', views.start_new_session, name='start_new_session'),

    #user
    url(r'^register', views.user_register, name='user_register'),
    url(r'^login', views.user_login, name='user_login'),
    url(r'^logout', views.user_logout, name='user_logout'),
    url(r'^profile', views.user_profile, name='user_profile'),

    # statistical
    url(r'^statistical', views.result_session, name='statistical'),
    url(r'^result_session$', views.result_session, name="result_session"),
    url(r'^video', views.video, name="video"),
    url(r'^user_account', views.user_account, name="user_account")

]
