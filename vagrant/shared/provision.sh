#!/usr/bin/env bash
if [ $(id -u) -ne 0 ]; then
    echo "Please run this script as root or using sudo!"
    exit 13
fi
rm /etc/apt/sources.list.d/cappelikan.sources /etc/apt/sources.list.d/home-alvistack.sources
apt-get update
apt purge -y ansible mainline
apt autopurge -y
apt-get upgrade
apt-get install ansible
reboot
