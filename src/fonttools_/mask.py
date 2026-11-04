"""API キーの伏せ字 (masked) バリアントを生成する。

`build/PleckJP-*.ttf` を入力に取り、GSUB へ `calt` フィーチャーを 1 つだけ追加した
`PleckJP Masked-*.ttf` を出力する。既存のフィーチャー・ルックアップには一切触れない
(新しいルックアップは LookupList の末尾に追加するので既存インデックスは不変)。

伏せ字の対象は、下のデータテーブルに並ぶプレフィックスの直後に続く英数字の連続。
テーブルの出発点は ObelMonoMasked-Regular.ttf の GSUB (ccmp の ChainContextSubst) から
抽出した全プレフィックスで、そこへ PleckJP 側で不足していたものを追加している
(現在 207 プレフィックス + 847 の代入コンテキスト)。

    sk-ant-api03-XXXX   ->  sk-•••-•••••-••••
    ghp_abc123          ->  ghp_••••••
    cmVmdGtuOjAxOjE3NjU ->  cmVmdG••••••••••••
    LS0tLS1CRUdJTiBSU0E ->  LS0tLS1CRUdJTi•••••••
    config["TOKEN"] = "ab" ->  config["TOKEN"] = "••"
    xoxb-123-abc        ->  xoxb-•••-•••
    task-runner         ->  task-runner      (誤爆しない)
    oc_sk_abc123        ->  oc_sk_••••••
    AIzaSyDxYz1234      ->  AIza••••••••••
    pattern matching    ->  pattern matching (長さガードで誤爆しない)

Note: ObelMonoMasked は「キーの後半だけを伏せる」など独自の判定を持つが、ここでは
      PleckJP 既存の素直な挙動 (プレフィックス直後の英数字の連続を最後まで潰す) を
      全プレフィックスに適用する。プレフィックスの一覧だけを Obel と揃える。
Note: 伏せ字は英数字 + 区切り (`-`, `_`, `:`, `/`, `.`) の範囲で継続する。空白・クォート・
      `,` などの記号で止まるので、`sk-abc def` の `def` はそのまま残る。
Note: PEM ヘッダは末尾の `-----` だけを伏せ字にする (Obel と同じ)。生の PEM 本文は
      行をまたぐため GSUB では追跡できず、伏せ字にならない。ただし PEM 全体を
      base64 で包んだ 1 行の形 (`LS0tLS1CRUdJTi...`) は、base64 プレフィックスを
      トリガーにして英数字の連続を伏せ字にする。

使い方:

    python3 src/fonttools_/mask.py                       # build/ の 4 スタイル全部
    python3 src/fonttools_/mask.py IN.ttf OUT.ttf        # 1 ファイルだけ
"""

import sys
from copy import deepcopy
from os.path import join

from fontTools.otlLib.builder import buildSingleSubstSubtable
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables as ot

STYLES = ("Regular", "Bold", "Italic", "BoldItalic")

FAMILY = "PleckJP"
MASKED_FAMILY = "PleckJP Masked"
BUILD_DIR = "build"

FEATURE_TAG = "calt"
MASK_GLYPH = "mask.dot"

# 伏せ字にする文字 (キー本体に現れる英数字のみ。記号は残す)
ALNUM_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
LETTER_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGIT_CHARS = "0123456789"

# 伏せ字を継続させる連結記号 (キー内部に現れる区切り。空白やクォートで伏せ字は止まる)
# 伏せ字の直後に来たら続きも伏せ字にする区切り。
# `:` `@` をはさんだ資格情報 (URL / DSN) と `/` 区切りの Discord Webhook、
# `.` 区切りの Airtable / JWT (`patXXXX.hex`, `eyJ...eyJ...sig`) を 1 つの規則で扱う。
# Note: 区切りの後ろが英数字のときだけ継続するので、`. ` のように空白が入れば止まる。
MASKED_SEPARATORS = ("-", "_", ":", "/", ".")

# Telegram Bot Token (`<数字ID>:<トークン>`) と誤認しないために要求する英数字の最小数
TELEGRAM_MIN_TOKEN = 11

