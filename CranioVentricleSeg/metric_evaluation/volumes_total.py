# This file fills in an excel with ventricle and brain volumes of model v1.0, v2.0 and ground truth as overview of all volumes
#Ground truth volumes are caclculated using volume_groundtruth.py

import os
import pandas as pd

BASE_DIR = "/data/scratch/r116411/ventricle_segmentation_train_test_t2/test/test_data"
GT_DIR = "/data/scratch/r116411/ventricle_segmentation_train_test_t2/test/test_ventricle_volume_groundtruth"

rows = []

print("Start processing patients...\n")

for patient in os.listdir(BASE_DIR):
    patient_path = os.path.join(BASE_DIR, patient)
    t2w_path = os.path.join(patient_path, "T2w")

    if not os.path.isdir(t2w_path):
        continue

    print(f"\nProcessing patient: {patient}")

    for version in ["v1.0", "v2.0", "Ground truth"]:
        print(f"  -> Version: {version}")

        row = {
            "Name": patient,
            "Model": version,
            "RV": None,
            "3V": None,
            "4V": None,
            "CSP": None,
            "LV": None,
            "Brain volume": None,
        }

        #Volume of ground truth
        if version == "Ground truth":
            files = os.listdir(GT_DIR)
            vent_file = None

            for f in files:
                if f.startswith(patient) and f.endswith(".xlsx"):
                    vent_file = os.path.join(GT_DIR, f)
                    break

            print(f"     GT file found: {vent_file}")

            if vent_file is None:
                print("     WARNING: No GT file found")

            elif os.path.exists(vent_file):
                df = pd.read_excel(vent_file)
                print(f"     Columns in GT file: {list(df.columns)}")

                if df.empty:
                    print("     WARNING: GT file is empty")

                else:
                    row["RV"] = df["Right Ventricle (ml)"].values[0]
                    row["3V"] = df["Third Ventricle (ml)"].values[0]
                    row["4V"] = df["Fourth Ventricle (ml)"].values[0]
                    row["CSP"] = df["CSP (ml)"].values[0]
                    row["LV"] = df["Left Ventricle (ml)"].values[0]
                    row["Brain volume"] = df["Total volume (ml)"].values[0]

                    print(f"     GT values loaded: RV={row['RV']}")

        #Volume of model 1.0 and 2.0
        else:
            vent_file = os.path.join(
                t2w_path, f"ventricle_volume_{version}_nomirror.xlsx"
            )
            brain_file = os.path.join(
                t2w_path, f"brain_volume_{version}_nomirror.xlsx"
            )

            print(f"     Ventricle file: {vent_file}")
            print(f"     Brain file: {brain_file}")

            if os.path.exists(vent_file):
                df = pd.read_excel(vent_file)

                if df.empty:
                    print("     WARNING: ventricle file empty")

                else:
                    row["RV"] = df["Right Ventricle (ml)"].values[0]
                    row["3V"] = df["Third Ventricle (ml)"].values[0]
                    row["4V"] = df["Fourth Ventricle (ml)"].values[0]
                    row["CSP"] = df["CSP (ml)"].values[0]
                    row["LV"] = df["Left Ventricle (ml)"].values[0]

                    print(f"     Model values loaded: RV={row['RV']}")
            else:
                print("     WARNING: ventricle file not found")

            if os.path.exists(brain_file):
                df = pd.read_excel(brain_file)

                if df.empty:
                    print("     WARNING: brain file empty")

                else:
                    row["Brain volume"] = df["Brain Volume (ml)"].values[0]
            else:
                print("     WARNING: brain file not found")

        rows.append(row)

print("\nFinished processing, creating dataframe...")

df_out = pd.DataFrame(rows)
df_out = df_out.sort_values(["Name", "Model"])

output_path = os.path.join(BASE_DIR, "Volumes_models.xlsx")
df_out.to_excel(output_path, index=False)

print(f"\nSaved to {output_path}")