from django.shortcuts import render
from rest_framework import routers,viewsets
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import views
from rest_framework import authentication, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication


#from drf_social_oauth2.authentication import SocialAuthentication
#from oauth2_provider.contrib.rest_framework import OAuth2Authentication

from django.contrib.auth.models import User
from datetime import datetime,timedelta,timezone
import pytz
from .Serializers import (
    TagLeadUserSerializer,
    OperatorUserSerializer,
    MemoMainSerializer,
    MemoMainInputSerializer,
    FollowInputSerializer,
    TagMainSerializer,
    TagInFormatedMemoSerializer,
    UserTagConfigSerializer,
    NoticeMainSerializer)
from core.models import (
    MemoMain,
    NoticeMain, 
    TagInFormatedMemo,
    TagMain,
    Facility,
    OperateUser,
    TagSearchIndex,
    UserTagConfig,
    IsUserReadInMemo,
    IsUserFavoriteInMemo,
    NoticeMain) 
from .ReplacedNumberLibrary import (
    NUM_TAGTYPE_MEMBER,
    NUM_TAG_STATUS_MAINLIST,
    NUM_TAG_STATUS_SUBLIST,
    NUM_MEMO_TYPE_FREE,
    NUM_MEMO_TYPE_FORMATTED)


#TagSearchで一度に検索をかける数
SEARCH_COUNT=300

# class TagLeadUserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = TagLeadUserSerializer

#     def get_queryset(self):
#         facId=self.request.GEY.get("facId")
#         userId=self.request.GEY.get("userId")

#         return OperateUser.objects.filter(pk=userId)
    


CHANGE_MAIN_VIEW="main";
CHANGE_TAG_VIEW="tag";
CHANGE_REPLY_VIEW="reply";


class TagLeadBaseView(views.APIView):

    def setRequestParams(self,request):

        # if  request.user.isauthenticated:
        #     print("AUthenticated")

        # else:
        #     print("none")

        gets=request.GET
        
        self.tagArray= gets.get("tagArray",default="").split(',')
        self.userId=gets.get("userId",default="-1")

        self.fromId= int(gets.get("fromId",default="-1"))
        self.facId=gets.get("facId",default="-1")
        self.mainText=gets.get("mainText",default="")
        self.datePublish=gets.get("datePublish",default="")
        self.dateRegist=gets.get("dateRegist",default="")
        self.followId=gets.get("followId")

        self.memoId=gets.get("memoId",default="-1")
        self.viewname=gets.get("viewname",default="-1")




#自由入力のタグリスト
class InitialDataListView(TagLeadBaseView):
#class TagMainDataListView(TagLeadTemplateView):

    #permission_classes = (permissions.AllowAny,)
   
    #permission_classes = [IsAuthenticated,  ]
    def get(self,request):


        auth_token = request.META.get('HTTP_AUTHORIZATION')

        print(auth_token)

        
        if  request.user.is_authenticated:
            print("AUthenticated")

        else:
            print("none")

        self.setRequestParams(request)

        res=self.getTagList()
        #print(res['main'])


        return Response({
            "user_list":OperatorUserSerializer(res["user_list"],many=True).data,
            "main": UserTagConfigSerializer(res['main'],many=True).data ,
            "sub":UserTagConfigSerializer(res['sub'],many=True).data,
            "all":TagMainSerializer(res['all'],many=True).data,
            "formatted":TagInFormatedMemoSerializer(res["formatted"],many=True).data,
            "noticeCount":res["noticeCount"]
            })


    def getTagList(self):
        user_list=OperateUser.objects.filter(keyFacility__id=self.facId)
        useTag=TagMain.objects.filter(facilityId__id=self.facId)
        mainTags=UserTagConfig.objects.filter(numTagStatus=NUM_TAG_STATUS_MAINLIST,keyOperateUser__id=self.userId, keyTag__in=useTag)
        subTags=UserTagConfig.objects.filter(numTagStatus=NUM_TAG_STATUS_SUBLIST,keyOperateUser__id=self.userId, keyTag__in=useTag)
        formatted=TagInFormatedMemo.objects.filter(keyTagMain__facilityId__id=self.facId)
        noticeCount=NoticeMain.objects.filter(keyOperateUser__id=self.userId,boolHasRead=False).count()

        return {"user_list":user_list,"main":mainTags,"sub":subTags,"all":useTag,"formatted":formatted,"noticeCount":noticeCount}


class TestAppendValueView(generics.ListAPIView):
    queryset=MemoMain.objects.all()
    serializer_class=MemoMainSerializer

    def get_queryset(self):
        dec=MemoMain.objects.all()

        # for d in dec:
        #     d["append"]="sss"


        return dec




