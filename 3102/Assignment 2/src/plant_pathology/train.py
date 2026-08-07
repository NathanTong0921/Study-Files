"""Task: implement model training and experiment recording.

Requirements:
1. Read the JSON config and set the random seed.
2. Build train and validation data loaders, model, loss, and optimizer.
3. Train for the configured number of epochs and evaluate on the fixed validation set after each
   epoch. The required baseline config must train manual ResNet18 from scratch for exactly 50
   configured epochs.
4. Save the checkpoint with the best validation macro F1.
5. Save the baseline training curves as `results/training_curves_baseline.png`.
6. Append the run settings and final validation results to `results/experiments.csv`.
7. Train both the baseline and transfer-learning configurations.
8. Run ablation experiments that change one factor at a time. These may include, but are not limited
   to, batch size and learning rate. Keep image_size=128 for required comparisons. Explore as many
   meaningful choices as the compute budget permits. Use no more than 50 epochs for each ablation;
   you may stop earlier when appropriate. Explain the experiments in `REPORT.md`.
9. For optional bonus work, save one comparison figure containing train and validation accuracy
   curves for both the original method and the algorithmically improved method.
10. You may use the model and configuration you consider best to generate the final prediction.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import shutil
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.optim import Optimizer
from torch.utils.data import DataLoader

from plant_pathology.data import (
    LeafDataset,
    build_bonus_transforms,
    build_transforms,
    load_labeled_csv,
)
from plant_pathology.metrics import classification_metrics
from plant_pathology.models import build_model


def load_config(path: Path) -> dict[str, Any]:
    """Read one JSON configuration file."""
    with path.open(encoding="utf-8") as file:
        config = json.load(file)
    return config


def select_device() -> torch.device:
    """Automatically select CUDA, MPS, or CPU."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def set_random_seed(seed: int) -> None:
    """Seed the random-number generators used by the training pipeline."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if torch.backends.cudnn.is_available():
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True


def load_model_checkpoint(
    model: nn.Module,
    checkpoint_path: Path,
    device: torch.device,
) -> dict[str, Any]:
    """Load a checkpoint produced by this project's training pipeline."""
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=True)
    model.load_state_dict(checkpoint["model_state_dict"])
    return checkpoint


def _make_loader(
    dataset: LeafDataset,
    batch_size: int,
    shuffle: bool,
    seed: int,
    num_workers: int,
    pin_memory: bool,
) -> DataLoader:
    generator = torch.Generator().manual_seed(seed)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory,
        persistent_workers=num_workers > 0,
        generator=generator,
    )


def _build_optimizer(model: nn.Module, config: dict[str, Any]) -> Optimizer:
    parameters = [parameter for parameter in model.parameters() if parameter.requires_grad]
    name = str(config["optimizer"]).lower()
    if name != "adamw":
        raise ValueError("Only the AdamW optimizer is supported")
    return torch.optim.AdamW(
        parameters,
        lr=float(config["learning_rate"]),
        weight_decay=float(config.get("weight_decay", 0.0)),
    )


def _train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: Optimizer,
    device: torch.device,
) -> tuple[float, float]:
    model.train()
    loss_sum = 0.0
    correct = 0
    example_count = 0
    non_blocking = device.type == "cuda"

    for images, targets in loader:
        images = images.to(device, non_blocking=non_blocking)
        targets = targets.to(device, non_blocking=non_blocking)
        optimizer.zero_grad(set_to_none=True)
        logits = model(images)
        loss = criterion(logits, targets)
        loss.backward()
        optimizer.step()

        batch_size = targets.size(0)
        loss_sum += loss.item() * batch_size
        correct += (logits.argmax(dim=1) == targets).sum().item()
        example_count += batch_size

    return loss_sum / example_count, correct / example_count


