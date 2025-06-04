import torch.nn as nn
import torchvision.models as models

class PoseNet(nn.Module):
    def __init__(self):
        super(PoseNet, self).__init__()
        base_model = models.googlenet(pretrained=True)
        self.feature_extractor = nn.Sequential(*list(base_model.children())[:-1])
        self.fc_pose = nn.Linear(1024, 7)

    def forward(self, x):
        x = self.feature_extractor(x).view(x.size(0), -1)
        pose = self.fc_pose(x)
        return pose
