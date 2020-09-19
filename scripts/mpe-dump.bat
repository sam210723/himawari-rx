@echo off
title MPEG-TS MPE Re-transmitter

REM Open input transport stream, slow bitrate down to actual off-air bitrate, handle encapsulation and output UDP datagrams to file, then drop TS packets
tsp -I file "E:\RF\HimawariCast\154.0E_4148H_2586_(2020-07-06 1736).ts" -P mpe --pid 0x03E9 --log --output-file "udp.dump" -O drop
pause
