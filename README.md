RIMA - Radiology IMage Analysis

Research prototype for Radiology images.

Prerequistes
 * Redis

For searching the PACS use [Meta](https://github.com/joshy/meta).
For downloading the images from the PACS [MOVA](https://github.com/joshy/mova) is used.
The processing is done via pydicom and other python libs. For orchestration
[luigi](https://github.com/spotify/luigi) is used.