#!/bin/bash
BENCHMARK=$1
if [ -z "$BENCHMARK" ]; then
	echo "Usage: $0 <benchmark>"
	exit 1
fi

STATS_DIR=~/full_system_images/disks/${BENCHMARK}

if [ "$BENCHMARK" == "sysbench" ] ; then
	SIZE=$2
	THREADS=$3
	if [ -z "$SIZE" ] || [ -z "$THREADS" ] ; then
		echo "Usage: $0 <benchmark> <size> <thread>"
		exit 1
	fi
	gem5.opt \
		-d ${STATS_DIR}/m5out-ATLAS-${THREADS}-${SIZE}/ \
		~/full_system_images/disks/${BENCHMARK}-x86-fs.py \
		--size=$SIZE --threads=$THREADS
elif [ "$BENCHMARK" == "parsec" ] ; then
	CHOOSE=$2
	SIZE=$3
	if [ -z "$CHOOSE" ] || [ -z "$SIZE" ] ; then
		echo "Usage: $0 <benchmark> <choose> <size>"
		exit 1
	fi
	gem5.opt \
		-d ${STATS_DIR}/m5out-ATLAS-${CHOOSE}-${SIZE}/ \
		~/full_system_images/disks/${BENCHMARK}-x86-fs.py \
		--benchmark=$CHOOSE --size=$SIZE
else
	echo "Invalid benchmark. Use 'sysbench' or 'parsec'."
	exit 1
fi
