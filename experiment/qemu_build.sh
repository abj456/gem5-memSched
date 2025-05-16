#!/bin/bash
ISO_FILE=$1
DISK_FILE=$2
qemu-system-x86_64 -m 6G \
		-cdrom "${ISO_FILE}" \
		-boot d -drive file="${DISK_FILE}",format=raw \
		-enable-kvm -cpu host -smp 6 \
		-net nic \
		-net user,hostfwd=tcp::2222-:22

# qemu-system-x86_64 \
# 	-enable-kvm \
# 	-cpu host,vmx=on,hypervisor=off \
# 	-smp 4 -m 4G \
# 	-cdrom ubuntu-20.04.6-live-server-amd64.iso \
# 	-drive format=raw,file=$1 \
# 	-boot d \
# 	-net nic \
# 	-net user,hostfwd=tcp:2222-:22
