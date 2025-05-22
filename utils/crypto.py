# <=========================================================================>

#    ██████╗██████╗ ██╗   ██╗██████╗ ████████╗ ██████╗    ██████╗ ██╗   ██╗
#   ██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝██╔═══██╗   ██╔══██╗╚██╗ ██╔╝
#   ██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   ██║   ██║   ██████╔╝ ╚████╔╝
#   ██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   ██║   ██║   ██╔═══╝   ╚██╔╝
#   ╚██████╗██║  ██║   ██║   ██║        ██║   ╚██████╔╝██╗██║        ██║
#    ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝    ╚═════╝ ╚═╝╚═╝        ╚═╝

# <=========================================================================>
#                Module implementing cryptographic algorithms
# <=========================================================================>
#                        @Author: Stefano Bia Carrasco
# <=========================================================================>
#  XAE: eXtreme Advanced Encryption -> Custom AES variant
#  XWH: eXtreme Whirpool Hash -> Custom Whirpool variant
# <=========================================================================>
#  CONSTANTS
# <=========================================================================>
#  eXtreme Advanced Encryption parameters
# <=========================================================================>
XAE_ORDER: int = 4
XAE_ROUNDS: int = 14
# <=========================================================================>
#  eXtreme Whirpool Hash parameters
# <=========================================================================>
XWH_ORDER: int = 8
XWH_ROUNDS: int = 10
# <=========================================================================>
#  Byte constant used as modulo on galois field operations
# <=========================================================================>
XAE_GALOIS_BYTE: int = 0b00011011
# <=========================================================================>
XWH_GALOIS_BYTE: int = 0b00011101
# <=========================================================================>
#  Byte constant used as padding when padding is needed
# <=========================================================================>
PADDING_BYTE: int = 0x01
# <=========================================================================>
#  First bytes of the round constants used for key expansions
# <=========================================================================>
XAE_RCONST: tuple = (0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80)
# <=========================================================================>
XWH_RCONST: tuple = (0x18, 0x23, 0xC6, 0xE8, 0x87, 0xB8, 0x01, 0x4F)
# <=========================================================================>
#  Spread and fold matrices for un/mixing the columns of a matrix
# <=========================================================================>
XAE_SPREAD_MATRIX: tuple = (
    0x02, 0x03, 0x01, 0x01,
    0x01, 0x02, 0x03, 0x01,
    0x01, 0x01, 0x02, 0x03,
    0x03, 0x01, 0x01, 0x02
)
XAE_FOLD_MATRIX: tuple = (
    0x0E, 0x0B, 0x0D, 0x09,
    0x09, 0x0E, 0x0B, 0x0D,
    0x0D, 0x09, 0x0E, 0x0B,
    0x0B, 0x0D, 0x09, 0x0E
)
# <=========================================================================>
XWH_SPREAD_MATRIX: tuple = (
    0x01, 0x01, 0x04, 0x01, 0x08, 0x05, 0x02, 0x09,
    0x09, 0x01, 0x01, 0x04, 0x01, 0x08, 0x05, 0x02,
    0x02, 0x09, 0x01, 0x01, 0x04, 0x01, 0x08, 0x05,
    0x05, 0x02, 0x09, 0x01, 0x01, 0x04, 0x01, 0x08,
    0x08, 0x05, 0x02, 0x09, 0x01, 0x01, 0x04, 0x01,
    0x01, 0x08, 0x05, 0x02, 0x09, 0x01, 0x01, 0x04,
    0x04, 0x01, 0x08, 0x05, 0x02, 0x09, 0x01, 0x01,
    0x01, 0x04, 0x01, 0x08, 0x05, 0x02, 0x09, 0x01
)
# <=========================================================================>
#  Initialization vectors for the cryptographic algorithms
# <=========================================================================>
XWH_IV: tuple = (
    0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
    0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F,
    0x00, 0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70,
    0x80, 0x90, 0xA0, 0xB0, 0xC0, 0xD0, 0xE0, 0xF0,
    0x00, 0x1F, 0x2E, 0x3D, 0x4C, 0x5B, 0x6A, 0x79,
    0x88, 0x97, 0xA6, 0xB5, 0xC4, 0xD3, 0xE2, 0xF1,
    0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
    0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF
)
# <=========================================================================>
#  Substitution boxes for the cryptographic algorithms
# <=========================================================================>
XAE_SBOX: tuple = (
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16
)
XAE_INV_SBOX: tuple = (
    0x52, 0x09, 0x6A, 0xD5, 0x30, 0x36, 0xA5, 0x38, 0xBF, 0x40, 0xA3, 0x9E, 0x81, 0xF3, 0xD7, 0xFB,
    0x7C, 0xE3, 0x39, 0x82, 0x9B, 0x2F, 0xFF, 0x87, 0x34, 0x8E, 0x43, 0x44, 0xC4, 0xDE, 0xE9, 0xCB,
    0x54, 0x7B, 0x94, 0x32, 0xA6, 0xC2, 0x23, 0x3D, 0xEE, 0x4C, 0x95, 0x0B, 0x42, 0xFA, 0xC3, 0x4E,
    0x08, 0x2E, 0xA1, 0x66, 0x28, 0xD9, 0x24, 0xB2, 0x76, 0x5B, 0xA2, 0x49, 0x6D, 0x8B, 0xD1, 0x25,
    0x72, 0xF8, 0xF6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xD4, 0xA4, 0x5C, 0xCC, 0x5D, 0x65, 0xB6, 0x92,
    0x6C, 0x70, 0x48, 0x50, 0xFD, 0xED, 0xB9, 0xDA, 0x5E, 0x15, 0x46, 0x57, 0xA7, 0x8D, 0x9D, 0x84,
    0x90, 0xD8, 0xAB, 0x00, 0x8C, 0xBC, 0xD3, 0x0A, 0xF7, 0xE4, 0x58, 0x05, 0xB8, 0xB3, 0x45, 0x06,
    0xD0, 0x2C, 0x1E, 0x8F, 0xCA, 0x3F, 0x0F, 0x02, 0xC1, 0xAF, 0xBD, 0x03, 0x01, 0x13, 0x8A, 0x6B,
    0x3A, 0x91, 0x11, 0x41, 0x4F, 0x67, 0xDC, 0xEA, 0x97, 0xF2, 0xCF, 0xCE, 0xF0, 0xB4, 0xE6, 0x73,
    0x96, 0xAC, 0x74, 0x22, 0xE7, 0xAD, 0x35, 0x85, 0xE2, 0xF9, 0x37, 0xE8, 0x1C, 0x75, 0xDF, 0x6E,
    0x47, 0xF1, 0x1A, 0x71, 0x1D, 0x29, 0xC5, 0x89, 0x6F, 0xB7, 0x62, 0x0E, 0xAA, 0x18, 0xBE, 0x1B,
    0xFC, 0x56, 0x3E, 0x4B, 0xC6, 0xD2, 0x79, 0x20, 0x9A, 0xDB, 0xC0, 0xFE, 0x78, 0xCD, 0x5A, 0xF4,
    0x1F, 0xDD, 0xA8, 0x33, 0x88, 0x07, 0xC7, 0x31, 0xB1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xEC, 0x5F,
    0x60, 0x51, 0x7F, 0xA9, 0x19, 0xB5, 0x4A, 0x0D, 0x2D, 0xE5, 0x7A, 0x9F, 0x93, 0xC9, 0x9C, 0xEF,
    0xA0, 0xE0, 0x3B, 0x4D, 0xAE, 0x2A, 0xF5, 0xB0, 0xC8, 0xEB, 0xBB, 0x3C, 0x83, 0x53, 0x99, 0x61,
    0x17, 0x2B, 0x04, 0x7E, 0xBA, 0x77, 0xD6, 0x26, 0xE1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0C, 0x7D
)
# <=========================================================================>
XWH_SBOX: tuple = (
    0x18, 0x23, 0xC6, 0xE8, 0x87, 0xB8, 0x01, 0x4F, 0x36, 0xA6, 0xD2, 0xF5, 0x79, 0x6F, 0x91, 0x52,
    0x60, 0xBC, 0x0B, 0x8E, 0xA3, 0x0C, 0x7B, 0x35, 0x1D, 0xE0, 0xD7, 0xC2, 0x2E, 0x4B, 0xFE, 0x57,
    0x15, 0x77, 0x37, 0xE5, 0x9F, 0xF0, 0x4A, 0xCA, 0x58, 0xC9, 0x29, 0x0A, 0xB1, 0xA0, 0x6B, 0x85,
    0xBD, 0x5D, 0x10, 0xF4, 0xCB, 0x3E, 0x05, 0x67, 0xE4, 0x27, 0x41, 0x8B, 0xA7, 0x7D, 0x95, 0xC8,
    0xFB, 0xEE, 0x7C, 0x66, 0xDD, 0x17, 0x47, 0x9E, 0xCA, 0x2D, 0xBF, 0x07, 0xAD, 0x5A, 0x83, 0x33,
    0x63, 0x02, 0xAA, 0x71, 0xC8, 0x19, 0x49, 0xC9, 0xF2, 0xE3, 0x5B, 0x88, 0x9A, 0x26, 0x32, 0xB0,
    0xE9, 0x0F, 0xD5, 0x80, 0xBE, 0xCD, 0x34, 0x48, 0xFF, 0x7A, 0x90, 0x5F, 0x20, 0x68, 0x1A, 0xAE,
    0xB4, 0x54, 0x93, 0x22, 0x64, 0xF1, 0x73, 0x12, 0x40, 0x08, 0xC3, 0xEC, 0xDB, 0xA1, 0x8D, 0x3D,
    0x97, 0x00, 0xCF, 0x2B, 0x76, 0x82, 0xD6, 0x1B, 0xB5, 0xAF, 0x6A, 0x50, 0x45, 0xF3, 0x30, 0xEF,
    0x3F, 0x55, 0xA2, 0xEA, 0x65, 0xBA, 0x2F, 0xC0, 0xDE, 0x1C, 0xFD, 0x4D, 0x92, 0x75, 0x06, 0x8A,
    0xB2, 0xE6, 0x0E, 0x1F, 0x62, 0xD4, 0xA8, 0x96, 0xF9, 0xC5, 0x25, 0x59, 0x84, 0x72, 0x39, 0x4C,
    0x5E, 0x78, 0x38, 0x8C, 0xC1, 0xA5, 0xE2, 0x61, 0xB3, 0x21, 0x9C, 0x1E, 0x43, 0xC7, 0xFC, 0x04,
    0x51, 0x99, 0x6D, 0x0D, 0xFA, 0xDF, 0x7E, 0x24, 0x3B, 0xAB, 0xCE, 0x11, 0x8F, 0x4E, 0xB7, 0xEB,
    0x3C, 0x81, 0x94, 0xF7, 0xB9, 0x13, 0x2C, 0xD3, 0xE7, 0x6E, 0xC4, 0x03, 0x56, 0x44, 0x7F, 0xA9,
    0x2A, 0xBB, 0xC1, 0x53, 0xDC, 0x0B, 0x9D, 0x6C, 0x31, 0x74, 0xF6, 0x46, 0xAC, 0x89, 0x14, 0xE1,
    0x16, 0x3A, 0x69, 0x09, 0x70, 0xB6, 0xC0, 0xED, 0xCC, 0x42, 0x98, 0xA4, 0x28, 0x5C, 0xF8, 0x86
)
# <=========================================================================>
#  ATOMIC FUNCTIONS
# <=========================================================================>
def sub_bytes(s: list, sx: list | tuple) -> list:
    """
    Substitute bytes of a list

    :param s: List of bytes to be substituted
    :param sx: Substitution box defining the substitution for each possible byte value
    :return: The passed list (s) with each byte substituted according to (sx) substitution box
    """
    for i in range(len(s)):
        s[i] = sx[s[i]]
    return s
