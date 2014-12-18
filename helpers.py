import urllib2 as urllib

from django.conf import settings


def copy_file(url, filename, slug):
    """
    Helper function to copy images from source
    """
    f = urllib.urlopen(url)
    destination = open(settings.MEDIA_ROOT + 'img/articles/'+ filename, 'wb+')
    destination.write(f.read())
    destination.close()
    f.close()


def clean_text(text):
    """
    Strips special characters and other CCI/Workbench clutter from a string, and sends it back.
    """
    for r in replacements:
        text = text.replace(r[0], r[1])
    return text


# replacements are done in order (for r in replacements: replace(r[0],r[1])) so you can replace, then replace again
replacements = [
    ("&amp;"        , '&'),

    ('&#x97;'       , '--'),
    ('&#x2014;'     , "--"),
    ('&#x2013;'     , "--"),
    ('&mdash;'      , '--'),
    ("&#8212;"      , '--'),
    ('&lt;p/&gt;'   , '\n\n'),
    ('<p/>'         , '\n\n'),
    ('<p></p>'      , '\n\n'),
    # single quotes
    ('&#x2018;'     , "'"),
    ('&#x2019;'     , "'"),
    ('&#39;'        , "'"),
    ('&#x91;'       , "'"),
    ('&#x92;'       , "'"),
    ('&#xD5;'       , "'"),
    ('&#8217;'      , "'"),
    ("&#8216;"      , "'"),
    # double quotes
    ('&#x93;'       , '"'),
    ('&#x94;'       , '"'),
    ('&#x201C;'     , '"'),
    ('&#x201c;'     , '"'),
    ('&#x201C;'     , '"'),
    ('&#x201D;'     , '"'),
    ('&#x201d;'     , '"'),
    ('&#xD2;'       , '"'),
    ('&#xD3;'       , '"'),
    ('&quot;'       , '"'),
    ("&#8220;"      , '"'),
    ("&#8221;"      , '"'),
    # other stuff
    ('&#x85;'       , '...'),
    ('&#8230;'      , '...'),
    ('&#x2026;'     , '...'),

    ("&bull;&nbsp;" , '* '),
    ("&bull;&#xA0;" , '* '),

    # superscripts
    ('{+t}'         , 't'),
    ('{+h}'         , 'h'),
]
