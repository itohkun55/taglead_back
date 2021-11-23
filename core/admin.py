from django.contrib import admin

# Register your models here.
from import_export.resources import ModelResource
from import_export.admin import ImportMixin
from import_export.formats import base_formats

from .models import (
    MemoMain,
    NoticeMain,
    OperateUser,
    Facility,
    TagMain,
    TagSearchIndex,
    UserTagConfig,
    TagInFormatedMemo,
    GuestMain,
    IsUserFavoriteInMemo,
    NoticeMain,
    MemoMainBackup
    )

class TagMainModelResource(ModelResource):
    class Meta:
        model=TagMain        

class OperateUserModelResources(ModelResource):
    class Meta:
        model=OperateUser

class MemoMainModelResources(ModelResource):
    class Meta:
        model=MemoMain

class TagSearchIndexResources(ModelResource):
    class Meta:
        model=TagSearchIndex

class TagMainAdmin(ImportMixin,admin.ModelAdmin):
    list_display=('pk','strTagName', 'numTagType', 'numTagRank','datePublish', 'facilityId')
    resource_class=TagMainModelResource
    formats=[base_formats.CSV]

class OperateUserAdmin(ImportMixin,admin.ModelAdmin):
    list_display=('id','strName', 'keyFacility', 'datePublish', 'tagId')
    resource_class=OperateUserModelResources
    formats=[base_formats.CSV]


class MemoMainAdmin(ImportMixin,admin.ModelAdmin):
    list_display=('pk','numMemotype','strTaglist','strMainText','keySender','listReceiver','datePublish','dateRegist')
    resource_class=MemoMainModelResources
    formats=[base_formats.CSV]

class TagSearchIndexAdmin(admin.ModelAdmin):
    list_display=('id','keyMemoMain','keyTagMain')
    resource_class=TagSearchIndexResources
    formats=[base_formats.CSV]


class UserTagConfigAdmin(admin.ModelAdmin):
    list_display=('keyOperateUser','keyTag','numTagStatus','boolIsShownInList')

class FacilityAdmin(admin.ModelAdmin):
    list_display=('id','strName')

class TagInformatedMemoAdmin(admin.ModelAdmin):
    list_display=("id","keyTagMain","numTagPhase","strGroup","strShow","strHide")

class GuestMainAdmin(admin.ModelAdmin):
    list_display=("strGuestName","keyTagMain","keyPlaceTagMain")

class FavoriteCheckAdmin(admin.ModelAdmin):
    list_display=("keyMemoMain","keyOperateUser")

class BackUpAdmin (admin.ModelAdmin):
    list_display=("keyMemoId","dateUpdate","typeBackUpCase","charBackUpText")


admin.site.register(MemoMain,MemoMainAdmin)
admin.site.register(TagMain,TagMainAdmin)
admin.site.register(OperateUser,OperateUserAdmin)
admin.site.register(UserTagConfig,UserTagConfigAdmin)
admin.site.register(TagSearchIndex,TagSearchIndexAdmin)
admin.site.register(Facility,FacilityAdmin)
admin.site.register(TagInFormatedMemo,TagInformatedMemoAdmin)
admin.site.register(GuestMain,GuestMainAdmin)
admin.site.register(IsUserFavoriteInMemo,FavoriteCheckAdmin)
admin.site.register(NoticeMain)
admin.site.register( MemoMainBackup,BackUpAdmin)
