#!/bin/bash

# Source and destination directories
# SOURCE_DIR="/data/scratch/r116411/data/nnUNet_results/Dataset001_Brain_T2"
# DEST_DIR="/trinity/home/r116411/repositories/TM2_ventrikels_inference/models/v1.0"
SOURCE_DIR=$1
DEST_DIR=$2

# Create destination directory if it doesn't exist
mkdir -p "$DEST_DIR"

# Copy checkpoint_final.pth files from each fold
for fold in fold_0 fold_1 fold_2 fold_3 fold_4; do
    if [ -f "$SOURCE_DIR/nnUNetTrainer__nnUNetPlans__3d_fullres/$fold/checkpoint_final.pth" ]; then
        mkdir -p "$DEST_DIR/$fold"
        cp "$SOURCE_DIR/nnUNetTrainer__nnUNetPlans__3d_fullres/$fold/checkpoint_final.pth" "$DEST_DIR/$fold/"
        echo "Copied $fold/checkpoint_final.pth"
    else
        echo "Warning: $fold/checkpoint_final.pth not found"
    fi
done

# Copy additional files to the main destination directory
files_to_copy=("dataset.json" "dataset_fingerprint.json" "plans.json")

for file in "${files_to_copy[@]}"; do
    if [ -f "$SOURCE_DIR/nnUNetTrainer__nnUNetPlans__3d_fullres/$file" ]; then
        cp "$SOURCE_DIR/nnUNetTrainer__nnUNetPlans__3d_fullres/$file" "$DEST_DIR/"
        echo "Copied $file to main folder"
    else
        echo "Warning: $file not found"
    fi
done

echo "Copy operation completed"