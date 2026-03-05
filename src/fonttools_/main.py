import sys
import os
from os.path import join, basename, splitext
from xml.etree.ElementTree import ElementTree, parse as xml_parse
import fontTools.ttx

if len(sys.argv) != 4:
    raise ValueError("Invalid argument")

FONT_FILE = sys.argv[1]
CACHE_DIR = sys.argv[2]
BUILD_FILE = sys.argv[3]


def main() -> None:
    ttx_file_path = join(CACHE_DIR, f"{splitext(basename(FONT_FILE))[0]}.ttx")

    xml = dump_ttx(ttx_file_path, "post", "OS/2")
    fix_post_table(xml)
    fix_os2_table(xml)
    xml.write(
        ttx_file_path,
        encoding="utf-8",
        xml_declaration=True,
    )

    fontTools.ttx.main(
        [
            "-o",
            BUILD_FILE,
            "-m",
            FONT_FILE,
            ttx_file_path,
        ]
    )
    os.remove(ttx_file_path)


def dump_ttx(ttx_file_path: str, *tables: str) -> ElementTree:
    args = []
    for table in tables:
        args += ["-t", table]
    fontTools.ttx.main(
        [
            *args,
            "-f",
            "-o",
            ttx_file_path,
            FONT_FILE,
        ]
    )
    return xml_parse(ttx_file_path)


def fix_post_table(xml: ElementTree) -> None:
    # isFixedPitchを編集
    # タグ形式: <isFixedPitch value="1"/>
    is_fixed_pitch = 1
    for elem in xml.iter("isFixedPitch"):
        elem.set("value", str(is_fixed_pitch))


def fix_os2_table(xml: ElementTree) -> None:
    # xAvgCharWidthをhalf-width(EM/2)に固定
    # FontForgeの自動計算では全角グリフも含めた平均になり、 Windows Excel等で文字幅が大きくなる問題の原因となる
    # タグ形式: <xAvgCharWidth value="1024"/>
    half_width = 1024  # EM // 2, see ../fontforge_/properties.py
    for elem in xml.iter("xAvgCharWidth"):
        elem.set("value", str(half_width))


if __name__ == "__main__":
    main()
