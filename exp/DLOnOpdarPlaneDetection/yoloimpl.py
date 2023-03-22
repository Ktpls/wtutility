import torch
import torch.nn as nn
import torch.nn.functional as F

class YOLOv1(nn.Module):
    def __init__(self, num_classes=20, num_boxes=2,S=7):
        super(YOLOv1, self).__init__()
        self.num_classes = num_classes
        self.num_boxes = num_boxes
        self.S=S
        self.convs=nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3),
            nn.ReLU(True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(64, 192, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(192, 128, kernel_size=1, stride=1, padding=0),
            nn.ReLU(True),
            nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.Conv2d(256, 256, kernel_size=1, stride=1, padding=0),
            nn.ReLU(True),
            nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(512, 256, kernel_size=1, stride=1, padding=0),
            nn.ReLU(True),
            nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.Conv2d(512, 256, kernel_size=1, stride=1, padding=0),
            nn.ReLU(True),
            nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.Conv2d(512, 256, kernel_size=1, stride=1, padding=0),
            nn.ReLU(True),
            nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.Conv2d(512, 256, kernel_size=1, stride=1, padding=0),
            nn.ReLU(True),
            nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(512, 512, kernel_size=1, stride=1, padding=0),
            nn.ReLU(True),
            nn.Conv2d(512, 1024, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.Conv2d(1024, 512, kernel_size=1, stride=1, padding=0),
            nn.ReLU(True),
            nn.Conv2d(512, 1024, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.Conv2d(1024, 1024, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.Conv2d(1024, 1024, kernel_size=3, stride=2, padding=1),
            nn.ReLU(True),
            nn.Conv2d(1024, 1024, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.Conv2d(1024, 1024, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
        )
        self.fcs=nn.Sequential(
            nn.Linear(7*7*1024, 4096),
            nn.ReLU(True),
            nn.Linear(4096, S*S*(self.num_classes + self.num_boxes*5)),
            nn.ReLU(True),
            )

    def forward(self, x):
        x=self.convs(x)
        x = x.view(-1, self.S*self.S*1024)
        x=self.fcs(x)
        x = x.view(-1, self.S, self.S, self.num_classes + self.num_boxes*5)
        return x

def yolo_loss(pred, target, S, B, C, lambda_coord, lambda_noobj):
    """
    pred: (batch_size, S, S, Bx5+C)
    target: (batch_size, S, S, Bx5+C)
    S: int, grid size
    B: int, number of boxes per grid cell
    C: int, number of classes
    lambda_coord: float, weight for coordinate loss
    lambda_noobj: float, weight for no-object loss
    """
    # separate predictions for objectness, box coordinates, and class probabilities
    pred_obj = pred[..., :B]
    pred_box = pred[..., B:B*5]
    pred_class = pred[..., B*5:]

    # separate targets for objectness, box coordinates, and class probabilities
    target_obj = target[..., :B]
    target_box = target[..., B:B*5]
    target_class = target[..., B*5:]

    # calculate binary cross-entropy loss for objectness
    obj_loss = F.binary_cross_entropy_with_logits(pred_obj, target_obj, reduction='none')

    # calculate MSE loss for box coordinates
    box_loss = F.mse_loss(pred_box, target_box, reduction='none')

    # create mask for cells with object
    obj_mask = target_obj > 0.5

    # calculate coordinate loss only for cells with object
    coord_loss = lambda_coord * torch.sum(box_loss[obj_mask])

    # calculate no-object loss only for cells without object
    noobj_mask = target_obj <= 0.5
    noobj_loss = lambda_noobj * torch.sum(obj_loss[noobj_mask])

    # calculate class loss
    class_loss = F.binary_cross_entropy_with_logits(pred_class, target_class, reduction='none')

    # sum up all losses
    total_loss = torch.sum(coord_loss + noobj_loss + class_loss)

    return total_loss

