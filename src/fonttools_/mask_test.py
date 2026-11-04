"""mask.py が生成した Masked バリアントの検証スクリプト。

    python3 src/fonttools_/mask_test.py [MASKED.ttf [BASE.ttf]]

BASE.ttf を省略した場合は、MASKED.ttf のパスから導出する
(`build/PleckJP Masked-*.ttf` 以外の場所を指定した場合は `build/PleckJP-<style>.ttf`)。

uharfbuzz が無い環境では SKIP して終了する (Docker イメージには入っていない)。
"""

import sys
from os.path import dirname, isfile

from fontTools.ttLib import TTFont

sys.path.insert(0, dirname(__file__))

import mask as mask_module  # noqa: E402

FAMILY = "PleckJP"
MASKED_FAMILY = "PleckJP Masked"
BASE_FONT = f"build/{FAMILY}-Regular.ttf"
MASKED_FONT = f"build/{MASKED_FAMILY}-Regular.ttf"
MASK_GLYPH = "mask.dot"
DOT = "•"

# 伏せ字になるべき入力と、その期待表示 (プレフィックスごとに代表例)
MASKED_CASES = [
    # OpenAI / Anthropic
    ("sk-abc123", "sk-••••••"),
    ("sk-ant-api03-AbCdEf", "sk-ant-api03-••••••"),
    ("sk-ant-admin01-xyz", "sk-ant-admin01-•••"),
    ("sk-proj-abc123", "sk-proj-••••••"),
    ("sk-svcacct-fedramp-abc", "sk-svcacct-fedramp-•••"),
    ("sk-or-v1-abc123", "sk-or-v1-••••••"),
    ("sk-lf-abc123", "sk-lf-••••••"),
    # GitHub
    ("ghp_abcdef0123456789", "ghp_••••••••••••••••"),
    ("github_pat_abc123", "github_pat_••••••"),
    ("ghs_abc123", "ghs_••••••"),
    # GitLab
    ("glpat-abcdefghij", "glpat-••••••••••"),
    ("gldt-abc123", "gldt-••••••"),
    # Slack
    ("xoxb-1234-5678-abcdef", "xoxb-••••-••••-••••••"),
    ("xapp-1-A012-abcdef", "xapp-•-••••-••••••"),
    # Stripe / Square
    ("sk_live_abc123", "sk_live_••••••"),
    ("rk_test_abc123", "rk_test_••••••"),
    ("sq0csp-abc123", "sq0csp-••••••"),
    # Cloudflare / DigitalOcean / Datadog
    ("cfk_abcdefgh", "cfk_••••••••"),
    ("CFPAT-abcdef", "CFPAT-••••••"),
    ("dop_v1_abcdef", "dop_v1_••••••"),
    ("dckr_pat_abcdefgh", "dckr_pat_••••••••"),
    # npm / Vercel / Supabase / Sentry
    ("npm_abcdefgh", "npm_••••••••"),
    ("sbp_abcdefgh", "sbp_••••••••"),
    ("sb_secret_abcdef", "sb_secret_••••••"),
    ("sntrys_abcdef", "sntrys_••••••"),
    # AI 系
    ("gsk_abcdefgh", "gsk_••••••••"),
    ("hf_abcdefgh", "hf_••••••••"),
    ("xai-abcdef", "xai-••••••"),
    ("pplx-abcdef", "pplx-••••••"),
    ("pcsk_abcdef", "pcsk_••••••"),
    ("sk-helicone-abc123", "sk-helicone-••••••"),
    # その他
    ("pul-abcdef", "pul-••••••"),
    ("tvly-abcdef", "tvly-••••••"),
    ("nvapi-abcdef", "nvapi-••••••"),
    ("whsec_abcdef", "whsec_••••••"),
    ("CLOJARS_abcdef", "CLOJARS_••••••"),
    ("GOCSPX-abcdef", "GOCSPX-••••••"),
    # ドット区切り
    ("ya29.a0AfH6", "ya29.••••••"),
    ("dp.st.abcdef", "dp.st.••••••"),
    (".atlasv1.abcdef", ".atlasv1.••••••"),
    # 終端記号なし
    ("Q~abcdefgh", "Q~••••••••"),
    # 代入コンテキスト
    ('API_KEY="abcdefgh"', 'API_KEY="••••••••"'),
    ("token='abcdefgh'", "token='••••••••'"),
    ('api_key: "abcdefgh"', 'api_key: "••••••••"'),
    ('aws_secret_access_key: "abcdef"', 'aws_secret_access_key: "••••••"'),
    ('--token="abcdef"', '--token="••••••"'),
    # `_sk_` 連結
    ("oc_sk_abc123", "oc_sk_••••••"),
    # PEM ヘッダ
    ("-----BEGIN RSA PRIVATE KEY-----", "-----BEGIN RSA PRIVATE KEY•••••"),
    ("-----BEGIN OPENSSH PRIVATE KEY-----", "-----BEGIN OPENSSH PRIVATE KEY•••••"),
    # Google (旧 API キー) / AWS / Databricks / 1Password / Atlassian
    ("AIzaSyDxYz1234567890", "AIza••••••••••••••••"),
    ("AKIAIOSFODNN7EXAMPLE", "AKIA••••••••••••••••"),
    ("dapi1234567890abcdef", "dapi••••••••••••••••"),
    ("ops_abcdefghijkl", "ops_••••••••••••"),
    ("ATATT3xFfGF0aBcDeF", "ATATT•••••••••••••"),
    # Bitcoin / age / PyPI / NuGet / JFrog
    ("xprv9s21ZrQH143K3abc", "xprv••••••••••••••••"),
    ("AGE-SECRET-KEY-1QZ4QZ4QZ4", "AGE-SECRET-KEY-1•••••••••"),
    ("pypi-AgEIcHlwaS5vcmc", "pypi-•••••••••••••••"),
    ("oy2abcdefghijklmnop", "oy2••••••••••••••••"),
    ("cmVhbGx5LWxvbmctYmFzZTY0", "cmV•••••••••••••••••••••"),
    # JFrog access token (base64 の `reftu:...`)。短いトークンでも cmVmdG で伏せる
    ("cmVmdGtuOjAx", "cmVmdG••••••"),
    (
        "cmVmdGtuOjAxOjE3NjU0Njg1MjY6SlBoYWZ4",
        "cmVmdG••••••••••••••••••••••••••••••",
    ),
    # base64 でエンコードされた PEM / OpenSSH 秘密鍵
    (
        "LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQ==",
        "LS0tLS1CRUdJTi••••••••••••••••••••••••••••==",
    ),
    (
        "b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQ",
        "b3BlbnNzaC1rZXkt••••••••••••••••••••••••••",
    ),
    # 連想配列 / 辞書のキー代入 (`config["TOKEN"] = "..."`)
    ('config["API_TOKEN"] = "7MMVuQhABCDEF"', 'config["API_TOKEN"] = "•••••••••••••"'),
    ("config['API_TOKEN'] = '7MMVuQhABCDEF'", "config['API_TOKEN'] = '•••••••••••••'"),
    ('cfg["SECRET"] = "abcdefgh"', 'cfg["SECRET"] = "••••••••"'),
    ("cfg['SECRET'] = 'abcdefgh'", "cfg['SECRET'] = '••••••••'"),
    # Airtable / JWT (ドットをはさんでも継続する)
    ("patABCDEFGHIJKLMN.1234567890abcdef", "pat••••••••••••••.••••••••••••••••"),
    ("eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIx", "eyJ•••••••••••••••••.••••••••••••"),
    # Discord Webhook
    (
        "https://discord.com/api/webhooks/1234567890/abcdefTOKEN",
        "https://discord.com/api/webhooks/••••••••••/•••••••••••",
    ),
    # Telegram Bot Token (`<数字ID>:<トークン>`)
    ("123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw", "123456789:••••••••••••••••••••••••••••••••••"),
    # クォートなしの代入コンテキスト
    ("TOKEN=abcdefgh", "TOKEN=••••••••"),
    ("--token=abcdefgh", "--token=••••••••"),
    ("AccountKey=abcdefgh", "AccountKey=••••••••"),
    ("aws_session_token = abcdefgh", "aws_session_token = ••••••••"),
    ("password: hunter2", "password: •••••••"),
    ("?api_key=abcdefgh", "?api_key=••••••••"),
    ("Authorization: Bearer abcdefgh", "Authorization: Bearer ••••••••"),
    # URL / DSN の資格情報
    ("postgres://admin:s3cret@db:5432/x", "postgres://•••••:••••••@db:5432/x"),
    ("postgres://:s3cret@db:5432/x", "postgres://:••••••@db:5432/x"),
]

