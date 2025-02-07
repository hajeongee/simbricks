#!/bin/bash -eux

set -eux

apt-get update
apt-get -y install \
    iperf \
    iputils-ping \
    lbzip2 \
    netperf \
    netcat \
    ethtool \
    tcpdump \
    pciutils \
    busybox \
    numactl \
    sysbench

pushd /tmp/input
mv guestinit.sh /home/ubuntu/guestinit.sh
mv bzImage /boot/vmlinuz-5.15.93
mv config-5.15.93 /boot/
mv m5 /sbin/m5
update-grub

# with stupid ubuntu22 /lib is a symlink at which point just untaring to / will
# replace that symlink with a directory, so first extract and then carefully
# copy... -.-
mkdir kheaders
cd kheaders
tar xf /tmp/input/kheaders.tar.bz2
cp -a lib/modules/* /lib/modules/
cp -a usr/* /usr/

# cleanup
popd
rm -rf /tmp/input
