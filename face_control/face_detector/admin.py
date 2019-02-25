from django.contrib import admin
from .models import Person, PersonFoto, Similarity
from django.utils.safestring import mark_safe
# Register your models here.

class PersonFotoAdminInline(admin.TabularInline):
    model = PersonFoto
    extra = 0


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):

    list_display = ('date', 'category', 'description', 'thumb_image')
    fields = ('id', 'date', 'thumb_image')
    readonly_fields = ['id', 'date', 'thumb_image']
    inlines = [PersonFotoAdminInline]

    def thumb_image(self, obj):
        return mark_safe('<img src="{url}" width="100" height="100" />'.format(
            url = obj.main_foto.foto.url,
            # width=obj.main_foto.foto.width,
            # height=obj.main_foto.foto.height,
            )
    )
    thumb_image.short_description = "Фото"


@admin.register(Similarity)
class SimilarityAdmin(admin.ModelAdmin):

    list_display = ('date', 'person_list', 'is_send')
    fields = ('date', 'person', 'uuid', 'thumb_image')
    readonly_fields = ['uuid', 'date', 'person', 'thumb_image']

    filter_horizontal = ('person',)

    def thumb_image(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height="{height}" />'.format(
            url = obj.foto.url,
            width=obj.foto.width,
            height=obj.foto.height,
            )
    )
    thumb_image.short_description = "Фото"

    def person_list(self, obj):
        resp = ''
        for person in obj.person.all():
            resp +='<img src="{url}" width="80" height="80" />'.format(
            url = person.main_foto.foto.url)
        return mark_safe(resp)
    person_list.short_description = 'Идентиф. личности'