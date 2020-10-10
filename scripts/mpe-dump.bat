@echo off
title MPEG-TS MPE Re-transmitter

REM Open input transport stream, slow bitrate down to actual off-air bitrate, handle encapsulation and output UDP datagrams to file, then drop TS packets
tsp -I file "E:\RF\HimawariCast\ts\154.0E_4148H_2586_(2020-09-20 1136 UTC)_6903X_FILTERED.ts" -P mpe --pid 0x03E9 --log --output-file "udp.dump" -O drop
pause
