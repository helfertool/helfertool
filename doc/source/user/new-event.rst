.. _new-event:

==================
Create a new event
==================

When creating a new event or editing and existing event there are a lot of
options.

Name for URL:
    This is the name used in the URL for the registration.

    Example: if the name for the URL is *testevent* then the registration is
    available under http://helfen.fs.tum.de/testevent.

    .. warning::
        You should not change this value after the registration was opened or
        you sent a link to someone.

Event name:
    This is the displayed name of the event, you can change it whenever you
    want.

Text before registration:
    This text is shown on the registration page on top.

Imprint:
    This text if displayed at the bottom on the registration page and after
    a helper registered.

    Please add a mail address here in case some people want to contact you.

Text after registration:
    This text is shown after a helper registered on top of the page.

E-Mail:
    This mail address is used as sender of the confirmation mails.
    It is possible that some people response to these mails when they want to
    contact you. So you should make sure that mails sent to this address are
    read.

    Additionally a mail is sent to this address if someone gives a wrong mail
    address in the registration form or the confirmation mail cannot be
    delivered for some other reason. But this should not happen too often.

Logo:
    This image is displayed on top of the registration form.

    Please use a reasonable image size!
    The image is not scaled down automatically at the moment.
    A width of 400 px should be really enough!

Maximal overlapping of shifts:
    If two shifts overlap more than this value in minutes it is not possible to
    register for both shifts. Leave empty to disable this check.

    For example if two successive shifts overlap by 15 minutes you should set
    15 here. Then a helper can register for both shifts but not for shifts
    with a higher overlap.

Admins:
    These people can edit the complete event (and also delete it, including
    all registrations!).

    When you create a new event you will be set as admin automatically.

Registration publicly visible:
    The event is visible publicly.

    .. note::
        The registration over links is possible even when this is not set.

Ask for T-shirt size:
    Obvious

Ask, if helper is vegetarian:
    Obvious

Helpers have to confirm to be full age:
    There is a checkbox in the registration form for this. If someone does not
    click it he cannot register.

Ask if helper wants to be notified about new events:
    The helper is asked if he wants to receive mails about further events.

Show number of helpers on registration page:
    Obvious

Registrations for public shifts must be validated by a link that is sent per mail:
    If a helper does not validate its mail address there is a red cross shown
    in the table beside the name.

    .. note::
       Even if a helper does not validate the mail address the helper is
       registered for the selected shifts anyway.

       But for you this is a sign that the helper does not read his mails and
       maybe does show up to his shifts.

Use badge creation:
    Activate the badge creation system, see :ref:`badges`.

Manage gifts for helpers:
    You can manage whether a helper got the T-shirt, the gifts for the shifts
    and payed caution for that, see :ref:`gifts`.
