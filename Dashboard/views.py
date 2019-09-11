__copyright__ = "Copyright (C) 2019 NXP Semiconductors"
__license__ = "MIT"

from django.shortcuts import render


# Create your views here.
def render_dashboard(request):
    return render(request, 'dashboard.html')