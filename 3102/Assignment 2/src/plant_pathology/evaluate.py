"""Task: evaluate the baseline and final models on the validation set.

Requirements:
1. Read the config, rebuild the model and transforms, and load the checkpoint.
2. Report accuracy, macro F1, and recall for each class.
3. Save labeled confusion matrices as `results/confusion_matrix_baseline.png` and
   `results/confusion_matrix_final.png`.
4. Inspect at least eight incorrect predictions and record them in
   `results/error_analysis.csv`.
5. Group the selected errors into at least two common error types for discussion in `REPORT.md`.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from PIL import Image
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
from torch.utils.data import DataLoader

from plant_pathology import CLASSES
from plant_pathology.data import LeafDataset, build_transforms, load_labeled_csv
from plant_pathology.metrics import classification_metrics
from plant_pathology.models import build_model
from plant_pathology.train import load_config, load_model_checkpoint, select_device


@torch.inference_mode()
def _collect_predictions(
    model: torch.nn.Module,
    loader: DataLoader,
    device: torch.device,
) -> tuple[list[int], list[int], np.ndarray]:
    model.eval()
    targets_all: list[int] = []
    predictions_all: list[int] = []
    probability_batches: list[torch.Tensor] = []
    non_blocking = device.type == "cuda"

    for images, targets in loader:
        images = images.to(device, non_blocking=non_blocking)
        logits = model(images)
        probabilities = torch.softmax(logits, dim=1)
        targets_all.extend(targets.tolist())
        predictions_all.extend(probabilities.argmax(dim=1).cpu().tolist())
        probability_batches.append(probabilities.cpu())

    return targets_all, predictions_all, torch.cat(probability_batches).numpy()


def _save_confusion_matrix(
    targets: list[int],
    predictions: list[int],
    output_path: Path,
) -> None:
    plt.switch_backend("Agg")
    matrix = confusion_matrix(targets, predictions, labels=range(len(CLASSES)))
    figure, axis = plt.subplots(figsize=(7.5, 6.5))
    display = ConfusionMatrixDisplay(matrix, display_labels=CLASSES)
    display.plot(ax=axis, cmap="Blues", colorbar=False, values_format="d")
    axis.set_title("Validation confusion matrix")
    axis.tick_params(axis="x", rotation=25)
    figure.tight_layout()
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def _existing_error_annotations(path: Path) -> dict[str, tuple[str, str]]:
    if not path.exists() or not path.stat().st_size:
        return {}
    existing = pd.read_csv(path).fillna("")
    required = {"image_id", "failure_group", "observation"}
    if not required.issubset(existing.columns):
        return {}
    annotations = {}
    for row in existing.itertuples(index=False):
        failure_group = str(row.failure_group)
        observation = str(row.observation)
        if failure_group != "pending_manual_review" or observation:
            annotations[str(row.image_id)] = (failure_group, observation)
    return annotations


def _save_error_contact_sheet(
    records: list[dict[str, object]],
    image_dir: Path,
    output_path: Path,
) -> None:
    if not records:
        return
    plt.switch_backend("Agg")
    columns = min(4, len(records))
    rows = math.ceil(len(records) / columns)
    figure, axes = plt.subplots(rows, columns, figsize=(4 * columns, 3.4 * rows))
    axes_array = np.atleast_1d(axes).reshape(-1)

    for axis, record in zip(axes_array, records, strict=False):
        image_path = image_dir / f"{record['image_id']}.jpg"
        with Image.open(image_path) as image:
            axis.imshow(image.convert("RGB"))
        axis.set_title(
            f"{record['image_id']}\n"
            f"true: {record['true_label']} | pred: {record['predicted_label']}\n"
            f"confidence: {float(record['confidence']):.3f}",
            fontsize=9,
        )
        axis.axis("off")
    for axis in axes_array[len(records) :]:
        axis.axis("off")

    figure.suptitle("Incorrect validation predictions selected for manual review")
    figure.tight_layout()
    figure.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(figure)


def _save_error_analysis(
    frame: pd.DataFrame,
    targets: list[int],
    predictions: list[int],
    probabilities: np.ndarray,
    image_dir: Path,
    results_dir: Path,
    requested_examples: int,
) -> int:
    error_csv = results_dir / "error_analysis.csv"
    annotations = _existing_error_annotations(error_csv)
    incorrect = [
        index
        for index, (target, prediction) in enumerate(zip(targets, predictions, strict=True))
        if target != prediction
    ]
    incorrect.sort(key=lambda index: probabilities[index, predictions[index]], reverse=True)
    selected = incorrect[:requested_examples]

    records: list[dict[str, object]] = []
    for index in selected:
        image_id = str(frame.iloc[index]["image_id"])
        failure_group, observation = annotations.get(
            image_id,
            (
                "pending_manual_review",
                "",
            ),
        )
        records.append(
            {
                "image_id": image_id,
                "true_label": CLASSES[targets[index]],
                "predicted_label": CLASSES[predictions[index]],
                "confidence": float(probabilities[index, predictions[index]]),
                "failure_group": failure_group,
                "observation": observation,
            }
        )

    columns = [
        "image_id",
        "true_label",
        "predicted_label",
        "confidence",
        "failure_group",
        "observation",
    ]
    pd.DataFrame(records, columns=columns).to_csv(error_csv, index=False)
    _save_error_contact_sheet(records, image_dir, results_dir / "error_examples.png")
    return len(records)


def evaluate(config_path: Path, checkpoint: Path) -> None:
    """Evaluate one checkpoint and save its confusion matrix and error examples."""
    config = load_config(config_path)
    device = select_device()
    frame = load_labeled_csv(Path(config["validation_csv"]))
    dataset = LeafDataset(
        frame,
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

    targets, predictions, probabilities = _collect_predictions(model, loader, device)
    metrics = classification_metrics(targets, predictions)
    print(f"Validation accuracy: {metrics['accuracy']:.4f}")
    print(f"Validation macro F1: {metrics['macro_f1']:.4f}")
    for index, class_name in enumerate(CLASSES):
        print(f"Recall ({class_name}): {metrics[f'recall_class_{index}']:.4f}")

    results_dir = Path(config.get("results_dir", "results"))
    results_dir.mkdir(parents=True, exist_ok=True)
    default_label = "baseline" if str(config["run_id"]) == "baseline" else "final"
    evaluation_label = str(config.get("evaluation_label", default_label))
    if evaluation_label not in {"baseline", "final"}:
        raise ValueError("evaluation_label must be either 'baseline' or 'final'")
    confusion_path = results_dir / f"confusion_matrix_{evaluation_label}.png"
    _save_confusion_matrix(targets, predictions, confusion_path)

    requested_examples = max(8, int(config.get("error_examples", 8)))
    error_count = _save_error_analysis(
        frame,
        targets,
        predictions,
        probabilities,
        Path(config["image_dir"]),
        results_dir,
        requested_examples,
    )
    print(f"Confusion matrix: {confusion_path}")
    print(f"Error examples recorded: {error_count} in {results_dir / 'error_analysis.csv'}")
    if error_count < 8:
        print("Warning: the model made fewer than eight validation errors; all were recorded.")
    else:
        print("Complete failure_group and observation after reviewing error_examples.png.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    args = parser.parse_args()
    evaluate(args.config, args.checkpoint)


if __name__ == "__main__":
    main()
