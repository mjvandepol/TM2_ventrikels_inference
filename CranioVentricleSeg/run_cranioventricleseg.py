"""
This module provides functionality to run the ventricle segmentation process.
The main function `run_ventricle_segmentation` initializes the segmentation process
and logs the progress.
Functions:
    run_ventricle_segmentation(logger): Runs the ventricle segmentation process and logs the steps.
Usage:
    To run the ventricle segmentation, execute this module as the main program.
    It will initialize the logger and start the segmentation process.
Example:
    $ python run_cranioventricleseg.py
"""

import argparse
import logging
import os

from postprocessing import cranio_postprocessing
from preprocessing import cranio_preprocessing
from segmentation import ventricle_segmentation
from utils.logger_utils import CranioLogger


def run_ventricle_segmentation(
    t1_path: str,
    logger=logging.Logger,
    patient_name: str = "",
    device: str = "cpu",
    model_version: str = "v3.3",
):
    """
    Runs the ventricle segmentation process.
    Parameters:
    logger (logging.Logger): A logger instance to log information and debug messages.
    Returns:
    None
    """

    logger.info("Run preprocessing")
    preprocessed_image_path = cranio_preprocessing.run_cranio_preprocessing(
        t1_path=t1_path, logger=logger, device=device
    )
    # preprocessed_image_path = t1_path.replace(".nii.gz", "_masked.nii.gz")
    logger.info(f"Preprocessed image path: {preprocessed_image_path}")

    logger.info("Run ventricle segmentation")
    predicted_image_path = ventricle_segmentation.run_ventricle_segmentation(
        image_path=preprocessed_image_path,
        logger=logger,
        device=device,
        model_version=model_version,
    )
    logger.info(f"Predicted image path: {predicted_image_path}")

    logger.info("Run postprocessing")
    postprocessed_image_path = cranio_postprocessing.run_cranio_postprocessing(
        image_path=predicted_image_path,
        masked_path=preprocessed_image_path,
        logger=logger,
        patient_name=patient_name,
        model_version=model_version,
    )
    logger.info(f"Postprocessed image path: {postprocessed_image_path}")

    logger.info("Finished ventricle segmentation")


def main(args: argparse.Namespace):
    """
    Main function to run the cranio ventricle segmentation process.
    This function initializes the logger and calls the function to run the ventricle segmentation.
    """
    cranio_logger = CranioLogger(logger_name="CranioVentricleSeg")
    logger = cranio_logger.logger
    logger.info("Running CranioVentricleSeg")
    logger.info(f"Collected the following arguments: {args}")

    if args.subcommand == "file_based":
        logger.info("Running file-based ventricle segmentation")
        t1_path = os.path.join(args.folder_name, "T1w/T1w.nii.gz")
        patient_name = os.path.basename(args.folder_name)
        cranio_logger.update_logger_folder(args.folder_name)

    elif args.subcommand == "xnat_based":
        logger.info("Running XNAT-based ventricle segmentation")

        logger.info("XNAT extraction not implemented yet")

    elif args.subcommand == "clinical_based":
        logger.info("Running clinical-based ventricle segmentation")
        cranio_logger.update_logger_folder(args.folder_name)

        logger.info("Transforming dicom to nifti")
        t1_path = xnat_extraction.dicom_to_nifti(
            patient_path=args.folder_name,
            save_path=os.path.join(args.folder_name, "T1w"),
            filename="T1w",
            logger=logger,
        )
        patient_name = os.path.basename(args.folder_name)

    logger.info(f"Patient name: {patient_name}")
    logger.info(f"Path to T1w: {t1_path}")
    logger.info("Start running ventricle segmentation")
    run_ventricle_segmentation(
        t1_path=t1_path,
        logger=logger,
        patient_name=patient_name,
        device=args.device,
        model_version=args.model_version,
    )

    logger.info("Finished CranioVentricleSeg")


if __name__ == "__main__":
    # Initialize the argument parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="help for subcommand", dest="subcommand")

    # create the parser for the "parser_file" command
    parser_file = subparsers.add_parser("file_based", help="file_based -h/help")
    parser_file.add_argument(
        "-f", "--folder", dest="folder_name", help="patient folder", required=True
    )
    parser_file.add_argument(
        "-d",
        "--device",
        dest="device",
        help="device to run the segmentation on, cpu or cuda",
        default="cpu",
    )
    parser_file.add_argument(
        "-m",
        "--model_version",
        dest="model_version",
        help="version of the segmentation model to use",
        default="v3.3",
    )

    # create the parser for the "parser_xnat" command
    parser_xnat = subparsers.add_parser("xnat_based", help="xnat_based -h/help")
    parser_xnat.add_argument(
        "-e",
        "--experiment",
        dest="experiment_id",
        help="Experiment ID",
        required=True,
    )
    parser_xnat.add_argument(
        "-b",
        "--base_folder",
        dest="base_folder",
        help="folder in which patient folders are stored",
        required=True,
    )
    parser_xnat.add_argument(
        "-d",
        "--device",
        dest="device",
        help="device to run the segmentation on, cpu or cuda",
        default="cpu",
    )
    parser_xnat.add_argument(
        "-m",
        "--model_version",
        dest="model_version",
        help="version of the segmentation model to use",
        default="v3.3",
    )

    # create the parser for the "parser_clinical" command
    parser_clinical = subparsers.add_parser(
        "clinical_based", help="clinical_based -h/help"
    )
    parser_clinical.add_argument(
        "-f", "--folder", dest="folder_name", help="patient folder", required=True
    )
    parser_clinical.add_argument(
        "-m",
        "--model_version",
        dest="model_version",
        help="version of the segmentation model to use",
        default="v3.3",
    )
    parser_clinical.add_argument(
        "-l",
        "--log_folder",
        dest="log_folder",
        help="folder in which the log files are stored",
        default=None,
    )

    args = parser.parse_args()

    main(args=args)
