import sys
import ast
from os.path import join, basename, splitext
from typing import Final, TypedDict
from collections.abc import Callable
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
#      modify: string
#          The script of glyph transforming
#  }
class SourceInfoRequiredKeys(TypedDict):
    path: str
    ranges: list[tuple[int, ...]]
    remaps: list[tuple[int, ...] | None]
    scale: tuple[float, float]
    translate: tuple[int, int]


class SourceInfoOptionalKeys(TypedDict, total=False):
    modify: str


class SourceInfo(SourceInfoRequiredKeys, SourceInfoOptionalKeys):
    pass


# Ref: https://github.com/ryanoasis/nerd-fonts/wiki/Glyph-Sets-and-Code-Points
SOURCES_INFO: Final[list[SourceInfo]] = [
    {  # Seti-UI + Custom
        "path": join(GLYPHS_PATH, "original-source.otf"),
        "ranges": [(0xE5FA, 0xE6B7)],
        "remaps": [(0xE4FA, 0xE5B7)],
        "scale": (0.83, 0.83),
        "translate": (-310, -140),
    },
    {  # Devicons (https://vorillaz.github.io/devicons/)
        "path": join(GLYPHS_PATH, "devicons", "devicons.otf"),
        "ranges": [(0xE700, 0xE8EF)],
        "remaps": [(0xE600, 0xE7EF)],
        "scale": (0.9, 0.9),
        "translate": (-405, -145),
    },
    {  # Font Awesome (https://github.com/FortAwesome/Font-Awesome)
        "path": join(GLYPHS_PATH, "font-awesome", "FontAwesome.otf"),
        "ranges": [(0xED00, 0xEFC1), (0xF000, 0xF2FF)],
        "remaps": [None, None],
        "scale": (0.8, 0.8),
        "translate": (-100, 160),
        "modify": """
                [0xf0d7, 0xf0da] (1, 1) (80, 0)   #  ~ 
                [0xf0dd, 0xf0de] (1, 1) (80, 0)   #  ~ 
                0xf0eb           (1, 1) (20, 0)   # 
                [0xf104, 0xf105] (1, 1) (220, 0)  #  ~ 
                [0xf175, 0xf176] (1, 1) (85, 0)   #  ~ 
                0xf276           (1, 1) (115, 0)  # 
                0xf294           (1, 1) (115, 0)  # 
                [0xf2c7, 0xf2cb] (1, 1) (135, 0)  #  ~ 
                """,
    },
    {  # Font Awesome Extension (https://github.com/AndreLZGava/font-awesome-extension)
        "path": join(GLYPHS_PATH, "font-awesome-extension.ttf"),
        "ranges": [(0xE200, 0xE2A9)],
        "remaps": [(0xE000, 0xE0A9)],
        "scale": (0.8, 0.8),
        "translate": (-310, -80),
    },
    {  # Material Design Icons (https://github.com/Templarian/MaterialDesign)
        "path": join(GLYPHS_PATH, "materialdesign", "MaterialDesignIconsDesktop.ttf"),
        "ranges": [(0xF0001, 0xF1AF0)],
        "remaps": [None],
        "scale": (0.9, 0.9),
        "translate": (-410, 0),
    },
    {  # Weather (https://github.com/erikflowers/weather-icons)
        "path": join(GLYPHS_PATH, "weather-icons", "weathericons-regular-webfont.ttf"),
        "ranges": [(0xE300, 0xE3E3)],
        "remaps": [(0xF000, 0xF0EB)],
        "scale": (0.9, 0.9),
        "translate": (0, 0),
        "modify": """
                [0xe300, 0xe338] (0.8, 0.8) (0, 0)      #  ~ 
                0xe339           (1, 1)     (0, -300)   # 
                0xe341           (1, 1)     (0, -300)   # 
                0xe34e           (0.9, 0.9) (75, -110)  # 
                0xe34f           (1, 1)     (270, 0)    # 
                0xe350           (0.9, 0.9) (75, -110)  # 
                [0xe35e, 0xe367] (0.9, 0.9) (0, 0)      #  ~ 
                [0xe3aa, 0xe3ad] (0.8, 0.8) (0, 0)      #  ~ 
                """,
    },
    {  # Octicons (https://github.com/primer/octicons)
        "path": join(GLYPHS_PATH, "octicons", "octicons.otf"),
        "ranges": [(0xF400, 0xF532), (0x2665,), (0x26A1,)],
        "remaps": [(0xF000, 0xF305), None, None],
        "scale": (0.695, 0.695),
        "translate": (-200, 170),
        "modify": """
                0xf480 (1, 1) (0, -250)  # 
                """,
    },
    {  # Powerline Symbols
        "path": join(GLYPHS_PATH, "powerline-symbols", "PowerlineSymbols.otf"),
        "ranges": [(0xE0A0, 0xE0A2), (0xE0B0, 0xE0B3)],
        "remaps": [None, None],
        "scale": (0.97, 0.887),
        "translate": (0, -109),
        "modify": """
                0xe0a0 (1, 1)     (-60, 0)  # 
                0xe0b0 (1, 0.995) (-74, 10) # 
                0xe0b2 (1, 0.995) (0, 10)   # 
                """,
    },
    {  # Powerline Extra Symbols (https://github.com/ryanoasis/powerline-extra-symbols)
        "path": join(GLYPHS_PATH, "powerline-extra", "PowerlineExtraSymbols.otf"),
        "ranges": [
            (0xE0A3,),
            (0xE0B4, 0xE0C8),
            (0xE0CA,),
            (0xE0CC, 0xE0D4),
            (0xE0D6, 0xE0D7),
        ],
        "remaps": [None, None, None, None, None],
        "scale": (1, 1),
        "translate": (0, 0),
        "modify": """
                0xe0a3           (0.85, 0.85)  (0, 0)      # 
                0xe0b4           (0.84, 0.845) (-70, 22)   # 
                0xe0b5           (0.84, 0.84)  (-273, 60)  # 
                0xe0b6           (0.84, 0.845) (-20, 14)   # 
                0xe0b7           (0.84, 0.84)  (0, 60)     # 
                0xe0b8           (0.41, 0.818) (-70, 6)    # 
                [0xe0b9, 0xe0ba] (0.41, 0.818) (0, 3)      #  , 
                0xe0bb           (0.41, 0.818) (-50, 6)    # 
                0xe0bc           (0.41, 0.818) (-70, 3)    # 
                [0xe0bd, 0xe0be] (0.41, 0.818) (0, 3)      #  , 
                0xe0bf           (0.41, 0.818) (-50, 3)    # 
                [0xe0c0, 0xe0c3] (0.87, 0.873) (0, 3)      #  ~ 
                [0xe0c4, 0xe0c7] (0.81, 0.81)  (0, 40)     #  ~ 
                0xe0c8           (0.88, 0.88)  (0, 50)     # 
                0xe0ca           (0.88, 0.88)  (0, 50)     # 
                [0xe0cc, 0xe0d2] (0.82, 0.82)  (0, 0)      #  ~ 
                0xe0d4           (0.82, 0.82)  (0, 0)      # 
                0xe0d6           (0.767, 0.82) (-58, -4)   # 
                0xe0d7           (0.767, 0.82) (0, -4)     # 
                """,
    },
    {  # IEC Power Symbols (https://unicodepowersymbol.com/)
        "path": join(GLYPHS_PATH, "Unicode_IEC_symbol_font.otf"),
        "ranges": [(0x23FB, 0x23FE), (0x2B58,)],
        "remaps": [None, None],
        "scale": (0.8, 0.8),
        "translate": (-280, -100),
    },
    {  # Font Logos (https://github.com/Lukas-W/font-logos)
        "path": join(GLYPHS_PATH, "font-logos.ttf"),
        "ranges": [(0xF300, 0xF381)],
        "remaps": [None],
        "scale": (0.73, 0.73),
        "translate": (0, 150),
    },
    {  # Pomicons (https://github.com/gabrielelana/pomicons)
        "path": join(GLYPHS_PATH, "pomicons", "Pomicons.otf"),
        "ranges": [(0xE000, 0xE00A)],
        "remaps": [None],
        "scale": (0.87, 0.87),
        "translate": (-300, 0),
        "modify": """
                0xe009 (1, 1) (330, 0)  # 
                0xe00a (1, 1) (170, 0)  # 
                """,
    },
    {  # Codicons (https://github.com/microsoft/vscode-codicons)
        "path": join(GLYPHS_PATH, "codicons", "codicon.ttf"),
        "ranges": [(0xEA60, 0xEC1E)],
        "remaps": [None],
        "scale": (0.8, 0.8),
        "translate": (-350, -220),
        "modify": """
                [0xea9d, 0xeaa0] (1, 1) (50, 0)  #  ~ 
                [0xeaa6, 0xeaa9] (1, 1) (40, 0)  #  ~ 
                0xeafc           (1, 1) (40, 0)  # 
                """,
    },
]


