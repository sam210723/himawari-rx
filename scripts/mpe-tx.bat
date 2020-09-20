@echo off
title MPEG-TS MPE Re-transmitter

REM Open input transport stream, slow bitrate down to actual off-air bitrate, handle encapsulation and output UDP datagrams on 239.0.0.1:8001, then drop TS packets
tsp -I file --infinite "E:\RF\HimawariCast\154.0E_4148H_2586_(2020-07-06 0936 UTC).ts" -P regulate --bitrate 3075700 -P mpe --pid 0x03E9 --udp-forward --log -O drop

