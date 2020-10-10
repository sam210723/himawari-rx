@echo off
title MPEG-TS MPE Re-transmitter

REM Open input transport stream, slow bitrate down to 20 Mbps, handle encapsulation and output UDP datagrams on 239.0.0.1:8001, then drop TS packets
tsp -I file "E:\RF\HimawariCast\ts\154.0E_4148H_2586_(2020-09-20 1136 UTC)_6903X_FILTERED.ts" -P regulate --bitrate 20000000 -P mpe --pid 0x03E9 --udp-forward --log -O drop
