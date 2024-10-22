import torch
from torchvision import models, transforms
from scipy.spatial import distance
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import os

class Model:
    def __init__(self):
        model = models.resnet50(weights='DEFAULT')
        self.model = torch.nn.Sequential(*list(model.children())[:-1])
        model.eval()

    def make_photo_preprocess(self, photo):
        preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        return preprocess(photo)


    def extract_features(self, image_path):
        image = Image.open(image_path)
        img_tensor = self.make_photo_preprocess(image).unsqueeze(0)
        with torch.no_grad():
            features = self.model(img_tensor).numpy()
        return features.flatten()

    def find_similar(self, pca_image, pca_features, filelist):
        similar_idx = [distance.cosine(pca_image, feat) for feat in pca_features]
        idx_closest = sorted(range(len(similar_idx)), key=lambda k: similar_idx[k])[1:6]
        return [filelist[id] for id in idx_closest]

