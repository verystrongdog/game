#!/usr/bin/env python3
# grilling #87 — 提取下载 HTML 的正文纯文本（尽力提取 <p> 文本，供本地快速阅读）
# 用法: python3 extract_text.py <目录>
import sys, os, re, html
from html.parser import HTMLParser

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0
        self.tag_stack = []
    def handle_starttag(self, tag, attrs):
        self.tag_stack.append(tag)
        if tag in ('script', 'style', 'noscript', 'svg', 'iframe'):
            self.skip += 1
        if tag in ('p', 'br', 'div', 'h1', 'h2', 'h3', 'li', 'blockquote'):
            self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'noscript', 'svg', 'iframe') and self.skip > 0:
            self.skip -= 1
        if tag in ('p', 'div', 'h1', 'h2', 'h3', 'li', 'blockquote'):
            self.parts.append('\n')
    def handle_data(self, data):
        if self.skip == 0:
            self.parts.append(data)

def extract(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        src = f.read()
    p = TextExtractor()
    try:
        p.feed(src)
    except Exception:
        pass
    text = ''.join(p.parts)
    text = html.unescape(text)
    # 压缩空行
    text = re.sub(r'[ \t\u3000]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    return text.strip()

def main():
    d = sys.argv[1]
    for fn in sorted(os.listdir(d)):
        if not fn.endswith('.html'):
            continue
        base = fn[:-5]
        txt = extract(os.path.join(d, fn))
        out = os.path.join(d, base + '.txt')
        with open(out, 'w', encoding='utf-8') as f:
            f.write(f"# 正文提取（自动生成，质量参考）\n# 来源 HTML: {fn}\n\n{txt}\n")
        print(f"{fn}: {len(txt)} chars")

if __name__ == '__main__':
    main()
