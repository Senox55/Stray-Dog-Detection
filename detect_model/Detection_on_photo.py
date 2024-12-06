import cv2
import torch
from PIL import Image
import pathlib
import datetime
from tkinter import Tk, filedialog

# Установка правильного пути для Windows
temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath


class DogDetector:
    def __init__(self, model_file_path, max_width=800, max_height=600):
        self.model_path = model_file_path
        self.max_width = max_width
        self.max_height = max_height
        self.model = self.load_model()

    def load_model(self):
        print("Загрузка модели...")
        return torch.hub.load('ultralytics/yolov5', 'custom', path=self.model_path, force_reload=True, device="cpu")

    @staticmethod
    def load_image():
        Tk().withdraw()  # Скрыть главное окно Tkinter
        print("Откройте изображение для анализа...")
        image_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not image_path:
            print("Изображение не выбрано!")
            return None
        return cv2.imread(image_path)

    def detect_objects(self, frame):
        print("Выполняется детекция объектов...")
        img = Image.fromarray(frame)
        results = self.model(img)
        detections = results.xyxy[0].numpy()

        cropped_images = []  # Список для хранения обрезанных изображений

        for result in detections:
            x1, y1, x2, y2, conf, cls = result[:6]
            if conf > 0.25:
                # Вывод коэффициента уверенности в консоль

                # Отрисовка прямоугольника вокруг объекта
                frame = cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

                # Обрезка изображения по области объекта и добавление в список
                cropped_img = frame[int(y1):int(y2), int(x1):int(x2)]
                cropped_images.append((cropped_img, conf))

        return frame, cropped_images

    def resize_frame(self, frame):
        height, width = frame.shape[:2]
        if width > self.max_width or height > self.max_height:
            scaling_factor = min(self.max_width / width, self.max_height / height)
            frame = cv2.resize(frame, (int(width * scaling_factor), int(height * scaling_factor)))

        return frame

    @staticmethod
    def show_image(frame):
        print("Отображение изображения...")
        cv2.imshow('YOLOv5 Dog Detection', frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    @staticmethod
    def show_cropped_images(cropped_images):
        for i, (cropped_img, conf) in enumerate(cropped_images):
            # Отображение обрезанного изображения в небольшом окне
            resized_cropped_img = cv2.resize(cropped_img, (600, 400))  # Сжать изображение для небольшого окна
            window_name = f'Cropped Image {i + 1} - Conf: {conf * 100:.2f}%'
            cv2.imshow(window_name, resized_cropped_img)
            cv2.waitKey(0)
            cv2.destroyWindow(window_name)

    @staticmethod
    def save_cropped_images(cropped_images, output_folder="cropped_images"):
        pathlib.Path(output_folder).mkdir(exist_ok=True)  # Создать папку, если не существует
        for i, (cropped_img, conf) in enumerate(cropped_images):
            # Создание уникального имени файла на основе времени
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
            output_path = f"{output_folder}/cropped_image_{timestamp}.jpg"
            cv2.imwrite(output_path, cropped_img)
            print(f"Сохранено: {output_path}")

    def run(self):
        frame = self.load_image()
        if frame is None:
            return
        frame, cropped_images = self.detect_objects(frame)
        frame = self.resize_frame(frame)
        self.show_image(frame)  # Отображение изображения
        self.show_cropped_images(cropped_images)  # Отображение обрезанных изображений
        self.save_cropped_images(cropped_images)  # Сохранение обрезанных изображений


# Определение пути к модели
model_path = r'C:\Users\Samsung\Dog-detection\best.pt'
# Создание и запуск экземпляра DogDetector
detector = DogDetector(model_file_path=model_path)
detector.run()
