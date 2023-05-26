import sys
import fontforge
import util
import properties as const

if len(sys.argv) != 3:
    raise ValueError("Invalid argument")

FONT_FILE = sys.argv[1]
BUILD_FILE = sys.argv[2]


def main():
    font = fontforge.open(FONT_FILE)

    # Remove all lookups
    for lookup in font.gpos_lookups:
        font.removeLookup(lookup)
    for lookup in font.gsub_lookups:
        font.removeLookup(lookup)

    extract_icon_font(font)

    util.font_set_em(font, const.ASCENT, const.DESCENT, const.EM)
    util.font_resize_all_width(font, const.EM // 2)

    util.fix_all_glyph_points(font)
    util.font_into_file(font, BUILD_FILE)
    util.log(FONT_FILE, " -> ", BUILD_FILE)


def extract_icon_font(font):
    # Select only nerd icon fonts
    # https://github.com/ryanoasis/nerd-fonts/wiki/Glyph-Sets-and-Code-Points

    def selectMore(start, end=None):
        nonlocal font
        if end is None:
            font.selection.select(("more",), start)
        else:
            font.selection.select(("ranges", "more"), start, end)

    # Seti-UI + Custom
    selectMore(0xe5fa, 0xe6ac)

    # Devicons (https://vorillaz.github.io/devicons/)
    selectMore(0xe700, 0xe7c5)

    # Font Awesome (https://github.com/FortAwesome/Font-Awesome)
    selectMore(0xf000, 0xf2e0)

    # Font Awesome Extension (https://github.com/AndreLZGava/font-awesome-extension)
    selectMore(0xe200, 0xe2a9)

    # Material Design Icons (https://github.com/Templarian/MaterialDesign)
    selectMore(0xf0001, 0xf1af0)

    # Weather (https://github.com/erikflowers/weather-icons)
    selectMore(0xe300, 0xe3e3)

    # Octicons (https://github.com/primer/octicons)
    selectMore(0xf400, 0xf532)
    # selectMore(font, 0x2665)  # Use IBM Plex Sans JP glyph
    selectMore(0x26A1)

    # Powerline Symbols
    selectMore(0xe0a0, 0xe0a2)
    selectMore(0xe0b0, 0xe0b3)

    # Powerline Extra Symbols (https://github.com/ryanoasis/powerline-extra-symbols)
    selectMore(0xe0a3)
    selectMore(0xe0b4, 0xe0c8)
    selectMore(0xe0ca)
    selectMore(0xe0cc, 0xe0d4)

    # IEC Power Symbols (https://unicodepowersymbol.com/)
    selectMore(0x23fb, 0x23fe)
    selectMore(0x2b58)

    # Font Logos (https://github.com/Lukas-W/font-logos)
    selectMore(0xf300, 0xf32f)

    # Pomicons (https://github.com/gabrielelana/pomicons)
    selectMore(0xe000, 0xe00a)

    # Codicons (https://github.com/microsoft/vscode-codicons)
    selectMore(0xea60, 0xebeb)

    # Additional sets
    #  - Use Hack glyph
    # Heavy Angle Brackets (276c-2771)
    # Box Drawing (2500-259f)

    # Remove not selected
    font.selection.invert()
    font.clear()


if __name__ == "__main__":
    main()