@torch.inference_mode()
def evaluate_model(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> dict[str, float]:
    """Compute validation loss and classification metrics."""
    model.eval()
    loss_sum = 0.0
    example_count = 0
    targets_all: list[int] = []
    predictions_all: list[int] = []
    non_blocking = device.type == "cuda"

    for images, targets in loader:
        images = images.to(device, non_blocking=non_blocking)
        targets = targets.to(device, non_blocking=non_blocking)
        logits = model(images)
        loss = criterion(logits, targets)

        batch_size = targets.size(0)
        loss_sum += loss.item() * batch_size
        example_count += batch_size
        targets_all.extend(targets.cpu().tolist())
        predictions_all.extend(logits.argmax(dim=1).cpu().tolist())

    metrics = classification_metrics(targets_all, predictions_all)
    metrics["loss"] = loss_sum / example_count
    return metrics


def _save_training_curves(
    history: dict[str, list[float]],
    run_id: str,
    results_dir: Path,
) -> Path:
    plt.switch_backend("Agg")
    completed_epochs = range(1, len(history["train_loss"]) + 1)
    figure, (loss_axis, metric_axis) = plt.subplots(1, 2, figsize=(12, 4.5))

    loss_axis.plot(completed_epochs, history["train_loss"], label="Train loss")
    loss_axis.plot(completed_epochs, history["val_loss"], label="Validation loss")
    loss_axis.set_xlabel("Epoch")
    loss_axis.set_ylabel("Cross-entropy loss")
    loss_axis.set_title("Loss")
    loss_axis.grid(alpha=0.3)
    loss_axis.legend()

    metric_axis.plot(completed_epochs, history["train_accuracy"], label="Train accuracy")
    metric_axis.plot(completed_epochs, history["val_accuracy"], label="Validation accuracy")
    metric_axis.plot(completed_epochs, history["val_macro_f1"], label="Validation macro F1")
    metric_axis.set_xlabel("Epoch")
    metric_axis.set_ylabel("Score")
    metric_axis.set_ylim(0.0, 1.0)
    metric_axis.set_title("Classification metrics")
    metric_axis.grid(alpha=0.3)
    metric_axis.legend()

    figure.suptitle(f"Training history: {run_id}")
    figure.tight_layout()
    safe_run_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", run_id)
    output_path = results_dir / f"training_curves_{safe_run_id}.png"
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)
    return output_path


def _training_history_path(run_id: str, results_dir: Path) -> Path:
    safe_run_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", run_id)
    return results_dir / f"training_history_{safe_run_id}.csv"


def _save_training_history(
    history: dict[str, list[float]],
    run_id: str,
    results_dir: Path,
) -> Path:
    completed_epochs = len(history["train_loss"])
    history_frame = pd.DataFrame(
        {
            "epoch": range(1, completed_epochs + 1),
            "train_loss": history["train_loss"],
            "train_accuracy": history["train_accuracy"],
            "val_loss": history["val_loss"],
            "val_accuracy": history["val_accuracy"],
            "val_macro_f1": history["val_macro_f1"],
        }
    )
    output_path = _training_history_path(run_id, results_dir)
    history_frame.to_csv(output_path, index=False)
    return output_path


def _save_bonus_comparison(
    reference_run_id: str,
    improved_run_id: str,
    improved_history: dict[str, list[float]],
    results_dir: Path,
    title: str,
    output_filename: str,
) -> Path:
    """Plot train and validation accuracy with and without the bonus improvement."""
    reference_path = _training_history_path(reference_run_id, results_dir)
    if not reference_path.exists():
        raise FileNotFoundError(
            f"Missing {reference_path}; rerun {reference_run_id} before the bonus run"
        )
    reference = pd.read_csv(reference_path)
    required_columns = {"epoch", "train_accuracy", "val_accuracy"}
    missing = required_columns.difference(reference.columns)
    if missing:
        raise ValueError(f"Reference history is missing columns: {sorted(missing)}")

    improved_epochs = range(1, len(improved_history["train_accuracy"]) + 1)
    plt.switch_backend("Agg")
    figure, axis = plt.subplots(figsize=(9, 5.5))
    axis.plot(
        reference["epoch"],
        reference["train_accuracy"],
        linestyle="--",
        color="tab:blue",
        label=f"{reference_run_id}: train",
    )
    axis.plot(
        reference["epoch"],
        reference["val_accuracy"],
        color="tab:blue",
        label=f"{reference_run_id}: validation",
    )
    axis.plot(
        improved_epochs,
        improved_history["train_accuracy"],
        linestyle="--",
        color="tab:orange",
        label=f"{improved_run_id}: train",
    )
    axis.plot(
        improved_epochs,
        improved_history["val_accuracy"],
        color="tab:orange",
        label=f"{improved_run_id}: validation",
    )
    axis.set_xlabel("Epoch")
    axis.set_ylabel("Accuracy")
    axis.set_ylim(0.0, 1.0)
    axis.set_title(title)
    axis.grid(alpha=0.3)
    axis.legend()
    figure.tight_layout()
    output_path = results_dir / output_filename
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)
    return output_path


