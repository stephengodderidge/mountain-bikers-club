from django.shortcuts import render

from bokeh.resources import INLINE


def bokeh_js(request):
    context = {
        'files': INLINE.js_raw,
    }
    return render(request, 'shell/vendor_files_content.html', context, content_type='application/javascript')


def bokeh_css(request):
    context = {
        'files': INLINE.css_raw,
    }
    return render(request, 'shell/vendor_files_content.html', context, content_type='text/css')
