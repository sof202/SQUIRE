#!/bin/bash
#SBATCH --export=ALL
#SBATCH -p queue
#SBATCH --time=12:00:00
#SBATCH --nodes=1 
#SBATCH --mem=50G
#SBATCH --output=squire_%j.log
#SBATCH --error=squire_%j.err
#SBATCH --job-name=squire

BEDMETHYL_DIR="path/to/bedmethyls"
find "${BEDMETHYL_DIR}" -type f -name "*.bed" -print0 | \
    xargs -0 realpath > \
    "bedmethyl_list.txt"

squire create --hdf5 squire.h5 --file "bedmethyl_list.txt"
squire reference --hdf5 squire.h5 reference_matrix.bed
squire cpglist --hdf5 squire.h5 cpg_list.bed
