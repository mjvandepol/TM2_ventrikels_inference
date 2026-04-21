#This file calculates the Dice score and NSD score (2 mm) for model v1.0 & v2.0 (T2w) and saves it in an excel

import os
import numpy as np
import SimpleITK as sitk
import pandas as pd

from surface_distance import compute_surface_distances, compute_surface_dice_at_tolerance

from openpyxl import Workbook
from openpyxl.styles import Alignment


ground_truth_folder = "/data/scratch/r116411/ventricle_segmentation_train_test_t2/test/test_ground_truth"

model_folders = {
    "v1.0": "/data/scratch/r116411/ventricle_segmentation_train_test_t2/test/test_inference_v1.0",
    "v2.0": "/data/scratch/r116411/ventricle_segmentation_train_test_t2/test/test_inference_v2.0",
}

output_path = "/data/scratch/r116411/ventricle_segmentation_train_test_t2/test/segmentation_metrics.xlsx"


# Label volgorde zoals jij wil
label_names = {
    1: "RV",
    2: "3V",
    3: "4V",
    4: "CSP",
    5: "LV"
}

ordered_labels = ["RV", "3V", "4V", "CSP", "LV"]
labels = list(label_names.keys())

csp_label = 4
nsd_tolerance_mm = 2.0

# =====================
# FUNCTIONS
# =====================

def load_image(path):
    img = sitk.ReadImage(path)
    arr = sitk.GetArrayFromImage(img)
    spacing = img.GetSpacing()[::-1]  # naar (z,y,x)
    return arr, spacing


def dice_score(pred, gt):
    intersection = np.sum((pred == 1) & (gt == 1))
    size_sum = np.sum(pred == 1) + np.sum(gt == 1)

    if size_sum == 0:
        return np.nan

    return 2.0 * intersection / size_sum


def nsd_score(pred, gt, spacing):
    if np.sum(pred) == 0 and np.sum(gt) == 0:
        return np.nan

    distances = compute_surface_distances(
        gt.astype(bool),
        pred.astype(bool),
        spacing_mm=spacing
    )

    return compute_surface_dice_at_tolerance(distances, nsd_tolerance_mm)


# =====================
# BUILD DATAFRAME PER MODEL
# =====================

def build_dataframe(model_folder):

    rows = []
    gt_files = sorted(os.listdir(ground_truth_folder))

    for file in gt_files:

        gt_path = os.path.join(ground_truth_folder, file)
        pred_path = os.path.join(model_folder, file)

        if not os.path.exists(pred_path):
            continue

        gt, spacing = load_image(gt_path)
        pred, _ = load_image(pred_path)

        row = {"case": file}
        dice_list = []
        nsd_list = []

        csp_in_gt = np.any(gt == csp_label)
        csp_in_pred = np.any(pred == csp_label)

        for label, name in label_names.items():

            gt_bin = (gt == label).astype(np.uint8)
            pred_bin = (pred == label).astype(np.uint8)

            # CSP logica
            if label == csp_label:

                if not csp_in_gt:
                    if csp_in_pred:
                        row["CSP_status"] = "False positive CSP segmentation"
                    row[f"dice_{name}"] = np.nan
                    row[f"nsd_{name}"] = np.nan
                    continue

                if csp_in_gt and not csp_in_pred:
                    row["CSP_status"] = "CSP missed (false negative)"
                    row[f"dice_{name}"] = np.nan
                    row[f"nsd_{name}"] = np.nan
                    continue

            d = dice_score(pred_bin, gt_bin)
            n = nsd_score(pred_bin, gt_bin, spacing)

            row[f"dice_{name}"] = d
            row[f"nsd_{name}"] = n

            if not np.isnan(d):
                dice_list.append(d)
            if not np.isnan(n):
                nsd_list.append(n)

        # per case mean (macro)
        row["dice_case_mean"] = np.mean(dice_list) if dice_list else np.nan
        row["nsd_case_mean"] = np.mean(nsd_list) if nsd_list else np.nan

        rows.append(row)

    return pd.DataFrame(rows)


# =====================
# WRITE EXCEL MET HEADER STRUCTUUR
# =====================

def write_sheet(ws, df):

    # Top headers
    top_headers = ["case",
                   "RV","", "3V","", "4V","", "CSP","", "LV","",
                   "Overall","",
                   "CSP info"]

    sub_headers = ["case",
                   "Dice","NSD",
                   "Dice","NSD",
                   "Dice","NSD",
                   "Dice","NSD",
                   "Dice","NSD",
                   "Dice","NSD",
                   ""]

    ws.append(top_headers)
    ws.append(sub_headers)

    # Merge cell blocks
    merges = [(2,3),(4,5),(6,7),(8,9),(10,11),(12,13)]
    for start, end in merges:
        ws.merge_cells(start_row=1, start_column=start, end_row=1, end_column=end)

    ws.merge_cells(start_row=1, start_column=1, end_row=2, end_column=1)
    ws.merge_cells(start_row=1, start_column=14, end_row=2, end_column=14)

    # Center align
    for col in range(1,15):
        ws.cell(row=1, column=col).alignment = Alignment(horizontal="center")
        ws.cell(row=2, column=col).alignment = Alignment(horizontal="center")

    # Data
    for _, r in df.iterrows():

        row = [
            r["case"],

            r.get("dice_RV"), r.get("nsd_RV"),
            r.get("dice_3V"), r.get("nsd_3V"),
            r.get("dice_4V"), r.get("nsd_4V"),
            r.get("dice_CSP"), r.get("nsd_CSP"),
            r.get("dice_LV"), r.get("nsd_LV"),

            r.get("dice_case_mean"), r.get("nsd_case_mean"),

            r.get("CSP_status","")
        ]

        ws.append(row)


# =====================
# MAIN
# =====================

wb = Workbook()
wb.remove(wb.active)

for model_name, model_folder in model_folders.items():

    print(f"Processing {model_name}")

    df = build_dataframe(model_folder)

    ws = wb.create_sheet(title=model_name)
    write_sheet(ws, df)

wb.save(output_path)

print(f"Excel saved to: {output_path}")