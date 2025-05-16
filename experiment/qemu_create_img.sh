#!/bin/bash
DISK_FILE=$1
SIZE=$2
qemu-img create -f raw $DISK_FILE $SIZE
