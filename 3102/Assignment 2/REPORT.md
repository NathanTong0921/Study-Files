# Assignment 2 Report

## Setup

- Name and student ID: Zhao TONG, 50025256
- Hardware used: Intel Core i9-13900 CPU and NVIDIA GeForce RTX 5070 Ti Laptop GPU
- Commands needed to run your final model:
```bash
uv sync --extra dev
uv run python -m plant_pathology.train --config configs/transfer_batch_16.json
uv run python -m plant_pathology.evaluate --config configs/transfer_batch_16.json --checkpoint checkpoints/best_transfer_batch_16.pt
uv run python -m plant_pathology.predict --config configs/transfer_batch_16.json --checkpoint checkpoints/best_transfer_batch_16.pt --output predictions/submission.csv
uv run python -m plant_pathology.validate_submission
```

## Data Processing

The provided manifests contain 1,274 training images, 273 validation images, and 274 test images. The training-set counts are 361 `healthy`, 63 `multiple_diseases`, 436 `rust`, and 414 `scab`; the corresponding validation counts are 77, 14, 93, and 89. Thus, `multiple_diseases` is substantially underrepresented, which makes accuracy alone an incomplete description of performance.

Each labeled row stores the target as a one-hot vector in the fixed order `healthy`, `multiple_diseases`, `rust`, and `scab`. The dataset converts this vector to a class index from 0 to 3. Images are opened from `data/images/<image_id>.jpg` and explicitly converted to RGB before preprocessing.

For both required models and every required ablation, each image is resized directly to 128 by 128 pixels, converted to a tensor with values in [0, 1], and normalized using the ImageNet channel mean (0.485, 0.456, 0.406) and standard deviation (0.229, 0.224, 0.225). The provided deterministic `build_transforms` pipeline is used unchanged for the required baseline and transfer runs. Both the baseline and transfer-learning configurations use `image_size=128`, as required for a fair comparison. The optional bonus changes only the training transform; its validation and test transforms remain identical to the required pipeline.

## Models

The required baseline is a manual ResNet18 implemented from PyTorch layers. Its stem consists of a 7 by 7 convolution with 64 output channels, batch normalization, ReLU, and 3 by 3 max pooling. This is followed by four stages with 64, 128, 256, and 512 channels and [2, 2, 2, 2] basic residual blocks. Each block contains two 3 by 3 convolutions. A 1 by 1 projection path is used when spatial resolution or channel count changes; otherwise the residual path is the identity. Adaptive average pooling and a fully connected layer produce four unnormalized class logits. Convolutional layers use Kaiming initialization, and normalization layers start with unit scale and zero bias. This model is initialized randomly and trained from scratch for exactly 50 configured epochs.

The transfer-learning model is torchvision ResNet18 initialized with `ResNet18_Weights.DEFAULT`. Its original classification layer is replaced with a randomly initialized four-output layer. In the required transfer configuration, `freeze_backbone=false`, so both the pretrained convolutional backbone and the new classification layer are fine-tuned. The model builder also supports a frozen-backbone setting used in one ablation: all backbone parameters are frozen while the replacement layer remains trainable.

## Results and Ablations

Except for the factor named in the `Change` column, the transfer ablations use the required transfer settings: pretrained ResNet18, image size 128, batch size 32, learning rate 0.0003, weight decay 0.0001, seed 398, AdamW, full-backbone fine-tuning, and 12 epochs. Results below are measured from each run's best validation-macro-F1 checkpoint. The complete machine-readable records are in `results/experiments.csv`.

| Run | Change | Batch | Learning rate | Weight decay | Best epoch | Val. accuracy | Val. macro F1 |
|---|---|---:|---:|---:|---:|---:|---:|
| `baseline` | Manual ResNet18 baseline | 32 | 0.0010 | 0.0001 | 36 | 0.7582 | 0.6105 |
| `transfer_resnet18` | ImageNet-pretrained ResNet18 | 32 | 0.0003 | 0.0001 | 6 | 0.8791 | 0.7900 |
| `transfer_lr_1e-4` | Learning rate 0.0003 to 0.0001 | 32 | 0.0001 | 0.0001 | 11 | 0.8938 | 0.7181 |
| `transfer_lr_1e-3` | Learning rate 0.0003 to 0.0010 | 32 | 0.0010 | 0.0001 | 3 | 0.8791 | 0.7530 |
| `transfer_batch_64` | Batch size 32 to 64 | 64 | 0.0003 | 0.0001 | 5 | 0.8974 | 0.7670 |
| `transfer_frozen` | Freeze the pretrained backbone | 32 | 0.0003 | 0.0001 | 11 | 0.7179 | 0.5518 |
| `transfer_weight_decay_0` | Weight decay 0.0001 to 0 | 32 | 0.0003 | 0 | 4 | 0.9048 | 0.7794 |
| `transfer_batch_16` | Batch size 32 to 16 | 16 | 0.0003 | 0.0001 | 5 | **0.9158** | 0.7877 |
| `bonus_augmentation` | Add light geometric training augmentation to `transfer_batch_16` | 16 | 0.0003 | 0.0001 | 10 | 0.8901 | **0.7974** |

