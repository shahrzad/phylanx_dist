#!/bin/bash

#SBATCH -N 8 
#SBATCH -p medusa
#SBATCH --time=72:00:00

node_name=$1
num_nodes=$2

script_dir="/work/sshirzad/phylanx_dist/scripts"
result_dir="/work/sshirzad/phylanx_dist/results"
phylanx_bin_dir="/home/sshirzad/src/phylanx/build_release_clang_no_hpxmp_medusa/bin"
batch=(10000)
length=(100)
out_channels=(100)
filter_length=(20)
modes=("master" "shahrzad" "bita")
export PATH=${phylanx_bin_dir}:$PATH

#rm  ${result_dir}/*.dat
export OMP_NUM_THREADS=1


for rb in ${batch[@]}
do
	b=$((num_nodes*rb))
	for l in ${length[@]}
	do
		for fl in ${filter_length[@]}
		do
			if [ $l -ge $fl ]
			then
	        	        for oc in ${out_channels[@]}
	        	        do
					for mode in ${modes[@]}
					do
						echo "mode ${mode} input ${b}x${l}x3 filter ${oc}x${fl}x3"
						touch ${result_dir}/${node_name}_${mode}_${b}_${l}_${oc}_${fl}_${num_nodes}.dat
						rm ${result_dir}/${node_name}_${mode}_${b}_${l}_${oc}_${fl}_${num_nodes}.dat
						srun -p ${node_name} -N ${num_nodes} ${phylanx_bin_dir}/conv1d_dist_instrumented_test --batch=${b} --length=${l} --channel=3 --filter_length=${fl} --out_channels=${oc} --mode=${mode} --hpx:localities=${num_nodes} --hpx:run-hpx-main>>${result_dir}/${node_name}_${mode}_${b}_${l}_${oc}_${fl}_${num_nodes}.dat
					done
				done
			fi
		done
	done
done
