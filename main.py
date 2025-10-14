import ssl
import cv2
from ultralytics import YOLO

MODEL_PATH = 'best.pt'

CONF_THRESHOLD = 0.6

try:
    model = YOLO(MODEL_PATH)
except Exception as e:
    exit()
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    results = model(frame, conf=CONF_THRESHOLD)
    annotated_frame = results[0].plot()
    cv2.imshow('test model', annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
