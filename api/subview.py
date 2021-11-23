from django.shortcuts import render
from django.utils import datastructures
from api.SendMessageLibrary import HAS_NO_ACCOUNT
from rest_framework import generics,views
from rest_framework.response import Response

from django.contrib.auth.models import User
from datetime import datetime,timedelta,timezone
from .views import TagLeadBaseView 


from rest_framework.permissions import IsAuthenticated
from drf_social_oauth2.authentication import SocialAuthentication
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
    
from core.models import GuestMain, MemoMain, TagInFormatedMemo,TagMain,Facility,OperateUser,TagSearchIndex,UserTagConfig

from .Serializers import (
    TagLeadUserSerializer,
    MemoMainSerializer,
    TagMainSerializer,
    
    TagInFormatedMemoSerializer,
    UserTagConfigSerializer)
    
from .ReplacedNumberLibrary import (
    NUM_COMMON_TAG_FACILITY,
    NUM_TAGTYPE_GUEST,
    NUM_TAGTYPE_MEMBER,
    NUM_TAG_STATUS_MAINLIST,
    NUM_TAG_STATUS_SUBLIST,
    NUM_MEMO_TYPE_FREE,
    NUM_MEMO_TYPE_FORMATTED,
    NUM_USER_HAS_CHANGE_AUTH)






#新規ユーザー作成　まず　UserTagConfigの初期値を設定して表示する
class NewUserSetView(TagLeadBaseView):


    def get(self,request):
        gets=request.GET
        
        facId=gets.get("facId")
        userName=gets.get("username")
        pwd=gets.get("pwd")

        newtag=TagMain.objects.create(strTagName=userName,numTagType=NUM_TAGTYPE_MEMBER,numTagRank=2,datePublish=datetime.now(),facilityId=Facility(pk=facId) ,strSuffix="")
        
        newOp=OperateUser.objects.create(strName=userName,keyFacility=Facility(pk=facId),datePublish=datetime.now(),tagId=newtag)

        
        OldUser=OperateUser.objects.filter(keyFacility=Facility(pk=facId),)
        for user in OldUser:
            #新ユーザはこの後まとめて入れ直し
            if user==newOp:
                continue
            UserTagConfig.objects.create(keyOperateUser=user,keyTag=newtag,numTagStatus=1,boolIsShownInList=True)
        
        #UserTagConfigで登録すべきTagMain（Typeが2・3・4・6)　※１は必須、5は補助タグ
        TargetTags=TagMain.objects.filter(numTagType__in=[1,2,3,4,6])
        for tag in TargetTags:
            newconfig=UserTagConfig.objects.create(keyOperateUser=newOp,keyTag=tag,numTagStatus=1,boolIsShownInList=True)

        

        return Response(UserTagConfigSerializer(UserTagConfig.objects.filter(keyOperateUser=newOp),many=True).data)


class ShowFacilityUserAdminView(TagLeadBaseView):
    def get(self,request):
        
        self.setRequestParams(request)

        facilityTags=TagMain.objects.filter(facilityId__pk=self.facId).exclude(numTagType=NUM_TAGTYPE_MEMBER)

        return Response({"tag_list": TagMainSerializer(facilityTags,many=True).data})

class MakeTagByFacilityAdminView(TagLeadBaseView):
    def get(self,request):

        self.setRequestParams(request)
        tagname=request.GET.get("tagname")
        tagtype=int(request.GET.get("tagtype")) 
        tagrank=int(request.GET.get("tagrank")) 

        newtag=TagMain.objects.create(strTagName=tagname,numTagType=tagtype,numTagRank=tagrank,facilityId=Facility(pk=self.facId))
        if tagtype==NUM_TAGTYPE_GUEST:
            GuestMain.objects.create(strGuestName=tagname,keyTagMain=newtag)

        #所属施設のUserTagConfigすべてに追加
        users=OperateUser.objects.filter(keyFacility__id=self.facId)
        for user in users:
            print("usertagconfig done",user,newtag)
            UserTagConfig.objects.create(keyOperateUser=user,keyTag=newtag,numTagStatus=-1,boolIsShownInList=False)

        return Response({"ok":"odk"})

