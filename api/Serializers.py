
from django.db.models import fields
from core.models import MemoMain, OperateUser, TagSearchIndex,TagMain,TagInFormatedMemo,UserTagConfig,NoticeMain,IsUserFavoriteInMemo
from django.contrib.auth.models import User
from django.db import models
from rest_framework import serializers, viewsets

class TagLeadUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


class OperatorUserSerializer(serializers.ModelSerializer):
    class Meta:
        model=OperateUser
        fields=['id','strName','password']


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model=MemoMain
        fields=( 'id','strTaglist','strMainText','keySender','listReceiver','datePublish','dateRegist')


class MemoMainSerializer(serializers.ModelSerializer):
    keyFollowId=FollowSerializer(many=False,read_only=True)

    class Meta:
        model=MemoMain
        fields=('id','strTaglist','strMainText','numMemotype','keySender','listReceiver','datePublish','dateRegist','keyFollowId','keyParent')

#メモ入力用シリアライザ　転送入力も同じものを使う
class MemoMainInputSerializer(serializers.ModelSerializer):

    class Meta:
        model=MemoMain
        fields=('strTaglist','strMainText','numMemotype','keySender','datePublish','dateRegist')

#メモ入力用シリアライザ　転送入力も同じものを使う
class FollowInputSerializer(serializers.ModelSerializer):

    class Meta:
        model=MemoMain
        fields=('strTaglist','strMainText','numMemotype','keySender','datePublish','dateRegist','keyFollowId')




class TagMainSerializer(serializers.ModelSerializer):
    class Meta:
        model=TagMain
        fields=('id','strTagName','numTagType')

class TagInFormatedMemoSerializer(serializers.ModelSerializer):
    keyTagMain=TagMainSerializer(many=False)

    class Meta:
        model=TagInFormatedMemo
        fields=('id','keyTagMain','numTagPhase','strGroup','strShow','strHide')

class UserTagConfigSerializer(serializers.ModelSerializer):
    #keyTag=TagMainSerializer(many=False)
    
    class Meta:
            model=UserTagConfig
            fields=('keyOperateUser','keyTag','numTagStatus','boolIsShownInList')

class UserTagConfigInsertSerializer(serializers.ModelSerializer):
    keyTag=TagMainSerializer(many=False)
    
    class Meta:
            model=UserTagConfig
            fields=('keyOperateUser','keyTag','numTagStatus','boolIsShownInList')



class TagSearchIndexSerializer(serializers.ModelSerializer):

    class Meta:
        model=TagSearchIndex
        fields=('keyMemoMain','keyTagMain','keyFacility','dateRegist')    


class NoticeMainSerializer(serializers.ModelSerializer):
    keyMemoMain=MemoMainSerializer(many=False)

    class Meta:
        model=NoticeMain
        fields=('id','keyMemoMain','keyOperateUser','numNoticeType')

class ShowFavoriteSerializer(serializers.ModelSerializer):
    keyMemoMain=MemoMainSerializer(many=False)

    class Meta:
        model=IsUserFavoriteInMemo
        fields=('keyMemoMain','keyOperateUser')