# 伏せ字になってはいけない入力 (誤爆ブロッカー)
UNMASKED_CASES = [
    "task-runner",
    "risk_assessment",
    "desk-top",
    "xsk_foo",
    "ask_me",
    "tusk_",
    "mask--test",
    "SK-ABC",
    "sk",
    "skeleton",
    "not-a-key",
    "monkey-business",
    # 長さガード付きプレフィックス (`pat` など) は一般語を巻き込まない
    "pattern matching",
    "patch notes",
    "path/to/file",
    "patriotic",
    "patriarchal",
    "eyesight",
    "cmV",
    # 連想配列のキーがシークレット名でなければ伏せない
    'config["timeout"] = "30"',
    'config["label"] = "main"',
    # ガードを満たさない短い base64 プレフィックス
    "LS0tLS1CRUdJTi",
    "AKIA",
    "dapi",
    "eyJ is a jwt prefix",
    # 時刻は Telegram Bot Token と誤認しない
    "10:30",
    "12:00:00",
    "2024-01-01 12:34:56",
    # 資格情報を持たない URL
    "http://example.com/a/b",
    "https://example.com/path/to/file",
    # `KEY=` の誤爆ブロッカー
    "monkey=abc",
    "PUBKEY=abc",
]

# 伏せ字が止まるべき入力 (区切り文字の後)
STOP_CASES = [
    ("sk-abc def", "def"),
    ("sk-abc,next", "next"),
    ("ghp_abc def", "def"),
    ("API_KEY=\"abc\" def", "def"),
    ("patABCDEFGHIJKLMN. next", "next"),
    ("postgres://admin:s3cret@db:5432/x", "5432/x"),
]

