# PleckJP (Web フォント)

> [Hack](https://sourcefoundry.org/hack/) と [IBM Plex Sans JP](https://www.ibm.com/plex/) を合成した日本語プログラミングフォント

[PleckJP](https://github.com/ryota2357/PleckJP) の Web フォント版です。

## 使い方

### CDN (jsDelivr)

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/pleckjp@2/dist/pleckjp.css">
```

```css
pre, code {
  font-family: "PleckJP", monospace;
}
```

`pleckjp.css` には 4 スタイル (Regular, Bold, Italic, BoldItalic) すべてが含まれています。

フォントファイルはページで使われた文字とスタイルの分だけダウンロードされますが、明示的に使うスタイルだけにすることもできます。

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/pleckjp@2/dist/PleckJP-Regular.css">    <!-- 400, normal -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/pleckjp@2/dist/PleckJP-Bold.css">       <!-- 700, normal -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/pleckjp@2/dist/PleckJP-Italic.css">     <!-- 400, italic -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/pleckjp@2/dist/PleckJP-BoldItalic.css"> <!-- 700, italic -->
```

### npm

```sh
npm install pleckjp
```

```js
import "pleckjp/dist/pleckjp.css"; // 4 スタイルすべて
import "pleckjp/dist/PleckJP-Regular.css"; // Regular のみ
```

### ファイルを直接配置する

[GitHub の Release](https://github.com/ryota2357/PleckJP/releases) から `PleckJP-web_v*.zip` をダウンロードし、展開したファイルをディレクトリ構成を変えずに配置してください。
CSS は WOFF2 ファイルを相対パスで参照しています。

```html
<link rel="stylesheet" href="/fonts/pleckjp/pleckjp.css">
```

## ライセンス

SIL Open Font License 1.1 です。詳しくは [LICENSE](https://github.com/ryota2357/PleckJP/blob/main/LICENSE) を確認してください。