### Baseline and transfer comparison

The pretrained transfer model exceeded the manual baseline by 12.09 percentage points in validation accuracy and 17.95 points in macro F1. This large gain is reasonable because the dataset has only 1,274 training images, while the transfer model starts from reusable ImageNet visual features. The manual model nevertheless fulfills the intended from-scratch baseline and provides evidence of the difficulty of learning a full ResNet18 from this small dataset.

The baseline curves below show severe overfitting. Training accuracy approaches 1.0 and training loss approaches zero, while validation accuracy settles near 0.78 and validation macro F1 near 0.60. Validation loss remains high and noisy. Completing 50 epochs therefore does not repair the generalization gap; the best checkpoint occurs at epoch 36 rather than at the final epoch.

![Baseline training curves](results/training_curves_baseline.png)

### Learning-rate ablations

Reducing the learning rate to 0.0001 raised accuracy from 0.8791 to 0.8938 but reduced macro F1 from 0.7900 to 0.7181. Increasing it to 0.0010 left accuracy at 0.8791 and reduced macro F1 to 0.7530. Therefore neither alternative improved both metrics. The default 0.0003 rate gave the best class-balanced result among the three and was retained for subsequent comparisons.

### Batch-size ablations

Batch size 64 raised accuracy to 0.8974 but lowered macro F1 to 0.7670. Batch size 16 produced the highest non-bonus accuracy, 0.9158, while its macro F1 of 0.7877 was only 0.24 percentage points below the required transfer run. The smaller batch may introduce useful gradient noise, although a single seed is insufficient to establish that explanation causally. Because both validation accuracy and macro F1 matter, batch size 16 offered the strongest overall trade-off and was selected for the final test prediction.

### Backbone-freezing ablation

Freezing the pretrained backbone reduced accuracy to 0.7179 and macro F1 to 0.5518, the weakest transfer result. Training only the new four-class head was therefore insufficient for the visual differences among the leaf conditions at 128 by 128 resolution. Fine-tuning the entire backbone was important for adapting ImageNet features to disease texture and lesion appearance.

### Weight-decay ablation

Removing weight decay increased accuracy from 0.8791 to 0.9048 but reduced macro F1 from 0.7900 to 0.7794. This suggests that the tested weight decay provided a small class-balance benefit but was not decisive for overall accuracy. Weight decay 0.0001 was retained in the final batch-size-16 model because it was the controlled default and because the accuracy gain from the batch-size change did not require removing regularization.

## Evaluation and Errors

The required baseline and selected final model were reloaded from their saved checkpoints and evaluated on the fixed 273-image validation set.

| Metric | Manual baseline | Final `transfer_batch_16` |
|---|---:|---:|
| Accuracy | 0.7582 | **0.9158** |
| Macro F1 | 0.6105 | **0.7877** |
| Recall: `healthy` | 0.6753 | **0.9740** |
| Recall: `multiple_diseases` | 0.0714 | **0.2143** |
| Recall: `rust` | 0.8602 | **0.9892** |
| Recall: `scab` | 0.8315 | **0.8989** |

![Baseline confusion matrix](results/confusion_matrix_baseline.png)

![Final-model confusion matrix](results/confusion_matrix_final.png)

The baseline correctly classified 207 of 273 validation images. Its largest error was predicting 24 of 77 healthy leaves as scab, and it recognized only 1 of 14 `multiple_diseases` examples. The final model correctly classified 250 images. It improved healthy recognition from 52 to 75 correct, rust from 80 to 92, scab from 74 to 80, and `multiple_diseases` from 1 to 3. The remaining systematic weakness is `multiple_diseases`: its 11 errors are distributed across healthy (2), rust (4), and scab (5). The other prominent confusion is scab to healthy (9 images).

The eight highest-confidence incorrect final-model predictions were manually reviewed and recorded in `results/error_analysis.csv`. Five are true `multiple_diseases` images and three are true scab images. Four recurring visual failure groups were identified:

- `subtle_or_low_contrast` (3 images): symptoms occupy little of the leaf or have weak contrast, causing one `multiple_diseases` and two scab images to appear healthy;
- `dominant_rust_pattern` (2 images): clear circular orange-brown lesions dominate mixed-disease images, so the model predicts rust and overlooks less conspicuous evidence;
- `mixed_or_ambiguous_symptoms` (2 images): several lesion types overlap, but a scab-like pattern is visually strongest;
- `uneven_illumination` (1 image): strong dappled shadow overwhelms small scab lesions and leads to a healthy prediction.

All eight selected errors have confidence between 0.9520 and 0.9982, showing that the model can be highly confident on ambiguous, low-contrast, or poorly illuminated cases. Because these were selected as the highest-confidence errors, their group counts are illustrative rather than representative of all 23 validation errors.

## Test Prediction

`predictions/submission.csv` was produced by `transfer_batch_16` using `checkpoints/best_transfer_batch_16.pt`, selected at epoch 5. It achieved the highest validation accuracy of the non-bonus runs, 0.9158, while retaining a macro F1 of 0.7877, very close to the required transfer model's 0.7900. The augmentation model was not selected for submission because its modest macro-F1 gain came with a 2.56-percentage-point reduction in checkpoint accuracy. Running `python -m plant_pathology.validate_submission` reported `Submission format is valid.`

