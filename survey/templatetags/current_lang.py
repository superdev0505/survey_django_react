from django import template
register = template.Library()

@register.simple_tag(takes_context=True)
def current_lang(context):
    request = context['request']
    language = request.session.get('selected_language')
    if not language:
        language = 'EN'

    result = '<option value="EN">English</option>' \
             '<option value="PT">Portugues</option>' \
             '<option value="ES">Española</option>' \
             '<option value="RU">Pусский</option>' \
             '<option value="TR">Türk</option>' \
             '<option value="FR">Fransızca</option>' \
             '<option value="IN">Bahasa Indonesia</option>' \
             '<option value="PL">Polskie</option>' \
             '<option value="IT">Italiana</option>' \
             '<option value="TH">ไทย</option>' \
             '<option value="ZH-CN">中文</option>' \
             '<option value="DE">Deutsche</option>' \
             '<option value="RO">Română</option>' \
             '<option value="BG">български</option>' \
             '<option value="NL">Nederlands</option>' \
             '<option value="AR">عربى</option>' \
             '<option value="SR">Српски</option>'
    origin = '<option value="'+language+'"'

    destination = '<option value="'+language+'" selected'

    result = result.replace(origin, destination)

    return result