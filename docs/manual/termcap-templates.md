% TERMCAP-TEMPLATES(5)
% rexwzh
% 2025年2月

## 描述
模板是 termcap 嵌入动画的 SVG 文件。使用模板可以：

* 拥有用户定义的终端颜色主题和字体
* 向动画添加终端 UI 或窗口框架
* 拥有交互式动画（例如播放/暂停按钮）

请参阅[此处](../templates.md)以获取 termcap 包含的模板库。

## 模板结构

以下是模板的基本结构：
```SVG
<?xml version="1.0" encoding="utf-8"?>
<svg id="terminal" baseProfile="full" viewBox="0 0 656 325" width="656" version="1.1"
     xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <defs>
        <termcap:template_settings xmlns:termcap="https://github.com/nbedos/termcap">
            <termcap:screen_geometry columns="82" rows="19"/>
            <termcap:animation type="css"/>
        </termcap:template_settings>
        <style type="text/css" id="generated-style">
            <!-- [snip!] -->
        </style>
        <style type="text/css" id="user-style">
            <!-- [snip!] -->
        </style>
    </defs>
    <svg id="screen" width="656" viewBox="0 0 656 323" preserveAspectRatio="xMidYMin meet">
        <!-- [snip!] -->
    </svg>
    <script type="text/javascript" id="generated-js">
        <!-- [snip!] -->
    </script>
</svg>
```

总的来说，可以识别出：

* 一个 ID 为 "terminal" 的 `svg` 元素
* 一个 `defs` 元素，其中包括：
    * 一个 termcap 特定的 `template_settings` 元素，指定：
        * 模板适用的终端大小（列数和行数）
        * termcap 使用的动画渲染方法（"css" 表示 CSS，"waapi" 表示 Web Animations API）
    * 一个 ID 为 "generated-style" 的 `style` 元素，将被 termcap 覆盖
    * 另一个 ID 为 "user-style" 的 `style` 元素，应至少包含终端颜色主题。此元素由模板创建者定义，不会被 termcap 覆盖
* 一个 ID 为 "screen" 的内部 `svg` 元素，将包含 termcap 生成的动画
* 一个 ID 为 "generated-js" 的脚本元素，将被 termcap 覆盖（仅限 "waapi" 渲染方法）


## 模板自定义
模板自定义背后的基本思想是 termcap 将保留其未修改的模板元素。因此可以：

* 通过修改 ID 为 "user-style" 的 `style` 元素的内容来自定义动画的样式
* 添加一个新的 `script` 元素以在动画中嵌入 JavaScript 代码
* 添加其他 SVG 元素，只要它们不是 ID 为 "screen" 的 `svg` 元素的子元素

