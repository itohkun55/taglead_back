from api.SendMessageLibrary import (
    FORMATTED_INSERT_MEMO, 
    HAS_NO_ACCOUNT, 
    HAS_NO_RESULT,
    HAS_NO_PERMISSION,
    INSERT_VARIDATION_ERROR,
    HAS_NO_VALID_USER,
    HAS_NO_DATA
    )
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import views
#from rest_framework import authentication, permissions
from rest_framework.permissions import IsAuthenticated
#from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from datetime import date, datetime as dt
from dateutil.relativedelta import relativedelta

from drf_social_oauth2.authentication import SocialAuthentication
from oauth2_provider.contrib.rest_framework import OAuth2Authentication

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
    UserMakePool,
    UserTagConfig,
    IsUserReadInMemo,
    IsUserFavoriteInMemo,
    NoticeMain,
    MemoMainBackup) 
from .ReplacedNumberLibrary import (
    NUM_COMMON_TAG_FACILITY,
    NUM_TAGTYPE_MEMBER,
    NUM_TAG_STATUS_MAINLIST,
    NUM_TAG_STATUS_SUBLIST,
    NUM_MEMO_TYPE_FREE,
    NUM_MEMO_TYPE_FORMATTED)



#TagSearchで一度に検索をかける数
SEARCH_COUNT=300

CHANGE_MAIN_VIEW="main";
CHANGE_TAG_VIEW="tag";
CHANGE_REPLY_VIEW="reply";


class TestRealView(views.APIView):
    def get(self,request):
        print("Welcome!")

        return Response({"ok":"OK!"})


class TagLeadBaseView(views.APIView):
    #認証　このクラスのサブクラスは全てここで認証済み
    authentication_classes=[OAuth2Authentication,SocialAuthentication]
    permission_classes = [IsAuthenticated,  ]


    def setRequestParams(self,request):
        self.errorFlg=False
        gets=request.GET
        
        self.tagArray= gets.get("tagArray",default="").split(',')
        #空文字対応
        if self.tagArray==['']:
            self.tagArray=[]

        self.settags= gets.get("settags",default="").split(',')
        #空文字対応
        if self.settags==['']:
            self.settags=[]
        
        self.fromDay=gets.get("fromDay",default="")
        self.mainText=gets.get("mainText",default="")
        self.datePublish=gets.get("datePublish",default="")
        self.dateRegist=gets.get("dateRegist",default="")
        self.followId=int(gets.get("followId",default="-1"))

        self.memoId=gets.get("memoId",default="-1")
        self.viewname=gets.get("viewname",default="-1")
        self.userId=-1
        self.facId=-1

        try:
            targetUser=OperateUser.objects.get(keyUser=request.user)
            self.userId=targetUser.pk
            self.userRank=targetUser.numRank
            self.username=targetUser.strName

            self.facId=targetUser.keyFacility.pk

        except OperateUser.DoesNotExist:
            print("初期認証エラー")
            # try:
            #     userCheck=UserMakePool.objects.get(keyUser=request.user,boolIsDone=False)
            # except UserMakePool.DoesNotExist:
            #     UserMakePool.objects.create(keyUser=request.user)
            
            
            self.errorFlg=True
            self.errorMsg=HAS_NO_ACCOUNT
            self.errorCode=1

        

#初期情報のロード
class InitialDataListView(TagLeadBaseView):

    def get(self,request):
        username=""

        try:
            userCheck=UserMakePool.objects.get(keyUser=request.user,boolIsDone=False)
        except UserMakePool.DoesNotExist:
            UserMakePool.objects.create(keyUser=request.user)
            return Response({"errorFlg":True,"errorMsg":HAS_NO_ACCOUNT,"errorCode":1})
        
        
        self.setRequestParams(request)

        if self.errorFlg:
            return Response({"errorFlg":True,"errorMsg":self.errorMsg,"errorCode":self.errorCode}) 

        res=self.getTagList()
        #print("userRank",self.userRank)
        
        if self.errorFlg:
            return Response({"errorFlg":True,"errorMsg":self.errorMsg,"errorCode":self.errorCode}) 


        return Response({
            "user_list":OperatorUserSerializer(res["user_list"],many=True).data,
            "main": UserTagConfigSerializer(res['main'],many=True).data ,
            "sub":UserTagConfigSerializer(res['sub'],many=True).data,
            "all":TagMainSerializer(res['all'],many=True).data,
            "formatted":TagInFormatedMemoSerializer(res["formatted"],many=True).data,
            "noticeCount":res["noticeCount"],
            "userId":self.userId,
            "username":self.username,
            "userRank":self.userRank
            })


    def getTagList(self):
        useFac=[NUM_COMMON_TAG_FACILITY,self.facId]

        user_list=OperateUser.objects.filter(keyFacility__id=self.facId)
        useTag=TagMain.objects.filter(facilityId__id__in=useFac)
        mainTags=UserTagConfig.objects.filter(numTagStatus=NUM_TAG_STATUS_MAINLIST,keyOperateUser__id=self.userId, keyTag__in=useTag)
        subTags=UserTagConfig.objects.filter(numTagStatus=NUM_TAG_STATUS_SUBLIST,keyOperateUser__id=self.userId, keyTag__in=useTag)
        formatted=TagInFormatedMemo.objects.filter(keyFacility=self.facId)
        noticeCount=NoticeMain.objects.filter(keyOperateUser__id=self.userId,boolHasRead=False).count()        

        return {"user_list":user_list,"main":mainTags,"sub":subTags,"all":useTag,"formatted":formatted,"noticeCount":noticeCount}



