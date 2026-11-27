import os
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat
from typing import Any, Final

from fontTools import subset
from fontTools.ttLib import TTFont

if len(sys.argv) < 3:
    raise ValueError("Invalid argument")

OUT_DIR = sys.argv[1]
FONT_FILES = sorted(sys.argv[2:])

SLICES_FILE: Final = os.path.join(
    os.path.dirname(__file__), "nam-files", "japanese_default.txt"
)

# NOTE: ASCII is scattered across several slices (e.g. space is in the kana slice), so take it first.
ASCII: Final = range(0x0000, 0x0080)
LATIN: Final = [
    range(0x0080, 0x0250),  # Latin-1 Supplement ~ Latin Extended-B
    range(0x2000, 0x2070),  # General Punctuation
]

MAX_REST_CHUNK_LEN: Final = 256

DEFAULT_GSUB_FEATURES: Final = {"ccmp", "liga", "locl", "rlig", "clig", "calt"}


def main() -> None:
    slices = load_slices(SLICES_FILE)
    css = "".join(split_font(font_file, slices) for font_file in FONT_FILES)
    with open(os.path.join(OUT_DIR, "pleckjp.css"), "w") as f:
        f.write(css)


def split_font(font_file: str, slices: list[set[int]]) -> str:
    with TTFont(font_file) as font:
        cmap = font.getBestCmap()
        if cmap is None:
            raise ValueError(f"No Unicode cmap in {font_file}")
        chunks = plan_chunks(set(cmap), slices, ligature_groups(font, cmap))

        name = font_name(font, 6)
        os.makedirs(os.path.join(OUT_DIR, name))
        urls = [f"{name}/{i:03d}.woff2" for i in range(len(chunks))]
        with ProcessPoolExecutor() as executor:
            files = [os.path.join(OUT_DIR, url) for url in urls]
            list(executor.map(write_woff2_subset, repeat(font_file), chunks, files))

        css = "".join(
            font_face_css(font, url, chunk) for url, chunk in zip(urls, chunks)
        )
        with open(os.path.join(OUT_DIR, f"{name}.css"), "w") as f:
            f.write(css)
        print("Generated:", name, f"({len(chunks)} chunks)", flush=True)
        return css


def load_slices(path: str) -> list[set[int]]:
    with open(path) as f:
        text = f.read()
    return [
        {int(cp) for cp in re.findall(r"codepoints:\s*(\d+)", block)}
        for block in re.findall(r"subsets\s*\{(.*?)\}", text, re.S)
    ]


def plan_chunks(
    codepoints: set[int], slices: list[set[int]], keep_together: list[set[int]]
) -> list[set[int]]:
    remaining = set(codepoints)
    chunks: list[set[int]] = []

    def take(wanted: set[int]) -> None:
        nonlocal remaining
        for group in keep_together:
            if group & wanted:
                wanted = wanted | group
        chunk = wanted & remaining
        if chunk:
            chunks.append(chunk)
            remaining -= chunk

    take(set(ASCII))
    take({cp for r in LATIN for cp in r})
    for s in slices:
        take(s)
    for block in group_by_block(remaining):  # Nerd Fonts, Greek, etc.
        take(block)
    return chunks


def group_by_block(codepoints: set[int]) -> list[set[int]]:
    blocks: dict[int, set[int]] = {}
    for cp in codepoints:
        blocks.setdefault(cp // 256, set()).add(cp)

    groups: list[set[int]] = []
    current: set[int] = set()
    for key in sorted(blocks):
        if current and len(current) + len(blocks[key]) > MAX_REST_CHUNK_LEN:
            groups.append(current)
            current = set()
        current |= blocks[key]
    if current:
        groups.append(current)
    return groups


def ligature_groups(font: TTFont, cmap: dict[int, str]) -> list[set[int]]:
    codepoints_of: dict[str, set[int]] = {}
    for cp, glyph in cmap.items():
        codepoints_of.setdefault(glyph, set()).add(cp)

    # NOTE: Contextual substitutions (LookupType 5, 6) are ignored. PleckJP has them only in locl within LATIN.
    gsub = font["GSUB"].table
    groups: list[set[int]] = []
    for record in gsub.FeatureList.FeatureRecord:
        if record.FeatureTag not in DEFAULT_GSUB_FEATURES:
            continue
        for index in record.Feature.LookupListIndex:
            for ligatures in ligature_subtables(gsub.LookupList.Lookup[index]):
                for first, ligature_list in ligatures.items():
                    for ligature in ligature_list:
                        group = {
                            cp
                            for glyph in [first, *ligature.Component]
                            for cp in codepoints_of.get(glyph, set())
                        }
                        if len(group) <= 1:
                            continue
                        for g in [g for g in groups if g & group]:
                            groups.remove(g)
                            group |= g
                        groups.append(group)
    return groups


def ligature_subtables(lookup):
    for subtable in lookup.SubTable:
        lookup_type = lookup.LookupType
        if lookup_type == 7:  # Extension Substitution
            lookup_type = subtable.ExtensionLookupType
            subtable = subtable.ExtSubTable
        if lookup_type == 4:  # Ligature Substitution
            yield subtable.ligatures


def write_woff2_subset(font_file: str, chunk: set[int], output_file: str) -> None:
    # Keep features like jp90 and zero for font-feature-settings
    options = subset.Options(flavor="woff2", layout_features=["*"])
    options.drop_tables += ["FFTM"]
    with TTFont(font_file) as font:
        subsetter = subset.Subsetter(options)
        subsetter.populate(unicodes=chunk)
        subsetter.subset(font)
        subset.save_font(font, output_file, options)


def font_face_css(font: TTFont, url: str, chunk: set[int]) -> str:
    # NOTE: No local(), since the installed PleckJP may be a different version.
    family = font_name(font, 1)
    os2: Any = font["OS/2"]
    style = "italic" if os2.fsSelection & 1 else "normal"
    return (
        f'@font-face{{font-family:"{family}";font-style:{style};font-weight:{os2.usWeightClass};font-display:swap;'
        f'src:url("{url}")format("woff2");unicode-range:{unicode_range(chunk)};}}\n'
    )


def font_name(font: TTFont, name_id: int) -> str:
    name = font["name"].getDebugName(name_id)
    if name is None:
        raise ValueError(f"No name ID {name_id}")
    return name


def unicode_range(codepoints: set[int]) -> str:
    ranges: list[list[int]] = []
    for cp in sorted(codepoints):
        if ranges and ranges[-1][1] + 1 == cp:
            ranges[-1][1] = cp
        else:
            ranges.append([cp, cp])
    return ",".join(
        f"U+{start:X}" if start == end else f"U+{start:X}-{end:X}"
        for start, end in ranges
    )


if __name__ == "__main__":
    main()
