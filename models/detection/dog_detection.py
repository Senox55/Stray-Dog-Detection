from ultralytics import YOLO
import cv2

# Загрузка модели YOLO
model = YOLO('best.pt')

# Открытие видео
cap = cv2.VideoCapture(r"C:\Users\very-\Desktop\Projects\Stray-Dog-Detection\models\detection\input_video.mp4")
fps = int(cap.get(cv2.CAP_PROP_FPS))  # Получение частоты кадров из исходного видео
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
output = cv2.VideoWriter("output2.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Детекция объектов с помощью YOLO
    results = model(frame)  # Потоковая обработка

    for r in results:
        for box, conf, cls in zip(r.boxes.xyxy, r.boxes.conf, r.boxes.cls):
            x1, y1, x2, y2 = map(int, box[:4])  # Координаты ограничивающей рамки
            confidence = float(conf)  # Уверенность
            class_id = int(cls)  # Класс детекции

            if confidence > 0.5:  # Порог уверенности
                # Рисуем рамку вокруг объекта
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f"Class: {class_id} Conf: {confidence:.2f}"
                # Выводим метку над рамкой
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    output.write(frame)
    cv2.imshow("Object Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
output.release()
cv2.destroyAllWindows()
