from django import forms
from django.forms import ModelForm, fields, models,ModelChoiceField
from .models import Facility, OperateUser,UserMakePool

class UserChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return (obj.keyUser.last_name +" "+ obj.keyUser.first_name )


class UserInsertForm(ModelForm):
    keyUser=UserChoiceField(queryset=UserMakePool.objects.filter(boolIsDone=False))

    class Meta:
        model=OperateUser
        fields=["keyFacility","keyUser"]

    # def __init__(self):
    #     super(UserInsertForm,self).__init__(*args,**kwargs)
    #     users=UserMakePool.objects.filter(boolIsDone=False).values_list("keyUser",flat=True)
        
    #     self.fields["keyUser"].queryset=users


class MultiUserChoiceField(models.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return (obj.keyUser.last_name +" "+ obj.keyUser.first_name )



class MultiUserInsertForm(forms.Form):
    chooseFacility=Facility.objects.all().values_list('pk','strName')


    facility=forms.fields.ChoiceField(
        label="施設",
        choices=chooseFacility
    )

    # chooseUser=UserMakePool.objects.filter(boolIsDone=False)
    # newUsers=forms.MultipleChoiceField(
    #     choices=chooseUser
    # )

    newUser=MultiUserChoiceField(
        queryset=UserMakePool.objects.filter(boolIsDone=False),
        label="未登録ユーザー",
        required=False,
        initial=[],
        widget=forms.CheckboxSelectMultiple(attrs={
               'id': 'user'})
    )