class TagLeadTemplateView(TagLeadBaseView):

    #メモの検索結果を送信する際のまとめ関数
    def makeResultSet(self,res,flg=True):

        resset=[]
        readSet=[]
        favoriteSet=[]
        if len(res)>0:

            resset=MemoMainSerializer(res,many=True).data
            readSet=IsUserReadInMemo.objects.filter(keyMemoMain__in=res,keyOperateUser__pk=self.userId).values_list("keyMemoMain",flat=True)
            favoriteSet=IsUserFavoriteInMemo.objects.filter(keyMemoMain__in=res,keyOperateUser__pk=self.userId).values_list("keyMemoMain",flat=True)
        # print(" リリース直前 ",flg)
        return {"timeline":resset,"read":readSet, "fav":favoriteSet, "endflg":flg}

    #一覧用検索
    def getMainListResult(self):
        
        resultmemos=[]
        endFlg=False

        utc=pytz.UTC

        #日にち指定がなかった時は1年後までを検索範囲にする
        if self.fromDay=="-1":
            
            self.fromDay=pytz.UTC.localize(datetime.utcnow())+relativedelta(years=+1)
            limitDate = utc.localize(datetime.utcnow())
        else:

            limitDate = utc.localize(dt.strptime(self.fromDay,'%Y-%m-%dT%H:%M:%S.%fZ'))
        last= limitDate

        tf=UserTagConfig.objects.filter(keyOperateUser__pk=self.userId,boolIsShownInList=True)
        tf_list=tf.values_list("keyTag",flat=True)

        #最終日時を先に取る
        for tag in tf_list:
                #            
                th= TagSearchIndex.objects.filter(keyTagMain__id=tag,keyFacility__pk= self.facId).order_by('-dateRegist')
                if len(th)==0:
                    #一覧検索で対象タグが存在しない　→　スルー
                    continue
                th_last=th.last().dateRegist
                #該当タグがある中で一番古いものを最古にして、ここまでは検索をさかのぼる指針とする
                if last>th_last:
                    last=th_last

        #lastがさっきと全く同じ→検索結果が一つもない
        if last==limitDate:
            return self.makeResultSet([],True)

        print("last:", last)
        #最後まで来たか今回送るメモが50件に達するまで検索を続ける
        while not endFlg  and len(resultmemos)<20:
            
            limitDate=limitDate-timedelta(days=30)
            print("limitdate",limitDate,self.fromDay)

            tagSet=[]
            for tag in tf_list:
                    tags= TagSearchIndex.objects.order_by('-dateRegist').filter(keyTagMain__id=tag,  dateRegist__lt=self.fromDay,keyFacility__pk=self.facId,dateRegist__gt=limitDate)
                    
                    if len(tags)==0:
                        #print(" NO TAGS ")
                        continue

                    sd=tags.values_list("keyMemoMain",flat=True)
                    tagSet.append(set(sd))
                    #このループでの最終
                    ths=tags.last()

                    if last==ths.dateRegist:
                        endFlg=True

            if len(tagSet)==0:
                #print("tagset 0 end")
                #return  self.makeResultSet([],endFlg)
                continue
            resset=tagSet[0]
            for st in tagSet:
                resset=resset.union(st)

            resultmemos.extend(list(resset))
            if len(resultmemos)==0:
                return self.makeResultSet([],True)
        
        resultSet=MemoMain.objects.filter(pk__in=resultmemos,numMemotype=NUM_MEMO_TYPE_FREE).order_by('-dateRegist')
        print(" ok end")
        return  self.makeResultSet(resultSet,endFlg)


    def getTagSearchResult(self):
        
        resultmemos=[]
        endFlg=False

        utc=pytz.UTC

        if self.fromDay=="-1":
    
            self.fromDay=pytz.UTC.localize(datetime.utcnow())+relativedelta(years=+1)
            limitDate = utc.localize(datetime.utcnow())
        else:

            limitDate = utc.localize(dt.strptime(self.fromDay,'%Y-%m-%dT%H:%M:%S.%fZ'))
        
        last= limitDate
        
        #最終日時を先に取る
        if len(self.tagArray)==0:
            return self.makeResultSet([],True)

        for tag in self.tagArray:
            th= TagSearchIndex.objects.filter(keyTagMain__id=tag,keyFacility__pk= self.facId).order_by('-dateRegist')
            if len(th)==0:
                return self.makeResultSet([],True)
            th_last=th.last().dateRegist
               
            if last>th_last:
                last=th_last

        while not endFlg  and len(resultmemos)<50:
            limitDate=limitDate-timedelta(days=30)

            tagSet=[]
            for tag in self.tagArray:
                
                tags= TagSearchIndex.objects.order_by('-dateRegist').filter(keyTagMain__id=tag,dateRegist__lt=self.fromDay,keyFacility__pk=self.facId,dateRegist__gt=limitDate)

                if len(tags)==0:                
                    print("check has TagSearchIndex 308" )
                    return self.makeResultSet([],True)
                sd=tags.values_list("keyMemoMain",flat=True)
                tagSet.append(set(sd))
                #このループでの最終
                ths=tags.last()
                if last==ths.dateRegist:
                    endFlg=True

            resset=tagSet[0]
            for st in tagSet:
                resset=resset.intersection(st)
            
            resultmemos.extend(list(resset))
            if endFlg and len(resultmemos)==0:
                return self.makeResultSet([],endFlg)

        resultSet=MemoMain.objects.filter( pk__in=resultmemos).order_by('-dateRegist')

        return self.makeResultSet(resultSet,endFlg)



    def insertNewMemo(self):
        
        #print(self.dateRegist,"dateRegist")
        #print(self.datePublish,"datePublish")

        memo_serialize=None
        setdata={'strTaglist': ','.join(self.settags) ,'strMainText':self.mainText ,'numMemoType':NUM_MEMO_TYPE_FREE,  'keySender': self.userId  ,'listReceiver':"" ,'datePublish':self.datePublish,'dateRegist':self.dateRegist}

        #print("validate check",self.followId)
        if self.followId==-1:
            print("no follow")
            memo_serialize=MemoMainInputSerializer(data=setdata)
        else:
            setdata['keyFollowId']=self.followId
            memo_serialize=FollowInputSerializer(data=setdata)

        #is_valid()を入れてチェックしておく
        if not memo_serialize.is_valid():
            print(memo_serialize.errors)
            self.errorFlg=True
            self.errorMsg=INSERT_VARIDATION_ERROR
            self.errorCode=3
            return

        memo=memo_serialize.save()

        #print("followCheck",self.followId, memo.keyFollowId)

        tcheck=TagMain.objects.filter(pk__in=self.settags)

        opArray=[]
        tagInsertArray=[]
        noticeArray=[]

        for tag in tcheck:
            if tag.numTagType==NUM_TAGTYPE_MEMBER:
                #TagMain検索後に行う事
                #勤務者タグから　宛先を取り出し、まとめておいて後で登録
                try:
                    opuser=OperateUser.objects.get(tagId=tag)
                    noticeArray.append(NoticeMain(keyMemoMain=memo,keyOperateUser=opuser,numNoticeType=1))

                    opArray.append(str(opuser.pk))
                    #勤務者タグの宛先に通知を送る
                except OperateUser.DoesNotExist:
                    self.errorFlg=True
                    self.errorCode=4
                    self.errorMsg=HAS_NO_VALID_USER+str(tag.pk)
                    return
                
            tagInsertArray.append(TagSearchIndex(keyMemoMain=memo,keyTagMain=tag,keyFacility=Facility(pk=self.facId),dateRegist=self.dateRegist))

        if len(opArray)>0:
            memo.listReceiver=",".join(opArray)
            memo.save()

        #送信者自身のタグも入れる
        sender=OperateUser.objects.get(keyUser=self.request.user)
        tagInsertArray.append(TagSearchIndex(keyMemoMain=memo,keyTagMain=sender.tagId,keyFacility=Facility(pk=self.facId),dateRegist=self.dateRegist))

        #TagSearchIndexにタグ情報を入れる
        
        TagSearchIndex.objects.bulk_create(tagInsertArray)
        NoticeMain.objects.bulk_create(noticeArray)

        #戻り値として登録したクエリーセットを返す　Replyではこれに情報を追加する
        return memo


    def insertFormattedMemo(self):
        
        #print(self.dateRegist,"dateRegist")
        #print(self.datePublish,"datePublish")
        senddata={'strTaglist': ','.join(self.settags) ,'strMainText':self.mainText ,'numMemotype':NUM_MEMO_TYPE_FORMATTED,'keySender': self.userId  ,'listReceiver':"" ,'datePublish':self.datePublish,'dateRegist':self.dateRegist,'keyFollowId':-1}

        memo_serialize=MemoMainSerializer(data=senddata)

        #is_valid()を入れてチェックしておく
        if not memo_serialize.is_valid():
            self.errorFlg=True
            self.errorMsg= FORMATTED_INSERT_MEMO
            self.errorCode=4
            return

            

        memo= memo_serialize.save()
        #print(" formatted :",memo_serialize.data)
        #数字タグを外す
        twArray=[]
        for tw in self.settags:
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
        return TagInFormatedMemo.objects.filter(keyTagMain__keyFacility__pk=facId)

    
