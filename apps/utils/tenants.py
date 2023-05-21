from apps.tenants.models import Tenant

def get_hostname_from_request(request):
    # split on `:` to remove port
    return request.get_host().split(':')[0].lower()


def get_tenant_from_request(request):
    return request.user.tenant