# PEM ヘッダ (末尾の `-----` を伏せ字にする)
PEM_HEADERS = (
    "BEGIN DSA PRIVATE KEY-----",
    "BEGIN EC PRIVATE KEY-----",
    "BEGIN ENCRYPTED PRIVATE KEY-----",
    "BEGIN OPENSSH PRIVATE KEY-----",
    "BEGIN PGP PRIVATE KEY BLOCK-----",
    "BEGIN PRIVATE KEY-----",
    "BEGIN RSA PRIVATE KEY-----",
)

# `-` 終端のプロバイダープレフィックス (OpenAI / Anthropic / GitLab / Slack / Stripe ...)
HYPHEN_PREFIXES = (
    "CFPAT-", "GOCSPX-", "HRKU-", "NRAK-",
    "NRII-", "PMAK-", "access-development-", "access-production-",
    "access-sandbox-", "csk-", "fc-", "glagent-",
    "glcbt-", "gldt-", "glffct-", "glft-",
    "glimt-", "gloas-", "glpat-", "glptt-",
    "glrt-", "glrtr-", "glsoat-", "glwt-",
    "nvapi-", "pa-", "pat-eu1-", "pat-na1-",
    "pplx-", "pul-", "pypi-", "sk-", "sk-admin-",
    "sk-ant-", "sk-ant-admin01-", "sk-ant-api01-", "sk-ant-api03-",
    "sk-ant-oat01-", "sk-helicone-", "sk-lf-", "sk-or-v1-",
    "sk-proj-", "sk-proj-fedramp-", "sk-svcacct-", "sk-svcacct-fedramp-",
    "sq0atp-", "sq0csb-", "sq0csp-", "tvly-",
    "xai-", "xapp-", "xoxa-", "xoxb-",
    "xoxe-", "xoxe.xapp-", "xoxe.xoxb-", "xoxe.xoxp-",
    "xoxo-", "xoxp-", "xoxr-", "xoxs-",
    "xwfp-",
)

# `_` 終端のプロバイダープレフィックス (GitHub / GitLab / Stripe / npm / Vercel ...)
UNDERSCORE_PREFIXES = (
    "CCIPAT_", "CCIPRJ_", "CLOJARS_", "aph0_",
    "api_org_", "bkaa_", "bkaj_", "bkar_",
    "bkct_", "bkjat_", "bkpat_", "bkps_",
    "bkpt_", "bktx_", "bkua_", "cfast_",
    "cfat_", "cfk_", "cfoat_", "cfut_",
    "cio_tp_", "crsr_", "dckr_oat_", "dckr_pat_",
    "ddapp_", "ddpat_", "ddsat_", "doo_v1_",
    "dop_v1_", "dor_v1_", "figd_", "fm1a_",
    "fm1r_", "fm2_", "fo1_", "fw_",
    "gho_", "ghp_", "ghr_", "ghs_",
    "ghu_", "github_pat_", "glc_", "glsa_",
    "gsk_", "hf_", "lin_api_", "lin_oauth_",
    "lsv2_pt_", "lsv2_sk_", "lsv2_tr_", "nfb_",
    "nfc_", "nfo_", "nfp_", "nfu_",
    "npm_", "ntn_", "ops_", "pcsk_", "pha_",
    "phr_", "phs_", "phx_", "pscale_app_secret_",
    "pscale_oauth_", "pscale_pw_", "pscale_tkn_", "r8_",
    "re_", "rk_live_", "rk_test_", "rubygems_",
    "sb_secret_", "sbp_", "sgp_", "shpat_",
    "shpca_", "shppa_", "shpss_", "sk_",
    "sk_live_", "sk_org_", "sk_test_", "sntrys_",
    "sntryu_", "sqa_", "sqp_", "squ_",
    "tfp_", "tgp_v1_", "vca_", "vck_",
    "vcp_", "vcr_", "whsec_",
)

# `.` 終端のプロバイダープレフィックス (Google OAuth / DigitalOcean / HashiCorp ...)
DOT_PREFIXES = (
    ".atlasv1.", "AQ.", "SG.", "dp.audit.",
    "dp.ct.", "dp.pt.", "dp.sa.", "dp.said.",
    "dp.scim.", "dp.st.", "hvb.", "hvr.",
    "hvs.", "ya29.",
)

# 終端記号を持たないプレフィックス (Asana の PAT)
BARE_PREFIXES = ("Q~",)

