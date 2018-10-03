from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

import logging
logger = logging.getLogger("helfertool")

from registration.views.utils import nopermission

from ..forms import HTMLSettingForm, TextSettingForm
from ..models import HTMLSetting, TextSetting


@login_required
def template_about(request):
    # must be superuser
    if not request.user.is_superuser:
        return nopermission(request)

    # form
    obj, c = HTMLSetting.objects.get_or_create(key='about')
    form = HTMLSettingForm(request.POST or None, instance=obj)

    if form.is_valid():
        form.save()

        logger.info("settings changed", extra={
            'changed': 'templates_about',
            'user': request.user,
        })

        return HttpResponseRedirect(reverse('toolsettings:index'))

    # render page
    context = {'form': form}
    return render(request, 'toolsettings/template_about.html', context)


@login_required
def template_privacy(request):
    # must be superuser
    if not request.user.is_superuser:
        return nopermission(request)

    # forms
    obj_privacy, c = HTMLSetting.objects.get_or_create(key='privacy')
    form_privacy = HTMLSettingForm(request.POST or None,
                                   instance=obj_privacy,
                                   prefix='privacy')

    obj_privacy_text, c = TextSetting.objects.get_or_create(key='privacy')
    form_privacy_text = TextSettingForm(request.POST or None,
                                        instance=obj_privacy_text,
                                        prefix='privacy_text')

    obj_news, c = HTMLSetting.objects.get_or_create(key='privacy_newsletter')
    form_news = HTMLSettingForm(request.POST or None,
                                instance=obj_news,
                                prefix='news')

    if form_privacy.is_valid() and form_privacy_text.is_valid() \
            and form_news.is_valid():
        form_privacy.save()
        form_privacy_text.save()
        form_news.save()

        logger.info("settings changed", extra={
            'changed': 'templates_privacy',
            'user': request.user,
        })

        return HttpResponseRedirect(reverse('toolsettings:index'))

    # render page
    context = {'form_privacy': form_privacy,
               'form_privacy_text': form_privacy_text,
               'form_news': form_news}
    return render(request, 'toolsettings/template_privacy.html', context)
