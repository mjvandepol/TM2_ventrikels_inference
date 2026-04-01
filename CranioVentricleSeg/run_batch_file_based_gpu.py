import argparse
import os
import subprocess


def main(args: argparse.Namespace):
    patient_folders = [f.path for f in os.scandir(args.folder_name) if f.is_dir()]

    for patient_folder in patient_folders:
        subprocess.run(
            [
                "sbatch",
                "./CranioVentricleSeg/slurm_cranioventricleseg_file_based_gpu.sh",
                patient_folder,
                args.device,
                args.model_version,
            ]
        )


if __name__ == "__main__":
    # Initialize the argument parser
    parser = argparse.ArgumentParser()

    # create the parser for the "parser_file" command
    parser.add_argument(
        "-f",
        "--folder",
        dest="folder_name",
        help="folder contains all patient folders, which already contain a T1w scan",
        required=True,
    )
    parser.add_argument(
        "-d",
        "--device",
        dest="device",
        help="device to run the segmentation on, cpu or cuda",
        default="cuda",
    )
    parser.add_argument(
        "-m",
        "--model_version",
        dest="model_version",
        help="version of the segmentation model to use",
        default="v3.3",
    )

    args = parser.parse_args()

    main(args=args)
