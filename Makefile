all: release

release: clean
	@echo. && @echo ====== Building release package ======

clean:
	@echo. && @echo ====== Cleaning development environment ======
	if exist src\__pycache__ rmdir /S /Q src\__pycache__
	if exist src\received rmdir /S /Q src\received

.PHONY: all release clean
