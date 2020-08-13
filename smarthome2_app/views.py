import paho.mqtt.client as mqtt
import os, django
os.environ["DJANGO_SETTINGS_MODULE"] = 'smarthome2_proj.settings'
django.setup()
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.conf import settings
import json
from smarthome2_app.models import *
from datetime import datetime as dt
from datetime import timedelta

client = mqtt.Client()
client.username_pw_set('smarthome2', 'smarthome2msq')
#client.connect('localhost')
#client.loop_forever()


class LightStatusView(View):
    def get(self, *args, **kwargs):
        state = True if SensorModel.objects.filter(channel='home2/light/level/lux').last().value != 0 else False
        return JsonResponse({"state": state,
                            "level_min": ThresholdModel.objects.filter(channel='home2/light/sensor/info').last().min_value,
                            "level_max": ThresholdModel.objects.filter(channel='home2/light/sensor/info').last().max_value})


class SetLightsView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        new_thr = ThresholdModel(
            channel='home2/light/sensor/info',
            min_value = data["level_min"],
            max_value = data["level_max"],
            flag="датчик освещенности в комнате")
        new_thr.save()
        state = "on" if data["state"] == True else "off"
        record = ActuatorModel(
            channel='home2/light/turning/status',
            time_sent=dt.now(),
            value=state
        )
        record.save()
        client.connect('localhost')
        client.publish('home2/light/turning/status',state)
        return HttpResponse('OK')


class SleepModeView(View):
    def get(self, *args, **kwargs):
        pass


class SetSleepMode(View):
    def post(self, request, *args, **kwargs):
        pass


class OpenDoorView(View):
    def post(self, request, *args, **kwargs):
        record = ActuatorModel(
            channel='home2/security/locker/set_lock',
            time_sent=dt.now(),
            value=1)
        client.connect('localhost')
        client.publish('home2/security/locker/set_lock',1)
        client.publish('home2/security/screen/set_message','Access allowed')
        record.save()
        return HttpResponse('Дверь открыта')


class SecurityLogView(View):
    def get(self, *args, **kwargs):
        now = dt.now()
        day1 = now - timedelta(hours=24)
        day2 = now - timedelta(hours=48)
        day3 = now - timedelta(hours=72)
        security_channels = ['home2/security/rfid/get_tag', 'home2/security/button_outside/position', 'home2/security/camera/get_photo']
        log_d1 = list(SensorModel.objects.filter(time_sent__gt=day1, time_sent__lt=now, channel__contains=security_channels))
        log_d2 = list(SensorModel.objects.filter(time_sent__gt=day2, time_sent__lt=day1, channel__contains=security_channels))
        log_d3 = list(SensorModel.objects.filter(time_sent__gt=day3, time_sent__lt=day2, channel__contains=security_channels))
        return JsonResponse({"Log": [{"Date": dt.strftime(day1, "%x"), "open_door": log_d1},
                                    {"Date": dt.strftime(day2, "%x"), "open_door": log_d2},
                                    {"Date": dt.strftime(day3, "%x"), "open_door": log_d3}]})


