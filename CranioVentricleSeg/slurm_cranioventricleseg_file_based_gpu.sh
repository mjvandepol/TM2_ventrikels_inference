#!/bin/bash
#SBATCH --ntasks=1                     ### Number of CPU cores
#SBATCH --mem=12G                      ### How much RAM memory
#SBATCH -p short                       ### Queue to submit to: express, short, long, interactive
#SBATCH --gres=gpu:1                   ### How many GPUs
#SBATCH --exclude=gpu002
#SBATCH -t 0-02:00:00                  ### The time limit in D-hh:mm:ss format
#SBATCH -o /trinity/home/r116411/repositories/TM2_ventrikels_inference/CranioVentricleSeg/Logs/Out/out_%j.log      ### Console output (%j is job number)
#SBATCH -e /trinity/home/r116411/repositories/TM2_ventrikels_inference/CranioVentricleSeg/Logs/Error/error_%j.log  ### Error output
#SBATCH --job-name=cvs_t2              ### Job-name
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=m.j.vandepol@erasmusmc.nl


# Load modules and virtual environment
module purge
module load Python/3.11.5-GCCcore-13.2.0
source ~/venv/cranio_env/bin/activate
module list

echo $1
echo $2
echo $3

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

# Run script
cd /trinity/home/r116411/repositories/TM2_ventrikels_inference
python ./CranioVentricleSeg/run_cranioventricleseg.py file_based -f $1 -d $2 -m $3


### #SBATCH --nodelist=gpu005
