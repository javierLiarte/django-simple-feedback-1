from django.utils.encoding import smart_unicode
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from urls import _PREFIX
from django.conf.urls.defaults import include, patterns
from django.template import RequestContext


def render_feedback(request,template='feedback/base.html'):
    #base_url = request.META.get("SCRIPT_NAME", '')
    feedback_media_url = u'%s/media/'%_PREFIX
    #return render_to_string(template, RequestContext({
    #                    'FEEDBACK_MEDIA_URL': feedback_media_url,
    #                    'FEEDBACK_PREFIX': _PREFIX}))
    context = RequestContext(request)
    context['FEEDBACK_MEDIA_URL']=feedback_media_url
    context['FEEDBACK_PREFIX']=_PREFIX
    return render_to_string(template, context)

def replace_insensitive(string, target, replacement):
    """
    Similar to string.replace() but is case insensitive
    Code borrowed from:
    http://forums.devshed.com/python-programming-11/case-insensitive-string-replace-490921.html
    """
    no_case = string.lower()
    index = no_case.rfind(target.lower())
    if index >= 0:
        return string[:index] + replacement + string[index + len(target):]
    else: # no results so return the original string
        return string

_HTML_TYPES = ('text/html', 'application/xhtml+xml')


class FeedbackMiddleware(object):
    def __init__(self):
        self.feedbacks={}
        self.head = u'</head>'
        self.body = u'</body>'

    def process_response(self,request,response):
        if response.status_code == 200 and request.user.is_authenticated():
            if response['Content-Type'].split(';')[0] in _HTML_TYPES:
                response.content = replace_insensitive(
                    smart_unicode(response.content),
                    self.body,
                    smart_unicode(render_feedback(request)
+ self.body))
                response.content = replace_insensitive(
                    smart_unicode(response.content),
                    self.head,
                    smart_unicode(
                        render_feedback(
                          request,
                          template='feedback/scripts.html') + self.head))
            if response.get('Content-Length', None):
                response['Content-Length'] = len(response.content)
        return response