# 終端記号を持たず、しかも短いため一般語と衝突しうるプレフィックス。
# (プレフィックス, 直後に必要な英数字の最小数) の形で持ち、lookahead で長さを要求する。
# 例: `pat` は `pattern` (後続 4 文字) を巻き込まないが、Airtable の PAT (`pat` + 14) は伏せる。
GUARDED_PREFIXES = (
    ("AGE-SECRET-KEY-1", 8),
    ("AIza", 8),
    ("AKIA", 8),
    ("ATATT", 8),
    ("cmV", 12),
    ("cmVmdG", 4),
    ("dapi", 8),
    ("eyJ", 8),
    ("oy2", 8),
    ("pat", 12),
    ("xprv", 8),
    # base64 でエンコードされた PEM / OpenSSH 秘密鍵のヘッダ
    # (`LS0tLS1CRUdJTi` = "-----BEGIN ", `b3BlbnNzaC1rZXkt` = "openssh-key-")。
    # 16 文字が固定なので一般語との衝突は実質なく、後続の長さガードは 4 で足りる。
    ("LS0tLS1CRUdJTi", 4),
    ("b3BlbnNzaC1rZXkt", 4),
)

# URL / DSN 形式のプレフィックス。直後のユーザー情報を伏せ字にする
# (`postgres://admin:secret@host` の `admin` と、`MASKED_SEPARATORS` 規則による `secret`)。
# Note: 資格情報を持たない `postgres://localhost:5432/db` でもホスト名が伏せ字になる
#       (GSUB では「@ が後ろにあるか」を可変長で判定できないため)。
URL_PREFIXES = (
    "amqp://", "amqps://", "discord.com/api/webhooks/",
    "discordapp.com/api/webhooks/", "mongodb://", "mongodb+srv://",
    "mysql://", "postgres://", "postgresql://",
    "redis://", "rediss://",
)

# HTTP ヘッダ形式 (値が続くときだけ伏せ字にする)
HEADER_PREFIXES = (
    "Authorization: Basic ",
    "Authorization: Bearer ",
    "authorization: Bearer ",
)

# `KEY="..."` / `KEY: '...'` のような代入コンテキスト。値が続くときだけ伏せ字にする。
# ベース名 × CONTEXT_TEMPLATES で展開する。
CONTEXT_KEYS = (
    "--access-token", "--api-key", "--auth-token", "--password",
    "--secret", "--token", "ACCESS_KEY", "ACCOUNT_KEY",
    "ADMIN_KEY", "APIKEY", "API_KEY", "APP_KEY", "AccountKey",
    "AUTH_KEY", "ApiKey", "DEPLOY_KEY", "ENCRYPTION_KEY",
    "HMAC_KEY", "JWT_KEY", "KEY", "LICENSE_KEY",
    "MASTER_KEY", "MYSQL_PWD", "PASSWD", "PASSWORD",
    "PGPASSWORD", "PRIVATE_KEY", "Password", "SECRET",
    "SECRET_KEY", "SERVICE_KEY", "SERVICE_ROLE_KEY", "SIGNING_KEY",
    "SUBSCRIPTION_KEY", "Secret", "TOKEN", "Token",
    "_KEY", "_access_token", "_api_key", "_apikey",
    "_auth", "_authToken", "_auth_token", "_client_secret",
    "_passwd", "_password", "_refresh_token", "_secret",
    "_secret_key", "accessKey", "accessToken", "access_key",
    "access_token", "api-key", "apiKey", "apiSecret",
    "api_key", "api_secret", "apikey", "authToken",
    "auth_token", "aws_secret_access_key", "aws_session_token", "clientSecret",
    "client_secret", "passwd", "password", "privateKey",
    "private_key", "private_key_id", "refreshToken", "refresh_token",
    "secret", "secretKey", "secret_key", "token",
)

# 代入の書き方 (値の直前で終わる形だけを並べる)
# `=` / ` = ` / `: ` はクォートなしの値 (`TOKEN=abc`, `aws_session_token = abc`,
# `password: abc`) を対象にする。`KEY=` は直前が英字なら誤爆ブロッカーが弾く
# (`MONKEY=` は伏せない)。
CONTEXT_TEMPLATES = (
    '="',
    "='",
    ': "',
    ": '",
    "=",
    " = ",
    ": ",
    # 連想配列 / 辞書のキー代入 (`config["API_TOKEN"] = "..."`, `cfg['TOKEN'] = '...'`)
    '"] = "',
    '\'"] = \'',
    "'\'] = \"",
    "'] = '",
)