# <=========================================================================>
def shift_row(s: list, i: int = 1, dx: int = 1) -> list:
    """
    Shift elements of a list

    :param s: List to be shifted
    :param i: The number of positions to shift the list => (1)
    :param dx: The direction of the shift [1, -1] => (1)
    :return: The passed list (s) with the elements shifted by (i) positions in (dx) direction
    """
    i = i*dx
    s = s[i:] + s[:i]
    return s
# <=========================================================================>
def shift_rows(s: list, dx: int = 1) -> list:
    """
    Shift rows of a matrix by row index (0..R) positions

    :param s: Matrix to be shifted [Square matrix]
    :param dx: The direction of the shift [1, -1] => (1)
    :return: The passed matrix (s) with the elements shifted by row index (0..R) positions in (dx) direction
    """
    ox, si, se = int(len(s)**(1/2)), 0, 0
    for i in range(ox):
        si, se = i*ox, (i+1)*ox
        s[si:se] = shift_row(s[si:se], i, dx)
    return s
# <=========================================================================>
def galois_mult(ax: int, bx: int, mx: int) -> int:
    """
    Multiply two elements in the Galois field GF(2^8)

    :param ax: First element to be multiplied [0, 255]
    :param bx: Second element to be multiplied [0, 255]
    :param mx: Modulo element to use
    :return: The product of (ax) and (bx) in GF(2^8) [0, 255]
    """
    sx = 0
    for _ in range(8):
        if ((bx & 0b00000001) == 1):
            sx ^= ax
        if ((ax & 0b10000000) == 128):
            ax = (ax << 1) ^ mx
        else:
            ax <<= 1
        bx >>= 1
    return (sx % 256)
