import cv2
from ultralytics import YOLO
import os

MODEL_PATH = 'yolov12n.pt'
CONF_THRESHOLD = 0.5

image_file_path = 'plant_1761574792.jpg'


try:
    model = YOLO(MODEL_PATH)
    print("Tải model thành công!")
except Exception as e:
    print(f"Lỗi khi tải model: {e}")
    exit()

print(f"Đang đọc ảnh: {image_file_path}")
frame = cv2.imread(image_file_path)

if frame is None:
    print(f"Lỗi: Không thể đọc file ảnh: {image_file_path}")
else:

    results = model(frame, conf=CONF_THRESHOLD)
    annotated_frame = results[0].plot()

    cv2.imshow(f'test {image_file_path}', annotated_frame)
    print(f"Đã xử lý: {image_file_path}. Nhấn phím bất kỳ để thoát.")

    cv2.waitKey(0)

cv2.destroyAllWindows()
print("Đã đóng chương trình.")