from django.db.models.query import QuerySet
from django.shortcuts import render
from rest_framework import routers,viewsets,generics,views
from rest_framework.response import Response

from django.contrib.auth.models import User
from datetime import datetime,timedelta,timezone

    
from core.models import MemoMain, TagInFormatedMemo,TagMain,Facility,OperateUser,TagSearchIndex,UserTagConfig

from .Serializers import (
    TagLeadUserSerializer,
    MemoMainSerializer,
    TagMainSerializer,
    
    TagInFormatedMemoSerializer,
    UserTagConfigSerializer)
    
from .ReplacedNumberLibrary import (
    NUM_TAGTYPE_MEMBER,
    NUM_TAG_STATUS_MAINLIST,
    NUM_TAG_STATUS_SUBLIST,
    NUM_MEMO_TYPE_FREE,
    NUM_MEMO_TYPE_FORMATTED)

#新規ユーザー作成　まず　UserTagConfigの初期値を設定して表示する
class NewUserSetView(views.APIView):

    def get(self,request):
        gets=request.GET
        
        facId=gets.get("facId")
        userName=gets.get("username")
        pwd=gets.get("pwd")

        newtag=TagMain.objects.create(strTagName=userName,numTagType=NUM_TAGTYPE_MEMBER,numTagRank=2,datePublish=datetime.now(),facilityId=Facility(pk=facId) ,strSuffix="")
        
        newOp=OperateUser.objects.create(strName=userName,keyFacility=Facility(pk=facId),password=pwd,datePublish=datetime.now(),tagId=newtag)

        
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

class ShowUserTagConfig(generics.ListAPIView):

    serializer_class=UserTagConfigSerializer
    #queryset=UserTagConfig.objects.all()
    def get_queryset(self):
        return   UserTagConfig.objects.filter(keyOperateUser__id=self.request.GET.get("userId"))

class UpdateUserTagConfig(views.APIView):

    def get(self,request):

        userId=request.GET.get("userId")
        tagId=request.GET.get("tagId")
        tagType=request.GET.get("tagstatus",default="-1")
        showlist=request.GET.get("isshow",default="false")

        target=UserTagConfig.objects.get(keyOperateUser__pk=userId,keyTag__pk=tagId)
        
        target.numTagStatus=tagType
        
        if showlist == "true":
            target.boolIsShownInList=True

        if showlist == "false":
            target.boolIsShownInList=False

        target.save()

        
        return Response(UserTagConfigSerializer(UserTagConfig.objects.filter(keyOperateUser__pk=userId),many=True).data)

class ResetUserTagConfig(views.APIView):

    def get(self,request):

        userId=request.GET.get("userId")

        targets=UserTagConfig.objects.filter(keyOperateUser__pk=userId).update(numTagStatus=-1,boolIsShownInList=False)

        return  Response({"userId":userId})






