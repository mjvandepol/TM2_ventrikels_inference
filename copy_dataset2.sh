#!/bin/bash


src_base="/data/scratch/r116411/ventricle_segmentation_train_test_t2/train_002"
dst_base="/data/scratch/r116411/data/nnUNet_raw/Dataset002_Brain_T2"

imagesTr="$dst_base/imagesTr"
labelsTr="$dst_base/labelsTr"

mkdir -p "$imagesTr"
mkdir -p "$labelsTr"

for patient_path in "$src_base"/*; do
    patient=$(basename "$patient_path")

    if [[ ! "$patient" =~ ^(C_|M_) ]]; then
        continue
    fi

    t2_path="$patient_path/T2w"

    if [ ! -d "$t2_path" ]; then
        echo "Geen T2w folder voor $patient"
        continue
    fi

    # IMAGE
    image_src="$t2_path/T2w_registered.nii.gz"
    image_dst="$imagesTr/${patient}_0000.nii.gz"

    if [ -f "$image_src" ]; then
        cp "$image_src" "$image_dst"
    else
        echo "Geen image voor $patient"
        continue
    fi

    # LABELS: eerst .nii proberen, anders .nii.gz
    mapfile -t nii_labels < <(find "$t2_path" -maxdepth 1 -type f -iname "*new*.nii")

    if [ "${#nii_labels[@]}" -gt 0 ]; then
        label_src="${nii_labels[0]}"
    else
        mapfile -t gz_labels < <(find "$t2_path" -maxdepth 1 -type f -iname "*new*.nii.gz")

        if [ "${#gz_labels[@]}" -eq 0 ]; then
            echo "Geen 'new' label voor $patient"
            continue
        fi

        if [ "${#gz_labels[@]}" -gt 1 ]; then
            echo "Meerdere 'new' labels voor $patient:"
            printf '   %s\n' "${gz_labels[@]}"
        fi

        label_src="${gz_labels[0]}"
    fi

    # indien .nii → maak .nii.gz in originele map (origineel blijft bestaan)
    if [[ "$label_src" != *.gz ]]; then
        if [ ! -f "${label_src}.gz" ]; then
            echo "Maak .nii.gz in originele map: $label_src"
            gzip -c "$label_src" > "${label_src}.gz"
        fi
        label_src="${label_src}.gz"
    fi

    # kopiëren naar nnU-Net dataset
    label_dst="$labelsTr/${patient}.nii.gz"
    cp "$label_src" "$label_dst"

    echo "$patient verwerkt"
done