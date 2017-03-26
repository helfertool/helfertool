from django.http import Http404
from django.shortcuts import render
from django.utils.translation import ugettext as _

def unsubscribe(request, token):
    if not token:
        raise Http404()
