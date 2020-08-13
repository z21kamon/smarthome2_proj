from django.db import models

class SensorModel(models.Model):
    channel = models.CharField('канал', max_length=256, primary_key=True)
    time_sent = models.DateTimeField('отправлено')
    value = models.FloatField('значение')

    def __str__(self):
        return self.channel

    class Meta:
        get_latest_by = 'time_sent'
        ordering  = ['time_sent']

        verbose_name = 'показания датчика'
        verbose_name_plural = 'показания датчиков'


class ActuatorModel(models.Model):
    channel = models.CharField('канал', max_length=256, primary_key=True)
    time_sent = models.DateTimeField('отправлено')
    value = models.FloatField('значение')

    def __str__(self):
        return self.channel

    class Meta:
        get_latest_by = 'time_sent'
        ordering  = ['time_sent']

        verbose_name = 'исполнитель'
        verbose_name_plural = 'исполнители'


class ThresholdModel(models.Model):
    channel = models.CharField('канал', max_length=256, primary_key=True)
    min_value = models.FloatField('минимум', null=True, blank=True)
    max_value = models.FloatField('максимум', null=True, blank=True)
    flag = models.CharField('флаг', max_length=128)

    def __str__(self):
        return self.channel

    class Meta:
        verbose_name = 'порог датчиков'
        verbose_name_plural = 'пороги датчиков'


class KeyModel(models.Model):
    data = models.CharField('метка', max_length=256, primary_key=True)
    name = models.CharField('имя', max_length=32)
    type = models.CharField('тип', max_length=32)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ключ'
        verbose_name_plural = 'ключи'
