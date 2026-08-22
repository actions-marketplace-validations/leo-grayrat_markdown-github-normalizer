# markdown-github-normalizer 演示输入

这个文件故意集中保留目前已经遇到过的各种 Markdown / LaTeX 兼容问题。运行 README 中的演示命令后，再比较生成的 `input-github.md`。

## 1. Typora 正文单换行

这是第一段正文
这是第二段正文，但源码里只有一次换行

## 2. 行内公式和正文粘在一起

中文$x+y$中文

AI 也经常写成中文\(x+y\)中文

## 3. `\[ ... \]` 块公式

前文直接连接块公式
\[
E = mc^2
\]
后文也直接连接

## 4. `$$ ... $$` 内空行导致渲染失败

前文直接连接块公式
$$
A = 1

B = 2
$$
后文也直接连接

## 5. `$$ ... $$` 内的 `=` 被 Markdown 当成标题结构

$$
A + B
=
C
$$

## 6. `$$ ... $$` 空行后的 `+` 被 Markdown 当成列表

$$
A = 1

+ B
$$

## 7. LaTeX 间距命令 `\,` 和 `\;`

$a\,b\;c$

## 8. GitHub 不接受的 `\operatorname`

$\operatorname{vec}(x)$

## 9. 人工随手写出的 `\cross`

$a \cross b$

## 10. AI 对下标做了多余转义

$D\_{m\times n}$

## 11. GitHub 不支持、AI 又很喜欢写的 `\makebox`

$A \qquad \makebox[0pt][r]{第1行} \qquad B$

## 12. 加粗结束符内部混入空格

这是 **错误加粗 **后面的正文

## 13. 加粗结束后直接粘正文

**结论：**正文直接跟在后面

## 14. 这些内容不应该被误改

行内代码：`$x$ **123 ** \(x\) \cross \operatorname{vec} \makebox[0pt][r]{第1行}`

```text
$x$ **123 ** \(x\) \cross \operatorname{vec} \makebox[0pt][r]{第1行}
$$
+ 这里也只是代码
$$
```
