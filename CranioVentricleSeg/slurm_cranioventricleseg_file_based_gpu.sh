#!/bin/bash
#SBATCH --ntasks=1             ### Number of CPU cores
#SBATCH --mem=12G              ### How much RAM memory
#SBATCH -p short             ### Queue to submit to: express, short, long, interactive
#SBATCH --gres=gpu:1           ### How many GPUs
#SBATCH --exclude=gpu002
#SBATCH -t 0-02:00:00          ### The time limit in D-hh:mm:ss format
#SBATCH -o /trinity/home/r059156/logging/cranioventricleseg/Out/out_%j.log      ### Console output (%j is job number)
#SBATCH -e /trinity/home/r059156/logging/cranioventricleseg/Error/error_%j.log  ### Error output
#SBATCH --job-name=cvs_t2     ### Job-name



# Load modules and virtual environment
module purge
module load Python
module load CUDA/11.8.0

source /trinity/home/r059156/venvs/CranioGeneral/bin/activate

echo $1
echo $2
echo $3

# Run script
python ./CranioVentricleSeg/run_cranioventricleseg.py file_based -f $1 -d $2 -m $3


### #SBATCH --nodelist=gpu005