# 既存の見た目が変わっていないことを確認する入力 (ASCII / かな / 漢字 / 合字)
UNCHANGED_CASES = [
    "abcdefghijklmnopqrstuvwxyz",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "0123456789 !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~",
    "あいうえおアイウエオ漢字日本語",
    "a -> b != c => d",
    "0123456789",
]


def main() -> int:
    try:
        import uharfbuzz as hb
    except ImportError:
        print("SKIP: uharfbuzz is not installed")
        return 0

    masked_path = sys.argv[1] if len(sys.argv) > 1 else MASKED_FONT
    base_path = sys.argv[2] if len(sys.argv) > 2 else resolve_base_path(masked_path)
    if base_path == masked_path:
        print(f"FAIL: base font and masked font are the same file: {base_path}")
        return 1
    for path in (base_path, masked_path):
        if not isfile(path):
            print(f"FAIL: not found: {path}")
            return 1
    base = Shaper(hb, base_path)
    masked = Shaper(hb, masked_path)

    failures = []
    cases = 0

    for text, expected in MASKED_CASES:
        cases += 1
        actual = masked.render(text)
        if actual != expected:
            failures.append(f"masked: {text!r} -> {actual!r} (expected {expected!r})")

    # データテーブルの全プレフィックスを機械的に検証する (代表例の取りこぼしを防ぐ)
    filler = "abc123xyz789"
    for prefix, kind, lookahead in mask_module.prefix_table():
        cases += 1
        if kind == "pem":
            actual = masked.render(prefix)
            expected = prefix[: -mask_module.PEM_TAIL_LEN] + DOT * mask_module.PEM_TAIL_LEN
        else:
            # 長さガード付きのプレフィックスは lookahead 分だけ余分に必要
            assert len(filler) >= lookahead + 1, prefix
            actual = masked.render(prefix + filler)
            expected = prefix + DOT * len(filler)
        if actual != expected:
            failures.append(f"table: {prefix!r} -> {actual!r} (expected {expected!r})")

    for text in UNMASKED_CASES:
        cases += 1
        if MASK_GLYPH in masked.shape(text):
            failures.append(f"false positive: {text!r} -> {masked.render(text)!r}")

    for text, word in STOP_CASES:
        cases += 1
        glyphs = masked.shape(text)
        tail = base.shape(word)
        if glyphs[-len(tail):] != tail:
            failures.append(f"masking did not stop before {word!r}: {glyphs}")

    for text in UNCHANGED_CASES:
        cases += 1
        if base.shape(text) != masked.shape(text):
            failures.append(f"shaping changed: {text!r}")

    # グリフ順は「元のグリフ + mask.dot」でなければならない
    base_order = TTFont(base_path).getGlyphOrder()
    masked_order = TTFont(masked_path).getGlyphOrder()
    if masked_order[: len(base_order)] != base_order or masked_order[len(base_order):] != [MASK_GLYPH]:
        failures.append("glyph order changed")

    family = TTFont(masked_path)["name"].getDebugName(1)
    if family != MASKED_FAMILY:
        failures.append(f"family name: {family!r}")

    for failure in failures:
        print(f"FAIL: {failure}")
    if failures:
        return 1
    print(f"OK: {masked_path} ({cases} cases)")
    return 0


def resolve_base_path(masked_path: str) -> str:
    """MASKED 側のパスから、比較対象の通常フォントのパスを求める。"""
    base_path = masked_path.replace(MASKED_FAMILY, FAMILY)
    if base_path != masked_path:
        return base_path
    # ファイル名に "PleckJP Masked" が含まれない場合は name テーブルからスタイルを引く
    subfamily = TTFont(masked_path)["name"].getDebugName(2) or "Regular"
    return f"build/{FAMILY}-{subfamily}.ttf"


class Shaper:
    def __init__(self, hb, path: str):
        self.order = TTFont(path).getGlyphOrder()
        self.hb = hb
        self.font = hb.Font(hb.Face(hb.Blob.from_file_path(path)))

    def shape(self, text: str) -> list:
        buffer = self.hb.Buffer()
        buffer.add_str(text)
        buffer.guess_segment_properties()
        self.hb.shape(self.font, buffer)
        return [self.order[info.codepoint] for info in buffer.glyph_infos]

    def render(self, text: str) -> str:
        """mask.dot を `•` に置き換えた表示文字列を返す (1 文字 = 1 グリフ前提)。"""
        glyphs = self.shape(text)
        if len(glyphs) != len(text):
            return f"<cluster mismatch: {len(glyphs)} glyphs for {len(text)} chars>"
        return "".join(DOT if g == MASK_GLYPH else c for g, c in zip(glyphs, text))


if __name__ == "__main__":
    sys.exit(main())
