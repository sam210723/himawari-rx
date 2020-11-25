all: release

release: clean
	@echo. && @echo ====== Building release package ======
	mkdir release
	copy /Y src\*.py release
	mkdir release\tools
	copy /Y src\tools\*.py release\tools
	copy /Y src\*.ini release
	copy /Y requirements.txt release
	7z a himawari-rx.zip ./release/*
	rmdir /S /Q release

clean:
	@echo. && @echo ====== Cleaning development environment ======
	if exist release rmdir /S /Q release
	if exist src\__pycache__ rmdir /S /Q src\__pycache__
	if exist received rmdir /S /Q received
	if exist src\received rmdir /S /Q src\received
	if exist himawari-rx.zip del /Q himawari-rx.zip

.PHONY: all release clean
