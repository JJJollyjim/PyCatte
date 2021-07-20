# PyCatte

Barebones Python driver for cat-shaped Bluetooth thermal printers.

Based on the6p4c's https://github.com/the6P4C/catteprinter, ported to Python
because I hit bugs in btleplug, and I have sworn off working with BlueZ for the
sake of my health, so I will not attempt to fix it :P

Accepts P4 PBM files (width=384px) on standard input.

Example usage with [imagemagick's dithering](https://legacy.imagemagick.org/Usage/quantize/):

    convert ~/Downloads/shrek.png -resize '384x' -monochrome pbm:- | python catte.py "D2:C9:64:A0:52:C3"

You may need to provide a lower-than-default `--mtu` argument if sending fails.
