import re, html as html_mod

md_path = r'D:\ObsidianDB\wiki\research\auth_evolution_deep_dive.md'
out_path = r'D:\ObsidianDB\outputs\auth_evolution_deep_dive.html'

with open(md_path, 'r', encoding='utf-8') as f:
    md = f.read()

# Remove YAML frontmatter
md = re.sub(r'^---\n.*?\n---\n', '', md, flags=re.DOTALL)

# Collect Mermaid blocks BEFORE any conversion
mermaid_blocks = []
def save_mermaid(m):
    mermaid_blocks.append(m.group(1))
    return f'%%MERMAID_{len(mermaid_blocks)-1}%%'
md = re.sub(r'```mermaid\n(.*?)```', save_mermaid, md, flags=re.DOTALL)

# Convert markdown to HTML
def convert_md(text):
    out = []
    in_code = False
    in_table = False
    table_rows = []
    code_lines = []
    code_lang = ''

    for line in text.split('\n'):
        # Code blocks
        if line.startswith('```'):
            if in_code:
                out.append(f'<pre><code>{"".join(code_lines).rstrip()}</code></pre>')
                code_lines = []
                code_lang = ''
                in_code = False
            else:
                in_code = True
                code_lang = line[3:].strip()
            continue
        if in_code:
            code_lines.append(line + '\n')
            continue

        # Tables
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                in_table = True
                table_rows = []
            if '|---|' in line or '| -- |' in line or '|----|' in line:
                continue  # Skip separator rows
            table_rows.append(line)
            continue
        elif in_table and line.strip() == '':
            in_table = False
            if table_rows:
                html_rows = []
                for i, row in enumerate(table_rows):
                    tag = 'th' if i == 0 else 'td'
                    cells = row.strip().strip('|').split('|')
                    html_cells = ''.join(f'<{tag}>{c.strip()}</{tag}>' for c in cells)
                    html_rows.append(f'<tr>{html_cells}</tr>')
                if len(html_rows) > 1:
                    out.append(f'<table><thead>{html_rows[0]}</thead><tbody>{"".join(html_rows[1:])}</tbody></table>')
                else:
                    out.append(f'<table>{"".join(html_rows)}</table>')
                table_rows = []
            continue
        elif in_table:
            in_table = False
            if table_rows:
                html_rows = []
                for i, row in enumerate(table_rows):
                    tag = 'th' if i == 0 else 'td'
                    cells = row.strip().strip('|').split('|')
                    html_cells = ''.join(f'<{tag}>{c.strip()}</{tag}>' for c in cells)
                    html_rows.append(f'<tr>{html_cells}</tr>')
                if len(html_rows) > 1:
                    out.append(f'<table><thead>{html_rows[0]}</thead><tbody>{"".join(html_rows[1:])}</tbody></table>')
                else:
                    out.append(f'<table>{"".join(html_rows)}</table>')
                table_rows = []

        # Headings
        if line.startswith('# ') and not line.startswith('## '):
            out.append(f'<h1>{line[2:].strip()}</h1>')
        elif line.startswith('## '):
            out.append(f'<h2>{line[3:].strip()}</h2>')
        elif line.startswith('### '):
            out.append(f'<h3>{line[4:].strip()}</h3>')
        elif line.startswith('#### '):
            out.append(f'<h4>{line[5:].strip()}</h4>')
        elif line.startswith('##### '):
            out.append(f'<h5>{line[6:].strip()}</h5>')
        # Horizontal rule
        elif line.strip() == '---':
            out.append('<hr>')
        # Regular paragraph
        elif line.strip():
            # Inline formatting
            line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
            line = re.sub(r'\*(.+?)\*', r'<em>\1</em>', line)
            line = re.sub(r'`([^`]+)`', r'<code>\1</code>', line)
            out.append(f'<p>{line}</p>')
        else:
            out.append('')

    return '\n'.join(out)

body = convert_md(md)

# Restore Mermaid blocks as literal HTML
for i, block in enumerate(mermaid_blocks):
    # Remove <br/> tags from Mermaid blocks
    block = block.replace('<br/>', '')
    body = body.replace(f'<p>%%MERMAID_{i}%%</p>', f'<div class="mermaid">\n{block}\n</div>')

