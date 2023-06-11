import sys
from os.path import join, dirname
import json
from math import sin, cos, pi as PI
import numpy as np
import fontforge
import util
import properties as P

if len(sys.argv) != 2:
    raise ValueError("Invalid argument")

BRAILLE_JSON_PATH = join(dirname(__file__), "braille.json")
BUILD_FILE = sys.argv[1]


def main():
    font = new_font()

    with open(BRAILLE_JSON_PATH, "r") as f:
        braille_json = json.load(f)
    table = braille_json['table']
    for data in braille_json['data']:
        code = int(data['code'], 16)
        points = [table[str(p)] for p in data['points']]
        create_braille(font, code, points)

    util.font_into_file(font, BUILD_FILE)
    util.log("Generated:", BUILD_FILE)


def create_braille(font, codepoint, points):
    glyph = font.createChar(codepoint, "uni" + (hex(codepoint)[2:]))
    pen = glyph.glyphPen()
    for points in points:
        center_pos = np.array([points[0], points[1] - P.DESCENT])
        draw_circle(pen, center_pos, 100)
    pen = None
    glyph.width = P.EM // 2
    glyph.round()


def draw_circle(pen, center_pos, radius):
    def vector_from_rad(rad):
        return np.array([cos(rad), sin(rad)])

    def intersection(normal_vec1, pos1, normal_vec2, pos2):
        # a(x - x1) + b(y - y1) = 0 <=> ax + by = ax1 + by1
        # c(x - x2) + d(y - y2) = 0 <=> cx + by = cx2 + by2
        #  ∴ A X = K
        #      X = A^-1 K
        a, b = normal_vec1
        c, d = normal_vec2
        x1, y1 = pos1
        x2, y2 = pos2
        mat_A = np.matrix([
            [a, b],
            [c, d]
        ])
        vec_K = np.array([
            a * x1 + b * y1,
            c * x2 + d * y2
        ])
        mat_X = mat_A.I @ vec_K
        return (mat_X[0, 0], mat_X[0, 1])

    for i in range(4):
        vec1 = vector_from_rad(-1 * i * PI / 2)
        vec2 = vector_from_rad(-1 * (i + 1) * PI / 2)
        vec3 = vector_from_rad(-1 * (2 * i + 1) * PI / 4)
        pos1 = center_pos + (vec1 * radius)
        pos2 = center_pos + (vec2 * radius)
        pos3 = center_pos + (vec3 * radius * 1.1)

        curve_point1 = intersection(vec1, pos1, vec3, pos3)
        curve_point2 = intersection(vec2, pos2, vec3, pos3)
        if i == 0:
            pen.moveTo(pos1)
        pen.curveTo(curve_point1, curve_point2, pos2)
    pen.closePath()


def new_font():
    familyname = "Braille"
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