def _record_experiment(
    config: dict[str, Any],
    metrics: dict[str, float],
    best_epoch: int,
) -> None:
    columns = [
        "run_id",
        "model",
        "main_change",
        "image_size",
        "batch_size",
        "epochs",
        "optimizer",
        "learning_rate",
        "seed",
        "val_accuracy",
        "val_macro_f1",
        "notes",
    ]
    run_id = str(config["run_id"])
    if "main_change" in config:
        main_change = str(config["main_change"])
    elif run_id == "baseline":
        main_change = "required manual ResNet18 baseline"
    elif bool(config.get("pretrained", False)):
        main_change = "ImageNet pretrained weights"
    else:
        main_change = ""

    details = [
        f"best_epoch={best_epoch}",
        f"pretrained={bool(config.get('pretrained', False))}",
        f"freeze_backbone={bool(config.get('freeze_backbone', False))}",
        f"weight_decay={float(config.get('weight_decay', 0.0))}",
    ]
    if bool(config.get("training_augmentation", False)):
        details.append("training_augmentation=light_geometric")
    if config.get("notes"):
        details.append(str(config["notes"]))
    record = {
        "run_id": run_id,
        "model": config["model"],
        "main_change": main_change,
        "image_size": int(config["image_size"]),
        "batch_size": int(config["batch_size"]),
        "epochs": int(config["epochs"]),
        "optimizer": config["optimizer"],
        "learning_rate": float(config["learning_rate"]),
        "seed": int(config["seed"]),
        "val_accuracy": metrics["accuracy"],
        "val_macro_f1": metrics["macro_f1"],
        "notes": "; ".join(details),
    }

    results_path = Path(config["results_csv"])
    results_path.parent.mkdir(parents=True, exist_ok=True)
    if results_path.exists() and results_path.stat().st_size:
        existing = pd.read_csv(results_path)
        if "run_id" in existing:
            existing = existing.loc[existing["run_id"].astype(str) != run_id]
    else:
        existing = pd.DataFrame(columns=columns)
    new_record = pd.DataFrame([record])
    if existing.empty:
        updated = new_record
    else:
        updated = pd.concat([existing, new_record], ignore_index=True)
    for column in columns:
        if column not in updated:
            updated[column] = ""
    updated.loc[:, columns].to_csv(results_path, index=False)


