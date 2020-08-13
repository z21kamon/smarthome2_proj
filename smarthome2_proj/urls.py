from django.contrib import admin
from django.urls import path
from smarthome2_app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('get/home/light/light_status', LightStatusView.as_view()),
    path('set/home/light/lights_state', SetLightsView.as_view()),
    #path('get/light/sleep', SleepModeView.as_view()),
    #path('set/light/sleep', SetSleepMode.as_view()),
    path('set/home/security/open_door', OpenDoorView.as_view()),
    path('get/home/security/log', SecurityLogView.as_view()),
    path('set/home/security/open_door_call', OpenDoorCall.as_view()),
    path('get/home/climate/data', ClimateDataView.as_view()),
    path('set/home/climate/window', ManualWindowView.as_view()),
    path('set/home/climate/pechka', ManualHeaterView.as_view()),
    path('set/home/climate/uvlaga', ManualHumidifierView.as_view()),
    path('set/home/climate/temp', SetHeaterView.as_view()),
    path('set/home/climate/vlaga', SetHumidifierView.as_view()),
    path('get/home/energy/history', EnergyLogView.as_view()),
    path('set/home/service/deviceToken', SetDeviceTokenView.as_view())
]
