# Fold-based evaluation for model v1.0, T2 

import os
import numpy as np
import SimpleITK as sitk
import pandas as pd

# Paths
BASE_DIR = "/data/scratch/r116411/data/inference_validatie_model1.0_v2/Results_inference_model1.0/"
GT_DIR   = "/data/scratch/r116411/data/nnUNet_raw/Dataset001_Brain_T2/labelsTr/"

OUTPUT_EXCEL = BASE_DIR + "fold_evaluation_model_v1.0.xlsx"

LABELS = {
    1: "RV",
    2: "3V",
    3: "4V",
    4: "CSP",
    5: "LV"
}

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

def dice_total(gt, pred):
    gt_bin = (gt > 0)
    pred_bin = (pred > 0)

    if gt_bin.sum() == 0 and pred_bin.sum() == 0:
        return np.nan

    inter = np.logical_and(gt_bin, pred_bin).sum()
    return 2 * inter / (gt_bin.sum() + pred_bin.sum())


rows = []

for fold in range(5):

    pred_dir = os.path.join(BASE_DIR, f"fold_{fold}")

    print(f"\nProcessing fold_{fold}")

    # per label lijst met case-dices
    dice_per_label = {l: [] for l in LABELS}
    dice_total_list = []

    for file in sorted(os.listdir(pred_dir)):
        if not file.endswith(".nii.gz"):
            continue

        pred_path = os.path.join(pred_dir, file)
        gt_path   = os.path.join(GT_DIR, file)

        if not os.path.exists(gt_path):
            print("Geen GT:", file)
            continue

        pred = load_nifti(pred_path)
        gt   = load_nifti(gt_path)

        # per label
        for l in LABELS:
            d = dice(gt, pred, l)
            if not np.isnan(d):
                dice_per_label[l].append(d)

        # total
        dt = dice_total(gt, pred)
        if not np.isnan(dt):
            dice_total_list.append(dt)

    # fold samenvatting
    row = {"fold": f"fold_{fold}"}

    for l, name in LABELS.items():
        row[f"{name}_dice"] = np.mean(dice_per_label[l]) if dice_per_label[l] else np.nan

    row["TOTAL_dice"] = np.mean(dice_total_list) if dice_total_list else np.nan

    print(row)

    rows.append(row)

df = pd.DataFrame(rows)

df.to_excel(OUTPUT_EXCEL, index=False)

print(f"\nopgeslagen naar: {OUTPUT_EXCEL}")