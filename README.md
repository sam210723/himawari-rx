# :satellite: himawari-rx - HimawariCast Downlink Processor

[![GitHub release](https://img.shields.io/github/release/sam210723/himawari-rx.svg)](https://github.com/sam210723/himawari-rx/releases/latest)
[![Github all releases](https://img.shields.io/github/downloads/sam210723/himawari-rx/total.svg)](https://github.com/sam210723/himawari-rx/releases/latest)
[![GitHub license](https://img.shields.io/github/license/sam210723/himawari-rx.svg)](https://github.com/sam210723/himawari-rx/blob/master/LICENSE)

**himawari-rx** is a file assembler built for receiving images from geostationary weather satellite [Himawari-8 (140.7˚E)](https://himawari8.nict.go.jp/) via the [HimawariCast](https://www.data.jma.go.jp/mscweb/en/himawari89/himawari_cast/himawari_cast.php) data service operated by [JMA](https://www.data.jma.go.jp/mscweb/en/index.html).

HimawariCast is a DVB-S2 based signal transmitted from [JCSAT-2B (154°E)](https://www.jsat.net/en/contour/jcsat-2b.html) on its [global C-band beam](https://www.satbeams.com/footprints?beam=8542). It can be received with a 2.4m satellite dish and a standard C-band LNB. It may be possible to use a smaller dish however this has not been verified.

**himawari-rx** receives UDP datagrams over the network from either a DVB-S2 receiver card such as a [TBS5520SE](https://www.tbsdtv.com/products/tbs5520se_multi-standard_tv_tuner_usb_box.html) or a satellite IP receiver such as the [Novra S300D](https://novra.com/product/s300d-receiver). A Software Defined Radio solution using GNU Radio is currently under development.


## List of options
#### `rx` section
| Setting | Description | Options | Default |
| ------- | ----------- | ------- | ------- |
| `path` | Root output path for received files | *Absolute or relative file path* | `"received"` |
| `format` | File type to output | `bz2`: Compressed xRIT files<br>`xrit`: LRIT/HRIT files | `xrit` |
| `ignored_channels` | List of channels (bands) to ignore<br>(e.g. `"B09", "IR2"`) | <a href="https://pbs.twimg.com/media/EjCwnFrUcAAl_Bl?format=png&name=small" target="_blank">Table of available bands</a> | *none* |

#### `udp` section
These two options generally do not need to be changed.
| Setting | Description | Options | Default |
| ------- | ----------- | ------- | ------- |
| `ip` | Multicast IP address of DVB-S2 receiver | `224.0.0.0` - `239.255.255.255` | `239.0.0.1` |
| `port` | UDP output port of DVB-S2 receiver | *Any UDP port number* | `8001` |


## Acknowledgments
  - [@yanderen2](https://twitter.com/yanderen2) - Software testing and TS recordings
  - [@Apsattv](https://twitter.com/Apsattv) - TS recordings