class MainListView (TagLeadTemplateView):
    
    #一覧ビューの仕様 構造としては取得タグを設定からとってTagSearchをOR検索にするだけ。
    #一瞬合同にしようかと思ったが、今後それぞれが別機能になると思ったので親クラスだけまとめた。

    def get(self,request):
        self.setRequestParams(request)
        if self.errorFlg:
            return Response({"errorFlg":True,"errorMsg":self.errorMsg,"errorCode":self.errorCode}) 

        
        return Response(self.getMainListResult())
#class ReadCheckInMainListView(MainListView):
class TagSearchView (TagLeadTemplateView):

    #serializer_class=MemoMainSerializer

    def get(self,request):

        self.setRequestParams(request)
        
        if self.errorFlg:
            return Response({"errorFlg":True,"errorMsg":self.errorMsg}) 

        return Response(self.getTagSearchResult())

class NoticeMainView(TagLeadTemplateView):

    def get(self,request):
        self.setRequestParams(request)

        if self.errorFlg:
            return Response({"errorFlg":True,"errorMsg":self.errorMsg}) 


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
        
        if self.errorFlg:
            return Response({"errorFlg":True,"errorMsg":self.errorMsg}) 

        self.insertNewMemo()
        if self.errorFlg:
            return Response({"errorFlg":True,"errorMsg":self.errorMsg}) 
        

        return Response({"ok":True})
        

