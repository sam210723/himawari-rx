# :satellite: himawari-rx - HimawariCast Downlink Processor

[![GitHub release](https://img.shields.io/github/release/sam210723/himawari-rx.svg)](https://github.com/sam210723/himawari-rx/releases/latest)
[![Github all releases](https://img.shields.io/github/downloads/sam210723/himawari-rx/total.svg)](https://github.com/sam210723/himawari-rx/releases/latest)
[![GitHub license](https://img.shields.io/github/license/sam210723/himawari-rx.svg)](https://github.com/sam210723/himawari-rx/blob/master/LICENSE)

**himawari-rx** is a decoder for receiving images from geostationary weather satellite [Himawari-8 (140.7˚E)](https://himawari8.nict.go.jp/) via the [HimawariCast](https://www.data.jma.go.jp/mscweb/en/himawari89/himawari_cast/himawari_cast.php) data service operated by [Japan Meteorological Agency](https://www.data.jma.go.jp/mscweb/en/index.html). HimawariCast is a DVB-S2 signal transmitted from [JCSAT-2B (154°E)](https://www.jsat.net/en/contour/jcsat-2b.html) on its [global C-band beam](https://www.satbeams.com/footprints?beam=8542). It can be received with a 2.4m satellite dish and a standard C-band LNB. It may be possible to use a smaller dish however this has not been verified.

**himawari-rx** receives UDP datagrams over a network connection and outputs decoded image files to disk. The UDP datagrams can come from either a DVB-S2 receiver card such as a [TBS5520SE](https://www.tbsdtv.com/products/tbs5520se_multi-standard_tv_tuner_usb_box.html) or a satellite IP receiver such as the [Novra S300D](https://novra.com/product/s300d-receiver). A Software Defined Radio solution using GNU Radio is currently under development.

![Himawari-8 Wavelengths](https://vksdr.com/bl-content/uploads/pages/211ee4ec1b2432204d0a98f46b47a131/wavelengths.png)


## Getting Started
A (work in progress) guide for setting up the hardware and software components of a HimawariCast receiver is [available on my site](https://vksdr.com/himawari-rx).

<a href="https://vksdr.com/himawari-rx" target="_blank"><p align="center"><img src="https://vksdr.com/bl-content/uploads/pages/211ee4ec1b2432204d0a98f46b47a131/guide-thumb-white.png" title="Receiving Images from Geostationary Weather Satellite Himawari-8 via HimawariCast"></p></a>

## Imaging Bands
Himawari-8 is capable of capturing Earth in 16 different wavelengths of light, 14 of which are transmitted via the HimawariCast service.

![HimawariCast Bands](https://vksdr.com/bl-content/uploads/pages/211ee4ec1b2432204d0a98f46b47a131/bands_w.png)

<!--
| Band | Detail  | Identifier  | Size  | Resolution    |
| ---- | ------- | ----------- | ----- | ------------- |
| 3    | 1 km/px | ``VIS``     | 75 MB | 11000 x 11000 |
| 4    | 4 km/px | ``B04``     | 6 MB  | 2750 x 2750   |
| 5    | 4 km/px | ``B05``     | 6 MB  | 2750 x 2750   |
| 6    | 4 km/px | ``B06``     | 6 MB  | 2750 x 2750   |
| 7    | 4 km/px | ``IR4``     | 6 MB  | 2750 x 2750   |
| 8    | 4 km/px | ``IR3``     | 4 MB  | 2750 x 2750   |
| 9    | 4 km/px | ``B09``     | 4 MB  | 2750 x 2750   |
| 10   | 4 km/px | ``B10``     | 4 MB  | 2750 x 2750   |
| 11   | 4 km/px | ``B11``     | 6 MB  | 2750 x 2750   |
| 12   | 4 km/px | ``B12``     | 5 MB  | 2750 x 2750   |
| 13   | 4 km/px | ``IR1``     | 6 MB  | 2750 x 2750   |
| 14   | 4 km/px | ``B14``     | 6 MB  | 2750 x 2750   |
| 15   | 4 km/px | ``IR2``     | 6 MB  | 2750 x 2750   |
| 16   | 4 km/px | ``B16``     | 5 MB  | 2750 x 2750   |
-->

## List of options
#### `rx` section
| Setting | Description | Options | Default |
| ------- | ----------- | ------- | ------- |
| `path` | Root output path for received files | *Absolute or relative file path* | `"received"` |
| `format` | File type to output | `bz2`: Compressed xRIT files<br>`xrit`: LRIT/HRIT files | `xrit` |
| `ignored_channels` | List of channels (bands) to ignore<br>(e.g. `"B09", "IR2"`) | <a href="https://vksdr.com/bl-content/uploads/pages/211ee4ec1b2432204d0a98f46b47a131/bands_w.png" target="_blank">Table of available bands</a> | *none* |

#### `udp` section
These two options generally do not need to be changed.
| Setting | Description | Options | Default |
| ------- | ----------- | ------- | ------- |
| `ip` | Multicast IP address of DVB-S2 receiver | `224.0.0.0` - `239.255.255.255` | `239.0.0.1` |
| `port` | UDP output port of DVB-S2 receiver | *Any UDP port number* | `8001` |


## Acknowledgments
  - [@yanderen2](https://twitter.com/yanderen2) - Software testing and TS recordings
  - [tcjj3](https://github.com/tcjj3) - Software testing
  - [@Apsattv](https://twitter.com/Apsattv) - TS recordings