希望这里提供的信息以及[默认模板的代码](https://github.com/rexwzh/termcap/blob/master/src/termcap/data/templates)足以开始自定义模板，但如果需要帮助，请随时[提交 issue](https://github.com/nbedos/termcap/issues/new)。

### 自定义颜色主题或字体
终端颜色主题必须在 ID 为 "user-style" 的 `style` 元素中指定，并且必须定义所有以下类：`foreground`，`background`，`color0`，`color1`，...，`color15`。
字体相关属性也可以与颜色主题一起指定。
请参见下面的示例。

```SVG
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" id="terminal" baseProfile="full" viewBox="0 0 656 325" width="656" version="1.1">
    <defs>
        <termcap:template_settings xmlns:termcap="https://github.com/nbedos/termcap">
            <termcap:screen_geometry columns="82" rows="19"/>
        </termcap:template_settings>
        <style type="text/css" id="generated-style">
            /* ... Snip! ... */
        </style>
        <style type="text/css" id="user-style">
            .foreground {fill: #c5c5c5;}
            .background {fill: #1c1c1c;}
            .color0 {fill: #1c1c1c;}
            .color1 {fill: #ff005b;}
            /* ... Snip! ... */
            .color15 {fill: #e5e5e5;}

            font-family: Monaco, monospace;
        </style>
    </defs>
    <svg id="screen" width="656" viewBox="0 0 656 323" preserveAspectRatio="xMidYMin meet">
    </svg>
</svg>
```
完整示例：[gjm8.svg](../../assets/templates/gjm8.svg)

### 自定义终端 UI
完整示例：[window_frame.svg](../../assets/templates/window_frame.svg)

### CSS 进度条
完整示例：[colors_progress_bar.svg](../../assets/templates/colors_progress_bar.svg)

### 嵌入 JavaScript
只需在一个新的 `script` 元素中添加代码。

完整示例：[window_frame_js](../../assets/templates/window_frame_js.svg)

### 限制动画为单次循环
对于使用 CSS 的模板，只需添加一个指定循环次数的自定义样式元素，如下所示：
```SVG
<style type="text/css" id="user-style">
    #screen_view {
        animation-iteration-count:1;
    }
</style>
```
完整示例：[gjm8_single_loop](../../assets/templates/gjm8_single_loop.svg)

## termcap 内部模板使用
为了生成最终动画，termcap 将以多种方式修改模板。
了解这种内部行为在编写自定义模板时可能会有用。

### 模板缩放
第一步是根据录制的终端大小和 `screen_geometry` 元素指定的模板大小，将模板缩放到合适的大小。
为此，termcap 将更新 ID 为 "terminal" 和 "screen" 的 `svg` 元素的 `viewBox`、`width` 和 `height` 属性。这些元素的 `height` 和 `width` 属性必须使用像素单位。

termcap 还将更新 `screen_geometry` 的 `columns` 和 `rows` 属性以匹配当前终端会话的值并保持一致。


### 样式更新
接下来，termcap 将用自己的样式表覆盖 ID 为 "generated-style" 的 `style` 元素的内容。此样式表指定了一些与文本相关的属性。请参见下面的示例。

```SVG
<style type="text/css" id="generated-style"><![CDATA[
    #screen {
        font-family: 'DejaVu Sans Mono', monospace;
        font-style: normal;
        font-size: 14px;
    }

    text {
        dominant-baseline: text-before-edge;
    }]]>
</style>
```


当设置为使用 CSS 动画时，termcap 还会为 ID 为 `screen_view` 的元素定义单个 CSS 动画。在这种情况下，样式表可能如下所示：

```SVG
<style type="text/css" id="generated-style"><![CDATA[
    #screen {
        font-family: 'DejaVu Sans Mono', monospace;
        font-style: normal;
        font-size: 14px;
    }

    text {
        dominant-baseline: text-before-edge;
    }

    @keyframes roll {
        0.000%{transform:translateY(0px)}
        1.426%{transform:translateY(-323px)}
        1.953%{transform:translateY(-646px)}
        /* Snip! */
        96.344%{transform:translateY(-29393px)}
    }

    #screen_view {
        animation-duration: var(--animation-duration);
        animation-iteration-count:infinite;
        animation-name:roll;
        animation-timing-function: steps(1,end);
    }
]]></style>
```


### 脚本更新
当设置为使用 Web Animations API 时，termcap 向 SVG 添加一个脚本元素，该元素定义对象 `termcap_vars`。此对象具有两个名为 `transforms` 和 `timings` 的属性，如下所示。
```SVG
<script type="text/javascript" id="generated-js"><![CDATA[
var termcap_vars = {
    transforms: [
        {transform: 'translate3D(0, 0px, 0)', easing: 'steps(1, end)'},
        {transform: 'translate3D(0, -323px, 0)', easing: 'steps(1, end)', offset: 0.014},
        {transform: 'translate3D(0, -646px, 0)', easing: 'steps(1, end)', offset: 0.020},
        /* Snip! */
        {transform: 'translate3D(0, -29393px, 0)', easing: 'steps(1, end)'}
    ],
    timings: {
        duration: 27349,
        iterations: Infinity
    }
};]]></script>
```
这两个属性应在另一个用户定义的脚本元素中使用，以为 ID 为 "screen_view" 的元素创建动画。这是从 window_frame_js 模板中截取的示例：

```SVG
<script type="text/javascript">
var animation = document.getElementById("screen_view").animate(
    termcap_vars.transforms,
    termcap_vars.timings
)
</script>
```


### 动画更新
最后，termcap 将使用渲染终端会话生成的代码覆盖 ID 为 "screen" 的 `svg` 元素的内容。


最终，termcap 生成的动画具有与初始模板相同的结构，这使得可以将动画用作模板（前提是动画是使用 termcap >= 0.5.0 创建的）。
