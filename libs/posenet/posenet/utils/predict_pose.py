import torch
from PIL import Image
import torchvision.transforms as transforms
from ..model import PoseNet

def predict_pose(image_path: str, model_path: str) -> tuple:
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])
    image = Image.open(image_path).convert('RGB')
    image_tensor = transform(image).unsqueeze(0)

    model = PoseNet()
    model.load_state_dict(torch.load(model_path, map_location='cpu'))
    model.eval()

    with torch.no_grad():
        output = model(image_tensor)
        tx, ty, tz, qx, qy, qz, qw = output[0].tolist()

    return tx, ty, tz, qx, qy, qz, qw