def main() -> None:
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
            remap_range(source, remaps[i], ranges[i])
        if "modify" in info:
            modify(source, info["modify"])
        for i in range(len(ranges)):
            copy_range(font, source, ranges[i])

        source.close()
        util.log("Bundled:", info["path"], "->", BUILD_FILE)

    util.fix_all_glyph_points(font, round=True, addExtrema=True)
    util.font_into_file(font, BUILD_FILE)
    util.log("Generated:", BUILD_FILE)


def remap_range(
    font, from_range: tuple[int, int] | None, to_range: tuple[int, int]
) -> None:
    if from_range is None:
        return
    next_to_codepoint, next_from_codepoint = _remap_util(font, from_range, to_range)

    to_codepoint = next_to_codepoint()
    from_codepoint = next_from_codepoint()
    while to_codepoint and from_codepoint:
        font.selection.select(from_codepoint)
        font.copy()
        font.selection.select(to_codepoint)
        font.paste()
        try:
            font[to_codepoint].glyphname = font[from_codepoint].glyphname
        except TypeError as e:
            if str(e) != "No such glyph":
                raise
        to_codepoint = next_to_codepoint()
        from_codepoint = next_from_codepoint()

    if to_codepoint:
        raise ValueError("Invalid range or remap (range is smaller than remap)")
    if from_codepoint:
        raise ValueError("Invalid range or remap (remap is smaller than range)")


