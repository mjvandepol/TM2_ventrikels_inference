#This file calculates the dice, NSD & volume error for ev

import os
import numpy as np
import nibabel as nib
import pandas as pd
import argparse

LABELS = [1, 2, 3, 4, 5]

#ground truth segmentatie 
ground_truth_folder = "/data/scratch/r116411/ventricle_segmentation_train_test_t2/test/test_ground_truth"


def load_nifti(path):
    nii = nib.load(path)
    return nii.get_fdata()


def dice_score(gt, pred, label):
    gt_bin = (gt == label)
    pred_bin = (pred == label)

    intersection = np.sum(gt_bin & pred_bin)
    size_sum = np.sum(gt_bin) + np.sum(pred_bin)

    if size_sum == 0:
        return np.nan

    return 2 * intersection / size_sum


def compute_metrics(model_prediction_folder):
    results = []

    for file in os.listdir(ground_truth_folder):
        if not file.endswith(".nii.gz"):
            continue

        gt_path = os.path.join(ground_truth_folder, file)
        pred_path = os.path.join(model_prediction_folder, file)

        if not os.path.exists(pred_path):
            print(f"Missing prediction for {file}")
            continue

        gt = load_nifti(gt_path)
        pred = load_nifti(pred_path)

        row = {"Name": file}

        dices = []
        for label in LABELS:
            d = dice_score(gt, pred, label)
            row[f"Dice_class_{label}"] = d
            if not np.isnan(d):
                dices.append(d)

        row["Dice_mean"] = np.mean(dices)
        results.append(row)

    df = pd.DataFrame(results)

    print("\n=== OVERALL ===")
    print("Mean Dice per class:")
    print(df.mean(numeric_only=True))

    print("\nStd Dice per class:")
    print(df.std(numeric_only=True))

    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Model version (e.g. v1.0)")
    args = parser.parse_args()

    # maak prediction folder dynamisch
    model_prediction_folder = f"/data/scratch/r116411/ventricle_segmentation_train_test_t2/test/test_inference_{args.model}"

    df = compute_metrics(model_prediction_folder)

    # opslaan IN dezelfde map als segmentaties
    output_path = os.path.join(model_prediction_folder, f"dice_{args.model}.csv")
    df.to_csv(output_path, index=False)

    print(f"\n Results saved to: {output_path}")