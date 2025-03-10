# minidisc-cuesheet
Scripts to operate on cuesheets and minidisc TOC's

## Purpose

The purpose of this collection of scripts is to make gapless recording possible through NetMD. 
It's not fully automatic and it requires the use of the homebrew mode of [Web MiniDisc Pro](https://web.minidisc.wiki/).

## Requirements
Besides Python, you will need to have a few packages installed, namely `cdrdao` and `cuetools`. 
On MacOS you can install them through homebrew:
```commandline
brew install cdrdao cuetools
```

## Workflow description

> [!WARNING]
> This is work in progress, the process will be simplified!

Before I go into details, these are the high level steps in order to get to a gapless recording with trackmarks:
1. Source a `bin/cue` or `wav/cue` pair for what you want to record. If it's a `bin/cue` you can convert the `bin` file to `wav` using [XLD](https://sourceforge.net/projects/xld/) for example. See below if you want to rip a CD on Mac.
2. Record the single `wav` file to your MD using Web MiniDisc Pro.
3. Convert the cue sheet to breakpoints using `cuebreakpoints image.cue > image_times.cue` (It will be missing the `00:00.00` mark, which indicates the first track)
4. Using WMD homebrew mode, download the TOC.
5. Update the track marks in the TOC `python toc_marks.py image_times.cue toc.bin`
6. Once done, pull out the USB cable, then remove power. The track marks should now be set.
7. Using WMD, download the titles (still empty), which will be a file called `Disc.csv`
8. Update the `Disc.csv` using `update_titles.py` and the original `cue` that includes titles. `python update_titles.py --csv Disc.csv --cue image.cue --outfile titles.csv`
9. Upload the newly generated `titles.csv` to the disc using WMD.

## Ripping a cd on Mac.

```commandline
diskutil unmount /dev/disk4 # unmount the device
cdrdao scanbus # to find the device name, up to the colon (:)
cdrdao read-cd --rspeed 8 --datafile image.bin --driver generic-mmc:0x20000 --device "IOService:/AppleACPIPlatformExpert/PCI0@0/AppleACPIPCI/XHC1@14/XHC1@14000000/HS14@14600000/USB to ATA/ATAPI bridge@14600000/MSC Bulk-Only Transfer@0/IOUSBMassStorageInterfaceNub/IOUSBMassStorageDriverNub/IOUSBMassStorageDriver/IOSCSILogicalUnitNub@0/IOSCSIPeripheralDeviceType05/IODVDServices" --read-raw image.toc
toc2cue image.toc image.cue # convert the toc to cue
```
