@echo off
title MPEG-TS MPE Re-transmitter

REM Open input transport stream, slow bitrate down to actual off-air bitrate (3075700 bps), handle encapsulation and output UDP datagrams on 239.0.0.1:8001, then drop TS packets
set out="%~1_FILTERED.ts"
tsp -I file %1 -P filter --pid 0x03E9 -O file %out%
