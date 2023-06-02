import sys
from os.path import join, basename, splitext
import fontforge
import psMat
import util
import properties as P

if len(sys.argv) != 3:
    raise ValueError("Invalid argument")

GLYPHS_PATH = sys.argv[1]
BUILD_FILE = sys.argv[2]

#  {
#      path: string
#          Path to the ttf/otf files.
#      ranges: list<(int, int)>
#          Locations in nerd font.
#      remaps: list<(int, int)>
#          Locations of source font.
#          If glyph is not found in some codepoint and len(ranges[i]) > len(remaps[i]), it will be skipped.
#          This list length must be same as `ranges`, so if you want to use same codepoint as `ranges` you should specify `None`.
#      scale: (float, float)
#          Scale to (x, y) before merging.
#      translate: (int, int)
#          Translate to (x, y) before merging.
#  }
SOURCES_INFO = [
    {   # Seti-UI + Custom
        "path": join(GLYPHS_PATH, "original-source.otf"),
        "ranges": [(0xe5fa, 0xe6ff)],
        "remaps": [(0xe4fa, 0xe5ff)],
        "scale": (1, 1),
        "translate": (0, 0)
    },
    {   # Devicons (https://vorillaz.github.io/devicons/)
        "path": join(GLYPHS_PATH, "devicons.ttf"),
        "ranges": [(0xe700, 0xe7c5)],
        "remaps": [(0xe600, 0xe6c5)],
        "scale": (1, 1),
        "translate": (0, 0)
    },
    {   # Font Awesome (https://github.com/FortAwesome/Font-Awesome)
        "path": join(GLYPHS_PATH, "font-awesome", "FontAwesome.otf"),
        "ranges": [(0xf000, 0xf2e0)],
        "remaps": [None],
        "scale": (1, 1),
        "translate": (0, 0)
    },
    {   # Font Awesome Extension (https://github.com/AndreLZGava/font-awesome-extension)
        "path": join(GLYPHS_PATH, "font-awesome-extension.ttf"),
        "ranges": [(0xe200, 0xe2a9)],
        "remaps": [(0xe000, 0xe0a9)],
        "scale": (1, 1),
        "translate": (0, 0)
    },
    {   # Material Design Icons (https://github.com/Templarian/MaterialDesign)
        "path": join(GLYPHS_PATH, "materialdesign", "MaterialDesignIconsDesktop.ttf"),
        "ranges": [(0xf0001, 0xf1af0)],
        "remaps": [None],
        "scale": (1, 1),
        "translate": (0, 0)
    },
    {   # Weather (https://github.com/erikflowers/weather-icons)
        "path": join(GLYPHS_PATH, "weather-icons", "weathericons-regular-webfont.ttf"),
        "ranges": [(0xe300, 0xe3e3)],
        "remaps": [(0xf000, 0xf0eb)],
        "scale": (1, 1),
        "translate": (0, 0)
    },
    {   # Octicons (https://github.com/primer/octicons)
        "path": join(GLYPHS_PATH, "octicons", "octicons.ttf"),
        "ranges": [(0xf400, 0xf532), (0x2665,), (0x26a1,)],
        "remaps": [(0xf000, 0xf305), None, None],
        "scale": (1, 1),
        "translate": (0, 0),
    },
    {   # Powerline Symbols
        "path": join(GLYPHS_PATH, "powerline-symbols", "PowerlineSymbols.otf"),
        "ranges": [(0xe0a0, 0xe0a2), (0xe0b0, 0xe0b3)],
        "remaps": [None, None],
        "scale": (1, 1),
        "translate": (0, 0)
    },
    {   # Powerline Extra Symbols (https://github.com/ryanoasis/powerline-extra-symbols)
        "path": join(GLYPHS_PATH, "PowerlineExtraSymbols.otf"),
        "ranges": [(0xe0a3,), (0xe0b4, 0xe0c8), (0xe0ca,), (0xe0cc, 0xe0d4)],  # 最後の間違ってそう
        "remaps": [None, None, None, None],
        "scale": (1, 1),
        "translate": (0, 0)
    },
    {   # IEC Power Symbols (https://unicodepowersymbol.com/)
        "path": join(GLYPHS_PATH, "Unicode_IEC_symbol_font.otf"),
        "ranges": [(0x23fb, 0x23fe), (0x2b58,)],
        "remaps": [None, None],
        "scale": (1, 1),
        "translate": (0, 0)
    },
    {   # Font Logos (https://github.com/Lukas-W/font-logos)
        "path": join(GLYPHS_PATH, "font-logos.ttf"),
        "ranges": [(0xf300, 0xf32f)],
        "remaps": [None],
        "scale": (1, 1),
        "translate": (0, 0)
    },
    {   # Pomicons (https://github.com/gabrielelana/pomicons)
        "path": join(GLYPHS_PATH, "Pomicons.otf"),
        "ranges": [(0xe000, 0xe00a)],
        "remaps": [None],
        "scale": (1, 1),
        "translate": (0, 0)
    },
    {   # Codicons (https://github.com/microsoft/vscode-codicons)
        "path": join(GLYPHS_PATH, "codicons", "codicon.ttf"),
        "ranges": [(0xea60, 0xebeb)],
        "remaps": [None],
        "scale": (1, 1),
        "translate": (0, 0),
    }
]