class TagLeadTemplateView(TagLeadBaseView):

    def makeResultSet(self,res,flg):

        resset=[]
        readSet=[]
        favoriteSet=[]
        if len(res)>0:

            resset=MemoMainSerializer(res,many=True).data
            readSet=IsUserReadInMemo.objects.filter(keyMemoMain__in=res,keyOperateUser__pk=self.userId).values_list("keyMemoMain",flat=True)
            favoriteSet=IsUserFavoriteInMemo.objects.filter(keyMemoMain__in=res,keyOperateUser__pk=self.userId).values_list("keyMemoMain",flat=True)
        

        return {"timeline":resset,"read":readSet, "fav":favoriteSet, "end":flg,"fromId":self.fromId}


    def getMainListResult(self):
        
        resultmemos=[]
        endFlg=False

        firstFlg=True
        if self.fromId!=-1:
            firstFlg=False

        utc=pytz.UTC

        limitDate=utc.localize(datetime.utcnow())

        last= utc.localize(datetime.utcnow()) 

        tf=UserTagConfig.objects.filter(keyOperateUser__pk=self.userId,boolIsShownInList=True)
        tf_list=tf.values_list("keyTag",flat=True)

        #print(tf_list)



        #最終日時を先に取る
        for tag in tf_list:
            
                th= TagSearchIndex.objects.filter(keyTagMain__id=tag,keyFacility= self.facId).order_by('-dateRegist')
                if len(th)==0:
                    continue
                
                #print(th)
                th_last=th.last().dateRegist
                
                if last>th_last:
                    last=th_last

        #print("last:", last)
        while not endFlg  and len(resultmemos)<50:
            limitDate=limitDate-timedelta(days=30)

            tagSet=[]
            #print('tf_list',tf_list)
            for tag in tf_list:
                    #print(tag,self.facId)
                    if  firstFlg:

                        tags= TagSearchIndex.objects.order_by('-dateRegist').filter(keyTagMain__id=tag,  keyFacility=self.facId,dateRegist__gt=limitDate)
                    else:
                        tags= TagSearchIndex.objects.order_by('-dateRegist').filter(keyTagMain__id=tag, pk__lt=self.fromId,keyFacility=self.facId,dateRegist__gt=limitDate)
                    
                    if len(tags)==0:
                        #print(" NO TAGS ")
                        continue

                    sd=tags.values_list("keyMemoMain",flat=True)
                    #sd2=set(sd)
                    #print(sd)
                    tagSet.append(set(sd))
                    #このループでの最終
                    ths=tags.last()

                    if firstFlg or  ths.pk<self.fromId:
                        self.fromId=ths.pk

                    if last==ths.dateRegist:
                        endFlg=True

            resset=tagSet[0]
            for st in tagSet:
                resset=resset.union(st)

            resultmemos.extend(list(resset))
            if len(resultmemos)==0:
                return self.makeResultSet([],True)
        
        resultSet=MemoMain.objects.filter(pk__in=resultmemos,numMemotype=NUM_MEMO_TYPE_FREE).order_by('-dateRegist')
        #print(MemoMainSerializer(resultSet,many=True).data)
        
        return  self.makeResultSet(resultSet,endFlg)


    def getTagSearchResult(self):
        
        resultmemos=[]
        endFlg=False

        firstFlg=True
        if self.fromId!=-1:
            firstFlg=False

        utc=pytz.UTC

        limitDate=utc.localize(datetime.utcnow())

        last= utc.localize(datetime.utcnow()) 
        #最終日時を先に取る
        for tag in self.tagArray:
            th= TagSearchIndex.objects.filter(keyTagMain__id=tag,keyFacility= self.facId).order_by('-dateRegist')
            if len(th)==0:
                return self.makeResultSet([],False)
            th_last=th.last().dateRegist
               
            if last>th_last:
                last=th_last

        while not endFlg  and len(resultmemos)<50:
            limitDate=limitDate-timedelta(days=30)

            tagSet=[]
            for tag in self.tagArray:
                
                if  firstFlg:
                    tags= TagSearchIndex.objects.order_by('-dateRegist').filter(keyTagMain__id=tag,keyFacility=self.facId,dateRegist__gt=limitDate)
                else:
                    tags= TagSearchIndex.objects.order_by('-dateRegist').filter(keyTagMain__id=tag, pk__lt=self.fromId,keyFacility=self.facId,dateRegist__gt=limitDate)

                if len(tags)==0:
                    return self.makeResultSet([],False)
                sd=tags.values_list("keyMemoMain",flat=True)
                tagSet.append(set(sd))
                #このループでの最終
                ths=tags.last()

                if firstFlg or  ths.pk<self.fromId:
                    self.fromId=ths.pk
                if last==ths.dateRegist:
                    endFlg=True

            resset=tagSet[0]
            #print( "intersectioncheck",tagSet )
            for st in tagSet:
                resset=resset.intersection(st)
                
            resultmemos.extend(list(resset))
            if endFlg and len(resultmemos)==0:
                return self.makeResultSet([],endFlg)

        resultSet=MemoMain.objects.filter( pk__in=resultmemos).order_by('-dateRegist')

        return self.makeResultSet(resultSet,endFlg)



    def insertNewMemo(self):
        
        print(self.dateRegist,"dateRegist")
        print(self.datePublish,"datePublish")

        memo_serialize=None
        setdata={'strTaglist': ','.join(self.tagArray) ,'strMainText':self.mainText ,'numMemoType':NUM_MEMO_TYPE_FREE,  'keySender': self.userId  ,'listReceiver':"" ,'datePublish':self.datePublish,'dateRegist':self.dateRegist,'keyFollowId':self.followId}

        if self.followId!=-1:
            setdata['keyFollowId']=self.followId
            memo_serialize=FollowInputSerializer(data=setdata)
        else:
            memo_serialize=MemoMainInputSerializer(data=setdata)


        #is_valid()を入れてチェックしておく
        if not memo_serialize.is_valid():
            print(memo_serialize.errors)
            pass

        memo=memo_serialize.save()

        print("followCheck",self.followId, memo.keyFollowId)

        tcheck=TagMain.objects.filter(pk__in=self.tagArray)

        opArray=[]
        tagInsertArray=[]
        noticeArray=[]

        for tag in tcheck:
            if tag.numTagType==NUM_TAGTYPE_MEMBER:
                #TagMain検索後に行う事
                #勤務者タグから　宛先を取り出し、まとめておいて後で登録
                opuser=OperateUser.objects.get(tagId=tag)
                noticeArray.append(NoticeMain(keyMemoMain=memo,keyOperateUser=opuser,numNoticeType=1))

                opArray.append(str(opuser.pk))
                #勤務者タグの宛先に通知を送る
                
            tagInsertArray.append(TagSearchIndex(keyMemoMain=memo,keyTagMain=tag,keyFacility=Facility(pk=self.facId),dateRegist=self.dateRegist))

        if len(opArray)>0:
            print(opArray)
            memo.listReceiver=",".join(opArray)
            memo.save()

        #TagSearchIndexにタグ情報を入れる
        
        TagSearchIndex.objects.bulk_create(tagInsertArray)
        NoticeMain.objects.bulk_create(noticeArray)

        #戻り値として登録したクエリーセットを返す　Replyではこれに情報を追加する
        return memo


    def insertFormattedMemo(self):
        
        print(self.dateRegist,"dateRegist")
        print(self.datePublish,"datePublish")

        memo_serialize=MemoMainSerializer(data={'strTaglist': ','.join(self.tagArray) ,'strMainText':self.mainText ,'numMemoType':NUM_MEMO_TYPE_FORMATTED,'keySender': self.userId  ,'listReceiver':"" ,'datePublish':self.datePublish,'dateRegist':self.dateRegist,'keyFollowId':-1})

        #is_valid()を入れてチェックしておく
        if not memo_serialize.is_valid():
            print(memo_serialize.errors)
            pass

        memo=memo_serialize.save()
        #数字タグを外す
        twArray=[]
        for tw in self.tagArray:
            if  ":" not in  tw:
                twArray.append(tw)

        tcheck=TagMain.objects.filter(pk__in=twArray)

        opArray=[]
        tagInsertArray=[]

        for tag in tcheck:
                
            tagInsertArray.append(TagSearchIndex(keyMemoMain=memo,keyTagMain=tag,keyFacility=Facility(pk=self.facId),dateRegist=self.dateRegist))
        #TagSearchIndexにタグ情報を入れる
        
        TagSearchIndex.objects.bulk_create(tagInsertArray)


