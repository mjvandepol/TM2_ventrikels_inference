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

    # Save the image
    logger.info
    # save_path = image_path.replace(".nii.gz", "_postprocessed.nii.gz")
    save_path = image_path
    common_utils.save_image(
        image_data=image_data,
        affine=image_nib.affine,
        header=image_nib.header,
        save_path=save_path,
    )
    logger.info("The postprocessed image has been saved")

    logger.info("Postprocessing done")

    return image_path


def calculate_brain_volume(
    image_data,
    image_nib,
    excel_path: str,
    patient_name: str,
    logger: logging.Logger,
) -> float:
    """
    Calculate the volume of the brain in a medical image and save the results to an Excel file.
    Parameters:
    image_data (numpy.ndarray): The image data array where the brain region is labeled with integers.
    image_nib (nibabel.Nifti1Image): The NIfTI image object containing header information.
    excel_path (str): The file path to the Excel file where the results will be saved.
    patient_name (str): The name of the patient whose data is being processed.
    logger (logging.Logger): Logger object for logging information.
    Returns:
    float: The total volume of the brain in cubic centimeters (cm^3).
    """

    logger.info("Calculating brain volume")

    # Calculate the volume
    dimensions_voxel = image_nib.header.get_zooms()
    volume_voxel = dimensions_voxel[0] * dimensions_voxel[1] * dimensions_voxel[2]
    image_data = image_data.astype("i")

    voxels_brain = np.sum(
        image_data > 0
    )  # Assuming brain is labeled with positive integers

    # Calculate in mm3
    volume_brain_mm = volume_voxel * voxels_brain

    # Transform to cm3 = ml
    volume_brain_cm = volume_brain_mm / 1000

    # Save data
    if not os.path.exists(excel_path):
        df = pd.DataFrame(columns=["Name", "Brain Volume (ml)"])
        logger.info(f"Saving brain volume to {excel_path}")
        df.to_excel(excel_path, index=False)

    df = pd.read_excel(excel_path)
    new_row = {
        "Name": str(patient_name),
        "Brain Volume (ml)": volume_brain_cm,
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    logger.info(f"Saving brain volume to {excel_path}")
    df.to_excel(excel_path, index=False)

    logger.info(f"Brain volume: {new_row} cm^3")


def calculate_ventricle_volume(
    image_data, image_nib, excel_path: str, patient_name: str, logger: logging.Logger
) -> float:
    """
    Calculate the volume of the ventricles in a medical image and save the results to an Excel file.
    Parameters:
    image_data (numpy.ndarray): The image data array where different ventricle regions are labeled with integers.
    image_nib (nibabel.Nifti1Image): The NIfTI image object containing header information.
    excel_path (str): The file path to the Excel file where the results will be saved.
    patient_name (str): The name of the patient whose data is being processed.
    logger (logging.Logger): Logger object for logging information.
    Returns:
    float: The total volume of the ventricles in cubic centimeters (cm^3).
    """

    logger.info("Calculating ventricle volume")

    # Calculate the volume
    dimensions_voxel = image_nib.header.get_zooms()
    volume_voxel = dimensions_voxel[0] * dimensions_voxel[1] * dimensions_voxel[2]
    image_data = image_data.astype("i")

    voxels_right = np.sum(np.sum(np.sum(image_data == 1) * 1))
    voxels_third = np.sum(np.sum(np.sum(image_data == 2) * 1))
    voxels_fourth = np.sum(np.sum(np.sum(image_data == 3) * 1))
    voxels_csp = np.sum(np.sum(np.sum(image_data == 4) * 1))
    voxels_left = np.sum(np.sum(np.sum(image_data == 5) * 1))

    # Calculate in mm3
    volume_right_mm = volume_voxel * voxels_right
    volume_third_mm = volume_voxel * voxels_third
    volume_fourth_mm = volume_voxel * voxels_fourth
    volume_csp_mm = volume_voxel * voxels_csp
    volume_left_mm = volume_voxel * voxels_left

    # Transform to cm3 = ml
    volume_right_cm = volume_right_mm / 1000
    volume_third_cm = volume_third_mm / 1000
    volume_fourth_cm = volume_fourth_mm / 1000
    volume_csp_cm = volume_csp_mm / 1000
    volume_left_cm = volume_left_mm / 1000

    # Save data
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
        df.to_excel(excel_path, index=False)

    df = pd.read_excel(excel_path)
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

    logger.info(f"Ventricle volume: {new_row} cm^3")


def dilate_image(data_array, cube_size=2):
    """
    Dilate an image using a custom structuring element.

    This function applies a dilation operation to the input image data using a
    cubic structuring element of the specified size.

    Parameters:
    data_array (numpy.ndarray): The image data to be dilated.
    cube_size (int): The size of the cubic structuring element. Default is 2.

    Returns:
    numpy.ndarray: The dilated image data.
    """
    custom_selem = mp.footprint_rectangle((cube_size, cube_size, cube_size))
    return mp.dilation(image=data_array, footprint=custom_selem) * 1