class OpenDoorCall(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        state = 1 if data["open_door"] == True else 0
        record = ActuatorModel(
            channel='home2/security/locker/set_lock',
            time_sent=dt.now(),
            value=state
        )
        record.save()
        client.connect('localhost')
        client.publish('home2/security/locker/set_lock',state)
        if state:
            client.publish('home2/security/screen/set_message','Access allowed')
            return HttpResponse('Дверь открыта')
        else:
            client.publish('home2/security/screen/set_message','Access denied')
            return HttpResponse('Доступ запрещён')


class ClimateDataView(View):
    def get(self, *args, **kwargs):
        now = dt.now()
        year, month, day = now.year, now.month, now.day
        day1 = dt(year, month, day, hour=0)
        day2 = dt(year, month, day - 1, hour=0)
        day3 = dt(year, month, day - 2, hour=0)
        #time_sent = SensorModel.time_sent
        hum1 = list(map(lambda s: s.value, SensorModel.objects.filter(channel='home2/climate/bme280_room/h', time_sent__gt=day1, time_sent__lte=now)))
        pres1 = list(map(lambda s: s.value, SensorModel.objects.filter(channel='home2/climate/bme280_room/p', time_sent__gt=day1, time_sent__lte=now)))
        temp1 = list(map(lambda s: s.value, SensorModel.objects.filter(channel='home2/climate/bme280_room/t', time_sent__gt=day1, time_sent__lte=now)))
        tsreet1 = list(map(lambda s: s.value, SensorModel.objects.filter(channel='home2/climate/bme280_street/t', time_sent__gt=day1, time_sent__lt=now)))
        hum2 = list(map(lambda s: s.value, SensorModel.objects.filter(channel='home2/climate/bme280_room/h', time_sent__gt=day2, time_sent__lte=day1)))
        pres2 = list(map(lambda s: s.value, SensorModel.objects.filter(channel='home2/climate/bme280_room/p', time_sent__gt=day2, time_sent__lte=day1)))
        temp2 = list(map(lambda s: s.value, SensorModel.objects.filter(channel='home2/climate/bme280_room/t', time_sent__gt=day2, time_sent__lte=day1)))
        tstreet2 = list(map(lambda s: s.value, SensorModel.objects.filter(channel='home2/climate/bme280_street/t', time_sent__gt=day2, time_sent__lte=day1)))
        hum3 = list(map(lambda s: s.value, SensorModel.objects.filter(channel='home2/climate/bme280_room/h', time_sent__gt=day3, time_sent__lte=day2)))
        pres3 = list(map(lambda s: s.value, SensorModel.objects.filter(channel='home2/climate/bme280_room/p', time_sent__gt=day3, time_sent__lte=day2)))
        temp3 = list(map(lambda s: s.value, SensorModel.objects.filter(channel='home2/climate/bme280_room/t', time_sent__gt=day3, time_sent__lte=day2)))
        tstreet3 = list(map(lambda s: s.value, SensorModel.objects.filter(channel='home2/climate/bme280_street/t', time_sent__gt=day3, time_sent__lte=day2)))
        return JsonResponse({"history": [{"date": dt.strftime(now, "%x"), "vlaga": hum1, "davl": pres1, "temp": temp1, "tempulica": tsreet1},
                                {"date": dt.strftime(day1, "%x"), "vlaga": hum2, "davl": pres2, "temp": temp2, "tempulica": tstreet2},
                                {"date": dt.strftime(day2, "%x"), "vlaga": hum3, "davl": pres3, "temp": temp3, "tempulica": tstreet3}]})


class SetHeaterView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        new_thr = ThresholdModel(
            channel='home2/climate/bme280_room/t',
            min_value = data["min"],
            max_value = data["max"],
            flag="датчик температуры в комнате")
        new_thr.save()
        state = 1 if data["tempcomnata"] == True else 0
        record = ActuatorModel(
            channel='home2/light/set_heater/state',
            time_sent=dt.now(),
            value=state
        )
        record.save()
        client.connect('localhost')
        client.publish('home2/light/set_heater/state',state)
        return HttpResponse('Новые пороговые значения для печки установлены')


class SetHumidifierView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        new_thr = ThresholdModel(
            channel='home2/climate/bme280_room/h',
            min_value = data["min"],
            max_value = data["max"],
            flag="датчик влажности в комнате")
        new_thr.save()
        state = 1 if data["vlaga"] == True else 0
        record = ActuatorModel(
            channel='home2/light/set_hum_gen/state',
            time_sent=dt.now(),
            value=state
        )
        record.save()
        client.connect('localhost')
        client.publish('home2/light/set_hum_gen/state',state)
        return HttpResponse('Новые пороговые значения для увлажнителя установлены')


class ManualHeaterView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        record = ActuatorModel(
            channel='home2/climate/set_heater/state',
            time_sent=dt.now(),
            value=data["pechka"]
        )
        record.save()
        client.connect('localhost')
        if data["pechka"] == True:
            client.publish('home2/climate/set_heater/state',1)
            return HttpResponse('Печка включена')
        else:
            client.publish('home2/climate/set_heater/state',0)
            return HttpResponse('Печка выключена')


class ManualWindowView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        record = ActuatorModel(
            channel='home2/climate/setWindow/position',
            time_sent=dt.now(),
            value=data["window"]
        )
        record.save()
        client.connect('localhost')
        if data["window"] == True:
            client.publish('home2/climate/set_window/position',1)
            return HttpResponse('Окно открыто')
        else:
            client.publish('home2/climate/set_window/position',0)
            return HttpResponse('Окно закрыто')


class ManualHumidifierView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        record = ActuatorModel(
            channel='home2/climate/set_hum_gen/state',
            time_sent=dt.now(),
            value=data["uvlaga"]
        )
        record.save()
        client.connect('localhost')
        if data["uvlaga"] == True:
            client.publish('home2/climate/set_hum_gen/state',1)
            return HttpResponse('Увлажнитель включен')
        else:
            client.publish('home2/climate/set_hum_gen/state',0)
            return HttpResponse('Увлажнитель выключен')


class EnergyLogView(View):
    def get(self, *args, **kwargs):
        now = dt.now()
        day1 = now - timedelta(hours=24)
        day2 = now - timedelta(hours=48)
        day3 = now - timedelta(hours=72)
        log_d1 = list(map(lambda s: s.value, SensorModel.objects.filter(channel='home2/energy/sensor/get_data', time_sent__gt=day1, time_sent__lt=now)))
        log_d2 = list(map(lambda s: s.value, SensorModel.objects.filter(channel='home2/energy/sensor/get_data', time_sent__gt=day2, time_sent__lt=day1)))
        log_d3 = list(map(lambda s: s.value, SensorModel.objects.filter(channel='home2/energy/sensor/get_data', time_sent__gt=day3, time_sent__lt=day2)))
        return JsonResponse({"history": [{"date": dt.strftime(day1, "%x"), "energy": log_d1},
                            {"date": dt.strftime(day2, "%x"), "energy": log_d2},
                            {"date": dt.strftime(day3, "%x"), "energy": log_d3}]})


class SetDeviceTokenView(View):
    def post(self, request, *args, **kwargs):
        deviceToken = json.loads(request.body)['deviceToken']
        record = KeyModel(
            name='Android',
            data=deviceToken,
            type='DeviceToken (для push-уведомлений)'
        )
        record.save()
        return HttpResponse('ok')