# mask.dot のアウトラインを借りる元グリフ (先頭から順に探す)
MASK_SOURCE_GLYPHS = ("uni2022", "period", "uni25CF", "uni0041")

# PEM ヘッダの末尾で伏せる `-----` の長さ
PEM_TAIL_LEN = 5


def main() -> None:
    args = sys.argv[1:]
    if not args:
        for style in STYLES:
            src = join(BUILD_DIR, f"{FAMILY}-{style}.ttf")
            dst = join(BUILD_DIR, f"{MASKED_FAMILY}-{style}.ttf")
            convert(src, dst)
        return
    if len(args) != 2:
        raise SystemExit("usage: mask.py [INPUT.ttf OUTPUT.ttf]")
    convert(args[0], args[1])


def convert(src_path: str, dst_path: str) -> None:
    font = TTFont(src_path)
    build_masked_variant(font)
    font.save(dst_path)
    print(f"masked: {src_path} -> {dst_path}")


def build_masked_variant(font: TTFont) -> None:
    gsub = font["GSUB"].table
    if FEATURE_TAG in {r.FeatureTag for r in gsub.FeatureList.FeatureRecord}:
        raise SystemExit(f"'{FEATURE_TAG}' already exists in {font.reader.file.name}")

    cmap = font.getBestCmap()
    mask_glyph = add_mask_glyph(font)
    lookups = add_mask_lookups(font, gsub, cmap, mask_glyph)
    add_feature(gsub, FEATURE_TAG, lookups)
    rename_family(font)


# ---------------------------------------------------------------- glyph


def add_mask_glyph(font: TTFont) -> str:
    """`mask.dot` を追加する。アウトラインは既存グリフを流用し、字幅は半角セルに合わせる。"""
    glyf = font["glyf"]
    hmtx = font["hmtx"]

    if MASK_GLYPH in font.getGlyphOrder():
        return MASK_GLYPH

    source = next((n for n in MASK_SOURCE_GLYPHS if n in glyf.glyphs), None)
    if source is None:
        raise SystemExit("no glyph to use as the mask dot")

    order = list(font.getGlyphOrder())
    order.append(MASK_GLYPH)
    font.setGlyphOrder(order)

    glyf.glyphs[MASK_GLYPH] = deepcopy(glyf[source])
    advance, lsb = hmtx[source]
    hmtx[MASK_GLYPH] = (advance, lsb)
    # Note: cmap には登録しない (伏せ字専用の内部グリフ)。
    #       サブセット化するツールでは落とされる可能性があるため、その場合は cmap 登録が必要。
    return MASK_GLYPH


# --------------------------------------------------------------- lookups


def prefix_table() -> list:
    """(プレフィックス, 種別, lookahead 長) を長い順に並べて返す。

    長いプレフィックスを先に置かないと `sk-` が `sk-ant-api03-` を食ってしまい、
    後続のルールが到達不能になる。種別は "alnum" (直後の英数字を伏せる)、
    "guarded" (直後に十分な長さの英数字があるときだけ伏せる)、
    "pem" (末尾の `-----` を伏せる) の 3 種類。
    lookahead 長は「入力 1 文字の後ろに追加で要求する英数字の数」。
    """
    seen = {}
    for prefix in (
        HYPHEN_PREFIXES
        + UNDERSCORE_PREFIXES
        + DOT_PREFIXES
        + BARE_PREFIXES
        + URL_PREFIXES
        + HEADER_PREFIXES
    ):
        seen[prefix] = ("alnum", 0)
    for prefix, min_alnum in GUARDED_PREFIXES:
        seen[prefix] = ("guarded", min_alnum - 1)
    for key in CONTEXT_KEYS:
        for template in CONTEXT_TEMPLATES:
            seen[f"{key}{template}"] = ("alnum", 0)
    for header in PEM_HEADERS:
        seen[header] = ("pem", 0)
    return sorted(
        ((prefix, kind, lookahead) for prefix, (kind, lookahead) in seen.items()),
        key=lambda item: (-len(item[0]), item[0]),
    )


