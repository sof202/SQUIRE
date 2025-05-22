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
squire cpglist -d squire.h5 -t 1e-15 cpg_list.bed

