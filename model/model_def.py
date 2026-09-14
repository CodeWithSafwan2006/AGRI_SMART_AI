import timm
import torch.nn as nn


def build_model(num_classes: int, backbone: str = "efficientnet_b0", pretrained: bool = True):
    model = timm.create_model(backbone, pretrained=pretrained, num_classes=num_classes)
    return model


def freeze_backbone(model: nn.Module, freeze: bool = True):
    for name, param in model.named_parameters():
        if name.startswith("classifier") or name.startswith("head"):
            param.requires_grad = not freeze
        else:
            param.requires_grad = not freeze


def unfreeze_last_blocks(model: nn.Module, backbone: str = "efficientnet_b0"):
    for param in model.parameters():
        param.requires_grad = False
    if backbone.startswith("efficientnet"):
        for param in model.blocks[-2:].parameters():
            param.requires_grad = True
        for param in model.conv_head.parameters():
            param.requires_grad = True
        for param in model.classifier.parameters():
            param.requires_grad = True
    elif "mobilenet" in backbone:
        for param in model.blocks[-3:].parameters():
            param.requires_grad = True
        for param in model.classifier.parameters():
            param.requires_grad = True
    else:
        for param in model.parameters():
            param.requires_grad = True
