#The file is updated so earlier model data files are not overruled if a new model run is done 

import logging
import os

import numpy as np
import pandas as pd
import skimage.morphology as mp
from utils import common_utils


def run_cranio_postprocessing(
    image_path: str,
    masked_path: str,
    logger: logging.Logger,
    patient_name: str,
    model_version: str,
) -> str:

    logger.info("Running cranio postprocessing")

    # Load the image
    logger.info("Loading the image")
    image_nib, image_data = common_utils.load_image(image_path)
    masked_nib, masked_data = common_utils.load_image(masked_path)
    logger.info("Image has been loaded")

    # Calculate the brain volume
    logger.info("Calculating brain volume")
    excel_path = os.path.join(
        os.path.dirname(image_path), f"brain_volume_{model_version}_nomirror.xlsx"
    )
    calculate_brain_volume(
        image_data=masked_data,
        image_nib=masked_nib,
        excel_path=excel_path,
        patient_name=patient_name,
        logger=logger,
    )
    logger.info("Finished calculating brain volume")

    # Calculate the ventricle volume
    logger.info("Calculating ventricle volume")
    excel_path = os.path.join(
        os.path.dirname(image_path), f"ventricle_volume_{model_version}_nomirror.xlsx"
    )

    calculate_ventricle_volume(
        image_data=image_data,
        image_nib=image_nib,
        excel_path=excel_path,
        patient_name=patient_name,
        logger=logger,
    )
    logger.info("Finished calculating ventricle volume")

    # Save the image. Segmentation saved to different folder than patient data 
    output_folder = f"/data/scratch/r116411/ventricle_segmentation_train_test_t2/test/test_inference_{model_version}"
    os.makedirs(output_folder, exist_ok=True)

    save_path = os.path.join(output_folder, f"{patient_name}.nii.gz")

    common_utils.save_image(
        image_data=image_data,
        affine=image_nib.affine,
        header=image_nib.header,
        save_path=save_path,
    )

    logger.info("The postprocessed image has been saved")
    logger.info("Postprocessing done")

    return save_path


def calculate_brain_volume(
    image_data,
    image_nib,
    excel_path: str,
    patient_name: str,
    logger: logging.Logger,
) -> float:

    logger.info("Calculating brain volume")

    dimensions_voxel = image_nib.header.get_zooms()
    volume_voxel = dimensions_voxel[0] * dimensions_voxel[1] * dimensions_voxel[2]
    image_data = image_data.astype("i")

    voxels_brain = np.sum(image_data > 0)
    volume_brain_cm = (volume_voxel * voxels_brain) / 1000

    if not os.path.exists(excel_path):
        df = pd.DataFrame(columns=["Name", "Brain Volume (ml)"])
    else:
        df = pd.read_excel(excel_path)

    df = df[df["Name"] != patient_name]

    new_row = {
        "Name": str(patient_name),
        "Brain Volume (ml)": volume_brain_cm,
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(excel_path, index=False)

    logger.info(f"Brain volume: {new_row}")


def calculate_ventricle_volume(
    image_data, image_nib, excel_path: str, patient_name: str, logger: logging.Logger
) -> float:

    logger.info("Calculating ventricle volume")

    dimensions_voxel = image_nib.header.get_zooms()
    volume_voxel = dimensions_voxel[0] * dimensions_voxel[1] * dimensions_voxel[2]
    image_data = image_data.astype("i")

    voxels_right = np.sum(image_data == 1)
    voxels_third = np.sum(image_data == 2)
    voxels_fourth = np.sum(image_data == 3)
    voxels_csp = np.sum(image_data == 4)
    voxels_left = np.sum(image_data == 5)

    volume_right_cm = (volume_voxel * voxels_right) / 1000
    volume_third_cm = (volume_voxel * voxels_third) / 1000
    volume_fourth_cm = (volume_voxel * voxels_fourth) / 1000
    volume_csp_cm = (volume_voxel * voxels_csp) / 1000
    volume_left_cm = (volume_voxel * voxels_left) / 1000

    if not os.path.exists(excel_path):
        df = pd.DataFrame(
            columns=[
                "Name",
                "Right Ventricle (ml)",
                "Third Ventricle (ml)",
                "Fourth Ventricle (ml)",
                "CSP (ml)",
                "Left Ventricle (ml)",
            ]
        )
    else:
        df = pd.read_excel(excel_path)

    df = df[df["Name"] != patient_name]

    new_row = {
        "Name": str(patient_name),
        "Right Ventricle (ml)": volume_right_cm,
        "Third Ventricle (ml)": volume_third_cm,
        "Fourth Ventricle (ml)": volume_fourth_cm,
        "CSP (ml)": volume_csp_cm,
        "Left Ventricle (ml)": volume_left_cm,
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(excel_path, index=False)

    logger.info(f"Ventricle volume: {new_row}")


def dilate_image(data_array, cube_size=2):
    custom_selem = mp.footprint_rectangle((cube_size, cube_size, cube_size))
    return mp.dilation(image=data_array, footprint=custom_selem) * 1