#!/usr/bin/env bash
set -euo pipefail
# Run as root inside the Ubuntu WSL2 replica, not inside Docker.
[[ $EUID -eq 0 ]] || { echo 'Execute with sudo.' >&2; exit 1; }
command -v zramctl >/dev/null
command -v modprobe >/dev/null
modprobe zram num_devices=0
if [[ -e /sys/block/zram0 ]]; then
    echo 'zram0 already exists; inspect it before configuring.' >&2
    exit 1
fi
device=$(zramctl --find --size 2G --algorithm lz4)
mkswap "$device"
swapon --priority 100 "$device"
zramctl "$device"
swapon --show
