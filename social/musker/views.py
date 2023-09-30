from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Meep
from django.contrib import messages
from .forms import MeepForm, SignUpForm, ProfilePicForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

def home(request):
    if request.user.is_authenticated:
        form = MeepForm(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                meep = form.save(commit=False)
                meep.user = request.user
                meep.save()
                messages.success(request, "Your meep has been posted!")
                return redirect('home')
        
        meeps = Meep.objects.all().order_by("-created_at")
        return render(request, 'musker/home.html', {"meeps":meeps, "form":form})
    
    else:
        meeps = Meep.objects.all().order_by("-created_at")
        return render(request, 'musker/home.html', {"meeps":meeps})


def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user=request.user)

        return render(request, 'musker/profile_list.html', {"profiles":profiles})

    else:
        messages.success(request, "You must be logged in to view this page!")
        return redirect("home")
    

def unfollow(request, pk):
    if request.user.is_authenticated:
        
        #get the profile to unfollow
        profile = Profile.objects.get(user_id=pk)

        #unfollow the user
        request.user.profile.follows.remove(profile)
        # save the profile
        request.user.profile.save()

        # return message
        messages.success(request, (f"You have successfully unfollowed {profile.user.username}..."))
        return redirect(request.META.get("HTTP_REFERER"))

   
    
    else:
        messages.success(request, "You must be logged in to unfollow someone...")
        return redirect("home")
    

def follow(request, pk):
    if request.user.is_authenticated:
        
        #get the profile to follow
        profile = Profile.objects.get(user_id=pk)

        #follow the user
        request.user.profile.follows.add(profile)
        # save the profile
        request.user.profile.save()

        # return message
        messages.success(request, (f"You have successfully followed {profile.user.username}..."))
        return redirect(request.META.get("HTTP_REFERER"))

   
    
    else:
        messages.success(request, "You must be logged in to unfollow someone...")
        return redirect("home")


    
def profile(request, pk):
    if request.user.is_authenticated:
        profile=Profile.objects.get(user_id=pk)
        meeps = Meep.objects.filter(user_id=pk).order_by("-created_at")

        if request.method == "POST":
            # get current user
            current_user_profile= request.user.profile
            action = request.POST['follow']

            if action == "unfollow":
                current_user_profile.follows.remove(profile)
            elif action == "follow":
                current_user_profile.follows.add(profile)
            
            # saving the changes
            current_user_profile.save() 

        return render(request, 'musker/profile.html',{"profile":profile,"meeps":meeps})
    else:
        
        messages.success(request, "You must be logged in to view this page!")
        return redirect("home")
    
def followers(request,pk):
    if request.user.is_authenticated:

        if request.user.id == pk:

            profiles = Profile.objects.get(user_id=pk)
            return render(request, 'musker/followers.html', {"profiles":profiles})
        
        else:
            messages.success(request, "You will not be able to check for other's profile!")
            return redirect("home")

    else:
        messages.success(request, "You must be logged in to view this page!")
        return redirect("home")
    
def follows(request,pk):
    if request.user.is_authenticated:

        if request.user.id == pk:

            profiles = Profile.objects.get(user_id=pk)
            return render(request, 'musker/follows.html', {"profiles":profiles})
        
        else:
            messages.success(request, "You will not be able to check for other's profile!")
            return redirect("home")

    else:
        messages.success(request, "You must be logged in to view this page!")
        return redirect("home")
    

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            messages.success(request, "You have been logged in. Keep meeping!")
            return redirect('home')
        else:
            messages.success(request, "There was an error logging in. Please try again!")
            return redirect('login')

    else:
        return render(request, 'musker/login.html',{})


def logout_user(request):
    logout(request)
    messages.success(request, "You have been Logged Out!")
    return redirect('home')


