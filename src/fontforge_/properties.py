from typing import Final, Literal, TypedDict


class StyleProperty(TypedDict):
    weight: Literal['Book', 'Bold']
    os2_weight: int
    os2_stylemap: int
    panose_weight: int
    panose_letterform: int


class StylePropertyAll(TypedDict):
    Regular: StyleProperty
    Bold: StyleProperty
    Italic: StyleProperty
    BoldItalic: StyleProperty


FAMILY = "PleckJP"
VERSION = "1.1.0"
ENCODING = 'UnicodeFull'

COPYRIGHT = "\n".join([
    "[Hack]",
    "Copyright (c) 2018 Source Foundry Authors",
    "",
    "[IBM Plex]",
    "Copyright © 2017 IBM Corp.",
    "",
    "[Nerd Fonts]",
    "Copyright (c) 2014, Ryan L McIntyre",
    "",
    "[PleckJP]",
    "Copyright (c) 2023 ryota2357",
])

ASCENT = 1618
DESCENT = 430
EM = ASCENT + DESCENT
ITALICANGLE = -11
UNDERLINE_POS = -255
UNDERLINE_HEIGHT = 90

STYLE_PROPERTY: Final[StylePropertyAll] = {
    'Regular': {
        'weight': 'Book',
        'os2_weight': 400,
        'os2_stylemap': 64,      # Regular
        'panose_weight': 5,      # 5-Book
        'panose_letterform': 2,  # 2-Normal/Contact
    },
    'Bold': {
        'weight': 'Bold',
        'os2_weight': 700,
        'os2_stylemap': 32,      # Bold
        'panose_weight': 8,      # 8-Bold
        'panose_letterform': 2,  # 2-Normal/Contact
    },
    'Italic': {
        'weight': 'Book',
        'os2_weight': 400,
        'os2_stylemap': 1,       # Italic
        'panose_weight': 5,      # 5-Book
        'panose_letterform': 9,  # 9-Oblique/Contact
    },
    'BoldItalic': {
        'weight': 'Bold',
        'os2_weight': 700,
        'os2_stylemap': 33,      # BoldItalic
        'panose_weight': 8,      # 8-Bold
        'panose_letterform': 9,  # 9-Oblique/Contact
    },
}
