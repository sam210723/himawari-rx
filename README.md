# :satellite: himawari-rx - HimawariCast Downlink Processor

[![GitHub release](https://img.shields.io/github/release/sam210723/himawari-rx.svg)](https://github.com/sam210723/himawari-rx/releases/latest)
[![Python versions](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue)](https://www.python.org/)
[![Github all releases](https://img.shields.io/github/downloads/sam210723/himawari-rx/total.svg)](https://github.com/sam210723/himawari-rx/releases/latest)
[![GitHub license](https://img.shields.io/github/license/sam210723/himawari-rx.svg)](https://github.com/sam210723/himawari-rx/blob/master/LICENSE)

**himawari-rx** is a decoder for receiving images from geostationary weather satellite [Himawari-8 (140.7˚E)](https://himawari8.nict.go.jp/) via the [HimawariCast](https://www.data.jma.go.jp/mscweb/en/himawari89/himawari_cast/himawari_cast.php) data service operated by [Japan Meteorological Agency](https://www.data.jma.go.jp/mscweb/en/index.html). HimawariCast is a DVB-S2 signal transmitted from [JCSAT-2B (154°E)](https://www.jsat.net/en/contour/jcsat-2b.html) on its [global C-band beam](https://www.satbeams.com/footprints?beam=8542). It can be received with a 2.4m satellite dish and a standard C-band LNB. It may be possible to use a smaller dish however this has not been verified.

**himawari-rx** receives UDP datagrams over a network connection and outputs decoded image files to disk. The UDP datagrams can come from either a DVB-S2 receiver card such as a [TBS5520SE](https://www.tbsdtv.com/products/tbs5520se_multi-standard_tv_tuner_usb_box.html) or a satellite IP receiver such as the [Novra S300D](https://novra.com/product/s300d-receiver). A Software Defined Radio solution using GNU Radio is currently under development.

![Himawari-8 Wavelengths](https://vksdr.com/bl-content/uploads/pages/95f4812a86753b6057b0e37ce4daa5d1/wavelengths.png)


## Getting Started
A (work in progress) guide for setting up the hardware and software components of a HimawariCast receiver is [available on my site](https://vksdr.com/himawari-rx).

<a href="https://vksdr.com/himawari-rx" target="_blank"><p align="center"><img src="https://vksdr.com/bl-content/uploads/pages/95f4812a86753b6057b0e37ce4daa5d1/guide-thumb-white.png" title="Receiving Images from Geostationary Weather Satellite Himawari-8 via HimawariCast"></p></a>

**In the meantime here is a quick overview of the required setup:**

HimawariCast is a C-band DVB-S2 downlink on geostationary communication satellite JCSAT-2B at 154°E. The downlink frequency is 4148 MHz with a symbol rate of 2586 ksps and horizontal polarisation. On a standard 5150 MHz LO C-band LNB it has an IF of 1002 MHz.

A standard DVB-S2 receiver card/box such as the [TBS6902](https://www.tbsdtv.com/products/tbs6902-dvb-s2-dual-tuner-pcie-card.html) (PCIe) or [TBS5520SE](https://www.tbsdtv.com/products/tbs5520se_multi-standard_tv_tuner_usb_box.html) (USB) can receive this downlink either using Windows or Linux. The downlink carries multicast UDP packets which are wrapped in [DVB-MPE](https://en.wikipedia.org/wiki/Multiprotocol_Encapsulation) and need to be unwrapped with software such as [TSDuck](https://tsduck.io/), the [TBS IP Tool](https://www.tbsdtv.com/blog/tbs-ip-tool-is-updated-to-v3-0-5-0-which-added-tbs5927-support.html) or [TSReader](https://www.tsreader.com/).

For TSDuck, the following command should work in most cases. 

```
tsp -I dvb --device-name /dev/dvb/adapter0:1  --lnb 5150 --delivery-system "DVB-S2" --frequency 4148000000 --modulation QPSK --symbol-rate 2586148 --fec-inner "3/5" --roll-off 0.2 --polarity "horizontal" -P mpe --pid 0x03E9 --udp-forward --log -O drop
```

For TSReader, use ``File -> IP/DVB Mode`` and select PID ``0x03E9 (1001)``, then right click on ``UDP: 239.0.0.1`` in the PID list and select ``Retransmit UDP payload``.

To install himawari-rx, download the ``himawari-rx.zip`` from the [latest release](https://github.com/sam210723/himawari-rx/releases/latest) and extract it to a new folder. Next, install the required Python packages with ``pip install -r requirements.txt``. Finally, run himawari-rx with ``python himawari-rx.py``.

himawari-rx will begin decoding images once UDP packets from the downlink are being transmitted onto the local network using TSDuck, the TBS IP Tool or TSReader.

To generate PNG image files from the received LRIT/HRIT files, use the `tools/xrit-img.py` script. These PNG files can then be combined into a false colour image using the `tools/false-colour.py` script.

## Imaging Bands
Himawari-8 is capable of capturing Earth in 16 different wavelengths of light, 14 of which are transmitted via the HimawariCast service.

<p align="center"><img src="https://vksdr.com/bl-content/uploads/pages/95f4812a86753b6057b0e37ce4daa5d1/bands_w.png" title="HimawariCast Bands"></p>

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
| Setting   | Description                                                                   | Options                                                 | Default      |
| --------- | ----------------------------------------------------------------------------- | ------------------------------------------------------- | ------------ |
| `input`   | Input source                                                                  | `nng`, `tcp` or `udp`                                   | `udp`      |
| `path`    | Root output path for received files                                           | *Absolute or relative file path*                        | `"received"` |
| `combine` | Save all images in a single directory (XRIT2PIC compatibility)                | `true` or `false`                                       | `false`      |
| `format`  | File type to output                                                           | `bz2`: Compressed xRIT files<br>`xrit`: LRIT/HRIT files | `xrit`       |
| `ignored` | List of channels (bands) to ignore<br>(e.g. `"B09", "IR2"`)                   | <a href="#imaging-bands">Table of available bands</a>   | *none*       |

#### `nng` section
| Setting | Description                              | Options               | Default     |
| ------- | ---------------------------------------- | ----------------------| ----------- |
| `ip`    | IP address of a **nanomsg** data source  | *Any IPv4 address*    | `127.0.0.1` |
| `port`  | Server port of a **nanomsg** data source | *Any TCP port number* | `8003`      |

#### `tcp` section
| Setting | Description                      | Options               | Default     |
| ------- | -------------------------------- | ----------------------| ----------- |
| `ip`    | IP address of a TCP data source  | *Any IPv4 address*    | `127.0.0.1` |
| `port`  | Server port of a TCP data source | *Any TCP port number* | `8002`      |

#### `udp` section
These two options generally do not need to be changed.
| Setting | Description                             | Options                         | Default     |
| ------- | --------------------------------------- | ------------------------------- | ----------- |
| `ip`    | Multicast IP address of DVB-S2 receiver | `224.0.0.0` - `239.255.255.255` | `239.0.0.1` |
| `port`  | UDP output port of DVB-S2 receiver      | *Any UDP port number*           | `8001`      |


## Acknowledgments
  - [@yanderen2](https://twitter.com/yanderen2) - Software testing and TS recordings
  - [tcjj3](https://github.com/tcjj3) - Software testing and scripting
  - [John Bell](https://twitter.com/eswnl) - Software testing and TS recordings
  - [@Apsattv](https://twitter.com/Apsattv) - TS recordings
