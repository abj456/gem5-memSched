#!/bin/bash
BENCHMARK=$1
if [ -z "$BENCHMARK" ]; then
	echo "Usage: $0 <benchmark>"
	exit 1
fi

CONFIG_SCRIPT_DIR=./gem5-config-scripts

if [ "$BENCHMARK" == "parsec" ] ; then
	SIZE=$2
	HEAVY_TAIL=$3
	LIGHT_TAIL=$4
	STATS_DIR=$5
	KVM_TICKS=$6
	TIMING_TICKS=$7
	if [ -z "$KVM_TICKS" ] || [ -z "$TIMING_TICKS" ]; then
		KVM_TICKS="0.5e12"
		TIMING_TICKS="0.5e12"
	fi
	if [ -z "$SIZE" ] || [ -z "$HEAVY_TAIL" ] || [ -z "$LIGHT_TAIL" ] || [ -z "$STATS_DIR" ]; then
		echo "Usage: $0 <benchmark> <size> <heavy> <light> <stats dir> [kvm ticks] [timing ticks]"
		exit 1
	fi
	/home/abj456/gem5/build/X86-ATLAS/gem5.fast \
		-d ./parsec-gem5/m5out-${SIZE}-h${HEAVY_TAIL}-l${LIGHT_TAIL}/${STATS_DIR}/atlas/ \
		${CONFIG_SCRIPT_DIR}/${BENCHMARK}-x86-fs.py \
		--size=$SIZE --heavy_threads=$HEAVY_TAIL --light_threads=$LIGHT_TAIL \
		--kvm_ticks=$KVM_TICKS --timing_ticks=$TIMING_TICKS
elif [ "$BENCHMARK" == "parsec-ckpt" ] ; then
	SIZE=$2
	HEAVY_TAIL=$3
	LIGHT_TAIL=$4
	STATS_DIR=$5
	KVM_SEC=$6
	MEM_MODEL=$7
	if [ -z "$KVM_SEC" ] || [ -z "$MEM_MODEL" ]; then
		KVM_SEC="0.5"
		MEM_MODEL="DDR5_4400"
	fi
	if [ -z "$SIZE" ] || [ -z "$HEAVY_TAIL" ] || [ -z "$LIGHT_TAIL" ] || [ -z "$STATS_DIR" ]; then
		echo "Usage: $0 <benchmark> <size> <heavy> <light> <stats dir> [kvm ticks] [memory model]"
		exit 1
	fi
	/home/abj456/gem5/build/X86/gem5.fast \
		-d ./parsec-gem5/m5out-${SIZE}-h${HEAVY_TAIL}-l${LIGHT_TAIL}/${MEM_MODEL}-ckpt-restore/${KVM_SEC}sec/${STATS_DIR} \
		${CONFIG_SCRIPT_DIR}/parsec-x86-take-checkpoint.py \
		--size=$SIZE --heavy_threads=$HEAVY_TAIL --light_threads=$LIGHT_TAIL \
		--kvm_ticks="${KVM_SEC}e12" --mem-model=$MEM_MODEL
elif [ "$BENCHMARK" == "parsec-ckpt-restore" ] ; then
	SIZE=$2
	HEAVY_TAIL=$3
	LIGHT_TAIL=$4
	MEM_MODEL=$5
	TIMING_TICKS=$6
	STATS_DIR=$7
	CKPT_SEC=$8
	if [ -z "$TIMING_TICKS" ] || [ -z "$MEM_MODEL" ]; then
		TIMING_TICKS="0.5e12"
		MEM_MODEL="DDR5_4400"
	fi
	if [ -z "$SIZE" ] || [ -z "$HEAVY_TAIL" ] || [ -z "$LIGHT_TAIL" ] || [ -z "$STATS_DIR" ] || [ -z "$CKPT_SEC" ] ; then
		echo "Usage: $0 <benchmark> <size> <heavy> <light> <stats dir> [kvm ticks] [memory model] <checkpoint sec>"
		exit 1
	fi
	/home/abj456/gem5/build/X86/gem5.fast \
		-d ./parsec-gem5/m5out-${SIZE}-h${HEAVY_TAIL}-l${LIGHT_TAIL}/${MEM_MODEL}-ckpt-restore/${CKPT_SEC}sec/${STATS_DIR}-${TIMING_TICKS} \
		${CONFIG_SCRIPT_DIR}/parsec-x86-restore-checkpoint.py \
		--size=$SIZE --heavy_threads=$HEAVY_TAIL --light_threads=$LIGHT_TAIL \
		--timing_ticks=$TIMING_TICKS --mem-model=$MEM_MODEL --ckpt_sec=$CKPT_SEC
else
	echo "Invalid benchmark. Use 'sysbench' or 'parsec'."
	exit 1
fi
