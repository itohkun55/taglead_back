from django.conf.urls import url, include
from rest_framework import routers
from .views import (
#    InitialUserDataView,
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
    ShowUserFavoriteView,
    MemoDeleteView,
    MemoModifyView
    )
from .subview import (
    MakeTagByFacilityAdminView,
    ModifyTagByFacilityAdminView,
    NewUserSetView,
    ShowFacilityUserAdminView,
    ShowUserTagConfigView,
    UpdateUserTagConfigView,
    ResetUserTagConfigView,
    MakeNewTagView
    )

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
    url(r'^tagconfig', ShowUserTagConfigView.as_view()),
    #url(r'^maketag', MakeNewTagView.as_view()),
    url(r'^changeconfig', UpdateUserTagConfigView.as_view()),
    url(r'^tagreset', ResetUserTagConfigView.as_view()),
    url(r'^memodelete', MemoDeleteView.as_view()),
    url(r'^memomodify', MemoModifyView.as_view()),
    
    #タグ追加用管理者のみ使用
    url(r'^showtagadmin', ShowFacilityUserAdminView.as_view()),
    url(r'^maketagadmin', MakeTagByFacilityAdminView.as_view()),
    url(r'^modifytagadmin', ModifyTagByFacilityAdminView.as_view()),
    
    
    
    
]

