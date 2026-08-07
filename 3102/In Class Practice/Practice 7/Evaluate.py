from pathlib import Path
import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader


class ResNetBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)

        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)

        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )
        else:
            self.shortcut = nn.Identity()
        
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        identity = self.shortcut(x)
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out = out + identity
        out = self.relu(out)
        return out
    
class InceptionModule(nn.Module):
    def __init__(self, in_channels, branch_channels):
        super().__init__()
        self.branch1 = nn.Sequential(
            nn.Conv2d(in_channels, branch_channels, kernel_size=1, bias=False),
            nn.BatchNorm2d(branch_channels),
            nn.ReLU(inplace=True)
        )
        self.branch2 = nn.Sequential(
            nn.Conv2d(in_channels, branch_channels, kernel_size=1, bias=False),
            nn.BatchNorm2d(branch_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(branch_channels, branch_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(branch_channels),
            nn.ReLU(inplace=True)
        )
        self.branch3 = nn.Sequential(
            nn.Conv2d(in_channels, branch_channels, kernel_size=1, bias=False),
            nn.BatchNorm2d(branch_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(branch_channels, branch_channels, kernel_size=5, padding=2, bias=False),
            nn.BatchNorm2d(branch_channels),
            nn.ReLU(inplace=True)
        )
        self.branch4 = nn.Sequential(
            nn.MaxPool2d(kernel_size=3, stride=1, padding=1),
            nn.Conv2d(in_channels, branch_channels, kernel_size=1, bias=False),
            nn.BatchNorm2d(branch_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        branch1 = self.branch1(x)
        branch2 = self.branch2(x)
        branch3 = self.branch3(x)
        branch4 = self.branch4(x)
        return torch.cat([branch1, branch2, branch3, branch4], dim=1)
    
class CIFAR10CNN(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        self.stem = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True)
        )
        self.features = nn.Sequential(
            ResNetBlock(64, 64),
            ResNetBlock(64, 128, stride=2),
            InceptionModule(128, 32),
            ResNetBlock(128, 256, stride=2),
            InceptionModule(256, 64)
        )
        self.global_avg_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.dropout = nn.Dropout(p=0.3)
        self.fc = nn.Linear(256, num_classes)

    def forward(self, x):
        x = self.stem(x)
        x = self.features(x)
        x = self.global_avg_pool(x)
        x = torch.flatten(x, 1)
        x = self.dropout(x)
        x = self.fc(x)
        return x
    
device = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")

def evaluate(model, dataloader):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in dataloader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            predictions = outputs.argmax(dim=1)
            total += labels.size(0)
            correct += (predictions == labels).sum().item()
    return 100.0 * correct / total

def count_parameters(model):
    return sum(parameter.numel() for parameter in model.parameters())

def main():
    custom_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

    pretrained_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(
            (0.4914, 0.4822, 0.4465),
            (0.2023, 0.1994, 0.2010)
        )
    ])

    custom_testset = torchvision.datasets.CIFAR10(
        root="./data",
        train=False,
        download=True,
        transform=custom_transform
    )
    pretrained_testset = torchvision.datasets.CIFAR10(
        root="./data",
        train=False,
        download=True,
        transform=pretrained_transform
    )

    custom_testloader = DataLoader(
        custom_testset,
        batch_size=128,
        shuffle=False,
        num_workers=0
    )
    pretrained_testloader = DataLoader(
        pretrained_testset,
        batch_size=128,
        shuffle=False,
        num_workers=0
    )

    weights_path = Path("mymodel.pth")

    custom_model = CIFAR10CNN().to(device)
    state_dict = torch.load(weights_path, map_location=device)
    custom_model.load_state_dict(state_dict)

    print("Evaluating custom CNN...")
    custom_accuracy = evaluate(custom_model, custom_testloader)

    print("Loading pretrained CIFAR-10 MobileNetV2 x0.5...")
    mobilenet_model = torch.hub.load(
        "chenyaofo/pytorch-cifar-models",
        "cifar10_mobilenetv2_x0_5",
        pretrained=True
    ).to(device)

    print("Evaluating pretrained MobileNetV2 x0.5...")
    mobilenet_accuracy = evaluate(
        mobilenet_model,
        pretrained_testloader
    )

    custom_parameters = count_parameters(custom_model)
    mobilenet_parameters = count_parameters(mobilenet_model)

    print("\nComparison")
    print("-" * 67)
    print(f"{'Model':<34}{'Accuracy':>14}{'Parameters':>19}")
    print("-" * 67)
    print(
        f"{'Custom ResNet-Inception CNN':<34}"
        f"{custom_accuracy:>13.2f}%"
        f"{custom_parameters:>19,}"
    )
    print(
        f"{'Pretrained MobileNetV2 x0.5':<34}"
        f"{mobilenet_accuracy:>13.2f}%"
        f"{mobilenet_parameters:>19,}"
    )
    print("-" * 67)

    accuracy_difference = custom_accuracy - mobilenet_accuracy
    if accuracy_difference > 0:
        print(
            "The custom CNN is "
            f"{accuracy_difference:.2f} percentage points more accurate."
        )
    elif accuracy_difference < 0:
        print(
            "The pretrained MobileNetV2 is "
            f"{-accuracy_difference:.2f} percentage points more accurate."
        )
    else:
        print("The two models have the same test accuracy.")


if __name__ == "__main__":
    main()