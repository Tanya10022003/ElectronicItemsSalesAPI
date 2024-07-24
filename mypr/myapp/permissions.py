# from rest_framework import permissions

# class IsAdminUser(permissions.BasePermission):
#     """
#     Custom permission to only allow admins to edit.
#     """
#     def has_permission(self, request, view):
#         return request.user and request.user.userprofile.role == 'admin'

# class IsManagerUser(permissions.BasePermission):
#     """
#     Custom permission to only allow managers to edit certain plans.
#     """
#     def has_permission(self, request, view):
#         return request.user and request.user.userprofile.role == 'manager'

#     def has_object_permission(self, request, view, obj):
#         return request.method in permissions.SAFE_METHODS or obj.created_by == request.user

# class IsRetailerUser(permissions.BasePermission):
#     """
#     Custom permission to only allow retailers to view plans.
#     """
#     def has_permission(self, request, view):
#         return request.user and request.user.userprofile.role == 'retailer'

#     def has_object_permission(self, request, view, obj):
#         return request.method in permissions.SAFE_METHODS
from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.userprofile.role == 'admin'

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.userprofile.role == 'manager'
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.item.managerassignment.store == request.user.userprofile.store

class IsRetailer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.userprofile.role == 'retailer'
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.plan.assigned_retailer
