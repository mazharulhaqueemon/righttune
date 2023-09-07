from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserAdminCreationForm, UserAdminChangeForm
from django.contrib.auth import get_user_model
from .models import PhoneOTP, Support

# Register your models here.
User = get_user_model()

admin.site.register(PhoneOTP)

class UserAdmin(BaseUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    list_display = ('name','phone','admin',)
    list_filter = ('staff','active','admin',)
    fieldsets = (
        (None,{'fields':('phone','password')}),
        ("Personal info",{'fields':('name',)}),
        ('Permissions',{'fields':('admin','staff','active')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2')
        }),
    )

    search_fields = ('phone','name')
    ordering = ('phone','name')
    filter_horizontal = ()

    def get_inline_instances(self,request,obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request,obj)

admin.site.register(User, UserAdmin)
admin.site.register(Support)