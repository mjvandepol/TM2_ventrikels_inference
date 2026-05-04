# This file calculates the global (voxel-based) foreground Dice (label 6) and global Dice per label, consistent with nnU-Net validation metrics.
# Also the NSD per fold is calculated, as the mean over the cases in one fold 

import os
import numpy as np
import pandas as pd
import SimpleITK as sitk

from surface_distance import compute_surface_distances, compute_surface_dice_at_tolerance

# -------- Paths for model 1 & 2

# Model 1
BASE_DIR_MODEL1 = "/data/scratch/r116411/data/inference_validatie_model1.0_v2/Results_inference_model1.0/"
GT_DIR_MODEL1 = "/data/scratch/r116411/data/nnUNet_raw/Dataset001_Brain_T2/labelsTr/"

# Model 2
BASE_DIR_MODEL2 = "/data/scratch/r116411/data/nnUNet_results/Dataset002_Brain_T2/nnUNetTrainer__nnUNetPlans__3d_fullres/"
GT_DIR_MODEL2 = "/data/scratch/r116411/data/nnUNet_raw/Dataset002_Brain_T2/labelsTr/"

OUTPUT_EXCEL = "/data/scratch/r116411/data/fold_evaluation_both_models.xlsx"


TOLERANCE_MM = 2.0 #tolerance for NSD in mm

LABELS = {
    1: "RV",
    2: "3V",
    3: "4V",
    4: "CSP",
    5: "LV",
    6: "TOTAL"
}

# Functions

def load_nifti(path):
    img = sitk.ReadImage(path)
    arr = sitk.GetArrayFromImage(img)
    spacing = img.GetSpacing()[::-1]
    return arr, spacing


def dice_score(gt, pred, label):
    gt_bin = (gt == label)
    pred_bin = (pred == label)

    if gt_bin.sum() == 0 and pred_bin.sum() == 0:
        return np.nan

    intersection = np.logical_and(gt_bin, pred_bin).sum()
    return 2.0 * intersection / (gt_bin.sum() + pred_bin.sum())


def nsd_score(gt, pred, spacing, label):
    gt_bin = (gt == label)
    pred_bin = (pred == label)

    if gt_bin.sum() == 0 and pred_bin.sum() == 0:
        return np.nan

    sd = compute_surface_distances(gt_bin, pred_bin, spacing_mm=spacing)
    return compute_surface_dice_at_tolerance(sd, TOLERANCE_MM)


def extract_id(filename):
    base = filename.replace(".nii.gz", "")
    parts = base.split("_")
    if len(parts) >= 3:
        return "_".join(parts[0:3])  # C_number_date 
    return base


def find_matching_gt(pred_file, gt_files):
    pred_id = extract_id(pred_file)
    for gt in gt_files:
        if extract_id(gt) == pred_id:
            return gt
    return None


# -------- Main evaluation function 

def evaluate_model(BASE_DIR, GT_DIR):

    gt_files = os.listdir(GT_DIR)
    rows = []

    for fold in sorted(os.listdir(BASE_DIR)):
        fold_dir = os.path.join(BASE_DIR, fold)

        # Only choosed folders, no files
        if not os.path.isdir(fold_dir):
            continue

        # detect validation folder
        if os.path.isdir(os.path.join(fold_dir, "validation")):
            fold_path = os.path.join(fold_dir, "validation")
        else:
            fold_path = fold_dir
        
        print(f"\n Processing fold: {fold} ")
    
        if not os.path.isdir(fold_path):
            print(f"No {fold}")
            continue

        # Per label: intersection and ammount of voxels
        intersection_global = {label: 0 for label in LABELS}
        volume_global = {label: 0 for label in LABELS}

        nsd_results = {label: [] for label in LABELS}

        for file in os.listdir(fold_path):
            if not file.endswith(".nii.gz"):
                continue

            pred_path = os.path.join(fold_path, file)
            matched_gt = find_matching_gt(file, gt_files)

            if matched_gt is None:
                print(f"geen match voor: {file}")
                continue

            gt_path = os.path.join(GT_DIR, matched_gt)

            pred, spacing = load_nifti(pred_path)
            gt, _ = load_nifti(gt_path)

            for label in LABELS:

                # label 6 = TOTAL (union), nnUnet foreground
                if label == 6:
                    gt_bin = (gt >= 1)
                    pred_bin = (pred >= 1)
                else:
                    gt_bin = (gt == label)
                    pred_bin = (pred == label)

                    # CSP skip indien leeg
                    if label == 4 and gt_bin.sum() == 0 and pred_bin.sum() == 0:
                        continue

                # global Dice accumulatie
                intersection_global[label] += np.logical_and(gt_bin, pred_bin).sum() #counts the ammount of voxels that overlap
                volume_global[label] += gt_bin.sum() + pred_bin.sum()

                # NSD per case
                n = nsd_score(gt, pred, spacing, label)
                if not np.isnan(n):
                    nsd_results[label].append(n)

        row = {"fold": fold}

        # Dice & NSD per label
        for label, name in LABELS.items():
            if volume_global[label] > 0:
                row[f"{name}_dice"] = 2 * intersection_global[label] / volume_global[label]
            else:
                row[f"{name}_dice"] = np.nan

            row[f"{name}_nsd"] = np.mean(nsd_results[label]) if nsd_results[label] else np.nan

        rows.append(row)

    return pd.DataFrame(rows)



# -------- Run

df_model1 = evaluate_model(BASE_DIR_MODEL1, GT_DIR_MODEL1)
df_model2 = evaluate_model(BASE_DIR_MODEL2, GT_DIR_MODEL2)



# -------- Save (2 tabs) 

with pd.ExcelWriter(OUTPUT_EXCEL, engine="openpyxl") as writer:
    df_model1.to_excel(writer, sheet_name="model1", index=False)
    df_model2.to_excel(writer, sheet_name="model2", index=False)

print(f"opgeslagen naar: {OUTPUT_EXCEL}")