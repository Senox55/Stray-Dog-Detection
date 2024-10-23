import csv
import os
from sklearn.decomposition import PCA

class Dataset:
    def __init__(self):
        pass

    def create_dataset_features(self, data_dir, output_file):
        with open(output_file, 'w', encoding='utf-8', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=['name', 'photo_path'])
            writer.writeheader()

            for animal_name in os.listdir(data_dir):
                animal_path = os.path.join(data_dir, animal_name)
                if os.path.isdir(animal_path):

                    for img_name in os.listdir(animal_path):
                        img_path = os.path.join(animal_path, img_name)
                        if img_path.endswith(('.jpg', '.jpeg', '.png')):
                            writer.writerow({'name': animal_name, 'photo_path': img_path})

class Decomposition:
    def __init__(self, embeddings):
        self.pca = PCA(n_components=100)
        self.pca.fit(embeddings)


    def do_decomposition(self, features):
        pca_features = self.pca.transform(features)
        return pca_features

dataset = Dataset()
dataset.create_dataset_features("/home/senox/PycharmProjects/StrayDogDetection/test_200_database", "dataset")