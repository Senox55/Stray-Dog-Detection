import streamlit as st
import cv2
from ultralytics import YOLO
import tempfile
import numpy as np

# Загрузка модели YOLO
model = YOLO('best3.pt')

def process_video(video_file):
    # Использование временного файла для загрузки видео из streamlit
    if hasattr(video_file, 'name'):
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video_file.read())
        cap = cv2.VideoCapture(tfile.name)
    else:
        cap = cv2.VideoCapture(video_file)

    try:
        if not cap.isOpened():
            st.error("Ошибка: Не удалось открыть видео.")
            return

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

            yield frame

    finally:
        cap.release()
        if hasattr(video_file, 'name'):
            tfile.close()
            import os
            os.remove(tfile.name)


def main():
    st.title("Детекция собак на видео")

    uploaded_file = st.file_uploader("Загрузите видеофайл", type=["mp4", "avi", "mov"])

    if uploaded_file is not None:
        st.subheader("Видео с детекцией")

        # Создание placeholder для отображения кадров
        video_placeholder = st.empty()

        # Обработка видео и отображение кадров
        for frame in process_video(uploaded_file):
            # Отображаем кадр
            video_placeholder.image(frame, channels="BGR", use_container_width=True)
        st.success("Видео обработано!")


if __name__ == "__main__":
    main()