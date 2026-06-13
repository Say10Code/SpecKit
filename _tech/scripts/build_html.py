import re

md_path = r'D:\ObsidianDB\wiki\syntheses\auth_evolution.md'
out_path = r'D:\ObsidianDB\outputs\auth_evolution.html'

with open(md_path, 'r', encoding='utf-8') as f:
    md = f.read()

md = re.sub(r'^---\n.*?\n---\n', '', md, flags=re.DOTALL)

# Save Mermaid blocks
mermaid_blocks = []
def save_mermaid(m):
    mermaid_blocks.append(m.group(1))
    return f'%%MERMAID_{len(mermaid_blocks)-1}%%'
md = re.sub(r'```mermaid\n(.*?)```', save_mermaid, md, flags=re.DOTALL)

# Convert Markdown
def convert(text):
    out = []
    in_code = False
    code_lines = []

    for line in text.split('\n'):
        if line.startswith('```'):
            if in_code:
                out.append(f'<pre><code>{"".join(code_lines).rstrip()}</code></pre>')
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line + '\n')
            continue

        # Tables
        if line.strip().startswith('|') and not line.strip().startswith('|---'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            out.append(('td','|').join(cells))
            continue

        if line.startswith('# ') and not line.startswith('## '): out.append(f'<h1>{line[2:].strip()}</h1>')
        elif line.startswith('## '): out.append(f'<h2>{line[3:].strip()}</h2>')
        elif line.startswith('### '): out.append(f'<h3>{line[4:].strip()}</h3>')
        elif line.startswith('#### '): out.append(f'<h4>{line[5:].strip()}</h4>')
        elif line.strip() == '---': out.append('<hr>')
        elif line.strip().startswith('> [!'):
            m = re.match(r'> \[!(\w+)\]\s*(.*)', line)
            if m:
                ctype = m.group(1).lower()
                ctext = m.group(2)
                out.append(f'<div class="callout callout-{ctype}"><div class="callout-title">{ctype.upper()}</div>{ctext}</div>')
        elif line.strip().startswith('> '):
            out.append(f'<blockquote>{line[2:].strip()}</blockquote>')
        elif line.strip():
            s = line
            s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
            s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
            s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
            out.append(f'<p>{s}</p>')
    return '\n'.join(out)

body = convert(md)

# Restore Mermaid
for i, block in enumerate(mermaid_blocks):
    block = block.replace('<br/>', '')
    body = body.replace(f'<p>%%MERMAID_{i}%%</p>', f'<div class="mermaid">\n{block}\n</div>')

# Generate comparison table manually (Section 6)
comp_table = '''<table><thead><tr><th>Property</th><th>GSM</th><th>UMTS</th><th>LTE</th><th>5G</th></tr></thead><tbody>
<tr><td><strong>Year</strong></td><td>1991</td><td>1999</td><td>2008</td><td>2018</td></tr>
<tr><td><strong>Spec</strong></td><td>GSM 11.11</td><td>TS 33.102</td><td>TS 33.401</td><td>TS 33.501</td></tr>
<tr><td><strong>Algorithm</strong></td><td>COMP128</td><td>MILENAGE</td><td>MILENAGE+KDF</td><td>MILENAGE+KDF / EAP-AKA&apos;</td></tr>
<tr><td><strong>Direction</strong></td><td>Network->SIM</td><td>Mutual</td><td>Mutual</td><td>Mutual</td></tr>
<tr><td><strong>Network key</strong></td><td>Kc (64 bit)</td><td>CK,IK (128 bit)</td><td>KASME (256 bit)</td><td>K_AUSF (256 bit)</td></tr>
<tr><td><strong>Integrity</strong></td><td>No</td><td>Yes (IK)</td><td>Yes (NAS+RRC)</td><td>Yes (NAS+RRC)</td></tr>
<tr><td><strong>SQN anti-replay</strong></td><td>No</td><td>Yes</td><td>Yes</td><td>Yes</td></tr>
<tr><td><strong>Privacy</strong></td><td>No (IMSI open)</td><td>No (IMSI open)</td><td>No (IMSI open)</td><td>Yes (SUCI!)</td></tr>
<tr><td><strong>Key hierarchy</strong></td><td>None</td><td>None (CK,IK direct)</td><td>KASME->chain</td><td>K_AUSF->K_SEAF->K_AMF->...</td></tr>
<tr><td><strong>Home Network Control</strong></td><td>No</td><td>Partial (AUC)</td><td>Partial</td><td>Yes (AUSF in HPLMN)</td></tr>
<tr><td><strong>Non-3GPP access</strong></td><td>No</td><td>No</td><td>No</td><td>Yes (EAP-AKA&apos;)</td></tr>
</tbody></table>'''

# Security table
sec_table = '''<table><thead><tr><th>Attack</th><th>GSM</th><th>UMTS</th><th>LTE</th><th>5G</th></tr></thead><tbody>
<tr><td><strong>False BTS</strong></td><td style="color:#f85149">Yes</td><td style="color:#3fb950">No (AUTN)</td><td style="color:#3fb950">No (AUTN)</td><td style="color:#3fb950">No (AUTN)</td></tr>
<tr><td><strong>IMSI-catching</strong></td><td style="color:#f85149">Yes</td><td style="color:#f85149">Yes</td><td style="color:#f85149">Yes</td><td style="color:#3fb950">No (SUCI!)</td></tr>
<tr><td><strong>Replay</strong></td><td style="color:#f85149">Yes</td><td style="color:#3fb950">No (SQN)</td><td style="color:#3fb950">No (SQN)</td><td style="color:#3fb950">No (SQN)</td></tr>
<tr><td><strong>Side-channel</strong></td><td style="color:#f85149">Yes (COMP128)</td><td style="color:#d29922">Harder (AES)</td><td style="color:#d29922">Harder</td><td style="color:#8b949e">TBD</td></tr>
<tr><td><strong>Quantum</strong></td><td style="color:#f85149">Vuln (64-bit Kc)</td><td style="color:#f85149">Vuln (128-bit K)</td><td style="color:#f85149">Vuln (128-bit K)</td><td style="color:#3fb950">Strong (256-bit K)</td></tr>
</tbody></table>'''

html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Evolution of Authentication: COMP128 to 5G AKA — ObsidianDB</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{font-size:16px;scroll-behavior:smooth}}
body{{font-family:'Segoe UI',system-ui,-apple-system,sans-serif;line-height:1.75;color:#e0e0e0;background:#0d1117}}
header{{background:linear-gradient(135deg,#0d324d,#0b1a2e 40%,#1a0a2e);border-bottom:2px solid #30363d;padding:3rem 2rem 2rem;text-align:center}}
header h1{{font-size:2.2rem;font-weight:700;color:#e6edf3;margin-bottom:.5rem}}
header .subtitle{{font-size:1.1rem;color:#8b949e;max-width:750px;margin:.5rem auto 1rem}}
.container{{max-width:960px;margin:0 auto;padding:2rem 1.5rem 4rem}}
h2{{font-size:1.6rem;color:#7ee787;border-bottom:1px solid #21262d;padding-bottom:.3rem;margin:2.5rem 0 1rem}}
h3{{font-size:1.3rem;color:#a5d6ff;margin:2rem 0 .8rem}}
h4{{font-size:1.1rem;color:#d2a8ff;margin:1.5rem 0 .5rem}}
p{{margin:.7rem 0}}
strong{{color:#f0f6fc;font-weight:600}}
hr{{border:none;border-top:1px solid #21262d;margin:2.5rem 0}}
code{{font-family:'Cascadia Code','Fira Code',Consolas,monospace;font-size:.88em;background:#161b22;padding:.15em .4em;border-radius:4px;color:#ffa657}}
pre{{background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:1rem 1.5rem;margin:1rem 0;overflow-x:auto;font-family:'Cascadia Code','Fira Code',Consolas,monospace;font-size:.85rem;line-height:1.6;color:#c9d1d9}}
pre code{{background:none;padding:0;color:inherit}}
blockquote{{border-left:4px solid #58a6ff;margin:1rem 0;padding:.8rem 1.2rem;background:#161b22;border-radius:0 8px 8px 0;color:#c9d1d9}}
table{{width:100%;border-collapse:collapse;margin:1rem 0;font-size:.9rem}}
thead{{background:#1a2332}}
th{{text-align:left;padding:.6rem .9rem;font-weight:600;color:#e6edf3;border-bottom:2px solid #30363d;white-space:nowrap}}
td{{padding:.5rem .9rem;border-bottom:1px solid #21262d;vertical-align:top}}
tr:nth-child(even){{background:#161b22}}
tr:hover{{background:#1c2433}}
.callout{{border-left:4px solid #484f58;margin:1rem 0;padding:.8rem 1.2rem;background:#161b22;border-radius:0 8px 8px 0}}
.callout-title{{font-size:.85rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.3rem}}
.callout-danger{{border-left-color:#f85149}}.callout-danger .callout-title{{color:#f85149}}
.callout-tip{{border-left-color:#3fb950}}.callout-tip .callout-title{{color:#3fb950}}
.callout-info{{border-left-color:#58a6ff}}.callout-info .callout-title{{color:#58a6ff}}
.mermaid{{background:#0d1117;border:1px solid #30363d;border-radius:10px;padding:1.5rem;margin:1.5rem 0;text-align:center;overflow-x:auto}}
.gen-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin:1.5rem 0}}
.gen-card{{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:1.2rem;text-align:center}}
.gen-2g{{border-top:3px solid #f85149}}.gen-3g{{border-top:3px solid #d29922}}.gen-4g{{border-top:3px solid #58a6ff}}.gen-5g{{border-top:3px solid #3fb950}}
@media(max-width:768px){{html{{font-size:14px}}header h1{{font-size:1.6rem}}.gen-grid{{grid-template-columns:repeat(2,1fr)}}table{{font-size:.8rem}}th,td{{padding:.35rem .5rem}}}}
</style>
</head>
<body>
<header>
<h1>Evolution of Authentication</h1>
<p class="subtitle">From COMP128 to 5G AKA — эволюция аутентификации в мобильных сетях:<br>от односторонней GSM до взаимной 5G с SUCI-privacy</p>
</header>
<div class="container">

<div class="gen-grid">
<div class="gen-card gen-2g"><strong>2G (GSM)</strong><br>COMP128<br>1991<br><span style="color:#f85149">One-way</span></div>
<div class="gen-card gen-3g"><strong>3G (UMTS)</strong><br>UMTS AKA<br>1999<br><span style="color:#3fb950">Mutual + integrity</span></div>
<div class="gen-card gen-4g"><strong>4G (LTE)</strong><br>EPS AKA<br>2008<br><span style="color:#58a6ff">Mutual + KASME</span></div>
<div class="gen-card gen-5g"><strong>5G</strong><br>5G AKA / EAP-AKA&apos;<br>2018<br><span style="color:#a371f7">Mutual + SUCI</span></div>
</div>

<h2>1. Overview</h2>
<pre>2G (GSM)          3G (UMTS)           4G (LTE)             5G
COMP128            UMTS AKA            EPS AKA               5G AKA / EAP-AKA&apos;
SIM                USIM                USIM                  USIM
GSM 11.11          TS 31.102           TS 31.102             TS 31.102
One-way            Mutual              Mutual +              Mutual +
                   auth                key hierarchy         SUCI privacy
                   + integrity         + KASME               + K_AUSF/K_SEAF</pre>

<hr>
<h2>2. GSM (2G) — COMP128</h2>
<h3>Process</h3>
<pre>HLR/AUC                           ME                          SIM
  |
  |-- RAND (128 bit) -------------->|-- RUN GSM ALGORITHM ---->|
  |                                  |                           |
  |                                  |         COMP128           |
  |                                  |    RAND + Ki ->           |
  |                                  |    SRES (32 bit)          |
  |                                  |    Kc (64 bit)            |
  |                                  |                           |
  |<---------- SRES -----------------|<-------- SRES ------------|
  |                                  |                           |
  |  Network verifies SRES          |                           |
  |  SRES == SRES' -> OK            |                           |
  |  Kc -> A5/x ciphering           |                           |</pre>

{comp_table}

<div class="callout callout-danger"><div class="callout-title">CRITICAL</div>GSM network does NOT authenticate itself to the SIM. This enables <strong>false base station</strong> attacks (IMSI-catcher).</div>

<hr>
<h2>3. UMTS (3G) — UMTS AKA: Mutual Authentication</h2>
<h3>Process</h3>
<pre>HLR/AUC                           ME                          USIM
  |
  |  [RAND, AUTN, XRES,            |
  |   CK, IK]                      |
  |                                  |
  |-- RAND, AUTN ------------------>|-- AUTHENTICATE ---------->|
  |                                  |                           |
  |                                  |        f1...f5            |
  |                                  |   RAND + K ->             |
  |                                  |   XMAC == AUTN.MAC?       |
  |                                  |   -> Yes: network valid!  |
  |                                  |   RES = f2(K, RAND)       |
  |                                  |   CK = f3(K, RAND)        |
  |                                  |   IK = f4(K, RAND)        |
  |                                  |                           |
  |<---------- RES -----------------|<------ RES, CK, IK -------|
  |                                  |                           |
  |  RES == XRES -> OK              |                           |
  |  CK -> UEA (cipher)             |                           |
  |  IK -> UIA (integrity!)         |                           |</pre>

{comp_table.replace('COMP128</td>','COMP128</td>').replace('MILENAGE</td>','MILENAGE</td>')}

<div class="callout callout-tip"><div class="callout-title">KEY ADVANTAGE OVER GSM</div>Mutual authentication + integrity + SQN anti-replay + 128-bit CK/IK (vs 64-bit Kc).</div>

<hr>
<h2>4. LTE (4G) — EPS AKA: Key Hierarchy</h2>
<pre>K (in USIM)
  |
  v UMTS AKA (f3, f4)
CK, IK
  |
  v KDF [CK || IK + SN_ID + SQN xor AK]
KASME (256 bit)
  |
  +-- K_NASenc (NAS encryption)
  +-- K_NASint (NAS integrity)
  +-- K_eNB (base station key)
        +-- K_UPenc (User Plane encryption)
        +-- K_RRCint (RRC integrity)
        +-- K_RRCenc (RRC encryption)
        +-- ...</pre>

<hr>
<h2>5. 5G — 5G AKA / EAP-AKA&apos; + SUCI Privacy</h2>
<h3>5G AKA</h3>
<pre>K (in USIM, DF_5GS)
  |
  v 5G AKA
K_AUSF (Authentication Server Function)
  |
  v
K_SEAF (Security Anchor Function)
  |
  v
K_AMF (Access and Mobility Management Function)
  |
  +-- K_NASenc, K_NASint
  +-- K_gNB
        +-- K_UPenc, K_RRCint, K_RRCenc</pre>

<h3>SUCI: Privacy Protection</h3>
<pre>BEFORE 5G (IMSI open):           IN 5G (SUCI):
  ME --IMSI--> Network              ME --SUCI--> Network
  ████████████                      ████ (encrypted IMSI!)
  IMSI-catcher!                     IMSI-catcher sees only
                                     encrypted SUCI</pre>

<p><strong>SUCI</strong> = Subscription Concealed Identifier. SUPI (IMSI analog) encrypted with Home Network Public Key. Only Home Network can decrypt. EF_SUCI_Calc_Info in DF_5GS contains public key and parameters.</p>

<hr>
<h2>6. Comparison Table</h2>
{comp_table}

<hr>
<h2>7. Key Evolution</h2>
<pre>GSM:    Ki (128) -> Kc (64)                         2 keys
UMTS:   K (128) -> CK (128) + IK (128)               3 keys
LTE:    K (128) -> CK+IK -> KASME (256) -> 7+ keys   ~10 keys
5G:     K (256) -> CK+IK -> K_AUSF -> K_SEAF -> ...  ~15+ keys</pre>

<hr>
<h2>8. Key EFs for Authentication</h2>

<h3>8.1 Key and Secret EFs</h3>
<table><thead><tr><th>EF</th><th>FID</th><th>Generation</th><th>Content</th><th>Role in AKA</th></tr></thead><tbody>
<tr><td><strong>EF_Kc</strong></td><td><code>0x6F20</code></td><td>GSM</td><td>Kc (64 bit)</td><td>GSM cipher key from COMP128, used for A5/x ciphering</td></tr>
<tr><td><strong>EF_Keys</strong></td><td><code>0x6F08</code></td><td>3G/4G</td><td>CK (128b) + IK (128b)</td><td>UMTS/EPS AKA keys from f3/f4; CK for UEA, IK for UIA</td></tr>
<tr><td><strong>EF_KeysPS</strong></td><td><code>0x6F09</code></td><td>3G/4G</td><td>CK + IK (PS domain)</td><td>Separate CS/PS keys</td></tr>
<tr><td><strong>EF_5GAUTHKEYS</strong></td><td><code>0x6FF3</code></td><td>5G</td><td>K (up to 256b) + RIN</td><td>5G AKA master key; RIN routes to correct AUSF</td></tr>
<tr><td><strong>EF_SUCI_Calc_Info</strong></td><td><code>0x6FF6</code></td><td>5G</td><td>Home Network PK + Protection Scheme</td><td>SUCI computation: encrypt SUPI with HPLMN public key</td></tr>
<tr><td><strong>EF_KAUSF_Derivation</strong></td><td><code>0x6FFC</code></td><td>5G</td><td>KDF parameters + Serving Network Name</td><td>K_AUSF derivation from CK,IK</td></tr>
</tbody></table>

<h3>8.2 LOCI Family</h3>
<table><thead><tr><th>EF</th><th>FID</th><th>Gen</th><th>Content</th><th>Updated on</th><th>Size</th></tr></thead><tbody>
<tr><td><strong>EF_LOCI</strong></td><td><code>0x6F7E</code></td><td>3G</td><td>TMSI(4B), LAI(5B), TMSI_TIME(1B)</td><td>TMSI reallocation</td><td>11B</td></tr>
<tr><td><strong>EF_PSLOCI</strong></td><td><code>0x6F73</code></td><td>3G</td><td>P-TMSI(4B)+sig(3B), RAI(6B)</td><td>PS attach/RA update</td><td>14B</td></tr>
<tr><td><strong>EF_EPSLOCI</strong></td><td><code>0x6FE3</code></td><td>4G</td><td>GUTI(11B), TAI(6B), KSI(1B)</td><td>GUTI reallocation/TAU</td><td>18B</td></tr>
<tr><td><strong>EF_5GS3GPPLOCI</strong></td><td><code>0x6FF0</code></td><td>5G</td><td>5G-GUTI(11B), TAI(6B), status(1B)</td><td>5G 3GPP registration</td><td>18B</td></tr>
<tr><td><strong>EF_5GSN3GPPLOCI</strong></td><td><code>0x6FF1</code></td><td>5G</td><td>5G-GUTI(11B), TAI(6B), status(1B)</td><td>Non-3GPP registration</td><td>18B</td></tr>
</tbody></table>

<div class="mermaid">
sequenceDiagram
    participant ME as Terminal (ME)
    participant NET as Network (MME/AMF)
    participant UICC as UICC (USIM)

    Note over ME,UICC: === Registration with GUTI from EPSLOCI ===

    ME->>UICC: SELECT EF_EPSLOCI
    UICC-->>ME: FCP (READ=PIN1, UPDATE=PIN1)

    ME->>UICC: READ BINARY (offset=0)
    UICC-->>ME: GUTI / TAI / KSI

    ME->>NET: Registration Request (GUTI + TAI)

    Note over NET: Network checks GUTI validity and TAI match.
    Note over NET: If OK skip AKA. If not request full AKA.

    NET->>ME: Authentication Request (RAND, AUTN)
    ME->>UICC: AUTHENTICATE (RAND, AUTN)

    Note over UICC: MILENAGE/TUAK f1 verifies XMAC vs AUTN.MAC
    Note over UICC: f2 computes RES, f3 computes CK, f4 computes IK

    UICC-->>ME: RES, CK, IK
    ME-->>NET: RES

    Note over NET: RES equals XRES authentication OK.
    Note over NET: Derive KASME/K_AUSF from CK, IK.

    NET->>ME: Security Mode Command
    NET->>ME: GUTI Reallocation (new GUTI, new TAI)

    ME->>UICC: UPDATE BINARY EF_EPSLOCI (GUTI / TAI / KSI)
    UICC-->>ME: 90 00 (OK)

    Note over UICC: Security context saved.
    Note over UICC: Next registration is fast re-auth without AKA.
</div>

<hr>
<h2>9. Security: Vulnerabilities and Protection</h2>
{sec_table}

<hr>
<h2>See Also</h2>
<p><strong>MILENAGE vs TUAK: Comparative Analysis</strong> — deep cryptographic analysis of both authentication algorithms</p>
<p><strong>Auth Evolution Deep Dive</strong> — exhaustive research with mathematical breakdown, quantum analysis, incident chronology</p>

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
    f.write(html)

# Verify
with open(out_path, 'r', encoding='utf-8') as f:
    result = f.read()

arrows = result.count('->>')
entities = result.count('&gt;')
print(f'Arrows (->\'>): {arrows}')
print(f'HTML entities (&gt;): {entities}')
print(f'File size: {len(result)} bytes')
mermaid_divs = result.count('<div class="mermaid">')
print(f'Mermaid divs: {mermaid_divs}')
print('DONE: outputs/auth_evolution.html')
