from django.db import models
from django.db.models.base import Model
from django.db.models.deletion import CASCADE, SET_NULL
from django.contrib.auth.models import User

# Create your models here.

class Facility(models.Model):
    
    #id	
    #id= models.IntegerField(verbose_name="ID")
    #施設名
    strName=models.CharField(verbose_name="施設名",max_length=50)
    #パスワード	
    password=models.CharField(verbose_name="パスワード", max_length=50)
    #登録日時	
    datePublish=models.DateField(verbose_name="登録日時", auto_now=False, auto_now_add=True)


    class Meta:
        verbose_name='施設'
        verbose_name_plural='施設'

    def __str__(self):
        return self.strName


class TagMain(models.Model):

    #id	
    #id= models.IntegerField(verbose_name="ID")
    #名前	
    strTagName=models.CharField(verbose_name="タグ名",max_length=20)
    #type	
    numTagType= models.IntegerField(verbose_name="タグタイプ")
    #重要度	
    numTagRank= models.IntegerField(verbose_name="タグランク")
    #登録日時	
    datePublish=models.DateTimeField(verbose_name="登録日",auto_now_add=True)
    #施設ID	
    facilityId=models.ForeignKey(Facility,verbose_name="所属施設",on_delete=models.CASCADE)
    #数値タグで使用した際の接尾辞
    strSuffix=models.CharField(verbose_name="数字タグの単位",blank=True,max_length=50)



    class Meta:
        verbose_name='タグ'
        verbose_name_plural='タグ'

    def __str__(self):
        return self.strTagName



class OperateUser(models.Model):
    
    #id	
    #id= models.IntegerField(verbose_name="ID")
    #名前
    strName=models.CharField(verbose_name="ユーザー名",max_length=50)
    #施設ID
    keyFacility=models.ForeignKey(Facility, verbose_name="施設", on_delete=models.CASCADE)
    #パスワード	認証をGoogleでやることにしたので削除
    #password=models.CharField(verbose_name="パスワード", max_length=50)
    #登録日時	
    datePublish=models.DateTimeField(verbose_name="登録日時")
    #ユーザーのタグ
    tagId=models.ForeignKey(TagMain,on_delete=models.CASCADE,default=1,related_name="main")
    #場所タグ　利用者タグが利用されたら同じ場所タグを持つ勤務者の一覧表示に表示される
    # いたずらに使用を複雑化させるため削除
    # keyTagPlace=models.ForeignKey(TagMain,verbose_name="所属タグ",on_delete=models.SET_NULL,null=True,related_name="place")

    #ユーザーのデータよりタグ名が優越するので、ユーザー追加の際はタグを新規に作ってから行うよう実装する
    #ユーザーの状態　退職などに対応
    numStatus=models.IntegerField(verbose_name="ステータス",default=1)
    #ユーザーのランク　各種権限に利用する
    numRank=models.IntegerField(verbose_name="ランク",default=1)

    keyUser=models.ForeignKey(User,verbose_name="利用ユーザ",on_delete=SET_NULL, null=True)

    class Meta:
        verbose_name='実施者'

        verbose_name_plural='グループ'

    def __str__(self):
        return self.strName

class UserMakePool(models.Model):
    keyUser=models.ForeignKey(User,verbose_name="待機ユーザ",on_delete=CASCADE)
    boolIsDone=models.BooleanField(verbose_name="登録待ちフラグ",default=False)


#タグのユーザーごと設定
class UserTagConfig(models.Model):
    #ユーザー
    keyOperateUser=models.ForeignKey(OperateUser,verbose_name="ユーザー",on_delete=models.CASCADE)
    #タグ
    keyTag=models.ForeignKey(TagMain, on_delete=models.CASCADE,verbose_name="タグ")
    #ユーザーの設定したステイタス
    numTagStatus=models.IntegerField(verbose_name="タグ設定",default=0)

    boolIsShownInList=models.BooleanField(verbose_name="一覧表示",default=False)


    class Meta:
        verbose_name='タグ利用設定'

        verbose_name_plural='タグ利用設定'

    def __str__(self):
        return self.keyOperateUser.strName+":"+self.keyTag.strTagName

class GuestMain(models.Model):
    
    strGuestName=models.CharField(verbose_name="利用者名",max_length=30)
    keyTagMain=models.ForeignKey(TagMain,verbose_name="所属タグ",on_delete=models.CASCADE,related_name="guest_main")
    keyPlaceTagMain=models.ForeignKey(TagMain,verbose_name="場所タグ",null=True,on_delete=models.SET_NULL,related_name="guest_place")
    numStatus=models.IntegerField(verbose_name="状態",default=1)

    class Meta:
        verbose_name='利用者メイン'
        verbose_name_plural='利用者メイン'

    def __str__(self):
        return self.strGuestName