#形式入力のデータのロード
class FormattedTagListView(generics.ListAPIView):
    queryset=TagInFormatedMemo.objects.all()

    serializer_class=TagInFormatedMemoSerializer

    def get_queryset(self):
        facId=self.request.GET.get("facId")
        return TagInFormatedMemo.objects.filter(keyTagMain__keyFacility__id=facId)

    
class MainListView (TagLeadTemplateView):
    
    #一覧ビューの仕様 構造としては取得タグを設定からとってTagSearchをOR検索にするだけ。
    #一瞬合同にしようかと思ったが、今後それぞれが別機能になると思ったので親クラスだけまとめた。

    def get(self,request):
        self.setRequestParams(request)
        
        return Response(self.getMainListResult())
#class ReadCheckInMainListView(MainListView):
class TagSearchView (TagLeadTemplateView):

    #serializer_class=MemoMainSerializer

    def get(self,request):

        self.setRequestParams(request)
        
        return Response(self.getTagSearchResult())

class NoticeMainView(TagLeadTemplateView):

    def get(self,request):
        self.setRequestParams(request)

        return Response(self.getNoticeResult())


    #通知一覧を表示する　固定量以上は削除する
    DELETE_COUNT=100

    def getNoticeResult(self):

        allnotice= NoticeMain.objects.filter(keyOperateUser__pk=self.userId).order_by('-pk')

        count=0
        newCount=0
        shownotice=[]
        for noti in allnotice:
            count=count+1

            if count < self.DELETE_COUNT:
                #通知の既読をチェック
                if not noti.boolHasRead:
                    newCount=newCount+1
                    noti.boolHasRead=True
                    noti.save()
                shownotice.append(noti)
            else:
                noti.delete()

        return  {"notices":NoticeMainSerializer(shownotice,many=True).data,"new":newCount} 


