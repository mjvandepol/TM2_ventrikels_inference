# Simple evaluation script model 2 (nnU-Net validation per fold)

import os
import numpy as np
import SimpleITK as sitk
import pandas as pd

BASE_DIR = "/data/scratch/r116411/data/nnUNet_results/Dataset002_Brain_T2/nnUNetTrainer__nnUNetPlans__3d_fullres/"
GT_DIR   = "/data/scratch/r116411/data/nnUNet_raw/Dataset002_Brain_T2/labelsTr/"

LABELS = [1,2,3,4,5]


def load_nifti(path):
    img = sitk.ReadImage(path)
    return sitk.GetArrayFromImage(img)


def dice(gt, pred, label):
    gt_bin = (gt == label)
    pred_bin = (pred == label)

    if gt_bin.sum() == 0 and pred_bin.sum() == 0:
        return np.nan

    inter = np.logical_and(gt_bin, pred_bin).sum()
    return 2 * inter / (gt_bin.sum() + pred_bin.sum())


def dice_foreground(gt, pred):
    gt_bin = (gt > 0)
    pred_bin = (pred > 0)

    inter = np.logical_and(gt_bin, pred_bin).sum()
    return 2 * inter / (gt_bin.sum() + pred_bin.sum())


all_rows = []

for fold in range(5):

    pred_dir = os.path.join(BASE_DIR, f"fold_{fold}", "validation")

    print(f"\nProcessing fold_{fold}")
    print("Aantal predictions:", len(os.listdir(pred_dir)))

    rows = []

    for file in sorted(os.listdir(pred_dir)):
        if not file.endswith(".nii.gz"):
            continue

        pred_path = os.path.join(pred_dir, file)
        gt_path   = os.path.join(GT_DIR, file)

        if not os.path.exists(gt_path):
            print("Geen GT voor:", file)
            continue

        pred = load_nifti(pred_path)
        gt   = load_nifti(gt_path)

        row = {"case": file, "fold": fold}

        for l in LABELS:
            row[f"dice_{l}"] = dice(gt, pred, l)

        fg = dice_foreground(gt, pred)
        row["foreground_mean"] = fg

        print(f"{file} | FG: {fg:.4f}")

        rows.append(row)
        all_rows.append(row)

    df_fold = pd.DataFrame(rows)
    print(f"Fold {fold} mean FG:", df_fold["foreground_mean"].mean())


df_all = pd.DataFrame(all_rows)
print("\nOverall mean FG:", df_all["foreground_mean"].mean())