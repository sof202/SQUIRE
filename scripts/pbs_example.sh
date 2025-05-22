#!/bin/bash
#PBS -V
#PBS -q queue
#PBS -l walltime=12:00:00
#PBS -l nodes=1
#PBS -l mem=50gb
#PBS -o squire_${PBS_JOBID}.log
#PBS -e squire_${PBS_JOBID}.err
#PBS -N squire

squire create -d squire.h5 -b neuron.bed,olig.bed,glial.bed
squire add -d squire.h5 -b astrocyte.bed
squire reference -d squire.h5 reference_matrix.bed

# Get threshold where number of passing CpGs is as close as possible to 
# some value
cpgs_to_keep=10000
threshold_list="1e-5,1e-10,1e-15,1e-20"
threshold_to_use=$(\
    squire report -d squire.h5 -m -t "${threshold_list}" | \
    awk \
        -v max_value="${cpgs_to_keep}"\
        -F":" \
        '{if ($2<max_value) {print $1; exit}}'
)

squire cpglist -d squire.h5 -t "${threshold_to_use}" cpg_list.bed

