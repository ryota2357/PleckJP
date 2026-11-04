# PleckJP

> [Hack](https://sourcefoundry.org/hack/) と [IBM Plex Sans JP](https://www.ibm.com/plex/) を合成した日本語プログラミングフォント

次の 4 つのスタイルが用意されています。

- PleckJP-Regular
- PleckJP-Bold
- PleckJP-Italic
- PleckJP-BoldItalic

全てのスタイルで [Nerd Fonts](https://www.nerdfonts.com/) が合成されています。

## ダウンロード

[Release](https://github.com/ryota2357/PleckJP/releases) から zip ファイルがダウンロードできます。  
最新バージョンの zip ファイルの SHA256 checksum は `build/PleckJP_v*.sha256` にて確認ができます。

Homebrew (Mac) の場合は次のコマンドからもダウンロード可能です。

```sh
brew tap ryota2357/pleck-jp
brew install pleck-jp
```

Nix の場合は [NUR](https://nur.nix-community.org/) からインストールできます。

```nix
# flake input に追加
inputs.nur = {
  url = "github:nix-community/NUR";
  inputs.nixpkgs.follows = "nixpkgs";
};

# packages から参照
nur.repos.ryota2357.pleckjp-font
```

## スクリーンショット

![code-cpp-rust](./images/code-cpp-rust.png)

![chars](./images/chars.png)

![nerdfonts](./images/nerdfonts.png)

![gotop](./images/gotop.png)

## 関連記事

- [プログラミング用合成フォント PleckJP を作った](https://ryota2357.com/blog/2023/dev-font-pleckjp/)
- [プログラミング用合成フォント PleckJP の合成スクリプトの実装解説](https://ryota2357.com/blog/2023/pleck-jp-impl-exp/)

## ビルド

docker がインストールされている環境で次のコマンドでビルドを行います。

```sh
make
```

ビルドが完了すると `build/` ディレクトリに ttf ファイルが生成されます。
より詳しくは [HowToBuild.md](./HowToBuild.md) を確認してください。

<details>
<summary>リリースの方法</summary>

docker に加えて、python, sed (GNU sed), zip, sha256sum などが必要です。

推奨する環境の構築方法は docker と nix をインストールし、`nix develop` でシェルを起動する方法です。
nix-direnv を利用すると、ディレクトリに入るだけで自動的に環境が構築されます (`direnv allow` が必要)。

また、[Docker Hub の ryota2357/pleck-jp](https://hub.docker.com/repository/docker/ryota2357/pleckjp/general) に release イメージを公開する処理も含まれています。
不要な場合は適宜 `Makefile` を修正してください。

次のコマンドでリリースビルドを行います。

```sh
make release
```

ビルドが完了すると `build/` ディレクトリに .ttf, .zip, .sha256 ファイルが生成されます。

</details>

## Masked バリアント (API キーの伏せ字)

代表的なプロバイダーの API キーを伏せ字で表示する `PleckJP Masked` ファミリーを生成できます。
207 プレフィックス (OpenAI, Anthropic, GitHub, GitLab, Slack, Stripe, AWS, Google, Atlassian,
Cloudflare, DigitalOcean, Datadog, npm, Vercel, Supabase, Sentry, Hugging Face, Airtable,
Databricks, 1Password, PyPI, NuGet, JFrog, JWT, age, Bitcoin など) と、1309 通りの代入コンテキスト
(`KEY="..."`, `TOKEN=...`, `password: ...`, `--token=...`, `config["TOKEN"] = "..."`,
`"api_key": "..."` (JSON / dict のクォートされたキー) など)、
HTTP ヘッダ (`Authorization: Bearer`)、
URL / DSN の資格情報 (`postgres://user:pass@host`)、Telegram Bot Token、Discord Webhook、
PEM ヘッダと、base64 で包んだ PEM / OpenSSH 秘密鍵に対応しています。
通常の `make` や `make release` では生成されず、次のコマンドで明示的にビルドします。
入力に `build/PleckJP-*.ttf` を使うので、先に通常のビルドを済ませてください。

```sh
make masked   # build/PleckJP Masked-*.ttf が生成される
```

表示例:

```text
OPENAI_API_KEY=sk-proj-AbCdEf123456   ->   OPENAI_API_KEY=••-••••-••••••••••••
gh auth token: ghp_16C7e42F292c6912   ->   gh auth token: •••_••••••••••••••••
SLACK=xoxb-1234-5678-abcdef           ->   SLACK=xoxb-••••-••••-••••••
AIzaSyDxYz1234567890abcdefg           ->   AIza•••••••••••••••••••••••
patABCDEFGHIJKLMN.1234567890abcdef    ->   pat••••••••••••••.••••••••••••••••
123456789:AAHdqTcvCH1vGWJxfSeofSAs0    ->   123456789:•••••••••••••••••••••••••
postgres://admin:s3cret@db:5432/x     ->   postgres://•••••:••••••@db:5432/x
cmVmdGtuOjAxOjE3NjU0Njg1MjY6SlBoYWZ4  ->   cmVmdG••••••••••••••••••••••••••••••
LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQ==
                                      ->   LS0tLS1CRUdJTi••••••••••••••••••••••••••••==
config["API_TOKEN"] = "7MMVuQhABCDEF" ->   config["API_TOKEN"] = "•••••••••••••"
"api_key": "DfXtE8h7VFL76snkPR3CAKK"   ->   "api_key": "•••••••••••••••••••••••"
```

- 伏せ字になるのは、対応プレフィックスの直後に続く英数字です (`oc_sk_...` のような `_sk_` 連結も対象)
- 直前が英字の場合は伏せ字にしません (`task-runner`, `risk_assessment`, `desk-top` はそのまま)
- 長いプレフィックスが優先されます (`sk-ant-api03-XyZ` はプレフィックス全体を残して本文だけ伏せる)
- 伏せ字は空白・クォートなどの記号で止まります (`sk-abc def` の `def` はそのまま)
- 区切り (`-`, `_`, `:`, `/`, `.`) を挟んでも伏せ字は継続します
  (`xoxb-1234-5678-abc`, `patXXX.YYY` (Airtable), `eyJ...eyJ...` (JWT) は全体が伏せ字)
- `pat` / `eyJ` / `cmV` のような短く一般語と衝突しうるプレフィックスは、直後に十分な長さの
  英数字があるときだけ伏せ字にします (`pattern`, `path`, `patriotic`, `eyesight` はそのまま)
- URL / DSN (`postgres://`, `mysql://`, `mongodb://`, `redis://`, `amqp://` など) は
  ユーザー情報とパスワードを伏せ字にします。資格情報を持たない URL でもホスト名が
  伏せ字になります (GSUB では「@ が後ろにあるか」を可変長で判定できないため)
- `10:30` のような時刻は Telegram Bot Token と誤認しません (トークン側に 11 文字以上を要求)
- PEM ヘッダは末尾の `-----` だけが伏せ字になります (生の PEM 本文は行をまたぐため対象外)
- PEM 全体を base64 で包んだ 1 行の形 (`LS0tLS1CRUdJTi...`) と base64 の `openssh-key-`
  (`b3BlbnNzaC1rZXkt...`) は、base64 プレフィックスをトリガーに英数字の連続を伏せ字にします
- 連想配列 / 辞書のキー代入 (`config["API_TOKEN"] = "..."`, `cfg['TOKEN'] = '...'`) も
  シークレット名のキーに限って伏せ字にします (`config["timeout"] = "30"` はそのまま)
- 代入コンテキスト (`KEY="..."`, `token: ...`) が先に当たると、値の先頭にある
  プロバイダープレフィックスも伏せ字になります (`OPENAI_API_KEY=sk-proj-...` は
  `OPENAI_API_KEY=••-••••-...`)。プレフィックスを残したい場合は値だけを別行に置いてください
- `re_` や `pa-` のような短いプレフィックスは一般語にも当たります (`re_runner` は伏せ字)
- あくまで描画だけの変化です。コピーしたテキストは元のままなので、貼り付け先には正しいキーが入ります

プレフィックスの一覧は `src/fonttools_/mask.py` のデータテーブル
(`HYPHEN_PREFIXES` / `UNDERSCORE_PREFIXES` / `DOT_PREFIXES` / `GUARDED_PREFIXES` /
`URL_PREFIXES` / `HEADER_PREFIXES` / `CONTEXT_KEYS` / `PEM_HEADERS`)
にまとまっています。追加したいプロバイダーがあれば、そこに 1 行足すだけで反映されます。

仕組みは OpenType の `calt` (Contextual Alternates) フィーチャーを 1 つ追加しているだけで、
既存のフィーチャーやグリフには一切手を加えていません (追加グリフは `mask.dot` の 1 つだけ)。
そのため `calt` を無効にすれば、フォントを切り替えずに元の表示へ戻せます。

```jsonc
// 例: VS Code の settings.json
"editor.fontLigatures": "'calt' 0"
```

`calt` を適用するかどうかは描画側の実装に依存します。HarfBuzz を使うターミナルやエディタ
(WezTerm, Kitty, VS Code など) では既定で有効です。

動作確認は `src/fonttools_/mask_test.py` で行えます (uharfbuzz が必要。未インストール時は SKIP)。

```sh
python3 src/fonttools_/mask_test.py
```

## ライセンス

- フォントの合成スクリプトは MIT License にてライセンスされています。
- 合成元のフォントデータなどは別のライセンスが適用されています。
- 詳しくは [LICENSE](./LICENSE) を確認してください。
