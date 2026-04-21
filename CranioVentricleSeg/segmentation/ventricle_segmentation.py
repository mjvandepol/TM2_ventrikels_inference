import os
import pathlib
import logging
import torch
import SimpleITK as sitk
from nnunetv2.inference.predict_from_raw_data import nnUNetPredictor


def get_ventricle_predictor(
    model_folder: str,
    device: torch.device = torch.device("cpu"),
    use_mirroring: bool = False,
    verbose: bool = False,
    checkpoint_name: str = "checkpoint_final.pth",
    logger: logging.Logger = None,
):
    """
    Initializes and returns a nnUNetPredictor for ventricle segmentation.
    Args:
        device (torch.device, optional): The device to run the model on. Defaults to CPU.
        use_mirroring (bool, optional): Whether to use mirroring during prediction. Defaults to False.
        verbose (bool, optional): Whether to enable verbose logging. Defaults to False.
        checkpoint_name (str, optional): The name of the checkpoint file to load. Defaults to "checkpoint_final.pth".
        logger (logging.Logger, optional): Logger for logging information. Defaults to None.
    Returns:
        nnUNetPredictor: An initialized nnUNetPredictor object for ventricle segmentation.
    """

    # logger.info("Getting model folder")
    # base_path = pathlib.Path(__file__).parent.resolve().parent
    # model_folder = os.path.join(base_path, model_version)
    print(use_mirroring)
    # os.environ['nnUNet_compile'] = 'F'
    logger.info("Initializing nnUNet predictor")
    predictor = nnUNetPredictor(
        tile_step_size=0.5,
        use_gaussian=True,
        use_mirroring=use_mirroring,
        perform_everything_on_device=True,
        device=device,
        verbose=verbose,
        verbose_preprocessing=verbose,
    )

    if "v4.01" in model_folder:
        logger.info("Initializing from trained model folder")
        predictor.initialize_from_trained_model_folder(
            model_training_output_dir=model_folder,
            use_folds=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
            checkpoint_name=checkpoint_name,
        )

        if device == torch.device("cpu"):
            logger.info("Setting number of threads")
            torch.set_num_threads(os.cpu_count())

        return predictor
    else:
        logger.info("Initializing from trained model folder")
        predictor.initialize_from_trained_model_folder(
            model_training_output_dir=model_folder,
            use_folds=(0, 1, 2, 3, 4),
            checkpoint_name=checkpoint_name,
        )

        if device == torch.device("cpu"):
            logger.info("Setting number of threads")
            torch.set_num_threads(os.cpu_count())

        return predictor


def run_ventricle_segmentation(
    image_path: str,
    logger: logging.Logger,
    device: str = "cpu",
    model_version: str = "v2.0",
) -> str:
    """
    Runs the ventricle segmentation process on the given image.
    Args:
        image_path (str): The file path to the input image in NIfTI format.
        logger (logging.Logger): Logger instance for logging information.
    Returns:
        str: The file path to the segmented ventricles image in NIfTI format.
    The function performs the following steps:
    1. Retrieves the model folder.
    2. Reads the input image and extracts its properties.
    3. Loads the plan and dataset information.
    4. Processes the image for ventricle segmentation.
    5. Initializes the ventricle predictor.
    6. Predicts the ventricles and saves the output image.
    """

    logger.info("Getting model folder")
    logger.info(f"Model version: {model_version}")
    base_path = pathlib.Path(__file__).parent.resolve().parent
    model_folder = os.path.join(base_path, "models/" + model_version)

    logger.info("Reading image")
    image_properties = {}
    masked_image = sitk.ReadImage(image_path)
    image_array = sitk.GetArrayFromImage(masked_image)
    image_array = image_array[None]

    logger.info("Getting image properties")
    image_properties["spacing"] = masked_image.GetSpacing()
    image_properties["sitk_stuff"] = {
        "spacing": masked_image.GetSpacing(),
        "origin": masked_image.GetOrigin(),
        "direction": masked_image.GetDirection(),
    }

    logger.info("Getting ventricle predictor")
    predictor = get_ventricle_predictor(
        model_folder=model_folder,
        device=torch.device(device),
        logger=logger,
        use_mirroring=False,
        verbose=False,
        checkpoint_name="checkpoint_final.pth",
    )

    logger.info("Predicting ventricles")
    predictor.predict_single_npy_array(
        input_image=image_array,
        image_properties=image_properties,
        output_file_truncated=image_path.replace(
            ".nii.gz", f"_ventricles_{model_version}_nonmirror"
        ),
    )

    logger.info("Finished ventricle prediction")

    return image_path.replace(
        ".nii.gz", f"_ventricles_{model_version}_nonmirror.nii.gz"
    )
