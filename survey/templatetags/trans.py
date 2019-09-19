# from distutils.command import register
from django import template
register = template.Library()
from googletrans import Translator

# @register.filter(name='trans', takes_context=True)
# @register.inclusion_tag('navigation.html', takes_context=True)
@register.simple_tag(takes_context=True)
def trans(context, field):
    request = context['request']
    language = request.session.get('selected_language')
    if not language:
        language = 'EN'
    translator = Translator()
    return translator.translate(field.__str__(), dest=language.lower()).text