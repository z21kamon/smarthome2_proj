from django.contrib import admin
from .models import *

class SensorModelAdmin(admin.ModelAdmin):
    list_filter = ('channel',)
    list_display = ('channel', 'time_sent', 'value',)

class ThresholdModelAdmin(admin.ModelAdmin):
    list_filter = ('channel',)
    list_display = ('channel', 'min_value', 'max_value', 'flag',)

class ActuatorModelAdmin(admin.ModelAdmin):
    list_filter = ('channel',)
    list_display = ('channel', 'time_sent', 'value',)

class KeyModelAdmin(admin.ModelAdmin):
    list_filter = ('name',)
    list_display = ('name', 'data', 'type')

admin.site.register(SensorModel, SensorModelAdmin)
admin.site.register(ThresholdModel, ThresholdModelAdmin)
admin.site.register(ActuatorModel, ActuatorModelAdmin)
admin.site.register(KeyModel, KeyModelAdmin)
