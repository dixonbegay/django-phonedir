from django import template

register = template.Library()


@register.inclusion_tag("django_phonedir/_contact_card.html")
def render_contact(contact):
    return {"contact": contact}


@register.inclusion_tag("django_phonedir/_contact_list.html")
def render_contact_list(contacts):
    return {"contacts": contacts}


@register.inclusion_tag("django_phonedir/_department_card.html")
def render_department(department):
    return {"department": department}


@register.inclusion_tag("django_phonedir/_department_list.html")
def render_department_list(departments):
    return {"departments": departments}


@register.inclusion_tag("django_phonedir/_search_form.html")
def search_form():
    return {}
