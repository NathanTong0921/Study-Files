"""Task: generate predictions for the course test set.

Requirements:
1. Read the config, rebuild the model and test transforms, and load the checkpoint.
2. Predict one four-class probability row for every image ID in `data/test.csv`.
3. Save `predictions/submission.csv` with columns in this exact order:
   image_id, healthy, multiple_diseases, rust, scab.
4. Preserve every test image ID exactly once and ensure each probability row sums to 1.
5. Run `python -m plant_pathology.validate_submission` after creating the file.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path

import pandas as pd
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

from plant_pathology import CLASSES
from plant_pathology.data import build_transforms, load_test_csv
from plant_pathology.models import build_model
from plant_pathology.train import load_config, load_model_checkpoint, select_device
from plant_pathology.validate_submission import validate_submission


class TestLeafDataset(Dataset[tuple[torch.Tensor, str]]):
    """Load unlabeled test images while preserving their manifest IDs."""

    def __init__(
        self,
        frame: pd.DataFrame,
        image_dir: Path,
        transform: Callable[[Image.Image], torch.Tensor],
    ) -> None:
        self.frame = frame.reset_index(drop=True)
        self.image_dir = image_dir
        self.transform = transform

    def __len__(self) -> int:
        return len(self.frame)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, str]:
        image_id = str(self.frame.iloc[index]["image_id"])
        image_path = self.image_dir / f"{image_id}.jpg"
        with Image.open(image_path) as image:
            image_tensor = self.transform(image.convert("RGB"))
        return image_tensor, image_id


def predict(config_path: Path, checkpoint: Path, output: Path) -> None:
    """Generate and validate four-class probabilities for the private test set."""
    config = load_config(config_path)
    device = select_device()
    test_frame = load_test_csv(Path(config["test_csv"]))
    dataset = TestLeafDataset(
        test_frame,
        Path(config["image_dir"]),
        build_transforms(int(config["image_size"]), training=False),
    )
    loader = DataLoader(
        dataset,
        batch_size=int(config["batch_size"]),
        shuffle=False,
        num_workers=int(config.get("num_workers", 0)),
        pin_memory=device.type == "cuda",
        persistent_workers=int(config.get("num_workers", 0)) > 0,
    )
    model = build_model(
        str(config["model"]),
        num_classes=4,
        pretrained=bool(config.get("pretrained", False)),
        freeze_backbone=bool(config.get("freeze_backbone", False)),
    ).to(device)
    load_model_checkpoint(model, checkpoint, device)
    model.eval()

    image_ids: list[str] = []
    probability_batches: list[torch.Tensor] = []
    non_blocking = device.type == "cuda"
    with torch.inference_mode():
        for images, batch_ids in loader:
            images = images.to(device, non_blocking=non_blocking)
            probabilities = torch.softmax(model(images), dim=1)
            probability_batches.append(probabilities.cpu())
            image_ids.extend(batch_ids)

    probability_array = torch.cat(probability_batches).numpy()
    submission = pd.DataFrame({"image_id": image_ids})
    for index, class_name in enumerate(CLASSES):
        submission[class_name] = probability_array[:, index]

    output.parent.mkdir(parents=True, exist_ok=True)
    submission.to_csv(output, index=False)
    validate_submission(Path(config["test_csv"]), output)
    print(f"Saved {len(submission)} predictions to {output}")
    print("Submission format is valid.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("predictions/submission.csv"))
    args = parser.parse_args()
    predict(args.config, args.checkpoint, args.output)


if __name__ == "__main__":
    main()
