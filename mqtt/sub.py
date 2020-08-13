import paho.mqtt.client as mqtt
import os, django
from django.http import JsonResponse
os.environ["DJANGO_SETTINGS_MODULE"] = 'smarthome2_proj.settings'
django.setup()
from django.conf import settings
from smarthome2_app.models import *
from datetime import datetime as dt
import json

publish_channels = ['home2/light/set_dimmer/data',
                    'home2/light/turning/status',
                    'home2/security/locker/set_lock',
                    'home2/security/screen/set_message'
                    'home2/climate/set_heater/state',
                    'home2/climate/set_window/position',
                    'home2/climate/set_hum_gen/state']
subscribe_channels = ['home2/light/button/sensor',
                      'home2/light/sensor/info',
                      'home2/light/level/lux',
                      'home2/security/rfid/get_tag',
                      'home2/security/camera/get_photo',
                      'home2/security/button_inside/get_position',
                      'home2/climate/bme280_street/t',
                      'home2/climate/bme280_room/t',
                      'home2/climate/bme280_room/h',
                      'home2/climate/bme280_room/p',
                      'home2/climate/water_sens/level',
                      'home2/energy/sensor/get_data']


def send_push(data):
    serverToken = 'AAAA8umkSoY:APA91bHi-6aBIefo7Pv8ag2SwlYfXJX7IMgru_RQuzS6ncZkJRNvKsK-phQ_F6DZly68rIPbn73-J08cO_4g9nIECj58ERB8B8gctI9t7IrFkA39eTfJ_EZWwhUtB3_NZU7iD2uLIwFK'
    deviceToken = KeyModel.objects.filter(name='Android').last().data
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + serverToken,
    }

    body = {
        'to': deviceToken,
        'priority': 'high',
        'data': data}
    resp = requests.post("https://fcm.googleapis.com/fcm/send",headers = headers, data=json.dumps(body))
    print(resp.status_code)
    print(resp.json())
    return JsonResponse(resp.json())


def on_log(client, userdata, level, buf):
    print("log: ",buf)


def on_connect(client, userdata, flags, rc):
    global subscribe_channels
    client.subscribe([(channel,2) for channel in subscribe_channels])


def on_message(client, userdata, msg):
    if msg.topic == 'home2/security/camera/get_photo':
        with open(os.path.join(settings.STATIC_ROOT, 'photo.jpg'), "wb") as photo:
            photo.write(msg.payload)
            photo.close()
        data = {'image': 'https://ms.newtonbox.ru/smarthome2/static/photo.jpg',
                'date': dt.now()}
        send_push(data)


    elif msg.topic == 'home2/security/rfid/get_tag':
        value = str(msg.payload).rstrip("'").lstrip("b'")
        time = dt.now()
        #tag = KeyModel.objects.filter(data=value).exists()
        #tags = list(map(lambda s: s.data, list(KeyModel.objects)))
        #if value in tags:
        #if tag:
        client.publish('home2/security/locker/set_lock',1)
        record = ActuatorModel(channel='home2/security/locker/set_lock',
                                time_sent=time,
                                value=0)
        client.publish('home2/security/screen/set_message','Access allowed')
        record.save()

    else:
        value = str(msg.payload).rstrip("'").lstrip("b'")
        time = dt.now()
        record = SensorModel(
            channel=msg.topic,
            time_sent=time,
            value=value)
        record.save()

        if msg.topic == 'home2/light/button/sensor':
            #last = SensorModel.objects.filter(channel='home2/light/level/lux').last().value
            if value == 1:
                client.publish('home2/light/turning/status','on')

        if msg.topic == 'home2/light/sensor/info':
            if value < ThresholdModel.objects.filter(channel='home2/light/sensor/info').last().min_value:
                client.publish('home2/light/set_dimmer/data',10)
            if value > ThresholdModel.objects.filter(channel='home2/light/sensor/info').last().max_value:
                client.publish('home2/light/set_dimmer/data',-10)

        if msg.topic == 'home2/security/button_inside/get_position':
            client.publish('home2/security/locker/set_lock',1)
            record = ActuatorModel(channel='home2/security/locker/set_lock',
                                    time_sent=dt.now(),
                                    value=0)
            client.publish('home2/security/screen/set_message','Access allowed')
            record.save()

        if msg.topic == 'home2/climate/bme280_room/t':
            if value < ThresholdModel.objects.filter(channel='home2/climate/bme280_room/t').last().min_value:
                client.publish('home2/light/set_heater/state',1)
            elif value > ThresholdModel.objects.filter(channel='home2/climate/bme280_room/t').last().max_value:
                client.publish('home2/light/set_heater/state',0)
                street_temp = SensorModel.objects.filter(channel='home2/climate/bme280_street/t').last().value
                if street_temp < value:
                    client.publish('home2/climate/set_window/position',1)
            else:
                client.publish('home2/climate/set_heater/state',0)
                client.publish('home2/climate/set_window/position',0)

        if msg.topic == 'home2/climate/bme280_room/h':
            if value < ThresholdModel.objects.filter(channel='home2/climate/bme280_room/h').last().min_value:
                client.publish('home2/climate/set_hum_gen/state',1)
            else:
                client.publish('home2/climate/set_hum_gen/state',0)

        if msg.topic == 'home2/climate/water_sens/level':
            if value == 0:
                data = {'msg': 'Критически низкий уровень воды в увлажнителе',
                        'date': dt.now()}
                send_push(data)


client = mqtt.Client()
client.on_log=on_log
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set('smarthome2', 'smarthome2msq')
client.connect('localhost')
client.loop_forever()
