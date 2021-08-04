from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from helfertool.utils import nopermission

from ..forms import HTMLSettingForm, TextSettingForm
from ..models import HTMLSetting, TextSetting

import logging
logger = logging.getLogger("helfertool.toolsettings")


# TODO: refactor to remove duplicated code


@login_required
def templates(request):
    # must be superuser
    if not request.user.is_superuser:
        return nopermission(request)

    context = {}
    return render(request, 'toolsettings/templates.html', context)


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

        return redirect('toolsettings:templates')

    # render page
    context = {'form': form}
    return render(request, 'toolsettings/template_about.html', context)


@login_required
def template_privacy(request):
    # must be superuser
    if not request.user.is_superuser:
        return nopermission(request)

    # forms
    all_forms = []

    # texts for registration
    obj_privacy, c = HTMLSetting.objects.get_or_create(key='privacy')
    form_privacy = HTMLSettingForm(request.POST or None,
                                   instance=obj_privacy,
                                   prefix='privacy')
    all_forms.append(form_privacy)

    obj_privacy_text, c = TextSetting.objects.get_or_create(key='privacy')
    form_privacy_text = TextSettingForm(request.POST or None,
                                        instance=obj_privacy_text,
                                        prefix='privacy_text')
    all_forms.append(form_privacy_text)

    # forms for newsletter texts (if enabled)
    if settings.FEATURES_NEWSLETTER:
        obj_news, c = HTMLSetting.objects.get_or_create(key='privacy_newsletter')
        form_news = HTMLSettingForm(request.POST or None,
                                    instance=obj_news,
                                    prefix='news')
        all_forms.append(form_news)

        obj_news_subscribe, c = HTMLSetting.objects.get_or_create(key='privacy_newsletter_subscribe')
        form_news_subscribe = HTMLSettingForm(request.POST or None,
                                              instance=obj_news_subscribe,
                                              prefix='news_subscribe')
        all_forms.append(form_news_subscribe)
    else:
        # for template
        form_news = None
        form_news_subscribe = None

    # check all forms and save
    if all([f.is_valid() for f in all_forms]):
        for f in all_forms:
            f.save()

        logger.info("settings changed", extra={
            'changed': 'templates_privacy',
            'user': request.user,
        })

        return redirect('toolsettings:templates')

    # render page
    context = {'form_privacy': form_privacy,
               'form_privacy_text': form_privacy_text,
               'form_news': form_news,
               'form_news_subscribe': form_news_subscribe}
    return render(request, 'toolsettings/template_privacy.html', context)


@login_required
def template_login(request):
    # must be superuser
    if not request.user.is_superuser:
        return nopermission(request)

    # form
    obj, c = HTMLSetting.objects.get_or_create(key='login')
    form = HTMLSettingForm(request.POST or None, instance=obj)

    if form.is_valid():
        form.save()

        logger.info("settings changed", extra={
            'changed': 'templates_login',
            'user': request.user,
        })

        return redirect('toolsettings:templates')

    # render page
    context = {'form': form}
    return render(request, 'toolsettings/template_login.html', context)


@login_required
def template_add_user(request):
    # must be superuser
    if not request.user.is_superuser:
        return nopermission(request)

    # form
    obj, c = HTMLSetting.objects.get_or_create(key='add_user')
    form = HTMLSettingForm(request.POST or None, instance=obj)

    if form.is_valid():
        form.save()

        logger.info("settings changed", extra={
            'changed': 'templates_add_user',
            'user': request.user,
        })

        return redirect('toolsettings:templates')

    # render page
    context = {'form': form}
    return render(request, 'toolsettings/template_add_user.html', context)
