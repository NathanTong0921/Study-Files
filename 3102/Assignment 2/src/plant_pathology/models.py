"""Task: implement the baseline and transfer-learning models.

Requirements:
1. Implement a manual ResNet18 baseline from PyTorch layers and residual blocks.
2. The baseline config must use `model="manual_resnet18"` and train from scratch.
3. The transfer config must use `model="resnet18"` and load pretrained torchvision ResNet18
   weights before replacing the final layer.
4. Both models must output four class logits.
5. Implement the frozen or fine-tuned backbone behavior used in your experiments.
"""

from __future__ import annotations

from torch import Tensor, nn
from torchvision import models


class BasicBlock(nn.Module):
    """Two-layer residual block used by ResNet18."""

    def __init__(self, in_channels: int, out_channels: int, stride: int = 1) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size=3,
            stride=stride,
            padding=1,
            bias=False,
        )
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(
            out_channels,
            out_channels,
            kernel_size=3,
            padding=1,
            bias=False,
        )
        self.bn2 = nn.BatchNorm2d(out_channels)

        if stride != 1 or in_channels != out_channels:
            self.downsample = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels),
            )
        else:
            self.downsample = nn.Identity()

    def forward(self, inputs: Tensor) -> Tensor:
        identity = self.downsample(inputs)
        outputs = self.conv1(inputs)
        outputs = self.bn1(outputs)
        outputs = self.relu(outputs)
        outputs = self.conv2(outputs)
        outputs = self.bn2(outputs)
        outputs += identity
        return self.relu(outputs)


class BaselineCNN(nn.Module):
    """ResNet18 implemented directly from PyTorch layers and residual blocks."""

    def __init__(self, num_classes: int = 4) -> None:
        super().__init__()
        self.in_channels = 64
        self.conv1 = nn.Conv2d(
            3,
            self.in_channels,
            kernel_size=7,
            stride=2,
            padding=3,
            bias=False,
        )
        self.bn1 = nn.BatchNorm2d(self.in_channels)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)

        self.layer1 = self._make_layer(out_channels=64, blocks=2)
        self.layer2 = self._make_layer(out_channels=128, blocks=2, stride=2)
        self.layer3 = self._make_layer(out_channels=256, blocks=2, stride=2)
        self.layer4 = self._make_layer(out_channels=512, blocks=2, stride=2)

        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512, num_classes)

        self._initialize_weights()

    def _make_layer(self, out_channels: int, blocks: int, stride: int = 1) -> nn.Sequential:
        layers = [BasicBlock(self.in_channels, out_channels, stride)]
        self.in_channels = out_channels
        layers.extend(BasicBlock(self.in_channels, out_channels) for _ in range(1, blocks))
        return nn.Sequential(*layers)

    def _initialize_weights(self) -> None:
        for module in self.modules():
            if isinstance(module, nn.Conv2d):
                nn.init.kaiming_normal_(module.weight, mode="fan_out", nonlinearity="relu")
            elif isinstance(module, (nn.BatchNorm2d, nn.GroupNorm)):
                nn.init.constant_(module.weight, 1)
                nn.init.constant_(module.bias, 0)

    def forward(self, inputs: Tensor) -> Tensor:
        outputs = self.conv1(inputs)
        outputs = self.bn1(outputs)
        outputs = self.relu(outputs)
        outputs = self.maxpool(outputs)
        outputs = self.layer1(outputs)
        outputs = self.layer2(outputs)
        outputs = self.layer3(outputs)
        outputs = self.layer4(outputs)
        outputs = self.avgpool(outputs)
        outputs = outputs.flatten(1)
        return self.fc(outputs)


def build_model(
    name: str,
    num_classes: int = 4,
    pretrained: bool = False,
    freeze_backbone: bool = False,
) -> nn.Module:
    """Construct a supported model and replace its classification head.

    Required names are `manual_resnet18` for the baseline and `resnet18` for transfer learning.
    For transfer learning, use `models.ResNet18_Weights.DEFAULT` as the pretrained weights.
    """
    if name == "manual_resnet18":
        if pretrained:
            raise ValueError("manual_resnet18 does not provide pretrained weights")
        model = BaselineCNN(num_classes=num_classes)
    elif name == "resnet18":
        weights = models.ResNet18_Weights.DEFAULT if pretrained else None
        model = models.resnet18(weights=weights)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    else:
        raise ValueError(f"Unsupported model: {name}")

    if freeze_backbone:
        for parameter in model.parameters():
            parameter.requires_grad = False
        for parameter in model.fc.parameters():
            parameter.requires_grad = True

    return model
