# :satellite: himawari-rx - HimawariCast Downlink Processor

[![GitHub release](https://img.shields.io/github/release/sam210723/himawari-rx.svg)](https://github.com/sam210723/himawari-rx/releases/latest)
[![Github all releases](https://img.shields.io/github/downloads/sam210723/himawari-rx/total.svg)](https://github.com/sam210723/himawari-rx/releases/latest)
[![GitHub license](https://img.shields.io/github/license/sam210723/himawari-rx.svg)](https://github.com/sam210723/himawari-rx/blob/master/LICENSE)

**himawari-rx** is a file assembler built for receiving images from geostationary weather satellite [Himawari-8 (140.7˚E)](https://himawari8.nict.go.jp/) via the [HimawariCast](https://www.data.jma.go.jp/mscweb/en/himawari89/himawari_cast/himawari_cast.php) data service operated by [JMA](https://www.data.jma.go.jp/mscweb/en/index.html). It implements parts of the KenCast Fazzt Digital Delivery System protocol in order to assemble transmitted files from a stream of UDP datagrams.
