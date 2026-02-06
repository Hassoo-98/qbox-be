from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
class HasPermission(BasePermission):
    permission=False
     
    def has_permission(self, request, view):
     if request.user.is_superuser:
        return True
     return request.user.has_perm(self.permission)
# driver_permissions
class hasCreateDriverPermission:
   permission="core.driver.add_driver"
class hasUpdateDriverPermission:
   permission="core.driver.update_driver"
class hasViewDriverPermission:
   permission="core.driver.view_driver"
class hasDeleteDriverPermission:
   permission="core.driver.delete_driver"
class hasChangeStatusDriverPermission:
   permission="core.driver.change_status_driver"
# staff_permissions
class hasCreateStaffPermission:
   permission="core.staff.add_staff"
class hasUpdateStaffPermission:
   permission="core.staff.update_staff"
class hasViewStaffPermission:
   permission="core.staff.view_staff"
class hasDeleteStaffPermission:
   permission="core.staff.delete_staff"
class hasChangeStatusStaffPermission:
   permission="core.staff.change_status_staff"
# service_provider permissions
class hasCreateServiceProviderPermission:
   permission="core.service_provider.add_service_provider"
class hasViewServiceProviderPermission:
   permission="core.service_provider.view_service_provider"
class hasUpdateServiceProviderPermission:
   permission="core.service_provider.update_service_provider"
class hasDeleteServiceProviderPermission:
   permission="core.service_provider.delete_service_provider"
class hasApproveDisApproveProviderPermission:
   permission="core.service_provider.approve_disapprove_provider"
# home_owner permissions
class hasCreateHomeOwnerPermission:
   permissions="core.home_owner.add_home_owner"
class hasViewHomeOwnerPermission:
   permission="core.home_owner.view_home_owner"
class hasUpdateHomeOwnerPermission:
   permission="core.home_owner.update_home_owner"
class hasDeleteHomeOwnerDeletePermission:
   permission="core.home_owner.delete_home_owner"
