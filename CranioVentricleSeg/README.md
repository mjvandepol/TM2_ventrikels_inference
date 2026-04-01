# CranioVentricleSeg

## Requirements
- Python 3.11

## Create and activate the environment
- Bash: create venv and activate (run .sh file, adjust path to venv) (for me: CranioVentricleSeg)
- Windows: create environment and activate (run .py file)

## Run Python code
- Use python ./CranioVentricleSeg/run_cranioventricleseg.py file_based to directly use on patient folder
    - Patient folder should be named: ...
    - Patient folders should contain "T1w" folder with T1w scan named: "T1w.nii.gz"

- Use python ./CranioVentricleSeg/run_cranioventricleseg.py xnat_based to first download data from xnat


### Command for single XNAT
python ./CranioVentricleSeg/run_cranioventricleseg.py xnat_based -e MR_15127 -b "\\storage\v\vcl08\PLCH\Data\aDATA\PERSOONLIJKE MAPPEN\059156_Wijnbergen\Temp" -d cuda

### Command for single File
python ./CranioVentricleSeg/run_cranioventricleseg.py file_based -f "\\storage\v\vcl08\PLCH\Data\aDATA\PERSOONLIJKE MAPPEN\059156_Wijnbergen\Temp\Trig_18_2022-02-08" -d cuda

python ./CranioVentricleSeg/run_cranioventricleseg.py file_based -f "D:\Ventricle_Segmentation\Data_Cranio\Test\Necker_A_001" -d cuda

### Command for single File Necker
python ./CranioVentricleSeg/run_cranioventricleseg.py necker_based -f "D:\Ventricle_Segmentation\Data_Cranio\Trigono\Necker_T_099" -d cuda

### Command for XNAT batches
python ./CranioVentricleSeg/run_xnat_batch.py -d cuda -f "\\storage\v\vcl08\PLCH\Data\aDATA\PERSOONLIJKE MAPPEN\059156_Wijnbergen\Temp\Test_Batch_XNAT.xlsx" -b "\\storage\v\vcl08\PLCH\Data\aDATA\PERSOONLIJKE MAPPEN\059156_Wijnbergen\Temp"

### Command for File batches
python ./CranioVentricleSeg/run_batch_file_based.py -d cuda -f "\\storage\v\vcl08\PLCH\Data\aDATA\PERSOONLIJKE MAPPEN\059156_Wijnbergen\Temp"

python ./CranioVentricleSeg/run_batch_file_based.py -d cuda -f "D:\Ventricle_Segmentation\Data_Cranio\Scapho"

### Command for Necker batches
python ./CranioVentricleSeg/run_batch_necker_based.py -d cuda -f "D:\Ventricle_Segmentation\Data"

python ./CranioVentricleSeg/run_batch_necker_based.py -d cuda -f "D:\Ventricle_Segmentation\Data_Cranio\Scapho"

### Modules installed
nibabel
xnat
dicom2nifti (pylib-openblas)
hb-bet
openpyxl
cc3d

pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

(Download CUDA toolkit: 
https://developer.nvidia.com/cuda-11-8-0-download-archive?target_os=Windows&target_arch=x86_64&target_version=11&target_type=exe_local)

n4 kopiëren naar folder en pad goed zetten!
Might need to adjust number of threads n4

### v1.0
With mirroring -> still works better

### v1.1
Without mirroring

## Necker files
1. Download from PACS
2. Run necker/move_dicom_files.py
3. Run necker_based CranioVentricleSeg (as XNAT download is not needed, but conversion to dicom is)
4. Run file_based if already converted to Nifti

## Find missing ventricle files:

for subject in */; do [ -f "./${subject}T1w/T1w_masked_n4_ventricles_v2.0.nii.gz" ] || echo "Missing: ${subject}T1w/T1w_masked_n4_ventricles_v2.0.nii.gz"; done

## Save file names in txt file
find . -maxdepth 1 -type f -name "*.nii.gz" | sed 's|^\./||; s|\.nii.gz$||' | sort > filenames.txt