#This file calculates the volume of the ground truth (manual) segmentations of the test set

import logging
import numpy as np
import pandas as pd
import os
from utils import common_utils


output_folder = "/data/scratch/r116411/test_ventricle_volume"
os.makedirs(output_folder, exist_ok=True)

    
def run_calculation(
    image_path: str,
    logger: logging.Logger,
    patient_name: str,
) -> str:

    # Load the image
    logger.info("Loading the image")
    image_nib, image_data = common_utils.load_image(image_path)
    logger.info("Image has been loaded")


    # Calculate the ventricle volume
    logger.info("Calculating ventricle volume")
    
    excel_path = os.path.join(
        output_folder,
        f"{patient_name}_ventricle_volume_test_segmentation.xlsx"
    )

    calculate_ventricle_volume(
        image_data=image_data,
        image_nib=image_nib,
        excel_path=excel_path,
        patient_name=patient_name,
        logger=logger,
    )
    logger.info("Finished calculating ventricle volume")
    logger.info("Calculation done")
    return image_path



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

    # Calculate the volume
    dimensions_voxel = image_nib.header.get_zooms()
    volume_voxel = dimensions_voxel[0] * dimensions_voxel[1] * dimensions_voxel[2] #volume = xyz
    image_data = image_data.astype(np.int32)

    #aantal voxels dat bij ventrikel hoort (==1 / 2 label etc) * volume ventrikel 
    voxels_right   = np.sum(image_data == 1)
    voxels_third   = np.sum(image_data == 2)
    voxels_fourth  = np.sum(image_data == 3)
    voxels_csp     = np.sum(image_data == 4)
    voxels_left    = np.sum(image_data == 5)

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


    total_volume = (
        volume_right_cm
        + volume_left_cm
        + volume_third_cm
        + volume_fourth_cm
        + volume_csp_cm
)
    
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
                "Total volume (ml)",

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
        "Total volume (ml)": total_volume,
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(excel_path, index=False)

    logger.info(f"Ventricle volume (ml): {new_row}")


#run for test data
if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()

    data_folder = "/data/scratch/r116411/ventricle_segmentation_train_test_t2/test/test_ground_truth/"

    for file in os.listdir(data_folder):
        if file.endswith(".nii.gz"):

            image_path = os.path.join(data_folder, file)
            patient_name = file.replace(".nii.gz", "")

            logger.info(f"Processing {patient_name}")

            run_calculation(
                image_path=image_path,
                logger=logger,
                patient_name=patient_name
            )