#This file checks the presence of the segmentation and volume files of as well model v1 and v2 of the test data

import os

BASE_DIR = "/data/scratch/r116411/ventricle_segmentation_train_test_t2/test/test_data"

required_files = [
    "ventricle_volume_v2.0_nomirror.xlsx",
    "ventricle_volume_v1.0_nomirror.xlsx",
    "T2w_registered_n4_masked_ventricles_v2.0_nonmirror.nii.gz",
    "T2w_registered_n4_masked_ventricles_v1.0_nonmirror.nii.gz",
    "brain_volume_v2.0_nomirror.xlsx",
    "brain_volume_v1.0_nomirror.xlsx",
]

for patient in os.listdir(BASE_DIR):
    patient_path = os.path.join(BASE_DIR, patient)

    if not os.path.isdir(patient_path):
        continue

    t2w_path = os.path.join(patient_path, "T2w")

    if not os.path.exists(t2w_path):
        print(f"{patient}: GEEN T2w map")
        continue

    missing = []

    for f in required_files:
        if not os.path.exists(os.path.join(t2w_path, f)):
            missing.append(f)

    if len(missing) == 0:
        print(f"{patient}: OK")
    else:
        print(f"{patient}: MIST -> {missing}")