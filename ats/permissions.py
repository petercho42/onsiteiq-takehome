from rest_framework import permissions


class IsApplicationViewer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.has_perm("ats.view_application")


class IsApplicationCreator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.has_perm("ats.add_application")


class IsApplicationDecisionMaker(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.has_perm("ats.change_application")


class IsApplicationNoteWriter(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.has_perm("ats.add_applicationnote")
