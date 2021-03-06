# Create your views here.
import datetime
from forms import UserRegistrationForm, OrganizationRegistrationForm
from ServicePad.apps.account.models import UserProfile
from ServicePad.apps.registration.models import ActivationKey
from django.shortcuts import render_to_response, RequestContext, redirect, get_object_or_404
from django.core.exceptions import MultipleObjectsReturned
from django.contrib.auth.models import User
from ServicePad.exceptions import InvalidRegistrationRequest
from ServicePad.emailer import send_email

def register(request,**kwargs):    
    if request.POST:
        new_data = request.POST.copy()
        #Create form with user data
        
        account_type = int(new_data['form_type'])
        if account_type is UserProfile.ACCOUNT_VOLUNTEER:
            registration = UserRegistrationForm(new_data)
        elif account_type is UserProfile.ACCOUNT_ORGANIZATION:
            registration = OrganizationRegistrationForm(new_data)
        else:
            raise InvalidRegistrationRequest
        
        #Process data
        if registration.is_valid():
            #Create user
            new_user = registration.save()
            
            try:
                activation_key = get_object_or_404(ActivationKey,user=new_user)
            except MultipleObjectsReturned:
                return render_to_response('confirm.djhtml',{'success':False})
            
            #Activation URL
            url = request.get_host() + "/register/confirm/%u/%s" % (new_user.id,activation_key.activation_key)
            #Send email
            send_email(new_user.username,"Activation Email",url)
            return render_to_response('register_thankyou.djhtml',{'url':url})
        else:
            context = RequestContext(request,
                                     {'errors':registration.errors,
                                     'form':registration})
            return render_to_response('register_manual.djhtml', context)
    
    #Show new form
    if kwargs['type'] == UserProfile.ACCOUNT_VOLUNTEER:
        registration = UserRegistrationForm()
    elif kwargs['type'] == UserProfile.ACCOUNT_ORGANIZATION:
        registration = OrganizationRegistrationForm()
    else:
        registration = UserRegistrationForm()
    context = RequestContext(request,
           {'form':registration}
    )
    return render_to_response('register_manual.djhtml', context)

def confirm(request, user, key):
    if request.user.is_authenticated():
        #Users is logged in and already confirmed
        return redirect("/account")
    #Verify the confirmation request
    try:
        user = get_object_or_404(User, id=user)
    except MultipleObjectsReturned:
        return render_to_response('confirm.djhtml', {'success':False})
    
    #If valid
    if user.is_active:
        #User was already activated
        return redirect("/")
    
    try:
        activation_key = get_object_or_404(ActivationKey,user=user)
    except MultipleObjectsReturned:
        return render_to_response('confirm.djhtml',{'success':False})
    
    if activation_key.activation_key != key:
        render_to_response('confirm.djhtml', {'success':False})
    
    if activation_key.key_expires < datetime.datetime.today():
        #Resend the confirmation email with a new confirmation challenge
        return render_to_response('confirm.djhtml', {'expired':True})
    
    #Activate User
    user.is_active = True
    user.save()
    return render_to_response('confirm.djhtml', {'success':True})