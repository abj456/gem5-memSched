#!/bin/bash
qemu-system-x86_64 -m 6G \
		-drive file=$1,format=raw \
		-enable-kvm -cpu host -smp 6 \
		-net nic \
		-net user,hostfwd=tcp::2222-:22
# qemu-system-x86_64 \
# 	-enable-kvm \
# 	-cpu host,vmx=on,hypervisor=off \
# 	-smp 4 -m 4096 \
# 	-vga qxl \
# 	-drive format=raw,file=$1 \
#	-monitor telnet::45454,server,nowait \
#	-nographic
#	-bios /usr/share/ovmf/OVMF.fd
#	-nic e1000