# <=========================================================================>
def mix_columns(s: list, mx: list | tuple, gx: int) -> list:
    """
    Mix the columns of a matrix using a matrix

    :param s: Matrix to mix columns of [Square matrix]
    :param mx: Matrix to mix columns with [Square matrix]
    :param gx: Galois modulo to use in galois multiplication
    :return: The passed matrix (s) with the columns mixed
    """
    ox, si = int(len(s)**(1/2)), 0
    cx = [0 for _ in range(ox)]
    for i in range(ox):
        for ix in range(ox):
            cx[ix] = s[(ox*ix)+i]
        for ix in range(ox):
            si = (ox*ix)+i
            s[si] = 0x00
            for ixx in range(ox):
                s[si] ^= galois_mult(mx[(si-i)+ixx], cx[ix], gx)
    return s
# <=========================================================================>
def rconst(i: int, rx: list | tuple) -> tuple:
    """
    Generate the round constant for the given round index

    The round constant is a four-byte word constant made from one constant byte per round index and three null bytes

    :param i: Round index to return the constant for [1..10]
    :param rx: Round constant first byte list to use
    :return: The round constant that matches the round index (i)
    """
    return (rx[i-1], 0, 0, 0, 0, 0, 0, 0)
# <=========================================================================>
def add_rows(ax: list, bx: list | tuple) -> list:
    """
    Add two lists with elements in the Galois field GF(2^8)

    :param ax: First list to be added [SizeOf (bx)]
    :param bx: Second list to be added [SizeOf (ax)]
    :return: The passed list (ax) with (bx) added
    """
    for i in range(len(ax)):
        ax[i] ^= bx[i]
    return ax