# Build final HTML
html_content = f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Auth Evolution Deep Dive — ObsidianDB Research</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
  *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
  html{{font-size:16px;scroll-behavior:smooth}}
  body{{font-family:'Segoe UI',system-ui,-apple-system,sans-serif;line-height:1.75;color:#e0e0e0;background:#0d1117}}
  header{{background:linear-gradient(135deg,#0d324d,#0b1a2e 40%,#1a0a2e);border-bottom:2px solid #30363d;padding:3rem 2rem 2rem;text-align:center}}
  header h1{{font-size:2.2rem;font-weight:700;color:#e6edf3;margin-bottom:.5rem}}
  header .subtitle{{font-size:1.1rem;color:#8b949e;max-width:700px;margin:.5rem auto 1rem}}
  .container{{max-width:960px;margin:0 auto;padding:2rem 1.5rem 4rem}}
  h2{{font-size:1.6rem;color:#7ee787;border-bottom:1px solid #21262d;padding-bottom:.3rem;margin:2.5rem 0 1rem}}
  h3{{font-size:1.3rem;color:#a5d6ff;margin:2rem 0 .8rem}}
  h4{{font-size:1.1rem;color:#d2a8ff;margin:1.5rem 0 .5rem}}
  h5{{font-size:1rem;color:#ffa657;margin:1.2rem 0 .4rem}}
  p{{margin:.7rem 0}}
  a{{color:#58a6ff}}
  strong{{color:#f0f6fc;font-weight:600}}
  hr{{border:none;border-top:1px solid #21262d;margin:2.5rem 0}}
  code{{font-family:'Cascadia Code','Fira Code',Consolas,monospace;font-size:.88em;background:#161b22;padding:.15em .4em;border-radius:4px;color:#ffa657}}
  pre{{background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:1rem 1.5rem;margin:1rem 0;overflow-x:auto;font-family:'Cascadia Code','Fira Code',Consolas,monospace;font-size:.85rem;line-height:1.6;color:#c9d1d9}}
  pre code{{background:none;padding:0;color:inherit}}
  table{{width:100%;border-collapse:collapse;margin:1rem 0;font-size:.9rem}}
  thead{{background:#1a2332}}
  th{{text-align:left;padding:.6rem .9rem;font-weight:600;color:#e6edf3;border-bottom:2px solid #30363d;white-space:nowrap}}
  td{{padding:.5rem .9rem;border-bottom:1px solid #21262d;vertical-align:top}}
  tr:nth-child(even){{background:#161b22}}
  tr:hover{{background:#1c2433}}
  .mermaid{{background:#0d1117;border:1px solid #30363d;border-radius:10px;padding:1.5rem;margin:1.5rem 0;text-align:center;overflow-x:auto}}
  @media(max-width:768px){{html{{font-size:14px}}header h1{{font-size:1.6rem}}table{{font-size:.8rem}}th,td{{padding:.35rem .5rem}}}}
</style>
</head>
<body>
<header>
<h1>Authentication Evolution — Deep Dive</h1>
<p class="subtitle">Исчерпывающее исследование эволюции аутентификации в мобильных сетях:<br>математика COMP128/MILENAGE/TUAK, квантовые угрозы, хронология инцидентов, полная EF-карта</p>
</header>
<div class="container">
{body}
</div>
<script>
mermaid.initialize({{
  startOnLoad:true,
  theme:'dark',
  themeVariables:{{
    primaryColor:'#1a2332',primaryTextColor:'#e6edf3',lineColor:'#58a6ff',
    fontSize:'14px',actorBkg:'#1a2332',actorBorder:'#30363d',actorTextColor:'#e6edf3',
    signalColor:'#e6edf3',signalTextColor:'#e6edf3',
    noteBkgColor:'#161b22',noteTextColor:'#c9d1d9',noteBorderColor:'#30363d'
  }}
}});
</script>
</body>
</html>'''

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

# Verify
with open(out_path, 'r', encoding='utf-8') as f:
    result = f.read()

arrows = result.count('->>')
entities = result.count('&gt;')
print(f'Arrows (->\'): {arrows}')
print(f'HTML entities (&gt;): {entities}')
print(f'File size: {len(result)} bytes')
div_count = result.count('<div class="mermaid">')
print(f'Mermaid divs: {div_count}')
print('DONE: outputs/auth_evolution_deep_dive.html')