def main():
    font = new_font()
    for info in SOURCES_INFO:
        source = fontforge.open(info["path"])
        source.em = P.EM
        transform_all(source, info["scale"], info["translate"])
        ranges = info["ranges"]
        remaps = info["remaps"]
        if len(ranges) != len(remaps):
            raise ValueError("len(ranges):", len(ranges), "len(remaps):", len(remaps))
        for i in range(len(ranges)):
            copy_range(font, source, ranges[i], remaps[i])
        source.close()
        util.log("Bundled:", info["path"], "->", BUILD_FILE)

    util.font_into_file(font, BUILD_FILE)
    util.log("Generated:", BUILD_FILE)


def transform_all(font, scale, translate):
    scale = psMat.scale(*scale)
    translate = psMat.translate(*translate)
    transform = psMat.compose(scale, translate)
    font.transform(transform)


def copy_range(font, source, range_, remap):
    def fixed_range(tuple_):
        fixed = (*tuple_, None)
        start = fixed[0]
        stop = (fixed[1] or fixed[0]) + 1
        return range(start, stop)
    _range = fixed_range(range_)
    _remap = fixed_range(remap or range_)
    _remain_skip_count = len(_remap) - len(_range)
    _remap_iter = iter(_remap)
    _range_iter = iter(_range)

    if _remain_skip_count > 0:
        def next_source_codepoint():
            nonlocal _remain_skip_count, _remap_iter
            ret = next(_remap_iter, None)
            while ret and _remain_skip_count >= 0:
                try:
                    _ = source[ret]
                    break
                except TypeError:  # No such glyph
                    _remain_skip_count -= 1
                    ret = next(_remap_iter, None)
                    continue
            return ret
    elif _remain_skip_count == 0:
        def next_source_codepoint():
            return next(_remap_iter, None)
    else:
        raise ValueError("remap is smaller than range: ", len(_remap), len(_range))

    def next_font_codepoint():
        return next(_range_iter, None)

    font_codepoint = next_font_codepoint()
    source_codepoint = next_source_codepoint()
    while font_codepoint and source_codepoint:
        source.selection.select(source_codepoint)
        source.copy()
        font.selection.select(font_codepoint)
        font.paste()
        try:
            glyphname = source[source_codepoint].glyphname + "#nf"
            font[font_codepoint].glyphname = glyphname
        except TypeError:  # No such glyph
            util.debug("skipped bundle from", hex(source_codepoint), "to", hex(font_codepoint))
            pass
        font_codepoint = next_font_codepoint()
        source_codepoint = next_source_codepoint()

    if font_codepoint:
        raise ValueError("Invalid range or remap (range is smaller than remap)")
    if source_codepoint:
        raise ValueError("Invalid range or remap (remap is smaller than range)")


def new_font():
    familyname = splitext(basename(BUILD_FILE))[0]
    font = fontforge.font()
    font.ascent = P.ASCENT
    font.descent = P.DESCENT
    font.italicangle = 0
    font.upos = P.UNDERLINE_POS
    font.uwidth = P.UNDERLINE_HEIGHT
    font.familyname = familyname
    font.encoding = P.ENCODING
    font.fontname = familyname
    font.fullname = familyname
    return font


if __name__ == "__main__":
    main()
