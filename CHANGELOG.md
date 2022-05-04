# Change Log
All notable changes to this project will be documented in this file.

<details>
<summary>Unreleased changes</summary>

### Added
  - [nanomsg](https://nanomsg.org/) (`nng`) input option
  - Raw TCP socket input option

### Changed
  - 

### Fixed
  - 
</details>


## [v0.1.3](https://github.com/sam210723/himawari-rx/releases/tag/v0.1.3) - Combined Image Output (2021-08-29)
<details>
<summary>Details</summary>

### Added
  - New `combine` option to save imgaes to single folder ([XRIT2PIC](http://www.alblas.demon.nl/wsat/software/soft_msg.html) compatibility, [Issue #8](https://github.com/sam210723/himawari-rx/issues/8))

### Changed
  - Renamed `ignored_channels` option to `ignored`

### Fixed
  - Relative paths when script is not in the CWD ([Issue #7](https://github.com/sam210723/himawari-rx/issues/7))
</details>


## [v0.1.2](https://github.com/sam210723/himawari-rx/releases/tag/v0.1.2) - Linux File Path Bugfix (2021-02-11)

Fixed file paths for Linux hosts.


## [v0.1.1](https://github.com/sam210723/himawari-rx/releases/tag/v0.1.1) - Non-Image File Path Bugfix (2020-11-28)

Fixed output file path exception for non-image files. Numpy version held back due to Windows 10 2004 bug.

<details>
<summary>Details</summary>

### Added
  - Launcher ``.bat`` file in release ZIP
  - Quickstart in README

### Changed
  - Limit numpy version to 1.19.3 (see https://stackoverflow.com/q/64729944)

### Fixed
  - Output path for non-image files
</details>


## [v0.1](https://github.com/sam210723/himawari-rx/releases/tag/v0.1) - Initial Release (2020-11-25)
