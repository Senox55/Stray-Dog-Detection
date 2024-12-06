import cv2
import torch
from PIL import Image
import pathlib
import datetime
import os

# Установка правильного пути для Windows
temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath

# Список классов
class_names = [
    'Chihuahua', 'Japanese_spaniel', 'Maltese_dog', 'Pekinese', 'Shih-Tzu', 'Blenheim_spaniel',
    'papillon', 'toy_terrier', 'Rhodesian_ridgeback', 'Afghan_hound', 'basset', 'beagle',
    'bloodhound', 'bluetick', 'black-and-tan_coonhound', 'Walker_hound', 'English_foxhound',
    'redbone', 'borzoi', 'Irish_wolfhound', 'Italian_greyhound', 'whippet', 'Ibizan_hound',
    'Norwegian_elkhound', 'otterhound', 'Saluki', 'Scottish_deerhound', 'Weimaraner',
    'Staffordshire_bullterrier', 'American_Staffordshire_terrier', 'Bedlington_terrier',
    'Border_terrier', 'Kerry_blue_terrier', 'Irish_terrier', 'Norfolk_terrier',
    'Norwich_terrier', 'Yorkshire_terrier', 'wire-haired_fox_terrier', 'Lakeland_terrier',
    'Sealyham_terrier', 'Airedale', 'cairn', 'Australian_terrier', 'Dandie_Dinmont',
    'Boston_bull', 'miniature_schnauzer', 'giant_schnauzer', 'standard_schnauzer',
    'Scotch_terrier', 'Tibetan_terrier', 'silky_terrier', 'soft-coated_wheaten_terrier',
    'West_Highland_white_terrier', 'Lhasa', 'flat-coated_retriever', 'curly-coated_retriever',
    'golden_retriever', 'Labrador_retriever', 'Chesapeake_Bay_retriever',
    'German_short-haired_pointer', 'vizsla', 'English_setter', 'Irish_setter', 'Gordon_setter',
    'Brittany_spaniel', 'clumber', 'English_springer', 'Welsh_springer_spaniel',
    'cocker_spaniel', 'Sussex_spaniel', 'Irish_water_spaniel', 'kuvasz', 'schipperke',
    'groenendael', 'malinois', 'briard', 'kelpie', 'komondor', 'Old_English_sheepdog',
    'Shetland_sheepdog', 'collie', 'Border_collie', 'Bouvier_des_Flandres', 'Rottweiler',
    'German_shepherd', 'Doberman', 'miniature_pinscher', 'Greater_Swiss_Mountain_dog',
    'Bernese_mountain_dog', 'Appenzeller', 'EntleBucher', 'boxer', 'bull_mastiff',
    'Tibetan_mastiff', 'French_bulldog', 'Great_Dane', 'Saint_Bernard', 'Eskimo_dog',
    'malamute', 'Siberian_husky', 'affenpinscher', 'basenji', 'pug', 'Leonberg',
    'Newfoundland', 'Great_Pyrenees', 'Samoyed', 'Pomeranian', 'chow', 'keeshond',
    'Brabancon_griffon', 'Pembroke', 'Cardigan', 'toy_poodle', 'miniature_poodle',
    'standard_poodle', 'Mexican_hairless', 'dingo', 'dhole', 'African_hunting_dog'
]


class DogDetector:
    def __init__(self, model_file_path, max_width=800, max_height=600):
        self.model_path = model_file_path
        self.max_width = max_width
        self.max_height = max_height
        self.model = self.load_model()

        # Создание папки для сохранения изображений
        self.output_dir = 'cropped_images'
        os.makedirs(self.output_dir, exist_ok=True)

    def load_model(self):
        print("Загрузка модели...")
        return torch.hub.load('ultralytics/yolov5', 'custom', path=self.model_path, force_reload=True, device="cpu")

    def detect_objects(self, frame):
        print("Выполняется детекция объектов...")
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))  # Преобразование в формат RGB для модели
        results = self.model(img)
        detections = results.xyxy[0].numpy()

        for result in detections:
            x1, y1, x2, y2, conf, cls = result[:6]
            if conf > 0.25:  # Порог уверенности
                # Определение класса объекта
                detected_class = class_names[int(cls)] if int(cls) < len(class_names) else "Unknown"

                # Отрисовка прямоугольника вокруг объекта
                frame = cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                label = f'{detected_class}: {conf * 100:.2f}%'
                frame = cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Обрезка изображения по координатам
                cropped_image = frame[int(y1):int(y2), int(x1):int(x2)]

                # Сохранение обрезанного изображения
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                cropped_photo_path = os.path.join(self.output_dir,
                                                  f'{detected_class}_{timestamp}_{int(x1), int(y1), int(x2), int(y2)}.jpg')
                cv2.imwrite(cropped_photo_path, cropped_image)

                # Сохранение информации в текстовый файл
                log_path = os.path.join(self.output_dir, 'detections_log.txt')
                with open(log_path, 'a') as log_file:
                    log_file.write(
                        f"Время: {timestamp}, Класс: {detected_class}, Координаты: x1={int(x1)}, y1={int(y1)}, x2={int(x2)}, y2={int(y2)}\n"
                    )

                # Вывод в консоль
                print(f"Собака обнаружена! Время: {timestamp}, Класс: {detected_class}")
                print(f"Координаты: x1={int(x1)}, y1={int(y1)}, x2={int(x2)}, y2={int(y2)}")
                print(f"Обрезанное изображение сохранено: {cropped_photo_path}")

        return frame

    def resize_frame(self, frame):
        height, width = frame.shape[:2]
        if width > self.max_width or height > self.max_height:
            scaling_factor = min(self.max_width / width, self.max_height / height)
            frame = cv2.resize(frame, (int(width * scaling_factor), int(height * scaling_factor)))

        return frame

    def run(self):
        cap = cv2.VideoCapture(0)  # Открытие видеопотока с веб-камеры (0 — для стандартной камеры)
        if not cap.isOpened():
            print("Не удалось открыть веб-камеру!")
            return

        print("Нажмите 'q', чтобы выйти.")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Не удалось захватить кадр!")
                break

            frame = self.detect_objects(frame)  # Выполнение детекции объектов
            frame = self.resize_frame(frame)  # Масштабирование кадра

            cv2.imshow('YOLOv5 Dog Detection (Live)', frame)  # Отображение текущего кадра

            if cv2.waitKey(1) & 0xFF == ord('q'):  # Выход при нажатии 'q'
                break

        cap.release()  # Освобождение ресурса камеры
        cv2.destroyAllWindows()  # Закрытие всех окон


if __name__ == '__main__':
    # Определение пути к модели
    model_path = r'C:\Users\Samsung\Dog-detection\best.pt'

    # Создание и запуск экземпляра DogDetector
    detector = DogDetector(model_file_path=model_path)
    detector.run()

