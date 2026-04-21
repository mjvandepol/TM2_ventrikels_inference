#!/bin/bash

SOURCE="/data/scratch/r116411/ventricle_segmentation_train_test_t2/train"
DEST="/data/scratch/r116411/ventricle_segmentation_train_test_t2/train_subset_001"

folders=(
C_008_2020-10-20
C_014_2011-08-02
C_014_2013-06-17 
C_017_2017-01-13
C_019_2023-06-02
C_027_2018-10-03
C_029_2022-05-11
C_033_2009-12-04
C_040_2014-01-28
C_042_2021-10-26
C_044_2009-02-13
C_044_2016-08-29
C_050_2021-10-22
C_054_2021-11-17
C_061_2009-04-16
C_061_2012-06-12
C_062_2017-05-26
C_063_2022-11-10
C_074_2016-10-21
C_078_2017-01-30
C_083_2022-08-08
M_004_2018-11-05
M_006_2021-04-23
M_031_2012-05-16
M_032_2014-06-27
M_042_2010-03-26
M_045_2023-03-24
)

for folder in "${folders[@]}"; do
    echo "Copying $folder..."
    cp -r "$SOURCE/$folder" "$DEST/"
done

echo "Klaar!"