#!/bin/bash

for server in icarus-evb01 icarus-evb02 icarus-evb03 icarus-evb04 icarus-evb05 icarus-evb06
do
    ssh $server 'crontab ~icarus/FileTransfer/sbndaq-xporter/Xporter/xporter_crontab.ctab'
done

