"""
This module contains common utility functions for the CranioVentricleSeg project.
Functions:
    create_path(path: str): Create a directory path if it does not exist.
"""

import os
import json
import shutil
import nibabel as nib
import numpy as np


def create_path(path: str):
    """
    Create a directory at the specified path if it does not already exist.
    Args:
        path (str): The path where the directory should be created.
    Returns:
        None
    """
    print(path)
    if not os.path.exists(path):
        os.makedirs(path)


def load_json_file(path: str):
    """
    Load a JSON file from the specified path.
    Args:
        path (str): The path to the JSON file.
    Returns:
        dict: The contents of the JSON file as a dictionary.
    """
    with open(path, "r") as file:
        return json.load(file)


def remove_path(path: str):
    """
    Remove the directory at the specified path if it exists.
    Args:
        path (str): The path to the directory to be removed.
    Returns:
        None
    """
    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)


def load_image(image_path: str) -> tuple:
    """
    Load a medical image using nibabel and return the image object and its data.
    Args:
        image_path (str): The file path to the image to be loaded.
    Returns:
        tuple: A tuple containing:
            - image_nib (nibabel.Nifti1Image): The loaded image object.
            - image_data (numpy.ndarray): The image data as a NumPy array.
    """
    image_nib = nib.load(image_path)
    image_data = image_nib.get_fdata()

    return image_nib, image_data


def save_image(
    image_data: np.ndarray, affine: np.ndarray, header: dict, save_path: str
):
    """
    Save a medical image using nibabel.
    Args:
        image_data (np.ndarray): The image data to be saved.
        affine (np.ndarray): The affine transformation matrix of the image.
        header (dict): The header information of the image.
        save_path (str): The file path where the image should be saved.
    Returns:
        None
    """
    nifti_image = nib.Nifti1Image(image_data, affine=affine, header=header)
    nib.save(nifti_image, save_path)
