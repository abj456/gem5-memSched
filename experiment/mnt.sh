#!/bin/bash
OFFSET=$((512 * 4096))

if [ "$1" == "mount" ]
then
    IMG_FILE=$2
    MNT_DIR=$3
    sudo mount -o loop,offset="${OFFSET}" "${IMG_FILE}" "${MNT_DIR}"
elif [ "$1" == "umount" ]
then
    MNT_DIR=$2
    sudo umount "${MNT_DIR}"
else
    echo "Not valid command."
fi
