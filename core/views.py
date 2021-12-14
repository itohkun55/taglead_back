from django.shortcuts import redirect, render
from django.views.generic import TemplateView,FormView
from datetime import datetime

from core.forms import MultiUserInsertForm, UserInsertForm
from core.models import Facility, OperateUser, TagMain, UserMakePool, UserTagConfig
from api.ReplacedNumberLibrary import NUM_STATUS_ENROLL, NUM_TAGTYPE_MEMBER, NUM_USER_RANK_MEMBER
# Create your views here.
class IndexView(TemplateView):
    template_name="index.html"

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context["title"]="Hello"

        return context

class InsertNewUserView(FormView):
    form_class=MultiUserInsertForm
    template_name="insertUser.html"

    def form_valid(self, form):
        
        return super().form_valid(form)


    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        if self.request.POST:
            print("post",self.request.POST["keyFacility"],self.request.POST["keyUser"])
        
        return context

    def post(self, request, *args, **kwargs):


        facId=request.POST["facility"]
        newuserList=request.POST.getlist("newUser")

        for user in newuserList:
            self.setUserData(facId,user)
        
        return redirect("")

    def setUserData(self,facId,userId):
        newuser=UserMakePool.objects.get(pk=int(userId))
        newuser.boolIsDone=True
        newuser.save()
        username=newuser.keyUser.last_name+newuser.keyUser.first_name

        newtag=TagMain.objects.create(
                strTagName=username,
                numTagType=NUM_TAGTYPE_MEMBER,
                numTagRank=100,
                datePublish=datetime.now(),
                facilityId=Facility(pk=facId) ,
                strSuffix="")
        
        newOp=OperateUser.objects.create(
                strName=username,
                keyFacility=Facility(pk=facId),
                datePublish=datetime.now(),
                tagId=newtag,
                numStatus=NUM_STATUS_ENROLL,
                numRank=NUM_USER_RANK_MEMBER,
                keyUser=newuser.keyUser
                )

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



        

