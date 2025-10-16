import ssl
import paho.mqtt.client as mqtt
import numpy as np
import torch
from PIL import Image
import re
import json
import cv2
from pyexpat.errors import messages
from ultralytics import YOLO

model = YOLO('best.pt')

# tien xu ly anh

def preprocess_img(img):
    blurred_img = cv2.GaussianBlur(img,(5,5),0)
    lab = cv2.cvtColor(blurred_img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    enhanced_img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    return Image.fromarray(cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2RGB))

# ket noi mqtt
def on_connect(client,userdata, flags,rc):
    print(f"Hive MQ connected, code: {rc}")
    client.subscribe("cam/image", qos = 1)


def on_message(client, userdata, msg):
    if msg.topic == "cam/image":
        print(f"Received image: {len(msg.payload)} bytes")
        nparr = np.frombuffer(msg.payload, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
         print("Failed to decode image.")
         return

        results = model(img)
        dectections = results[0].boxes.xyxy.cpu().numpy()
        confs = results[0].boxes.conf.cpu().numpy()
        class_ids = results[0].boxes.cls.cpu().numpy()
        class_names = results[0].names

        max_conf = -1
        best_label = None
        has_detection = len(dectections) > 0

        if has_detection:

            for i, box in enumerate(dectections):
                x1, y1, x2, y2 = map(int,box)
                conf = confs[i]
                class_id = int(class_ids[i])
                class_name = class_names[class_id]


                print(f"Checking {class_name} with confidence {conf:.2f}")  # Debug
                if conf > max_conf:
                    max_conf = conf
                    best_label = class_name
                    best_box = (x1, y1, x2, y2)

        if has_detection and max_conf >= 0.6:
            try:
                result = client.publish("object/image", best_label, qos=1)
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    print(f"gui nhan den object/image: {best_label}")
                else:
                    print(f"khong gui duoc,{result.rc}")
            except Exception as e:
                print(f"loi mqtt: {e}")
        else:
            try:
                result = client.publish("object/image","unknown", qos = 1)
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    print("no detection")
                else:
                    print(f"khong gui nhan 'unknown', code: {result.rc} ")
            except Exception as e:
                print(f"loi gui 'unknown' den MQTT: {e}")


        if has_detection and max_conf >= 0.65 and best_box:
            x1, y1, x2, y2 = best_box
            cv2.rectangle(img, (x1, y1 - 10), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, best_label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            print(f"Displayed {best_label} with confidence {max_conf:.2f}")

        cv2.imshow("YOLO Detection", img)
        cv2.waitKey(1)
        cv2.destroyAllWindows()

#mqtt client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.tls_set()
client.username_pw_set("tuduchiep123", "Tuduchiep1405")

print("Connecting to HiveMQ Cloud.")
client.connect("e081335f47cb4fb78a222c0bca0ac487.s1.eu.hivemq.cloud", 8883, 60)
client.loop_forever()




























# def preprocess_image(img):
#     blurred_img = cv2.GaussianBlur(img, (5, 5), 0)
#     lab = cv2.cvtColor(blurred_img, cv2.COLOR_BGR2LAB)
#     l, a, b = cv2.split(lab)
#     clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
#     l = clahe.apply(l)
#     lab = cv2.merge((l, a, b))
#     enhanced_img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
#     return Image.fromarray(cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2RGB))
#
# def on_connect(client, userdata, flags, rc):
#     print(f"HiveMQ Connected, code: {rc}")
#     client.subscribe("cam/image", qos = 1 )
#
# def on_message(client, userdata, msg):
#     if msg.topic == "cam/image":
#         print(f"Received image from ESP32-CAM: {len(msg.payload)} bytes")
#         nparr = np.frombuffer(msg.payload, np.uint8)
#         img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#         if img is None:
#             print("Failed to decode image.")
#             return
#
#         results = model(img)
#         dectections = results[0].boxes.xyxy.cpu().numpy()
#         confs = results[0].boxes.conf.cpu().numpy()
#         class_ids = results[0].boxes.cls.cpu().numpy()
#         class_names = results[0].names
#
#
#         for i, box in enumerate(dectections):
#             x1, y1, x2, y2 = map(int,box)
#             conf = confs[i]
#             class_id = int(class_ids[i])
#             class_name = class_names[class_id]
#
#
#             if conf >= 0.65:
#                 cv2.rectangle(img, (x1,y1 -10), (x2,y2), (0,255,0), 2)
#                 label = f"{class_name}: {conf:.2f}"
#                 cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
#                 print(f"Detected {class_name} with confidence {conf:.2f} at {x1},{y1},{x2},{y2}")
#
#         cv2.imshow("YOLO Detection", img)
#         cv2.waitKey(1)
#         cv2.destroyAllWindows()
#
#
#
# #Mqtt client
# client = mqtt.Client()
# client.on_connect = on_connect
# client.on_message = on_message
# client.tls_set()
# client.username_pw_set("tuduchiep123", "Tuduchiep1405")
#
# print("Connecting to HiveMQ Cloud...")
# client.connect("e081335f47cb4fb78a222c0bca0ac487.s1.eu.hivemq.cloud", 8883, 60)
# client.loop_forever()