def _remap_util(
    font, from_range: tuple[int, int], to_range: tuple[int, int]
) -> tuple[Callable[[], int | None], Callable[[], int | None]]:
    fixed_from = _tuple_to_range(from_range or to_range)
    fixed_to = _tuple_to_range(to_range)
    remain_skip_count = len(fixed_from) - len(fixed_to)
    from_iter = iter(fixed_from)
    to_iter = iter(fixed_to)

    if remain_skip_count > 0:

        def next_from_codepoint():
            nonlocal remain_skip_count, from_iter
            ret = next(from_iter, None)
            while ret and remain_skip_count >= 0:
                try:
                    _ = font[ret]
                    break
                except TypeError:  # No such glyph
                    remain_skip_count -= 1
                    ret = next(from_iter, None)
                    continue
            return ret

    elif remain_skip_count == 0:

        def next_from_codepoint():
            return next(from_iter, None)

    else:
        raise ValueError(
            "from_range is smaller than to_range: ",
            "from_range:",
            len(fixed_from),
            "to_range:",
            len(fixed_to),
        )

    def next_to_codepoint():
        return next(to_iter, None)

    return next_to_codepoint, next_from_codepoint


def transform_all(font, scale: tuple[float, float], translate: tuple[int, int]) -> None:
    scale = psMat.scale(*scale)
    translate = psMat.translate(*translate)
    transform = psMat.compose(scale, translate)
    font.selection.all()
    font.transform(transform)
    for glyph in list(font.selection.byGlyphs):
        if glyph.width != 0:
            glyph.left_side_bearing = int(max(glyph.left_side_bearing, 0))
            glyph.right_side_bearing = int(max(glyph.right_side_bearing, 0))
        glyph.width = P.EM // 2
    font.selection.none()


def modify(font, script: str) -> None:
    for line in script.split(sep="\n"):
        line = line.strip().replace(" ", "").replace("(", ",(")
        if len(line) < 1 or line.startswith("#"):
            continue
        try:
            ops = ast.literal_eval(line)
        except SyntaxError:
            util.log("invalid syntax:", line)
            continue
        if type(ops[0]) is int:
            codepoints = range(ops[0], ops[0] + 1)
        else:
            codepoints = range(ops[0][0], ops[0][1] + 1)
        scale = psMat.scale(*ops[1])
        translate = psMat.translate(*ops[2])
        transform_mat = psMat.compose(scale, translate)
        for codepoint in codepoints:
            font[codepoint].transform(transform_mat)
            font[codepoint].width = P.EM // 2


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


def copy_range(font, source, range_: tuple[int, int | None]) -> None:
    range_iter = iter(_tuple_to_range(range_))
    codepoint = next(range_iter, None)
    while codepoint:
        source.selection.select(codepoint)
        source.copy()
        font.selection.select(codepoint)
        font.paste()
        try:
            new_glyphname = font[codepoint].glyphname + "#nf"
            font[codepoint].glyphname = new_glyphname
        except TypeError as e:
            if str(e) != "No such glyph":
                raise
        codepoint = next(range_iter, None)


def _tuple_to_range(tuple_: tuple[int, int | None]) -> range:
    fixed = (*tuple_, None)
    start = fixed[0]
    stop = (fixed[1] or fixed[0]) + 1
    return range(start, stop)


if __name__ == "__main__":
    main()