def train(config_path: Path) -> None:
    """Train one configured experiment and append its result record.

    The best checkpoint is selected by validation macro F1.
    """
    config = load_config(config_path)
    seed = int(config["seed"])
    set_random_seed(seed)
    device = select_device()
    image_size = int(config["image_size"])
    batch_size = int(config["batch_size"])
    num_workers = int(config.get("num_workers", 0))
    pin_memory = device.type == "cuda"
    results_dir = Path(config.get("results_dir", "results"))
    results_dir.mkdir(parents=True, exist_ok=True)
    bonus_reference_run_id = config.get("bonus_reference_run_id")
    if bonus_reference_run_id is not None:
        reference_path = _training_history_path(str(bonus_reference_run_id), results_dir)
        if not reference_path.exists():
            raise FileNotFoundError(
                f"Missing {reference_path}; rerun {bonus_reference_run_id} before the bonus run"
            )

    train_frame = load_labeled_csv(Path(config["train_csv"]))
    validation_frame = load_labeled_csv(Path(config["validation_csv"]))
    image_dir = Path(config["image_dir"])
    if bool(config.get("training_augmentation", False)):
        train_transform = build_bonus_transforms(image_size)
    else:
        train_transform = build_transforms(image_size, training=True)
    train_dataset = LeafDataset(
        train_frame,
        image_dir,
        train_transform,
    )
    validation_dataset = LeafDataset(
        validation_frame,
        image_dir,
        build_transforms(image_size, training=False),
    )
    train_loader = _make_loader(
        train_dataset,
        batch_size,
        shuffle=True,
        seed=seed,
        num_workers=num_workers,
        pin_memory=pin_memory,
    )
    validation_loader = _make_loader(
        validation_dataset,
        batch_size,
        shuffle=False,
        seed=seed,
        num_workers=num_workers,
        pin_memory=pin_memory,
    )

    model = build_model(
        str(config["model"]),
        num_classes=4,
        pretrained=bool(config.get("pretrained", False)),
        freeze_backbone=bool(config.get("freeze_backbone", False)),
    ).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = _build_optimizer(model, config)

    history = {
        "train_loss": [],
        "train_accuracy": [],
        "val_loss": [],
        "val_accuracy": [],
        "val_macro_f1": [],
    }
    checkpoint_dir = Path(config["checkpoint_dir"])
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    safe_run_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(config["run_id"]))
    run_checkpoint = checkpoint_dir / f"best_{safe_run_id}.pt"
    default_checkpoint = checkpoint_dir / "best.pt"
    best_macro_f1 = -1.0
    best_epoch = 0

    print(f"Training {config['run_id']} on {device} with {len(train_dataset)} examples")
    for epoch in range(1, int(config["epochs"]) + 1):
        train_loss, train_accuracy = _train_one_epoch(
            model,
            train_loader,
            criterion,
            optimizer,
            device,
        )
        validation_metrics = evaluate_model(model, validation_loader, criterion, device)
        history["train_loss"].append(train_loss)
        history["train_accuracy"].append(train_accuracy)
        history["val_loss"].append(validation_metrics["loss"])
        history["val_accuracy"].append(validation_metrics["accuracy"])
        history["val_macro_f1"].append(validation_metrics["macro_f1"])

        print(
            f"Epoch {epoch:03d}/{int(config['epochs']):03d} | "
            f"train_loss={train_loss:.4f} | train_acc={train_accuracy:.4f} | "
            f"val_acc={validation_metrics['accuracy']:.4f} | "
            f"val_macro_f1={validation_metrics['macro_f1']:.4f}"
        )
        if validation_metrics["macro_f1"] > best_macro_f1:
            best_macro_f1 = validation_metrics["macro_f1"]
            best_epoch = epoch
            checkpoint = {
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "epoch": epoch,
                "val_metrics": validation_metrics,
                "config": config,
            }
            torch.save(checkpoint, run_checkpoint)

    shutil.copyfile(run_checkpoint, default_checkpoint)
    load_model_checkpoint(model, run_checkpoint, device)
    best_metrics = evaluate_model(model, validation_loader, criterion, device)

    curve_path = _save_training_curves(history, str(config["run_id"]), results_dir)
    history_path = _save_training_history(history, str(config["run_id"]), results_dir)
    bonus_figure_path = None
    if bonus_reference_run_id is not None:
        bonus_figure_path = _save_bonus_comparison(
            str(bonus_reference_run_id),
            str(config["run_id"]),
            history,
            results_dir,
            str(config.get("bonus_comparison_title", "Bonus method comparison")),
            str(config.get("bonus_comparison_filename", "bonus_comparison.png")),
        )
    _record_experiment(config, best_metrics, best_epoch)
    print(
        f"Best checkpoint: {run_checkpoint} (epoch {best_epoch}, "
        f"macro_f1={best_metrics['macro_f1']:.4f})"
    )
    print(f"Training curves: {curve_path}")
    print(f"Training history: {history_path}")
    if bonus_figure_path is not None:
        print(f"Bonus comparison: {bonus_figure_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    train(args.config)


if __name__ == "__main__":
    main()