# <=========================================================================>
def add_asym(ax: list, bx: list | tuple) -> list:
    """
    Add two lists with different lengths and elements in the Galois field GF(2^8)

    :param ax: First list to be added [SizeOf (bx)]
    :param bx: Second list to be added [SizeOf (ax)]
    :return: The passed list (ax) with (bx) added
    """
    for i in range(min(len(ax), len(bx))):
        ax[i] ^= bx[i]
    return ax
# <=========================================================================>
def expand_key(s: list, ox: int, rx: int) -> tuple:
    """
    Expand key generating multiple key schedules from the original key

    :param s: List representing the original key to be expanded
    :param ox: Order of the matrix to which the key will be applied
    :param rx: Number of rounds the key will be expanded for
    :return: The passed list (s) as a tuple, now representing the expanded key
    """
    ws, si = len(s)//ox, 0
    ms = ws // 2
    for i in range(ws, (rx+1)*ox):
        s += s[-ox::]
        si = ox*(i-ws)
        match (i % ws):
            case 0:
                s[-ox::] = add_rows(
                    sub_bytes(
                        shift_row(s[-ox::]),
                        XAE_SBOX
                    ), rconst(i//ws, XAE_RCONST)
                )
            case ms:
                s[-ox::] = sub_bytes(s[-ox::], XAE_SBOX)
        s[-ox::] = add_rows(s[-ox::], s[si:si+ox])
    return tuple(s)
# <=========================================================================>
def expand_skey(s: list, ox: int, rx: int) -> tuple:
    """
    Expand key generating one key schedule

    :param s: List representing the initial key to be expanded
    :param ox: Order of the matrix to which the key will be applied
    :param rx: Number of rounds the key will be expanded for
    :return: The passed list (s) as a tuple, now representing the expanded key schedule
    """
    sx, si, se, sf = ox**2, 0, 0, 0
    for i in range(rx):
        si, se, sf = i*sx, (i+1)*sx, (i+2)*sx
        s += s[si:se]
        s[se:sf] = sub_bytes(s[se:sf], XWH_SBOX)
        s[se:sf] = shift_rows(s[se:sf], 1)
        s[se:sf] = mix_columns(s[se:sf], XWH_SPREAD_MATRIX, XWH_GALOIS_BYTE)
        s[se:sf] = add_asym(s[se:sf], XWH_RCONST)
    return tuple(s)
# <=========================================================================>
#  MOLECULAR FUNCTIONS
# <=========================================================================>
def xae_round(s: list, rx: list | tuple) -> list:
    """
    Perform a single round of the XAE encryption algorithm

    :param s: State matrix to be transformed [4x4]
    :param rx: Round key to be added to the state [256bit]
    :return: The passed state (s) after the transformations
    """
    sub_bytes(s, XAE_SBOX)
    shift_rows(s, 1)
    mix_columns(s, XAE_SPREAD_MATRIX, XAE_GALOIS_BYTE)
    return add_rows(s, rx)
# <=========================================================================>
def xae_inv_round(s: list, rx: list | tuple) -> list:
    """
    Perform a single round of the XAE decryption algorithm

    :param s: State matrix to be transformed [4x4]
    :param rx: Round key to be added to the state [256bit]
    :return: The passed state (s) after the transformations
    """
    add_rows(s, rx)
    mix_columns(s, XAE_FOLD_MATRIX, XAE_GALOIS_BYTE)
    shift_rows(s, -1)
    return sub_bytes(s, XAE_INV_SBOX)
# <=========================================================================>
def xwh_round(s: list, rx: list | tuple) -> list:
    """
    Perform a single round of the XWH hash algorithm

    :param s: State matrix to be transformed [8x8]
    :param rx: Round key to be added to the state [512bit]
    :return: The passed state (s) after the transformations
    """
    sub_bytes(s, XWH_SBOX)
    shift_rows(s, 1)
    mix_columns(s, XWH_SPREAD_MATRIX, XWH_GALOIS_BYTE)
    return add_rows(s, rx)
# <=========================================================================>
#  CRYPTOGRAPHIC FUNCTIONS
# <=========================================================================>
def encrypt(s: list, k: list) -> list:
    """
    Encrypt a string with a key using XAE

    :param s: Input list to encrypt [bytearray]
    :param k: Symmetric key used for encryption [256bit]
    :return: The encrypted input as a list [bytearray]
    """
    si, xi, se, xe = 0, 0, 0, 0
    ox, sx, rx = XAE_ORDER, XAE_ORDER**2, XAE_ROUNDS
    l = pad_bytes(s, ox)
    k = expand_key(k, ox, rx)
    for i in range(len(s)//sx):
        si, se = i*sx, (i+1)*sx
        for ii in range(rx+1):
            xi, xe = ii*sx, (ii+1)*sx
            s[si:se] = xae_round(s[si:se], k[xi:xe])
    s.append(l)
    return s
# <=========================================================================>
def decrypt(s: list, k: list) -> list:
    """
    Decrypt a list of bytes with a key using XAE

    :param s: Input list to decrypt [bytearray]
    :param k: Symmetric key used for decryption [256bit]
    :return: The decrypted input as a list [bytearray]
    """
    si, xi, se, xe = 0, 0, 0, 0
    ox, sx, rx = XAE_ORDER, XAE_ORDER**2, XAE_ROUNDS
    l = s.pop()
    k = expand_key(k, ox, rx)
    for i in range(len(s)//sx):
        si, se = i*sx, (i+1)*sx
        for ii in range(rx+1):
            xi, xe = (rx-ii)*sx, (rx-ii+1)*sx
            s[si:se] = xae_inv_round(s[si:se], k[xi:xe])
    return s[:-l]
# <=========================================================================>
def hash(s: list | tuple) -> list:
    """
    Hash a list of bytes using XWH

    :param s: Input list to hash [bytearray]
    :return: The hashed input as a list [bytearray]
    """
    sa, si, xi, se, xe = 0, 0, 0, 0, 0
    ox, sx, rx, cx = XWH_ORDER, XWH_ORDER**2, XWH_ROUNDS, []
    s = bytearray(XWH_IV) + str_to_bytes(str(len(s))) + bytearray(s)
    pad_bytes(s, ox)
    for i in range(1, (len(s)//sx)+1):
        sa, si, se = (i-1)*sx, i*sx, (i+1)*sx
        k = expand_skey(s[sa:si], ox, rx)
        cx = s[si:se]
        for ii in range(rx+1):
            xi, xe = ii*sx, (ii+1)*sx
            cx = xwh_round(cx, k[xi:xe])
        s[si:se] = add_rows(add_rows(s[si:se], s[sa:si]), cx)
    return s[-sx:]
# <=========================================================================>
def halve_hash(s: list | tuple) -> list:
    """
    Halve a hash length

    Takes a the list of bytes of a hash, splits it in half,
    and applies a XOR operation with both halves.

    :param s: List of bytes to be processed
    :return: List of bytes string representing the result of halving the hash
    """
    return add_rows(s[:(len(s)//2)], s[(len(s)//2):])
# <=========================================================================>
def pw_hash(s: list | tuple, ix: int) -> list:
    """
    Hash a list of bytes multiple times

    This function takes a list of bytes and hashes it a specified number of times.
    Each iteration uses the result of the previous hash as the input for the next hash.

    :param s: List of bytes to be hashed
    :param ix: Number of times to apply the hash function
    :return: Final hashed list of bytes after the specified number of iterations
    """
    for _ in range(ix):
        s = hash(s)
    return s
# <=========================================================================>
#  CRYPTOGRAPHIC WRAPPER FUNCTIONS
# <=========================================================================>
def encrypt_str(s: str, k: str) -> str:
    """
    Encrypt a string with a key using XAE

    :param s: Input string to encrypt [str]
    :param k: Symmetric key used for encryption [hex64 -> str]
    :return: The encrypted input as a string [hex -> str]
    """
    return bytes_to_hex(
        encrypt(
            str_to_bytes(s),
            hex_to_bytes(k)
        )
    )
# <=========================================================================>
def decrypt_str(s: str, k: str) -> str:
    """
    Decrypt a string with a key using XAE

    :param s: Input string to decrypt [hex -> str]
    :param k: Symmetric key used for decryption [hex64 -> str]
    :return: The decrypted input as a string [str]
    """
    return bytes_to_str(
        decrypt(
            hex_to_bytes(s),
            hex_to_bytes(k)
        )
    )
# <=========================================================================>
def hash_str(s: str) -> str:
    """
    Hash a string using XWH

    :param s: Input string to hash [str]
    :return: The hashed input as a string [hex -> str]
    """
    return bytes_to_hex(
        hash(
            str_to_bytes(s)
        )
    )
# <=========================================================================>
def halve_hash_str(s: str) -> str:
    """
    Halve a hash length

    Takes a the hex string representation of a hash, converts it to bytes,
    splits it in half, and applies a XOR operation with both halves.
    Finally, it returns the result as a hex string.

    :param s: Hexadecimal string to be processed [hex -> str]
    :return: Hexadecimal string representing the result of halving the hash [hex -> str]
    """
    return bytes_to_hex(
        halve_hash(
            hex_to_bytes(s)
        )
    )
# <=========================================================================>
def pw_hash_str(s: str, ix: int) -> str:
    """
    Hash a string multiple times

    This function takes a string and hashes it a specified number of times.
    Each iteration uses the result of the previous hash as the input for the next hash.

    :param s: String to be hashed [str]
    :param ix: Number of times to apply the hash function [int]
    :return: Final hashed value after the specified number of iterations [hex -> str]
    """
    return bytes_to_hex(
        pw_hash(
            str_to_bytes(s), ix
        )
    )
# <=========================================================================>
#  DATA UTILS
# <=========================================================================>
def pad_bytes(bx: list, ox: int) -> int:
    """
    Pad a byte array until its length is a multiple of a given matrix order

    :param bx: Byte array to be padded
    :param ox: Order to which the byte array should be padded
    :return: The number of padding bytes added to the byte array
    """
    ox **= 2
    px, lx = PADDING_BYTE, len(bx)
    for n in bx:
        px ^= n
    for i in range(ox - (lx % ox)):
        bx.append(px)
    return (len(bx) - lx)
# <=========================================================================>
def bytes_to_hex(cx: list | tuple) -> str:
    """
    Convert a byte array to a hexadecimal string representation

    :param cx: Byte array to be converted to a hexadecimal string
    :return: Hexadecimal string representing the byte array (cx)
    """
    hx = []
    for n in cx:
        hx.append(f'{n:0>2X}')
    return "".join(hx)
# <=========================================================================>
def hex_to_bytes(cx: str) -> list:
    """
    Convert a hexadecimal string to a byte array representation

    :param cx: Hexadecimal string to be converted to byte array
    :return: Byte array representing the hexadecimal string (cx)
    """
    bx = bytearray(len(cx)//2)
    for i in range(0, len(cx), 2):
        bx[i//2] = (int(cx[i:i+2], 16))
    return bx
# <=========================================================================>
def str_to_bytes(cx: str, enc: str = 'UTF-8') -> list:
    """
    Convert a string to a list of bytes

    :param cx: String to be converted to bytes
    :param enc: Encoding to use => ('UTF-8')
    :return: List of bytes representing the string (cx)
    """
    return bytearray(cx.encode(enc))
# <=========================================================================>
def bytes_to_str(cx: list | tuple, enc: str = 'UTF-8') -> str:
    """
    Convert a list of bytes to a string

    :param cx: List of bytes to be converted to string
    :param enc: Encoding to use => ('UTF-8')
    :return: String representing the list of bytes (cx)
    """
    return cx.decode(enc)
# <=========================================================================>
#  TESTS
# <=========================================================================>
def tests() -> None:
    """
    Run a series of tests for cryptographic functions

    This function evaluates the correctness of several transformation and cryptographic
    functions through assertions. It checks the following properties:

    - Substitution operation using predefined S-boxes (sub_bytes)
    - Inversion of row shifting operation (shift_rows)
    - Inversion of column mixing operation (mix_columns)
    - Inversion of row addition operation (add_rows)
    - Inversion between encryption and decryption operations (de/encrypt)
    - Determinism of encryption and decryption operations (de/encrypt)
    - Correctness of hash operation (hash)
    - Determinism of hash operation (hash)
    - Correctness of power hash operation (pw_hash)
    - Determinism of power hash operation (pw_hash)

    The tests use predefined input values and check that the transformations return the expected results.
    If an assertion fails, it indicates a discrepancy in the implementation of the functions being tested.
    """

    # Check for equality in iterables
    def list_eq(ax: list | tuple | bytearray, bx: list | tuple | bytearray) -> bool:
        ax, bx = list(ax), list(bx)
        return ((len(ax) == len(bx)) and (ax == bx))

    # Test constants
    tx = str_to_bytes('TestsPassed')
    sx = (1, 2, 3, 4, 5, 6,7 ,8, 9, 10, 11, 12, 13, 14, 15, 16)
    hx = hex_to_bytes('F16C66ECDEC5B3CE6F4734576D146BD5948368733B715E57F6762433AAC89CB17B6BF7D1D383DEFF8EEA868FD0F5658464816B023F52878D36CF2D20CBC3CFE4')
    h5x = hex_to_bytes('265BF37FFD201D5BACA2F1DC58BA3F5183A4B4490F636482BED7C9CD157CB00E0000875F3AD5F43504F8E95A27861E0A0CADAB903E546012E40A62F0A89167DD')
    kx = (0x60, 0x3e, 0xeb, 0x10, 0x15, 0xca, 0x71, 0xbe, 0x2b, 0x73, 0xae, 0xf0, 0x85, 0x7d, 0x77, 0x81, 0x1f, 0x35, 0x2c, 0x07, 0x3b, 0x61, 0x08, 0xd7, 0x2d, 0x98, 0x10, 0xa3, 0x09, 0x14, 0xdf, 0xf4)

    # Sub_bytes inversion test
    assert list_eq(
        sx,
        sub_bytes(
            sub_bytes(list(sx), XAE_SBOX),
            XAE_INV_SBOX
        )
    )

    # Shift_rows inversion test
    assert list_eq(
        sx,
        shift_rows(
            shift_rows(list(sx), 1),
            -1
        )
    )

    # Mix_columns inversion test
    assert list_eq(
        sx,
        mix_columns(
            mix_columns(list(sx), XAE_SPREAD_MATRIX, XAE_GALOIS_BYTE),
            XAE_FOLD_MATRIX,
            XAE_GALOIS_BYTE
        )
    )

    # Add_rows inversion test
    assert list_eq(
        sx,
        add_rows(
            add_rows(list(sx), kx),
            kx
        )
    )

    # Encryption inversion test
    assert list_eq(
        tx,
        decrypt(
            encrypt(list(tx), list(kx)),
            list(kx)
        )
    )

    # Encryption determinism test
    assert list_eq(
        encrypt(list(tx), list(kx)),
        encrypt(list(tx), list(kx))
    )

    # Decryption determinism test
    assert list_eq(
        decrypt(list(tx), list(kx)),
        decrypt(list(tx), list(kx))
    )

    # Hash correctness test
    assert list_eq(hx, hash(list(tx)))

    # Hash determinism test
    assert list_eq(hash(list(tx)), hash(list(tx)))

    # Power hash correctness test
    assert list_eq(h5x, pw_hash(list(tx), 5))

    # Power hash determinism test
    assert list_eq(pw_hash(list(tx), 5), pw_hash(list(tx), 5))
# <=========================================================================>
#  SCRIPT EXECUTION
# <=========================================================================>
# If executing as a script
# <=========================================================================>
if (__name__ == '__main__'):
    tests()
# <=========================================================================>
