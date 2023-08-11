import sys
from os.path import join, basename
from xml.etree.ElementTree import ElementTree, parse as xml_parse
import fontTools.ttx

if len(sys.argv) != 4:
    raise ValueError("Invalid argument")

FONT_FILE = sys.argv[1]
CACHE_DIR = sys.argv[2]
BUILD_FILE = sys.argv[3]


def main() -> None:
    ttx_file_path = join(CACHE_DIR, f"{basename(FONT_FILE)}.ttx")

    xml = dump_ttx(ttx_file_path, "post")
    fix_post_table(xml)
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


def dump_ttx(ttx_file_path: str, table: str) -> ElementTree:
    fontTools.ttx.main(
        [
            "-t",
            table,
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


if __name__ == "__main__":
    main()
