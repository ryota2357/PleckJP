import sys
import fontforge
import psMat
import util
import properties as const

if len(sys.argv) != 3:
    raise ValueError("Invalid argument")

FONT_FILE = sys.argv[1]
BUILD_FILE = sys.argv[2]


def main() -> None:
    font = fontforge.open(FONT_FILE)

    remove_gpos_lookup(
        font,
        [
            "'vhal'",  # Vertical Halant
            "'kern'",  # Kerning
            "'vkrn'",  # Vertical Kerning
            "'palt'",  # Proportional Alternate
            "'vpal'",  # Vertical Proportional Alternate
        ],
    )

    # remove vertical writing
    remove_gsub_lookup(font, "'vert'", [".vert", ".vertl", ".vert.001"])
    remove_gsub_lookup(font, "'vrt2'", [".rotat"])

    # remove proportional
    remove_gsub_lookup(font, "'pkna'", [".prop"])
    remove_gsub_lookup(font, "'pwid'", [".prop"])

    # remove italic correction
    remove_gsub_lookup(font, "'ital'", [".italic"])

    # remove 1/3 width
    remove_gsub_lookup(font, "'twid'", [".thirdwidths"])

    # Use Hack glyph
    util.font_clear_glyph(font, 0x20, 0x2002)  # number, alphabet, etc
    util.font_clear_glyph(font, 0x2004, 0x20AC)  # basic symbols
    util.font_clear_glyph(font, 0x2116)  # №
    util.font_clear_glyph(font, 0x2122)  # ™
    util.font_clear_glyph(font, 0x2126, 0x2127)  # Ω ℧
    util.font_clear_glyph(font, 0x2135)  # ℵ
    util.font_clear_glyph(font, 0x2150, 0x215E)  # ⅐ ⅑ ⅒ ⅓ ⅔ ⅕ ⅖ ⅗ ⅘ ⅙ ⅚ ⅛ ⅜ ⅝ ⅞
    util.font_clear_glyph(font, 0x2190, 0x21FF)  # arrow
    util.font_clear_glyph(font, 0x2200, 0x22A5)  # math
    util.font_clear_glyph(font, 0x22DA, 0x22DB)  # math
    util.font_clear_glyph(font, 0x229B, 0x23AD)  # hook, bracket
    util.font_clear_glyph(font, 0x2500, 0x25FF)  # border, block
    util.font_clear_glyph(font, 0x2B05, 0x2B07)  # ⬅ ⬆ ⬇

    util.font_set_em(font, const.ASCENT, const.DESCENT, const.EM)

    modify_whitespace(font)

    shrink_zenkaku_scale(font)
    shrink_shogi_piece_scale(font)

    # Enforce glyph width
    util.glyph_riseze_width(font[0x2103], const.EM // 2)  # ℃
    util.glyph_riseze_width(font[0x2109], const.EM // 2)  # ℉
    util.glyph_riseze_width(font[0x2121], const.EM // 2)  # ℡
    util.glyph_riseze_width(font[0x212B], const.EM // 2)  # Å
    util.glyph_riseze_width(font[0xFB00], const.EM // 2)  # ﬀ
    util.glyph_riseze_width(font[0xFB01], const.EM // 2)  # ﬁ
    util.glyph_riseze_width(font[0xFB02], const.EM // 2)  # ﬂ
    util.glyph_riseze_width(font[0xFB03], const.EM // 1)  # ﬃ
    util.glyph_riseze_width(font[0xFB04], const.EM // 1)  # ﬄ
    for code in range(0x2160, 0x216B + 1):  # Ⅰ Ⅱ Ⅲ Ⅳ Ⅴ Ⅵ Ⅶ Ⅷ Ⅸ Ⅹ Ⅺ Ⅻ
        util.glyph_riseze_width(font[code], const.EM // 2)
    for code in range(0x2170, 0x217B + 1):  # ⅰ ⅱ ⅲ ⅳ ⅴ ⅵ ⅶ ⅷ ⅸ ⅹ ⅺ ⅻ
        util.glyph_riseze_width(font[code], const.EM // 2)
    for code in range(0x23BE, 0x23CC + 1):  # ⎾ ⎿ ⏀ ⏁ ⏂ ⏃ ⏄ ⏅ ⏆ ⏇ ⏈ ⏉ ⏊ ⏋ ⏌
        util.glyph_riseze_width(font[code], const.EM)
    util.glyph_riseze_width(font[0x29FA], const.EM // 2)  # ⧺
    util.glyph_riseze_width(font[0x29FB], const.EM // 2)  # ⧻

    # Debug
    # for glyph in font.glyphs():
    #     width = glyph.width
    #     if width not in (const.EM, const.EM // 2, const.EM // 4):
    #         name = glyph.glyphname
    #         util.log(f"unkown scale: {width} name: {name}")

    # Enforce glyph width (Note that I don't know the meaning of the following glyphs)
    # unkown scale: 1290 name: zero.zero
    # unkown scale: 1251 name: E_ring
    # unkown scale: 856  name: I_ring
    # unkown scale: 1517 name: O_ring
    # unkown scale: 1177 name: e_ring
    # unkown scale: 534  name: i_ring
    # unkown scale: 1202 name: o_ring
    # unkown scale: 1855 name: ae_grave
    # unkown scale: 1079 name: uni0254_uni00B4
    # unkown scale: 1081 name: uni0254_uni0060
    # unkown scale: 1177 name: uni0259_uni00B4
    # unkown scale: 1177 name: uni0259_uni0060
    # unkown scale: 1435 name: uni025A_uni00B4
    # unkown scale: 1435 name: uni025A_uni0060
    # unkown scale: 1052 name: uni028C_uni00B4
    # unkown scale: 1052 name: uni028C_uni0060
    # unkown scale: 2084 name: uni26BE
    # unkown scale: 1214 name: uni210F
    # unkown scale: 1290 name: tonerising
    # unkown scale: 1290 name: tonefalling
    # unkown scale: 903  name: uni207F
    # unkown scale: 1255 name: uniA7B5
    # unkown scale: 1208 name: theta.RomanSupp
    # unkown scale: 1067 name: uniAB53
    # unkown scale: 1720 name: bartop.dentistry
    # unkown scale: 1720 name: barbottom.dentistry
    # unkown scale: 1867 name: uni2713
    # unkown scale: 1290 name: uni2423
    # unkown scale: 1290 name: ordmasculine.alt
    # unkown scale: 1290 name: ordfeminine.alt
    # unkown scale: 1075 name: Lcaron.alt
    # unkown scale: 583  name: lcaron.alt
    # unkown scale: 1560 name: estimated
    # unkown scale: 1832 name: quoteright_S
    # unkown scale: 1245 name: a.alt01
    # unkown scale: 1245 name: g.alt01
    # unkown scale: 1142 name: g.alt02
    # unkown scale: 1290 name: zero.alt01
    # unkown scale: 1228 name: minus
    for name in (
        "zero.zero",
        "E_ring",
        "I_ring",
        "O_ring",
        "e_ring",
        "i_ring",
        "o_ring",
        "ae_grave",
        "uni0254_uni00B4",
        "uni0254_uni0060",
        "uni0259_uni00B4",
        "uni0259_uni0060",
        "uni025A_uni00B4",
        "uni025A_uni0060",
        "uni028C_uni00B4",
        "uni028C_uni0060",
        "uni210F",
        "tonerising",
        "tonefalling",
        "uni207F",
        "uniA7B5",
        "theta.RomanSupp",
        "uniAB53",
        "bartop.dentistry",
        "barbottom.dentistry",
        "uni2713",
        "uni2423",
        "ordmasculine.alt",
        "ordfeminine.alt",
        "Lcaron.alt",
        "lcaron.alt",
        "estimated",
        "quoteright_S",
        "a.alt01",
        "g.alt01",
        "g.alt02",
        "zero.alt01",
        "minus",
    ):
        util.glyph_riseze_width(font[name], const.EM // 2)
    for name in ("uni26BE",):
        util.glyph_riseze_width(font[name], const.EM)

    util.fix_all_glyph_points(font, round=True)
    util.font_into_file(font, BUILD_FILE)
    util.log("Modified:", FONT_FILE, "->", BUILD_FILE)


def remove_gpos_lookup(font, lookup_prefixs: list[str]) -> None:
    for lookup in font.gpos_lookups:
        for prefix in lookup_prefixs:
            if lookup.startswith(prefix):
                font.removeLookup(lookup)
                break


def remove_gsub_lookup(font, lookup_prefix: str, glyph_suffix: list[str]) -> None:
    for lookup in font.gsub_lookups:
        if lookup.startswith(lookup_prefix):
            font.removeLookup(lookup)
    for glyph in font.glyphs():
        if glyph.unicode != -1:
            continue
        name: str = glyph.glyphname
        for sufix in glyph_suffix:
            if name.endswith(sufix):
                util.font_clear_glyph(font, name)
                break


def shrink_zenkaku_scale(font) -> None:
    scale = 0.82
    x_to_center = const.EM * (1 - scale) / 2
    mat = psMat.compose(psMat.scale(scale), psMat.translate(x_to_center))
    for glyph in font.glyphs():
        width = glyph.width
        if width == const.EM:
            glyph.transform(mat)
            glyph.width = const.EM


def shrink_shogi_piece_scale(font) -> None:
    # 0x2616 ☖ (WHITE SHOGI PECE)
    # 0x2617 ☗ (BLACK SHOGI PECE)
    mat = psMat.compose(psMat.scale(0.8, 0.9), psMat.translate(-118, 0))
    for code in (0x2616, 0x2617):
        glyph = font[code]
        glyph.transform(mat)
        glyph.width = const.EM // 2


def modify_whitespace(font) -> None:
    # NOTE: if modify 0x3000, it also apply to 0x2003 (EM SPACE)
    pen = font[0x3000].glyphPen(replace=False)

    # draw square frame
    util.draw_square(
        pen,
        (const.EM // 2, (const.EM - const.DESCENT) // 2),
        round(const.EM * 0.8),
        round(const.EM * 0.8),
    )
    util.draw_square(
        pen,
        (const.EM // 2, (const.EM - const.DESCENT) // 2),
        round(const.EM * 0.7),
        round(const.EM * 0.7),
        clockwise=False,
    )

    util.draw_square(
        pen,
        (const.EM // 2, (const.EM - const.DESCENT) // 2),
        round(const.EM * 0.35),
        round(const.EM * 2),
    )
    util.draw_square(
        pen,
        (0, (const.EM - const.DESCENT) // 2),
        round(const.EM * 0.5),
        round(const.EM * 0.35),
    )
    util.draw_square(
        pen,
        (const.EM, (const.EM - const.DESCENT) // 2),
        round(const.EM * 0.5),
        round(const.EM * 0.35),
    )
    pen = None

    font.selection.select(0x3000)
    font.intersect()
    font.selection.none()


if __name__ == "__main__":
    main()
