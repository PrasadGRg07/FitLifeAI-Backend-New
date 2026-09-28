from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Category, Product, UserProfile, Cart, CartItem


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('name', 'age', 'height', 'weight', 'image', 'address', 'phone_number', 'birth_date', 'weekly_score', 'monthly_score')


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'get_name', 'get_weekly_score', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'userprofile__name')
    ordering = ('-date_joined',)
    actions = ['activate_users', 'deactivate_users']

    def get_name(self, obj):
        try:
            return obj.userprofile.name or '-'
        except UserProfile.DoesNotExist:
            return '-'
    get_name.short_description = 'Full Name'

    def get_weekly_score(self, obj):
        try:
            return obj.userprofile.weekly_score
        except UserProfile.DoesNotExist:
            return 0
    get_weekly_score.short_description = 'Weekly Score'

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} user(s) activated.')
    activate_users.short_description = 'Activate selected users'

    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} user(s) deactivated.')
    deactivate_users.short_description = 'Deactivate selected users'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'name', 'age', 'height', 'weight', 'weekly_score', 'monthly_score')
    search_fields = ('user__username', 'user__email', 'name')
    list_filter = ('age',)
    readonly_fields = ('user',)

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'created_at')
    list_filter = ('category',)
    search_fields = ('name',)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)