def register_user(request):
    form=SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']

            user = authenticate(username=username,password=password,first_name=first_name,last_name=last_name,email=email)
            login(request, user)
            messages.success(request,"You have successfully registered!")
            return redirect('home')

    return render(request, 'musker/register.html',{"form":form})


def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        profile_user = Profile.objects.get(user__id=request.user.id)
        
        user_form = SignUpForm(request.POST or None, request.FILES or None, instance=current_user)
        profile_form = ProfilePicForm(request.POST or None, request.FILES or None, instance=profile_user)

        if user_form.is_valid() and profile_form.is_valid():
            
            user_form.save()
            profile_form.save()

            login(request,current_user)
            messages.success(request,"Your profile has been updated!")
            return redirect('home')
        

        return render(request,'musker/update_user.html',{'user_form':user_form,'profile_form':profile_form})
    
    
    else:
        messages.success(request,"You must be logged in to update the profile...")
        return redirect('login')

    
def meep_like(request,pk):
    if request.user.is_authenticated:
        meep = get_object_or_404(Meep, id=pk)
        if meep.likes.filter(id=request.user.id):
            meep.likes.remove(request.user)
        else:
            meep.likes.add(request.user)
        # it will refer to the same webpage where we are currently on..
        return redirect(request.META.get("HTTP_REFERER"))  

    else:
        messages.success(request,"You must be logged in to update the profile...")
        return redirect('home')
    
def meep_show(request, pk):
    meep = get_object_or_404(Meep, id=pk)

    if meep:
        return render(request,'musker/show_meep.html',{"meep":meep})
    
    
    else:
        messages.success(request,"The meep you are looking for doesn't exist...")
        return redirect('home')

@login_required(login_url='login')
def delete_meep(request, pk):
    # if request.user.is_authenticated:
    #     meep = get_object_or_404(Meep, id=pk)
        
    #     if request.user.username == meep.user.username:
    #         # delete the meep
    #         meep.delete()
    #         messages.success(request,"The meep has been deleted!")
    #         return redirect(request.META.get("HTTP_REFERER"))
        
    #     else:
    #         messages.success(request,"You don't own that meep!")
    #         return redirect('home')
        
    # else:
    #     messages.success(request,"Please log in...")
    #     return redirect(request.META.get("HTTP_REFERER")) 
    meep = Meep.objects.get(id=pk)

    if request.user.username != meep.user.username:
        return HttpResponse("You are not allowed to delete!")   

    if request.method == 'POST':
        meep.delete()
        messages.success(request,"The meep has been deleted!")
        return redirect('home') 

    context = {'meep':meep}
    return render(request,'musker/delete_meep.html',context)

def edit_meep(request,pk):
    if request.user.is_authenticated:
        meep = get_object_or_404(Meep, id=pk)
        
        if request.user.username == meep.user.username:
            
            
            form = MeepForm(request.POST or None, instance=meep)
        
            if request.method == "POST":
                if form.is_valid():
                    meep = form.save(commit=False)
                    meep.user = request.user
                    meep.save()
                    messages.success(request, "Your meep has been updated!")
                    return redirect('home')
                
            else:
                return render(request,'musker/edit_meep.html',{"form":form,"meep":meep})
        
        else:
            messages.success(request,"You don't own that meep!")
            return redirect('home')
        
    else:
        messages.success(request,"Please log in...")
        return redirect('home') 
    

def search(request):

    if request.method == "POST":
        # grab the form field input
        search = request.POST.get('search','')
        # search the database for the input
        searched = Meep.objects.filter(body__contains = search)

        return render(request, 'musker/search.html',{"search":search, "searched":searched})

    else:
        return render(request, 'musker/search.html',{})
    

def search_user(request):

    if request.method == "POST":
        # grab the form field input
        search = request.POST.get('search','')
        # search the database for the input
        searched = User.objects.filter(username__contains = search)

        return render(request, 'musker/search_user.html',{"search":search, "searched":searched})

    else:
        return render(request, 'musker/search_user.html',{})
    