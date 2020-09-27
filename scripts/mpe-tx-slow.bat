@echo off
title MPEG-TS MPE Re-transmitter

REM Open input transport stream, slow bitrate down to 500kbps, handle encapsulation and output UDP datagrams on 239.0.0.1:8001, then drop TS packets
tsp -I file --infinite "E:\RF\HimawariCast\TS\154.0E_4148H_2586_(2020-09-20 1121 UTC)_6983.ts" -P regulate --bitrate 500000 -P mpe --pid 0x03E9 --udp-forward --log -O drop