class ModifyTagByFacilityAdminView(TagLeadBaseView):
    def get(self,request):

        self.setRequestParams(request)
        tagId=request.GET.get("tagId")
        tagname=request.GET.get("tagname")
        tagtype=int(request.GET.get("tagtype")) 
        tagrank=int(request.GET.get("tagrank")) 

        #実行者は権限があるか
        targetuser=OperateUser.objects.get(pk=self.userId)
        if targetuser.numRank>NUM_USER_HAS_CHANGE_AUTH:

            return Response({"error":True,"errorMsg":HAS_NO_ACCOUNT,"errorCode":1}) 


        try:
            mTag=TagMain.objects.get(pk=tagId)
            mTag.strTagName=tagname
            mTag.numTagType=tagtype
            mTag.numTagRank=tagrank
            mTag.save()

        except TagMain.DoesNotExist:
            return Response({"error":True,"errorMsg":HAS_NO_ACCOUNT,"errorCode":1}) 

        return Response({"ok":"ok"})


class ShowUserTagConfigView(TagLeadBaseView):
    
    def get(self,request):
        self.setRequestParams(request)
        config=UserTagConfig.objects.filter(keyOperateUser__pk=self.userId).order_by('-keyTag__numTagRank')
        return Response(UserTagConfigSerializer(config,many=True).data)

#ユーザー権限でタグを新規作成する
#ヴァリデーションが必要
class MakeNewTagView(TagLeadBaseView):
    def get(self,request):
        self.setRequestParams(request)

        gets=request.GET
        tagname=gets.get("tagname")
        tagtype=gets.get("tagtype")
        tagrank=gets.get("tagrank")
        print("SSSSSS")



        TagMain.objects.create(strTagName=tagname,numTagType=tagtype,numTagRank=tagrank,facilityId=Facility(pk=self.facId))

        return Response({"ok":"ok"})


class UpdateUserTagConfigView(TagLeadBaseView):

    def get(self,request):
        self.setRequestParams(request)

        tagId=request.GET.get("tagId")
        tagType=request.GET.get("tagstatus",default="-1")
        showlist=request.GET.get("isshow",default="false")

        target=UserTagConfig.objects.get(keyOperateUser__pk=self.userId,keyTag__pk=tagId)
        
        target.numTagStatus=tagType
        
        if showlist == "true":
            target.boolIsShownInList=True

        if showlist == "false":
            target.boolIsShownInList=False

        target.save()
        useFac=[NUM_COMMON_TAG_FACILITY,self.facId]

        useTag=TagMain.objects.filter(facilityId__id__in=useFac)

        res= {
            "main":UserTagConfigSerializer(UserTagConfig.objects.filter(numTagStatus=NUM_TAG_STATUS_MAINLIST,keyOperateUser__id=self.userId, keyTag__in=useTag),many=True).data,
            "sub":UserTagConfigSerializer(UserTagConfig.objects.filter(numTagStatus=NUM_TAG_STATUS_SUBLIST,keyOperateUser__id=self.userId, keyTag__in=useTag),many=True).data ,
            "user_config":UserTagConfigSerializer(UserTagConfig.objects.filter(keyOperateUser__pk=self.userId),many=True).data
        }
        
        return Response(res)

class ResetUserTagConfigView(TagLeadBaseView):

    def get(self,request):
        self.setRequestParams(request)

        targets=UserTagConfig.objects.filter(keyOperateUser__pk=self.userId).update(numTagStatus=-1,boolIsShownInList=False)

        #return  Response({"userId":userId})
        return Response(UserTagConfigSerializer(UserTagConfig.objects.filter(keyOperateUser__pk=self.userId),many=True).data)






