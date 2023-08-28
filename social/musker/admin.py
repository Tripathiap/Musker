from django.contrib import admin
from django.contrib.auth.models import Group,User
from .models import Profile, Meep


# unregister groups
admin.site.unregister(Group)

# mix profile info into user info
class ProfileInline(admin.StackedInline):
    model = Profile

# extend user model
class UserAdmin(admin.ModelAdmin):
    model= User
    fields = ["username"]
    inlines = [ProfileInline]

# unregister initial User
admin.site.unregister(User)

# re-register and profile
admin.site.register(User, UserAdmin)
# admin.site.register(Profile)

admin.site.register(Meep)
