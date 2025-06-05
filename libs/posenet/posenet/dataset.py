import torch
from torch.utils.data import Dataset
from PIL import Image
import pandas as pd

class PoseDataset(Dataset):
    def __init__(self, csv_file, transform=None):
        self.data = pd.read_csv(csv_file)
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        img_path = self.data.iloc[idx, 0]
        image = Image.open(img_path).convert('RGB')
        pose = torch.tensor(self.data.iloc[idx, 1:].values.astype('float32'))
        if self.transform:
            image = self.transform(image)
        return image, pose