def add_mask_lookups(font: TTFont, gsub: ot.GSUB, cmap: dict, mask_glyph: str) -> list:
    """calt で使うルックアップを末尾に追加し、そのインデックスを返す。

    ルックアップは「先頭グリフごとのグループ」に分割する。1 つの巨大な chain lookup に
    すると、HarfBuzz が各文字位置で全サブテーブルを総当たりするため、テキスト描画が
    目に見えて遅くなる (実測: 785 プレフィックスを 1 lookup に詰めると 3 倍強)。
    分割しても結果は同じで、calt は全ルックアップを左から右へ順に適用するので、
    前半 (トリガー) の伏せ字を後半 (継続) のルックアップが引き継げる。
    """
    glyph = lambda ch: cmap[ord(ch)]  # noqa: E731

    alnum = [glyph(ch) for ch in ALNUM_CHARS]
    letter = [glyph(ch) for ch in LETTER_CHARS]
    digit = [glyph(ch) for ch in DIGIT_CHARS]

    # 誤爆ブロッカー用の無変換ルックアップ (letter を letter に置換するだけ)
    noop = add_lookup(gsub, 1, [buildSingleSubstSubtable({glyph("s"): glyph("s")})])
    mask = add_lookup(
        gsub, 1, [buildSingleSubstSubtable({g: mask_glyph for g in alnum})]
    )
    # PEM ヘッダ末尾の `-----` を伏せるためのルックアップ
    pem = add_lookup(gsub, 1, [buildSingleSubstSubtable({glyph("-"): mask_glyph})])

    groups = {}
    for prefix, kind, lookahead in prefix_table():
        chars = [glyph(ch) for ch in prefix]
        rules = groups.setdefault(prefix[0], [])
        # 1) ブロッカー: 直前が英字なら何もしない (task- / risk_ / xsk_ を弾く)
        rules.append(chain_rule(font, [letter], [[c] for c in chars], [(0, noop)]))
        if kind == "pem":
            # 2) PEM: ヘッダ末尾の `-----` を伏せ字にする
            records = [(i, pem) for i in range(len(chars) - PEM_TAIL_LEN, len(chars))]
            rules.append(chain_rule(font, [], [[c] for c in chars], records))
        else:
            # 2) トリガー: プレフィックス直後の英数字 1 文字を伏せ字にする
            rules.append(
                chain_rule(
                    font,
                    [],
                    [[c] for c in chars] + [alnum],
                    [(len(chars), mask)],
                    [alnum] * lookahead,
                )
            )

    # 3) 継続: 伏せ字の直後の英数字も伏せ字にする (英数字の連続を最後まで潰す)。
    #    区切り (- _ : / .) を挟んでも継続させるが、区切りの直前が伏せ字である
    #    ことを条件にする (task-runner のような通常のハイフン連結を巻き込まない)。
    tail = [chain_rule(font, [[mask_glyph]], [alnum], [(0, mask)])]
    for separator in MASKED_SEPARATORS:
        tail.append(
            chain_rule(font, [[glyph(separator)], [mask_glyph]], [alnum], [(0, mask)])
        )
    # 4) URL / DSN の資格情報 (`scheme://:password@host` のようにユーザー名が空の形)
    tail.append(
        chain_rule(
            font,
            [[glyph("/")], [glyph("/")]],
            [[glyph(":")], alnum],
            [(1, mask)],
        )
    )
    # 5) Telegram Bot Token (`<数字ID>:<トークン>`)。時刻 (`12:30`) を巻き込まないよう
    #    トークン側に十分な長さを要求する。
    tail.append(
        chain_rule(
            font,
            [digit],
            [[glyph(":")], alnum],
            [(1, mask)],
            [alnum] * (TELEGRAM_MIN_TOKEN - 1),
        )
    )

    return [add_lookup(gsub, 6, rules) for _, rules in sorted(groups.items())] + [
        add_lookup(gsub, 6, tail)
    ]


def add_lookup(gsub: ot.GSUB, lookup_type: int, subtables: list) -> int:
    lookup = ot.Lookup()
    lookup.LookupType = lookup_type
    lookup.LookupFlag = 0
    lookup.SubTable = subtables
    lookup.SubTableCount = len(subtables)
    lookups = gsub.LookupList.Lookup
    lookups.append(lookup)
    gsub.LookupList.LookupCount = len(lookups)
    return len(lookups) - 1


