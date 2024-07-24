
# Register your models here.
from django.contrib import admin
from .models import Customer, Partner, Store, UserProfile, Item, Plan, PartnerItem, PartnerPlan, ManagerAssignment, RetailerAssignment, PlanSale

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    """
    Admin view for the Partner model.
    """
    list_display = ['name']

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    """
    Admin view for the Store model.
    """
    list_display = ['partner', 'gst_number', 'mobile_number', 'email', 'address', 'is_active']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin view for the UserProfile model.
    """
    list_display = ['user', 'first_name', 'last_name', 'mobile', 'email', 'address', 'store', 'role', 'manager']

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """
    Admin view for the Item model.
    """
    list_display = ['name', 'type', 'brand_warranty','managerassignment', 'retailerassignment', 'manager', 'store', 'item_purchase_date','esn_number']
@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    """
    Admin view for the Plan model.
    """
    list_display = ['item','name', 'duration_in_months', 'is_active', 'created_date', 'modified_date', 'created_by', 'modified_by', 'assigned_retailer']

@admin.register(PartnerItem)
class PartnerItemAdmin(admin.ModelAdmin):
    """
    Admin view for the PartnerItem model.
    Displays the 'partner' and 'item' fields in the admin list view.
    """

    list_display = ['partner', 'item']

@admin.register(PartnerPlan)
class PartnerPlanAdmin(admin.ModelAdmin):
    """
    Admin view for the PartnerPlan model.
    Displays the 'partner' and 'plan' fields in the admin list view.
    """
    list_display = ['partner', 'plan']

@admin.register(ManagerAssignment)
class ManagerAssignmentAdmin(admin.ModelAdmin):
    """
    Admin view for the ManagerAssignment model.
    """
    list_display = ['manager', 'store', 'plan']

@admin.register(RetailerAssignment)
class RetailerAssignmentAdmin(admin.ModelAdmin):
    """
    Admin view for the RetailerAssignment model.
    Displays the 'retailer', 'store', and 'plan' fields in the admin list view.
    """
    list_display = ['retailer', 'store', 'plan']

@admin.register(Customer)
class RetailerAssignmentAdmin(admin.ModelAdmin):
    """
    Admin view for the Customer model.
    """
    list_display = ['name', 'email', 'address', 'phone_number']

@admin.register(PlanSale)
class PlanSaleAdmin(admin.ModelAdmin):
    """
    Admin view for the PlanSale model.
    Displays the 'item_sale', 'plan', 'retailer', 'plan_sale_date', 'plan_start_date', 'plan_end_date', and 'plan_price' fields in the admin list view.
    """
    list_display = ['item', 'plan', 'retailer','customer', 'plan_purchase_date', 'plan_start_date', 'plan_end_date', 'plan_price']