class FormattedMemoInsertView(TagLeadTemplateView):

    def get(self,request):

        self.setRequestParams(request)
        if self.errorFlg:
            return Response({"errorFlg":True,"errorMsg":self.errorMsg}) 
        
        self.insertFormattedMemo()
        
        if self.errorFlg:
            return Response({"errorFlg":True,"errorMsg":self.errorMsg})

        return Response({"ok":True})
        



class MemoDeleteView(TagLeadTemplateView):
    def get(self,request):
        self.setRequestParams(request)
        
        if self.errorFlg:
            return Response({"errorFlg":True,"errorMsg":self.errorMsg})

        self.deleteMemo()
        
        if self.errorFlg:
            return Response({"errorFlg":True,"errorMsg":self.errorMsg})

        return Response({"ok":"ok"})



    def deleteMemo(self):
        #memoTarget={}
        try:
            memoTarget=MemoMain.objects.get(pk=self.memoId)
            
            print("memoTarget",memoTarget.keySender.id,self.userId)

        except MemoMain.DoesNotExist:
            self.errorFlg=True
            self.errorMsg=HAS_NO_RESULT+self.memoId
            return

        if memoTarget.keySender.id!=self.userId:
            #送信者以外は削除できない
            self.errorFlg=True
            self.errorMsg=HAS_NO_PERMISSION+str(self.userId)
            return

        #完全削除可能チェック　すでに他のメモと関係性が出来ていたら文章の削除のみとする
        canDelete=True
        if memoTarget.keyReplyBase:
            canDelete=False
        #メモを残すかチェック
        #親になっているメモはNG
        try :
            MemoMain.objects.get(keyParent=memoTarget)
            canDelete=False
        except MemoMain.DoesNotExist:
            pass
        
        #フォローされているメモはNG
        try :
            MemoMain.objects.get(keyFollowId=memoTarget)
            canDelete=False
        except MemoMain.DoesNotExist:
            pass
        
        #既読になっているメモはNG
        try:
            IsUserReadInMemo.objects.get(keyMemoMain=memoTarget)
            canDelete=False
        except IsUserReadInMemo.DoesNotExist:
            pass

        #お気に入りになっているメモはNG
        try:
            IsUserFavoriteInMemo.objects.get(keyMemoMain=memoTarget)
            canDelete=False
        except IsUserFavoriteInMemo.DoesNotExist:
            pass

        #バックアップ
        MemoMainBackup.objects.create(keyMemoId=self.memoId,typeBackUpCase="modify", dateUpdate=datetime.now(),charBackUpText=memoTarget.strMainText)

        #NGになっていないメモは削除可能　TagSearchIndexは勝手に削除されるはず
        if canDelete:
            memoTarget.delete()

        else:
            #NGになっているメモは本文だけ削除する
            memoTarget.strMainText=""
            memoTarget.boolHasDeleted=True
            memoTarget.save()