def chain_rule(
    font: TTFont, backtrack: list, inputs: list, records: list, lookahead: list = None
) -> ot.ChainContextSubst:
    """ChainContextSubst (format 3) を 1 ルール分組み立てる。

    backtrack は「直前のグリフ」を先頭にした逆順のリスト、inputs は入力シーケンス
    (各要素はグリフ名のリスト = クラス)、records は (sequenceIndex, lookupIndex)、
    lookahead は入力シーケンスの後ろに要求するグリフ (同形式、任意)。
    """
    subtable = ot.ChainContextSubst()
    subtable.Format = 3
    subtable.BacktrackCoverage = [coverage(font, g) for g in backtrack]
    subtable.InputCoverage = [coverage(font, g) for g in inputs]
    subtable.LookAheadCoverage = [coverage(font, g) for g in (lookahead or [])]
    subtable.SubstLookupRecord = [subst_record(i, lookup) for i, lookup in records]
    return subtable


def coverage(font: TTFont, glyphs: list) -> ot.Coverage:
    cov = ot.Coverage()
    cov.glyphs = sorted(set(glyphs), key=font.getGlyphID)
    return cov


def subst_record(sequence_index: int, lookup_index: int) -> ot.SubstLookupRecord:
    record = ot.SubstLookupRecord()
    record.SequenceIndex = sequence_index
    record.LookupListIndex = lookup_index
    return record


# --------------------------------------------------------------- feature


def add_feature(gsub: ot.GSUB, tag: str, lookup_indices: list) -> None:
    """FeatureList に tag を追加し、全 LangSys から参照させる。

    FeatureList はタグの昇順で並んでいる必要があるため挿入位置を保ち、
    FeatureIndex の繰り上がりを全 LangSys に反映する。
    """
    records = gsub.FeatureList.FeatureRecord
    tags = [r.FeatureTag for r in records]
    position = sum(1 for t in tags if t < tag)

    feature = ot.Feature()
    feature.FeatureParams = None
    feature.LookupListIndex = lookup_indices
    feature.LookupCount = len(lookup_indices)

    record = ot.FeatureRecord()
    record.FeatureTag = tag
    record.Feature = feature

    records.insert(position, record)
    gsub.FeatureList.FeatureCount = len(records)

    remap = [i if i < position else i + 1 for i in range(len(records) - 1)]
    for lang_sys in all_lang_systems(gsub):
        indices = [remap[i] for i in lang_sys.FeatureIndex]
        indices.insert(sum(1 for i in indices if i < position), position)
        lang_sys.FeatureIndex = indices
        lang_sys.FeatureCount = len(indices)


def all_lang_systems(gsub: ot.GSUB) -> list:
    lang_systems = []
    for script_record in gsub.ScriptList.ScriptRecord:
        script = script_record.Script
        if script.DefaultLangSys is not None:
            lang_systems.append(script.DefaultLangSys)
        lang_systems.extend(r.LangSys for r in script.LangSysRecord)
    return lang_systems


# ------------------------------------------------------------------ name


def rename_family(font: TTFont) -> None:
    """ファミリー名を `PleckJP Masked` にする (スタイル名はそのまま)。"""
    name = font["name"]
    family = name.getDebugName(1) or FAMILY
    if not family.startswith(FAMILY):
        raise SystemExit(f"unexpected family name: {family!r}")
    subfamily = name.getDebugName(2) or "Regular"
    suffix = family[len(FAMILY):]  # 空文字 (通常) か既存のサフィックス
    masked_family = f"{MASKED_FAMILY}{suffix}"

    for record in list(name.names):
        if record.nameID == 1:
            name.setName(masked_family, 1, record.platformID, record.platEncID, record.langID)
        elif record.nameID == 3:
            unique_id = (name.getDebugName(3) or "").replace(
                f"{family} {subfamily}", f"{masked_family} {subfamily}"
            )
            name.setName(unique_id, 3, record.platformID, record.platEncID, record.langID)
        elif record.nameID == 4:
            name.setName(
                f"{masked_family} {subfamily}",
                4,
                record.platformID,
                record.platEncID,
                record.langID,
            )
        elif record.nameID == 6:
            postscript_name = f"{masked_family.replace(' ', '')}-{subfamily}"
            name.setName(postscript_name, 6, record.platformID, record.platEncID, record.langID)


if __name__ == "__main__":
    main()
