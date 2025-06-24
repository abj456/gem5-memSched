#!/bin/bash
BENCHMARK=$1
if [ -z "$BENCHMARK" ]; then
	echo "Usage: $0 <benchmark>"
	exit 1
fi

CONFIG_SCRIPT_DIR=./gem5-config-scripts

if [ "$BENCHMARK" == "sysbench" ] ; then
	SIZE=$2
	THREADS=$3
	SYS_CMD=$4
	STATS_DIR=$5
	if [ -z "$SIZE" ] || [ -z "$THREADS" ] || [ -z "$SYS_CMD" ] || [ -z "$STATS_DIR" ]; then
		echo "Usage: $0 <benchmark> <size> <thread> <sysbench command> <stats dir>"
		exit 1
	fi

	/home/abj456/gem5/build/X86-ATLAS/gem5.fast \
		-d ${STATS_DIR}/ \
		${CONFIG_SCRIPT_DIR}/${BENCHMARK}-x86-fs.py \
		--size=$SIZE --threads=$THREADS --sys_cmd="${SYS_CMD}"
elif [ "$BENCHMARK" == "parsec" ] ; then
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
	/home/abj456/gem5/build/X86/gem5.opt \
		-d ./parsec-gem5/m5out-${SIZE}-h${HEAVY_TAIL}-l${LIGHT_TAIL}/atlas-${STATS_DIR}/ \
		${CONFIG_SCRIPT_DIR}/${BENCHMARK}-x86-fs.py \
		--size=$SIZE --heavy_threads=$HEAVY_TAIL --light_threads=$LIGHT_TAIL \
		--kvm_ticks=$KVM_TICKS --timing_ticks=$TIMING_TICKS
else
	echo "Invalid benchmark. Use 'sysbench' or 'parsec'."
	exit 1
fi
