from django.conf.urls import url, include
from rest_framework import routers
from .views import (
#    InitialUserDataView,
    TestAppendValueView,
    TagSearchView,
    MemoInsertView,
    FormattedMemoInsertView,
    MainListView,
    FormattedTagListView,
    ReplyThreadView,
    ReplyInsertView,
    InitialDataListView,
    SetReadMarkView,
    SetFavoriteMarkView,
    NoticeMainView,
    ShowUserFavoriteView
    )
from .subview import (
    NewUserSetView,
    ShowUserTagConfig,
    UpdateUserTagConfig,
    UpdateUserTagConfig)

# Create your views here.
router = routers.DefaultRouter()
#router.register(r'test', TestAppendValueView)
#router.register(r'users', TagLeadUserViewSet)
#router.register(r'tagsearch', TagSearchView)


urlpatterns = [
    
    url('auth/',include('drf_social_oauth2.urls',namespace='drf')), #add this
    url(r'^', include(router.urls)),
    #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^inituser', InitialDataListView.as_view()),
#    url(r'^test', TestAppendValueView.as_view()),
    url(r'^newuser', NewUserSetView.as_view()),
    url(r'^main', MainListView.as_view()),
    url(r'^tags', TagSearchView.as_view()),
    url(r'^memoinsert', MemoInsertView.as_view()),
    url(r'^formattedinsert', FormattedMemoInsertView.as_view()),
    url(r'^formtaglist', FormattedTagListView.as_view()),
    url(r'^reply', ReplyThreadView.as_view()),
    url(r'^repinsert', ReplyInsertView.as_view()),
    url(r'^setread', SetReadMarkView.as_view()),
    url(r'^setfav', SetFavoriteMarkView.as_view()),
    url(r'^getnotice', NoticeMainView.as_view()),
    url(r'^favorite', ShowUserFavoriteView.as_view()),
    url(r'^tagconfig', ShowUserTagConfig.as_view()),
    url(r'^changeconfig', UpdateUserTagConfig.as_view()),
    
]

