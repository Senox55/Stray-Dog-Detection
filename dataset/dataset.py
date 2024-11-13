import csv
import os
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from sklearn.decomposition import PCA

class DogDataset(Dataset):
    def __init__(self, image_paths, labels, transform=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert("RGB")
        label = self.labels[idx]

        if self.transform:
            image = self.transform(image)

        return image, label

class Decomposition:
    def __init__(self, embeddings):
        self.pca = PCA(n_components=100)
        self.pca.fit(embeddings)


    def do_decomposition(self, features):
        pca_features = self.pca.transform(features)
        return pca_features


def create_dataset_features(data_dir, output_file):
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
            else:
                if animal_path.endswith(('.jpg', '.jpeg', '.png')):
                    writer.writerow({'name': animal_name.replace('.jpg', ''), 'photo_path': animal_path})



if __name__ == '__main__':
    create_dataset_features("test_200_single_img", "test_dataset_single")