class MemoMain(models.Model):
    #タグリスト
    strTaglist=models.CharField(verbose_name="タグリスト表示用",max_length=50)
    #メモタイプ　自由入力と形式入力でタイプを変える
    numMemotype=models.IntegerField(verbose_name="メモタイプ",default=1)

    #本文	
    strMainText=models.TextField(verbose_name="本文",blank=True)
    #送信者	
    keySender=models.ForeignKey(OperateUser,verbose_name="送信者",on_delete=models.CASCADE,null=False,default=1)
    #受信者(リスト）	
    listReceiver=models.CharField(verbose_name="受信者リスト",max_length=100,blank=True,null=True)
    #作成日時	
    datePublish=models.DateTimeField(verbose_name="作成日時")
    #登録日時	
    dateRegist=models.DateTimeField(verbose_name="登録日時")
    #スレッドID	
    keyReplyBase=models.ForeignKey("self",verbose_name="スレッド", on_delete=models.SET_NULL,  blank=True ,null=True,related_name="reply")
    #親ID	
    keyParent =models.ForeignKey("self",verbose_name="親メモ",on_delete=models.SET_NULL,blank=True ,null=True,related_name="parent")
    #転送ID	
    keyFollowId=models.ForeignKey("self",verbose_name="転送メモ",on_delete=models.SET_NULL, blank=True ,null=True,related_name="follow")

    keyFacility=models.ForeignKey(Facility,verbose_name="施設",on_delete=models.CASCADE,default=1)

    #strHasReadChecked=models.CharField(verbose_name="既読者",default="",max_length=100)
    boolHasModified=models.BooleanField(verbose_name="修正済みフラグ",blank=True,default=False)
    boolHasDeleted=models.BooleanField(verbose_name="削除済みフラグ",default=False)



    class Meta:
        verbose_name='メモ'
        verbose_name_plural='ノート'

    def __str__(self):
        return self.strMainText[:20]

#MemoMainに記録された内容のバックアップ。　修正・削除があった時のみ記録する
class MemoMainBackup (models.Model):
    keyMemoId=models.IntegerField(verbose_name="メモID")

    dateUpdate=models.DateField(verbose_name="更新日時")

    typeBackUpCase=models.CharField(verbose_name="バックアップ種類",default="none", max_length=20)

    charBackUpText=models.TextField("元の文")



class TagSearchIndex(models.Model):

    keyMemoMain=models.ForeignKey(MemoMain,verbose_name="メモ",on_delete=models.CASCADE)

    keyTagMain=models.ForeignKey(TagMain,verbose_name="タグ",on_delete=models.CASCADE)

    keyFacility=models.ForeignKey(Facility,verbose_name="施設",on_delete=models.CASCADE)

    dateRegist=models.DateTimeField(verbose_name="登録日時",null=True)


    class Meta:
        verbose_name='タグ検索'
        verbose_name_plural='タグ検索'

class TagInFormatedMemo(models.Model):

    keyTagMain=models.ForeignKey(TagMain,verbose_name="タグ",on_delete=models.CASCADE)
    keyFacility=models.ForeignKey(Facility,verbose_name="利用施設",default=1, on_delete=models.CASCADE)
    numTagPhase=models.IntegerField(verbose_name="フェーズ",default=-1)
    strGroup=models.CharField(verbose_name="グループ",max_length=50)
    strShow=models.CharField(verbose_name="表示用数列",max_length=100,blank=True)
    strHide=models.CharField(verbose_name="消滅用数列",max_length=100,blank=True)



    class Meta:
        verbose_name='誘導入力方タグ'
        verbose_name_plural='誘導入力方タグ'


    def __str__(self):
        return self.keyTagMain.strTagName


class IsUserReadInMemo(models.Model):

    keyMemoMain=models.ForeignKey(MemoMain,on_delete=models.CASCADE)

    keyOperateUser=models.ForeignKey(OperateUser,on_delete=models.CASCADE)

    hasFavorite=models.BooleanField(default=True)

    class Meta:
        verbose_name='既読'
        verbose_name_plural='既読'



class IsUserFavoriteInMemo(models.Model):

    keyMemoMain=models.ForeignKey(MemoMain,on_delete=models.CASCADE)

    keyOperateUser=models.ForeignKey(OperateUser,on_delete=models.CASCADE)

    hasFavorite=models.BooleanField(default=True)


    class Meta:
        verbose_name='お気に入り'
        verbose_name_plural='お気に入り'

class NoticeMain(models.Model):

    keyMemoMain=models.ForeignKey(MemoMain,on_delete=models.CASCADE)

    keyOperateUser=models.ForeignKey(OperateUser,on_delete=models.CASCADE)

    numNoticeType=models.IntegerField(verbose_name="通知タイプ",default=-1)

    boolHasRead=models.BooleanField(verbose_name="既読",default=False)

