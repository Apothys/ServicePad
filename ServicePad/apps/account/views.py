# Create your views here.
from django.shortcuts import redirect, render
from ServicePad.apps.events.models import Event
from ServicePad.apps.account.models import UserProfile, Availability
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as djangoLogout
from ServicePad.apps.account.forms import VolunteerProfileForm, OrganizationProfileForm, AvailabilityForm
from ServicePad.apps.team.models import Team, TeamMembership
from ServicePad.apps.bookmarks.models import Bookmark

@login_required
def index(request):
    if request.user.is_authenticated():
        
        #Get a list of stuff to show on the page
        return render(request,'account_index.djhtml')
    return redirect("/")


def teams(request):
    #Teams the user is a member in
    #Invites are teams the user has been invited to
    teams = TeamMembership.objects.filter(member=request.user,invite=False).select_related('team')
    invites = TeamMembership.objects.filter(member=request.user,invite=True).select_related('team')
    teams = [ m.team for m in teams ]
    invites = [m.team for m in invites ]
    
    
    #Teams the user is an admin
    admin_of_teams = Team.objects.filter(admin=request.user) or None
    context = { 'teams' : teams,
               'invites': invites,
                'admin_of_teams' : admin_of_teams }
    return render(request,'account_teams.djhtml',context)

@login_required
def profile(request):
    profile = request.user.get_profile()
    if request.method == 'POST':
        if profile.account_type == UserProfile.ACCOUNT_VOLUNTEER:
            profile_form = VolunteerProfileForm(request.POST,instance=profile)
        if profile.account_type == UserProfile.ACCOUNT_ORGANIZATION:
            profile_form = OrganizationProfileForm(request.POST,instance=profile)
        if profile_form.is_valid():
            profile_form.save()
        return render(request,'profile.djhtml', {'profile_form':profile_form})
    else:
        if profile.account_type == UserProfile.ACCOUNT_VOLUNTEER:
            profile_form = VolunteerProfileForm(instance=profile)
        if profile.account_type == UserProfile.ACCOUNT_ORGANIZATION:
            profile_form = OrganizationProfileForm(instance=profile)
        return render(request, 'profile.djhtml', {'profile_form':profile_form})

@login_required    
def events(request):
    events = Event.objects.filter(owner__exact=request.user)
    bookmarks = Bookmark.objects.filter(user=request.user)
    return render(request,'account_events.djhtml',
                               {'events':events, 'bookmarks':bookmarks})
    
@login_required
def availability(request):
    if request.method == 'POST':
        pass
    else:
        form = AvailabilityForm()
    my_avail = Availability.objects.filter(user__exact=request.user)
    return render(request, 'account_availability.djhtml',
                  {'availability': my_avail, 'form': form})    
    
def logout(request):
    if request.user.is_authenticated():
        djangoLogout(request)
    return redirect("/")
    