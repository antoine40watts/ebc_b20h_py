import os
import sys
import time
import struct
import libusb1
from PIL import Image
from libusb1 import USBError

# Constants
VENDOR_ID = 0x09cb
PRODUCT_ID = 0x1996
REQ_TYPE = 1
REQ = 0xb
V_STOP = 0
V_START = 1
INDEX = lambda i: i
LEN = lambda l: l
BUF85SIZE = 1048576

# Global variables
video_device1 = ""
video_device2 = ""
frame_width2 = 80
frame_height2 = 80
frame_owidth2 = 80
frame_oheight2 = 60
flirone_pro = False
pal_inverse = False
pal_colors = False
FFC = False
fdwr1 = 0
fdwr2 = 0
devh = None
buf85pointer = 0
buf85 = bytearray(BUF85SIZE)


def print_format(vid_format):
    print(f"     vid_format->type                ={vid_format.type}")
    print(f"     vid_format->fmt.pix.width       ={vid_format.fmt.pix.width}")
    print(f"     vid_format->fmt.pix.height      ={vid_format.fmt.pix.height}")
    print(f"     vid_format->fmt.pix.pixelformat ={vid_format.fmt.pix.pixelformat}")
    print(f"     vid_format->fmt.pix.sizeimage   ={vid_format.fmt.pix.sizeimage}")
    print(f"     vid_format->fmt.pix.field       ={vid_format.fmt.pix.field}")
    print(f"     vid_format->fmt.pix.bytesperline={vid_format.fmt.pix.bytesperline}")
    print(f"     vid_format->fmt.pix.colorspace  ={vid_format.fmt.pix.colorspace}")


def font_write(fb, x, y, string, color):
    for char in string:
        char_index = ord(char) & 0x7F
        for ry in range(7):
            for rx in range(5):
                v = (font5x7_basic[char_index - CHAR_OFFSET][rx] >> ry) & 1
                pos = (y + ry) * FRAME_WIDTH2 + (x + rx)
                if v:
                    fb[pos] = color


def raw2temperature(RAW):
    RAW *= 4
    RAWrefl = PlanckR1 / (PlanckR2 * (math.exp(PlanckB / (TempReflected + 273.15)) - PlanckF)) - PlanckO
    RAWobj = (RAW - (1 - Emissivity) * RAWrefl) / Emissivity
    return PlanckB / math.log(PlanckR1 / (PlanckR2 * (RAWobj + PlanckO)) + PlanckF) - 273.15


def startv4l2():
    pass  # Not implemented in Python


def vframe(ep, ep_error, r, actual_length, buf, colormap):
    pass  # Not implemented in Python


def find_lvr_flirusb():
    global devh
    devh = None
    context = libusb1.USBContext()
    for device in context.getDeviceIterator(skip_on_error=True):
        if device.getVendorID() == VENDOR_ID and device.getProductID() == PRODUCT_ID:
            devh = device.open()
            return 0 if devh else -libusb1.LIBUSB_ERROR_IO
    return -libusb1.LIBUSB_ERROR_IO


def usb_exit():
    global devh
    if devh:
        devh.reset()
        devh.close()
        devh = None


def usb_init():
    r = 0
    try:
        context = libusb1.USBContext()
        global devh
        devh = None
        devh = context.getByVendorIDAndProductID(VENDOR_ID, PRODUCT_ID)
        if not devh:
            return -1
        devh.setConfiguration(3)
        devh.claimInterface(0)
        devh.claimInterface(1)
        devh.claimInterface(2)
        return 0
    except USBError:
        usb_exit()
        return -1


def ep_loop(colormap):
    pass  # Not implemented in Python


def usage():
    print(
        "Usage:\n"
        "\n"
        "./flirone [option]* palletes/<palette.raw>\n"
        "\n"
        "Options:\n"
        "\t-i\tUse inverse pallete colors\n"
        "\t-p\tShow pallete colors instead of sensor data\n"
        "\t--pro\tSelect FLIR ONE PRO camera (default is FLIR ONE G3)\n"
        "\t-v <n>\tUse /dev/video<n> and /dev/video<n+1> devices (default is n=1)\n")
    sys.exit(1)


def main():
    global video_device1, video_device2, flirone_pro, pal_inverse, pal_colors
    global frame_width2, frame_height2, frame_owidth2, frame_oheight2

    # Parse arguments
    args = sys.argv[1:]
    if len(args) < 2:
        usage()

    n = 1
    palpath = None
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--pro":
            flirone_pro = True
            frame_width2 = 160
            frame_height2 = 128
            frame_owidth2 = 160
            frame_oheight2 = 120
        elif arg == "-v":
            i += 1
            n = int(args[i])
        elif arg == "-i":
            pal_inverse = True
        elif arg == "-p":
            pal_colors = True
        else:
            if palpath is not None:
                usage()
            palpath = arg
        i += 1

    if palpath is None:
        usage()

    video_device1 = f"/dev/video{n}"
    video_device2 = f"/dev/video{n + 1}"

    # Read palette
    with open(palpath, "rb") as fp:
        colormap = bytearray(fp.read(768))

    # Loop for EP
    while True:
        ep_loop(colormap)


if __name__ == "__main__":
    main()