class MemoInsertView(TagLeadTemplateView):
    def get(self,request):
        self.setRequestParams(request)
        self.insertNewMemo()
        
        if self.viewname==CHANGE_MAIN_VIEW:
            return Response(self.getMainListResult())
        else:
            return Response(self.getTagSearchResult())
        

class FormattedMemoInsertView(TagLeadTemplateView):

    def get(self,request):

        self.setRequestParams(request)

        self.insertFormattedMemo()
        
        if self.viewname==CHANGE_MAIN_VIEW:
            return Response(self.getMainListResult())
        else :
            return Response(self.getTagSearchResult())


class ReplyThreadView(TagLeadTemplateView):

    def get(self,request):
        self.setRequestParams(request)

        return Response(self.getReplyList())


    def getReplyList(self):
        print("getReplyList")
        #リプライの元データを引く
        try:
            baseMemo=MemoMain.objects.get(pk=self.memoId)
        except MemoMain.DoesNotExist:
            print(" なっちゃねーな ")
        print(baseMemo)
        if not baseMemo.keyReplyBase:
            return self.makeResultSet([baseMemo],True) 

        return  self.makeResultSet(MemoMain.objects.filter(keyReplyBase=baseMemo.keyReplyBase),True)

class ReplyInsertView(ReplyThreadView):

    def get(self,request):
        self.setRequestParams(request)
        self.replyInsert()

        return Response(self.getReplyList())

    def replyInsert(self):
        print("memoId",self.memoId)

        memo=self.insertNewMemo()
        baseMemo=MemoMain.objects.get(pk=self.memoId)
        
        if not baseMemo.keyReplyBase:

            baseMemo.keyReplyBase=baseMemo
            baseMemo.save()
            
        memo.keyReplyBase=baseMemo.keyReplyBase
        memo.keyParent=baseMemo
        memo.save()

        #そのスレッドに書き込みをしたすべての人に通知を作成する
        allRep=MemoMain.objects.filter(keyReplyBase=baseMemo.keyReplyBase)

        noticeArray=[]
        for rep in allRep:
            noticeArray.append(NoticeMain(keyMemoMain=memo,keyOperateUser=rep.keySender,numNoticeType=2))

        NoticeMain.objects.bulk_create(noticeArray)

        #ターゲットが差し替えになったので
        self.memoId=memo.pk

class SetReadMarkView(views.APIView):

    def get(self,request):

        userId=request.GET.get("userId")
        memoId=request.GET.get("memoId")
        readMark=request.GET.get("read")

        if readMark=="true":

            IsUserReadInMemo.objects.create(keyMemoMain=MemoMain(pk=memoId),keyOperateUser=OperateUser(pk=userId))
        elif readMark=="false":
            IsUserReadInMemo.objects.filter(keyMemoMain=MemoMain(pk=memoId),keyOperateUser=OperateUser(pk=userId)).delete()

        return Response({"userId":userId,"memoId":memoId,"read":readMark})



class SetFavoriteMarkView(views.APIView):

    def get(self,request):

        userId=request.GET.get("userId")
        memoId=request.GET.get("memoId")
        favMark=request.GET.get("fav")

        if favMark=="true":

            IsUserFavoriteInMemo.objects.create(keyMemoMain=MemoMain(pk=memoId),keyOperateUser=OperateUser(pk=userId))
        elif favMark=="false":
            IsUserFavoriteInMemo.objects.filter(keyMemoMain=MemoMain(pk=memoId),keyOperateUser=OperateUser(pk=userId)).delete()

        return Response({"userId":userId,"memoId":memoId,"read":favMark})

class ShowUserFavoriteView(TagLeadTemplateView):

    def get(self,request):

        self.setRequestParams(request)

        fav=IsUserFavoriteInMemo.objects.filter(keyOperateUser=OperateUser(pk=self.userId))
        results=[]
        for f in fav:
            results.append(f.keyMemoMain)

        return Response(self.makeResultSet(results,True))

















    