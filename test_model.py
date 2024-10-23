import os
import csv

def create_test_dataset(data_dir, output_file):
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'photo_path'])
        for animal_name in os.listdir(data_dir):
            photo_path = os.path.join(data_dir, animal_name)
            writer.writerow([animal_name, photo_path])


# create_test_dataset('/home/senox/PycharmProjects/StrayDogDetection/test_200_single_img', 'test_dataset')
