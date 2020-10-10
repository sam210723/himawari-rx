@echo off
title MPEG-TS MPE Re-transmitter

REM Open input transport stream, filter out all PIDs except MPE PID then write to file
set out="%~1_FILTERED.ts"
tsp -I file %1 -P filter --pid 0x03E9 -O file %out%
