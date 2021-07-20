import asyncio
import crcmod.predefined
from bleak import BleakClient
import sys
import argparse

crc = crcmod.predefined.mkCrcFun("crc-8")

char = "0000ae01-0000-1000-8000-00805f9b34fb"

good_function = lambda x: int(f"{bin(x)[2:]:0>8}"[::-1], 2)


def make_command(cmd, payload):
    assert 0 < len(payload) < 0x100

    msg = bytearray([0x51, 0x78, cmd, 0x00, len(payload), 0x00])
    msg += payload
    msg.append(crc(payload))
    msg.append(0xFF)

    return bytes(msg)


async def run():
    im = sys.stdin.buffer.read()
    assert im[0:3] == b"P4\n", f"stdin was not a P4 PBM file, first 3 bytes: {im[0:3]}"
    im = im[3:]
    while im[0] == b"#"[0]:
        print("skipping")
        im = im[(im.index(b"\n") + 1) :]
    w, h = map(int, im[: (im.index(b"\n"))].decode("ascii").split(" "))
    assert w == 384, f"input image's width was {w}, expected 384"
    im = im[(im.index(b"\n") + 1) :]
    assert (
        len(im) == 48 * h
    ), f"input PBM file was a weird length, expected w*h/8 = {48*h}, got {len(im)}"

    buf = bytearray()

    for i in range(h):
        buf += make_command(
            0xA2, bytes(map(good_function, im[(i * 48) : ((i + 1) * 48)]))
        )

    if args.feed_after > 0:
        buf += make_command(
            0xA1, bytes([args.feed_after % 256, args.feed_after // 256])
        )

    print("Connecting... ", end="", flush=True)
    async with BleakClient(args.bdaddr) as client:
        print("Connected.", flush=True)
        print("Sending", end="", flush=True)

        mtu = args.mtu

        while len(buf) > mtu:
            await client.write_gatt_char(char, buf[0:mtu], True)
            buf = buf[mtu:]
            print(".", end="", flush=True)

        if len(buf) > 0:
            await client.write_gatt_char(char, buf, True)
            print(".", end="", flush=True)
        print(" Sent.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Print a P4 PBM file from stdin to a Cat Printer"
    )
    parser.add_argument("bdaddr", help="The bluetooth address of the printer")
    parser.add_argument(
        "--mtu",
        type=int,
        metavar="BYTES",
        default=200,
        help="The ATT MTU size: increase for speed, decrease if errors",
    )
    parser.add_argument(
        "--feed-after",
        type=int,
        metavar="N",
        default=128,
        help="Blank lines to print after the image",
    )

    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
