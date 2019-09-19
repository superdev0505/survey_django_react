from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from survey.models import SurveyUser
from django.forms import ModelForm, Textarea,NumberInput,CheckboxInput,RadioSelect
from .models import *
from django.forms import modelformset_factory

from django.forms import formset_factory

class SignUpForm(UserCreationForm):
    # username = forms.CharField(max_length=254, help_text='', label='',
    # widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    email = forms.EmailField(max_length=254, help_text='', label='',
                             widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    password1 = forms.CharField(max_length=254, help_text='', label='',
                                widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(max_length=254, help_text='', label='',
                                widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    class Meta:
        model = SurveyUser
        fields = ('email', 'password1', 'password2')    

    def clean_email(self):
        """
        Returns the email if entered email is unique otherwise gives duplicate_email error.
        """
        email = self.cleaned_data['email']        
        if SurveyUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already Exists!')
        return email

    # def clean_password2(self):
    #     password1 = self.cleaned_data.get('password1')
    #     password2 = self.cleaned_data.get('password2')
 
    #     if password1 and password2 and password1 != password2:
    #         raise ValidationError("Password don't match")
 
    #     return password2



class authentication_form(AuthenticationForm):
    username = forms.CharField(max_length=30, required=True, help_text='', label='',
                               widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(max_length=254, help_text='', label='',
                               widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class BannerForm(forms.ModelForm): 

    def __init__(self, *args, **kwargs):
        super(BannerForm, self).__init__(*args, **kwargs)
        # self.fields['active'].choices=Banner.active.BOOLEAN_CHOICES 


        self.fields['bannersize'].choices= [(banner.id, banner.size) for banner in BannerSize.objects.all()]  

    class Meta:   

        model = Banners
        fields = '__all__'

        widgets = {                       
            'partnername': Textarea(attrs={'class':'form-control','cols': 0, 'rows': 1}),
            'head': Textarea(attrs={'class':'form-control','cols': 0, 'rows': 1}),
            'body': Textarea(attrs={'class':'form-control','cols': 0, 'rows': 3}),             
            'ratio': NumberInput(attrs={'class': 'form-control'}),
            'active' : CheckboxInput(attrs={'class': 'form-control '}),
        } 

