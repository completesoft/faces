from django.db import models
import uuid
import os
from django.dispatch import receiver
from django.utils import timezone

class Person(models.Model):

    THIEF = 0
    CUSTOMER = 1

    PERSON_CATEGORY = (
        (THIEF, 'Вор'),
        (CUSTOMER, 'Покупатель')
    )

    date = models.DateTimeField('Дата', auto_now_add=True)
    category = models.PositiveIntegerField('Категория', choices=PERSON_CATEGORY, null=False, blank=False)
    description = models.CharField('Описание', max_length=255, null=True, blank=True)
    main_foto = models.OneToOneField('PersonFoto', related_name='main_foto', verbose_name='Основное фото', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return 'ID:{}, категория: {}'.format(self.id, self.get_category_display())

    class Meta:
        verbose_name = 'Люди в БД'
        verbose_name_plural = 'Люди в БД'

class PersonFoto(models.Model):
    UPLOAD_TO = 'faces'

    face_descriptor = models.BinaryField('Дескриптор лица', null=True, blank=True)
    person = models.ForeignKey(Person, verbose_name='Person', null=False, blank=False, on_delete=models.CASCADE)
    foto = models.ImageField(verbose_name='Фото', upload_to=UPLOAD_TO, null=True, blank=True)

    def __str__(self):
        return 'FotoID: {}, тип: {}'.format(self.id, self.person.get_category_display())





class Similarity (models.Model):
    UPLOAD_TO = 'similarity'

    uuid = models.UUIDField('Идентификатор', primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ManyToManyField(Person, verbose_name='Субъект')
    date = models.DateTimeField('Дата фиксации', auto_now_add=True)
    foto = models.ImageField(verbose_name='Кадр БД+камера', upload_to=UPLOAD_TO, null=False, blank=True)
    is_send = models.BooleanField(verbose_name='Отправлена клиенту', default=False, null=False, blank=True)

    def __str__(self):
        person_id = ", ".join(pers.get_category_display() for pers in self.person.all())
        return 'Зафиксировано {} категории: {}'.format(self.date.strftime('%Y-%m-%d %H:%M:%S'), person_id)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Совпадения с БД'
        verbose_name_plural = 'Совпадения с БД'


@receiver(models.signals.post_delete, sender=PersonFoto)
@receiver(models.signals.post_delete, sender=Similarity)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.foto:
        if os.path.isfile(instance.foto.path):
            os.remove(instance.foto.path)

@receiver(models.signals.pre_save, sender=PersonFoto)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).foto
    except sender.DoesNotExist:
        return False

    new_file = instance.foto
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)