class MemoModifyView(TagLeadTemplateView):

    def get(self,request):
        self.setRequestParams(request)

        #バックアップ
        bText=""
        
        #本文と設定日時のみ更新可能
        try:
            memoTarget=MemoMain.objects.get(pk=self.memoId)
            bText=memoTarget.strMainText
            MemoMainBackup.objects.create(keyMemoId=self.memoId,typeBackUpCase="modify", dateUpdate=datetime.now(),charBackUpText=bText)

            memoTarget.strMainText=self.mainText
            #memoTarget.dataRegist=self.dateRegist
            #更新済みフラグが付く
            memoTarget.boolHasModified=True
            memoTarget.save()
            return Response(MemoMainSerializer(memoTarget).data)


        except MemoMain.DoesNotExist:
            self.errorFlg=True
            self.errorCode=6
            self.errorMsg= HAS_NO_DATA+self.memoId
            return Response({"error":True,"errorMsg":self.errorMsg})
        


class ReplyThreadView(TagLeadTemplateView):

    def get(self,request):
        self.setRequestParams(request)
        if self.errorFlg:
            return Response({"error":True,"errorMsg":self.errorMsg,"errorCode":self.errorCode}) 

        res=self.getReplyList()
        if self.errorFlg:
            return Response({"error":True,"errorMsg":self.errorMsg,"errorCode":self.errorCode}) 


        return Response(res)


    def getReplyList(self):
        #print("getReplyList")
        #リプライの元データを引く
        try:
            baseMemo=MemoMain.objects.get(pk=self.memoId)
        except MemoMain.DoesNotExist:
            #print(" なっちゃねーな ")
            self.errorFlg=True
            self.errorCode=5
            self.errorMsg=HAS_NO_DATA+self.memoId
            return

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
        try:
            baseMemo=MemoMain.objects.get(pk=self.memoId)
        except MemoMain.DoesNotExist:
            self.errorFlg=True
            self.errorCode=6
            self.errorMsg=HAS_NO_DATA+self.memoId
            return
            
        
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

class SetReadMarkView(TagLeadBaseView):

    def get(self,request):
        self.setRequestParams(request)

        memoId=request.GET.get("memoId")
        readMark=request.GET.get("read")

        if readMark=="true":

            IsUserReadInMemo.objects.create(keyMemoMain=MemoMain(pk=memoId),keyOperateUser=OperateUser(pk=self.userId))
        elif readMark=="false":
            IsUserReadInMemo.objects.filter(keyMemoMain=MemoMain(pk=memoId),keyOperateUser=OperateUser(pk=self.userId)).delete()

        return Response({"userId":self.userId,"memoId":memoId,"read":readMark})



class SetFavoriteMarkView(TagLeadBaseView):

    def get(self,request):
        self.setRequestParams(request)

        memoId=request.GET.get("memoId")
        favMark=request.GET.get("fav")

        if favMark=="true":

            IsUserFavoriteInMemo.objects.create(keyMemoMain=MemoMain(pk=memoId),keyOperateUser=OperateUser(pk=self.userId))
        elif favMark=="false":
            IsUserFavoriteInMemo.objects.filter(keyMemoMain=MemoMain(pk=memoId),keyOperateUser=OperateUser(pk=self.userId)).delete()

        return Response({"userId":self.userId,"memoId":memoId,"read":favMark})

class ShowUserFavoriteView(TagLeadTemplateView):

    def get(self,request):

        self.setRequestParams(request)

        fav=IsUserFavoriteInMemo.objects.filter(keyOperateUser=OperateUser(pk=self.userId))
        results=[]
        for f in fav:
            results.append(f.keyMemoMain)

        return Response(self.makeResultSet(results,True))

















    