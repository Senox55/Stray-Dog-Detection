import os
import json
import numpy as np
from sklearn.decomposition import PCA
from model import Model
class Dataset:
    def __init__(self):
        pass

    def create_dataset_features(self, data_dir, output_file):
        embeddings = {}
        image_ids = []
        filelist = []
        for animal_name in os.listdir(data_dir):
            animal_path = os.path.join(data_dir, animal_name)
            if os.path.isdir(animal_path):
                embeddings[animal_name] = []
                for img_name in os.listdir(animal_path):
                    img_path = os.path.join(animal_path, img_name)
                    if img_path.endswith(('.jpg', '.jpeg', '.png')):
                        # embedding = Model().extract_features(img_path)
                        # embeddings[animal_name].append(embedding)
                        filelist.append(img_path)
                        image_ids.append(img_name)

        with open(output_file, 'w') as f:
            json.dump({'image_ids': image_ids, 'filelist': filelist}, f)


class Decomposition:
    def __init__(self, embeddings):
        self.pca = PCA(n_components=100)
        self.pca.fit(embeddings)


    def do_decomposition(self, features):
        pca_features = self.pca.transform(features)
        return pca_features

dataset = Dataset()
dataset.create_dataset_features("/home/senox/PycharmProjects/StrayDogDetection/test_200_database", "dataset")