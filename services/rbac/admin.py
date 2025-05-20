from django.contrib import admin
from idvalid_core.admin import ShadowAdmin
from rbac import models


# class UserRoleInline(admin.TabularInline):
#     model = models.RoleUser


@admin.register(models.User)
class UserAdmin(ShadowAdmin):
    # fields = [("id", "subid"), "is_active", "name"]
    list_display = ["id", "subid", "name", "is_active"]
    list_filter = ["is_active"]
    list_display_links = ["subid"]
    search_fields = ["=subid", "name"]

    readonly_fields = ["id", "subid", "is_active", "name"]
    # inlines = [UserRoleInline]


@admin.register(models.Tenant)
class TenantAdmin(ShadowAdmin):
    list_display = ["id", "subid", "name", "is_active"]
    list_filter = ["is_active"]
    list_display_links = ["subid"]
    search_fields = ["=subid", "name"]

    readonly_fields = ["id", "subid", "is_active", "name"]


@admin.register(models.TenantUser)
class TenantUserAdmin(ShadowAdmin):
    list_display = ["id", "tenant_id", "user_id", "is_owner", "is_registered", "is_active"]
    list_filter = ["id", "tenant_id", "user_id", "is_owner", "is_registered", "is_active"]


class ModuleInline(admin.TabularInline):
    model = models.Module
    extra = 1


@admin.register(models.Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        "id", "subid", "codename", "name", "is_active", "created_time"]
    list_filter = ["is_active"]
    list_display_links = ["subid"]
    search_fields = ["=subid", "name"]
    inlines = [ModuleInline]


class PermissionInline(admin.TabularInline):
    model = models.Permission
    extra = 1


@admin.register(models.Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = [
        "id", "subid", "service", "codename", "name", "is_active", "created_time"]
    list_filter = ["is_active", "service"]
    list_display_links = ["subid"]
    list_select_related = ["service"]
    search_fields = ["=subid", "name"]
    inlines = [PermissionInline]


@admin.register(models.Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = [
        "id", "subid", "module", "codename", "name", "is_active", "created_time"]
    list_filter = ["is_active"]
    list_display_links = ["subid"]
    list_select_related = ["module"]
    search_fields = ["=subid", "name"]


class PolicyPermissionInline(admin.TabularInline):
    model = models.PolicyPermission
    extra = 1

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("permission__module__service")


@admin.register(models.Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ["id", "subid", "name", "is_active", "created_time"]
    list_filter = ["is_active"]
    list_display_links = ["subid"]
    search_fields = ["=subid", "name"]
    readonly_fields = ["id", "subid"]
    filter_horizontal = ["permissions"]
    inlines = [PolicyPermissionInline]


class RolePolicyInline(admin.TabularInline):
    model = models.RolePolicy
    ordering = ("policy__name",)


class RoleUserInline(admin.TabularInline):
    model = models.RoleUser
    ordering = ("user__name",)


@admin.register(models.Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["id", "subid", "name", "is_active", "created_time"]
    list_filter = ["is_active"]
    list_display_links = ["subid"]
    search_fields = ["=subid", "name"]
    readonly_fields = ["id", "subid"]
    inlines = [RolePolicyInline, RoleUserInline]