## Bonus Improvement

### Method and controlled comparison

The transfer runs reached nearly perfect training accuracy after only a few epochs while validation accuracy remained substantially lower, indicating overfitting on the 1,274-image training set. The bonus method adds light, label-preserving geometric augmentation to the training images: independent horizontal and vertical flips with probability 0.5 and a random rotation within 15 degrees. Leaf orientation does not determine the disease class, so these transformations encourage the model to rely less on memorized orientation and composition. Rotation uses bilinear interpolation and a fill color close to the ImageNet mean to avoid high-contrast black corners. Aggressive crops and color jitter were excluded because small lesions and disease-related color are diagnostically important.

The paired reference is `transfer_batch_16`, not the required batch-size-32 transfer run. Both paired runs use the same pretrained ResNet18, cross-entropy loss, batch size 16, learning rate 0.0003, weight decay 0.0001, seed 398, validation set, validation preprocessing, and 12 epochs. The only experimental change is the training augmentation. The required baseline and transfer runs continue to use the provided deterministic `build_transforms` function.

The required comparison figure shows train and validation accuracy across every epoch for both versions. Augmentation slows memorization: final training accuracy falls from 0.9937 without augmentation to 0.9545 with augmentation, while both runs finish with validation accuracy 0.9048. Validation accuracy fluctuated and did not consistently exceed the no-augmentation reference. The main observed benefit was therefore improved macro F1 and class-recall balance, rather than an across-the-board accuracy gain.

![Bonus comparison: light geometric augmentation](results/bonus_comparison_augmentation.png)

### Class-balanced benefit and trade-off

The table compares the macro-F1-selected checkpoint from each paired run. The augmentation run obtains the highest validation macro F1 of all experiments, but it does so by trading some overall accuracy for more balanced class recall. Balanced accuracy is computed here as the unweighted mean of the four reported class recalls and is included only as a supplementary summary; accuracy and macro F1 remain the primary metrics.

| Metric | Without augmentation | With augmentation | Change |
|---|---:|---:|---:|
| Accuracy | 0.9158 | 0.8901 | -0.0256 |
| Macro F1 | 0.7877 | **0.7974** | **+0.0097** |
| Balanced accuracy | 0.7691 | **0.8078** | **+0.0387** |
| Recall: `healthy` | **0.9740** | 0.8831 | -0.0909 |
| Recall: `multiple_diseases` | 0.2143 | **0.5000** | **+0.2857** |
| Recall: `rust` | **0.9892** | 0.8817 | -0.1075 |
| Recall: `scab` | 0.8989 | **0.9663** | **+0.0674** |

The clearest benefit is for the difficult and underrepresented `multiple_diseases` class: recall increases from 3/14 to 7/14 validation images. Scab recall also increases from 80/89 to 86/89. Consequently, balanced accuracy rises by 3.87 percentage points and macro F1 rises by 0.97 points. This pattern suggests that light geometric augmentation shifted the trade-off toward more balanced class recall. It is not a universal improvement, because healthy and rust recall decline and overall accuracy falls by 2.56 points.

This bonus result should be interpreted cautiously. The validation set contains only 14 `multiple_diseases` images, so the large recall change corresponds to four additional correct predictions and may be sensitive to the seed. Nevertheless, the comparison is controlled, and the improvement directly addresses the largest failure identified by the final model's confusion matrix.

## Conclusion

First, ImageNet transfer learning is substantially more effective than training the same ResNet18 architecture from scratch on this small dataset: the required transfer run improves validation accuracy by 12.09 percentage points and macro F1 by 17.95 points. The frozen-backbone result further shows that full fine-tuning, rather than only training a new classification head, is important for this task.

Second, batch size 16 gives the strongest final-model trade-off, achieving the highest non-bonus validation accuracy of 0.9158 with macro F1 0.7877. Light geometric augmentation provides a different benefit: it raises macro F1 and balanced accuracy, especially through improved `multiple_diseases` recall, but does not replace the final model because its overall accuracy is lower.

The main limitation is the small, imbalanced validation set, especially its 14 `multiple_diseases` examples. All settings and the bonus were evaluated with one seed on the same validation split, so small differences may reflect sampling or training variation. Repeating each experiment with multiple seeds would reduce uncertainty but exceeded the available compute budget. Cross-validation was not used because the provided training and validation sets are required to be used for every experiment.

## References

1. K. He, X. Zhang, S. Ren, and J. Sun, [Deep Residual Learning for Image Recognition](https://openaccess.thecvf.com/content_cvpr_2016/html/He_Deep_Residual_Learning_CVPR_2016_paper.html), CVPR, 2016.
2. PyTorch, [torchvision.models.resnet18 and ResNet18 weights documentation](https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.resnet18.html).
3. PyTorch, [CrossEntropyLoss documentation](https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html).
4. PyTorch, [AdamW documentation](https://docs.pytorch.org/docs/stable/generated/torch.optim.AdamW.html).
