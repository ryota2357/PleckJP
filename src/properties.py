FAMILY = "PleckJP"
VERSION = "0.3.0"
ENCODING = 'UnicodeFull'

COPYRIGHT = "\n".join([
    "[PleckJP]",
    "Copyright (c) 2023 ryota2357",
    "",
    "[IBM Plex]",
    "Copyright © 2017 IBM Corp.",
    "",
    "[Hack]",
    "Copyright (c) 2018 Source Foundry Authors",
    "",
    "[Nerd Fonts]",
    "opyright (c) 2014, Ryan L McIntyre",
])

ASCENT = 1618
DESCENT = 430
EM = ASCENT + DESCENT
ITALICANGLE = -11
UNDERLINE_POS = -255
UNDERLINE_HEIGHT = 90

STYLE_PROPERTY = {
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
