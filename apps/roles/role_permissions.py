from django.contrib.auth.models import Permission


def get_sales_permissions():
    sales_permissions = []
    return sales_permissions

def get_manager_permissions():
    manager_permissions = []
    manager_permissions.append(Permission.objects.get(codename='list_userprofile'))
    return manager_permissions
    
def get_admin_permissions():
    admin_permissions = []
    # Allow access to Role model
    admin_permissions.append(Permission.objects.get(codename='add_role'))
    admin_permissions.append(Permission.objects.get(codename='change_role'))
    admin_permissions.append(Permission.objects.get(codename='delete_role'))
    admin_permissions.append(Permission.objects.get(codename='view_role'))

    # Allow access to UserProfile model
    admin_permissions.append(Permission.objects.get(codename='add_userprofile'))
    admin_permissions.append(Permission.objects.get(codename='change_userprofile'))
    admin_permissions.append(Permission.objects.get(codename='view_userprofile'))
    admin_permissions.append(Permission.objects.get(codename='list_userprofile'))
    
    # Allow access to Contacts model
    admin_permissions.append(Permission.objects.get(codename='add_contact'))
    admin_permissions.append(Permission.objects.get(codename='change_contact'))
    admin_permissions.append(Permission.objects.get(codename='delete_contact'))
    admin_permissions.append(Permission.objects.get(codename='view_contact'))
    # Allow access to Contact Associate model
    admin_permissions.append(Permission.objects.get(codename='add_contactassociate'))
    admin_permissions.append(Permission.objects.get(codename='change_contactassociate'))
    admin_permissions.append(Permission.objects.get(codename='delete_contactassociate'))
    admin_permissions.append(Permission.objects.get(codename='view_contactassociate'))
    # Allow access to Contact Note model
    admin_permissions.append(Permission.objects.get(codename='add_contactnote'))
    admin_permissions.append(Permission.objects.get(codename='change_contactnote'))
    admin_permissions.append(Permission.objects.get(codename='delete_contactnote'))
    admin_permissions.append(Permission.objects.get(codename='view_contactnote'))
    # Allow access to Contact Timeline model
    admin_permissions.append(Permission.objects.get(codename='view_contacttimeline'))
    return admin_permissions
