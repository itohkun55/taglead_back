from django.urls import path,include
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
    MemoModifyView,
    TestRealView,
    FirstAccessView,
    CallGoogleView
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

urlpatterns = [
    path('ok', TestRealView.as_view()),
    
    path('auth/',include('drf_social_oauth2.urls',namespace='drf')), #add this
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('firstend', FirstAccessView.as_view()),
    path('inituser', InitialDataListView.as_view()),
    path('newuser', NewUserSetView.as_view()),
    path('main', MainListView.as_view()),
    path('tags', TagSearchView.as_view()),
    path('memoinsert', MemoInsertView.as_view()),
    path('formattedinsert', FormattedMemoInsertView.as_view()),
    path('formtaglist', FormattedTagListView.as_view()),
    path('reply', ReplyThreadView.as_view()),
    path('repinsert', ReplyInsertView.as_view()),
    path('setread', SetReadMarkView.as_view()),
    path('setfav', SetFavoriteMarkView.as_view()),
    path('getnotice', NoticeMainView.as_view()),
    path('favorite', ShowUserFavoriteView.as_view()),
    path('tagconfig', ShowUserTagConfigView.as_view()),
    path('maketag', MakeNewTagView.as_view()),
    path('changeconfig', UpdateUserTagConfigView.as_view()),
    path('tagreset', ResetUserTagConfigView.as_view()),
    path('memodelete', MemoDeleteView.as_view()),
    path('memomodify', MemoModifyView.as_view()),
    
    #タグ追加用管理者のみ使用
    path('showtagadmin', ShowFacilityUserAdminView.as_view()),
    path('maketagadmin', MakeTagByFacilityAdminView.as_view()),
    path('modifytagadmin', ModifyTagByFacilityAdminView.as_view()),
    #GoogleAssistant接続用
    path('callgoogle', CallGoogleView.as_view()),
    
]

