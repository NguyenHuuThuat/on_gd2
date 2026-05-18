"""Step 2/2: Build index.html — single-file interactive study app.
Embeds tools/tai_lieu_data.json directly so it works offline via file://.

Re-run any time after editing 01_extract_data.py inputs:
    python tools/01_extract_data.py
    python tools/02_build_html.py
Or run both via `rebuild.bat` at project root.
"""
import sys, io, os, json
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.chdir(Path(__file__).resolve().parent.parent)
print(f'Working dir: {os.getcwd()}')

with open('tools/tai_lieu_data.json', encoding='utf-8') as f:
    data = json.load(f)

# Load practice questions if available
practice = {'total': 0, 'questions': []}
practice_path = 'tools/practice_questions.json'
if os.path.exists(practice_path):
    with open(practice_path, encoding='utf-8') as f:
        practice = json.load(f)
data['practice'] = practice

# Load ÔN TẬP NHANH quiz data (separate section based on ON_TAP markdown files)
ontap_nhanh = {'title': '', 'sets': []}
ontap_path = 'tools/ontap_nhanh_quiz.json'
if os.path.exists(ontap_path):
    with open(ontap_path, encoding='utf-8') as f:
        ontap_nhanh = json.load(f)
# Inline the markdown content of each set's source_md so users can read on the web
for _set in ontap_nhanh.get('sets', []):
    src = _set.get('source_md')
    if src:
        md_path = os.path.join('vcb_cds_202605', src)
        if os.path.exists(md_path):
            with open(md_path, encoding='utf-8') as _f:
                _set['content_md'] = _f.read()
        else:
            _set['content_md'] = ''
data['ontap_nhanh'] = ontap_nhanh

# Load reading guide MD content
reading_guide_md = ''
if os.path.exists('HUONG_DAN_DOC.md'):
    with open('HUONG_DAN_DOC.md', encoding='utf-8') as f:
        reading_guide_md = f.read()
data['reading_guide_md'] = reading_guide_md

HTML = r'''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ôn tập 39 VB Pháp lý — Hội thi CĐS Ngân hàng</title>
<style>
*,*::before,*::after{box-sizing:border-box}
:root{
  /* VCB Green Light Theme */
  --bg:#f6f9f5;         /* very light green-tinted bg */
  --bg2:#ffffff;        /* pure white drawer/modal */
  --card:#ffffff;       /* white cards */
  --card2:#eef5eb;      /* light green hover */
  --text:#1a2e22;       /* dark green text */
  --muted:#67786c;      /* muted green-gray */
  --accent:#00853F;     /* VCB primary green */
  --accent2:#b8860b;    /* warm gold accent (VCB secondary) */
  --green:#00853F;      /* same as accent */
  --red:#c62828;        /* error red */
  --yellow:#c47d00;     /* warm amber (readable on white) */
  --purple:#6b21a8;     /* deep purple */
  --pink:#be185d;
  --teal:#0e7490;
  --indigo:#3730a3;
  --blue:#1e40af;
  --border:#d4e1cf;     /* light green-gray border */
  --shadow:0 2px 8px rgba(0,133,63,0.08);
  --shadow-hover:0 6px 16px rgba(0,133,63,0.15);
}
body{margin:0;font-family:-apple-system,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--text);line-height:1.65;font-size:14px}
.container{max-width:1400px;margin:0 auto;padding:0 24px}
header{background:linear-gradient(135deg,#00853F 0%,#006B3F 50%,#00471F 100%);padding:48px 24px;border-bottom:3px solid #b8860b;color:#fff}
header h1{margin:0;font-size:30px;font-weight:700;color:#fff;text-shadow:0 1px 3px rgba(0,0,0,0.2)}
header .subtitle{color:rgba(255,255,255,0.85);margin-top:8px;font-size:15px}
header .stats{display:flex;gap:16px;margin-top:24px;flex-wrap:wrap}
header .stat{background:rgba(255,255,255,0.15);padding:14px 22px;border-radius:12px;backdrop-filter:blur(10px);min-width:120px;border:1px solid rgba(255,255,255,0.2)}
header .stat-value{font-size:26px;font-weight:700;color:#fff}
header .stat-label{font-size:12px;color:rgba(255,255,255,0.75);text-transform:uppercase;letter-spacing:0.5px}

section{padding:24px 0}
section h2{font-size:21px;margin:0 0 12px;display:flex;align-items:center;gap:10px}
section h2 .badge-count{background:var(--accent);color:#0f172a;padding:2px 10px;border-radius:12px;font-size:13px;font-weight:600}

.tips-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}
.tip-card{background:var(--card);padding:14px 18px;border-radius:10px;border-left:3px solid var(--accent);font-size:13px;box-shadow:var(--shadow);transition:transform 0.15s,box-shadow 0.15s}
.tip-card:hover{transform:translateY(-2px);box-shadow:var(--shadow-hover)}
.tip-card h3{margin:0 0 6px;font-size:14px;color:var(--accent)}
.tip-card p{margin:0;font-size:13px;color:var(--text);line-height:1.5}

.filter-bar{position:sticky;top:0;background:var(--bg);padding:14px 0;z-index:50;border-bottom:1px solid var(--border)}
.filter-row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
#search{flex:1;min-width:240px;padding:10px 14px;background:var(--card);border:1px solid var(--border);border-radius:8px;color:var(--text);font-size:14px}
#search:focus{outline:none;border-color:var(--accent)}
.chip{padding:5px 11px;border-radius:14px;border:1px solid var(--border);background:var(--card);color:var(--text);cursor:pointer;font-size:12px;transition:all 0.15s;white-space:nowrap}
.chip:hover{border-color:var(--accent)}
.chip.active{background:var(--accent);color:#0f172a;border-color:var(--accent);font-weight:600}
.chip-group{display:flex;gap:5px;flex-wrap:wrap}

.topic-overview-card{background:var(--card);border-left:3px solid var(--accent);padding:16px 20px;border-radius:8px;margin:12px 0;display:none;font-size:14px}
.topic-overview-card.show{display:block}
.topic-overview-card h3{margin:0 0 8px;color:var(--accent);font-size:15px}
.topic-overview-card .content{white-space:pre-wrap;max-height:480px;overflow-y:auto;line-height:1.7}
.topic-overview-card .content::-webkit-scrollbar{width:6px}
.topic-overview-card .content::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}

.docs-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:14px;margin-top:14px}
.doc-card{background:var(--card);border-radius:10px;padding:16px;border:1px solid var(--border);cursor:pointer;transition:all 0.2s;display:flex;flex-direction:column;gap:6px;min-height:200px;box-shadow:var(--shadow)}
.doc-card:hover{border-color:var(--accent);transform:translateY(-2px);box-shadow:var(--shadow-hover)}
.doc-card .head{display:flex;justify-content:space-between;align-items:flex-start;gap:8px}
.doc-card .roman-id{font-size:13px;font-weight:700;color:var(--accent);font-family:Consolas,monospace;background:rgba(0,133,63,0.08);padding:2px 8px;border-radius:4px}
.doc-card .cat-icon{font-size:20px}
.doc-card .title{font-size:15px;font-weight:600;line-height:1.3;color:var(--text)}
.doc-card .code{font-size:11px;color:var(--muted);font-family:Consolas,monospace}
.doc-card .topics{display:flex;gap:4px;flex-wrap:wrap}
.topic-badge{font-size:10px;padding:2px 7px;border-radius:9px;font-weight:600;text-transform:uppercase;letter-spacing:0.3px}
.topic-badge.main{color:#fff}
.topic-badge.sec{background:transparent;border:1px solid currentColor}
.topic-I{background:var(--blue);color:#fff}.topic-I.sec{color:var(--blue);background:transparent;border-color:var(--blue)}
.topic-II{background:var(--green);color:#fff}.topic-II.sec{color:var(--green);background:transparent;border-color:var(--green)}
.topic-III{background:var(--purple);color:#fff}.topic-III.sec{color:var(--purple);background:transparent;border-color:var(--purple)}
.topic-IV{background:var(--red);color:#fff}.topic-IV.sec{color:var(--red);background:transparent;border-color:var(--red)}
.topic-V{background:var(--accent2);color:#fff}.topic-V.sec{color:var(--accent2);background:transparent;border-color:var(--accent2)}
.topic-VI{background:var(--indigo);color:#fff}.topic-VI.sec{color:var(--indigo);background:transparent;border-color:var(--indigo)}
.topic-VII{background:var(--pink);color:#fff}.topic-VII.sec{color:var(--pink);background:transparent;border-color:var(--pink)}
.topic-VIII{background:var(--teal);color:#fff}.topic-VIII.sec{color:var(--teal);background:transparent;border-color:var(--teal)}

.doc-card .metrics{display:flex;gap:8px;font-size:11px;color:var(--muted);margin-top:auto;flex-wrap:wrap}
.metric{padding:2px 8px;border-radius:6px;background:rgba(0,133,63,0.05);display:inline-flex;align-items:center;gap:3px}
.metric.has{color:var(--green)}
.metric.has-q{color:var(--accent2)}
.doc-card.s-done{border-color:var(--green);border-left:4px solid var(--green)}
.doc-card.s-done .roman-id::after{content:" ✓";color:var(--green)}
.doc-card.s-review{border-color:var(--accent2);border-left:4px solid var(--accent2);background:rgba(184,134,11,0.04)}
.doc-card.s-review .roman-id::after{content:" 🔄"}
.doc-card.s-important{border-color:var(--red);border-left:4px solid var(--red);background:rgba(198,40,40,0.04)}
.doc-card.s-important .roman-id::after{content:" ⭐"}

.doc-card .has-note{position:absolute;top:6px;right:6px;font-size:11px;background:var(--accent);color:#fff;width:18px;height:18px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700}

.status-select{padding:7px 11px;border-radius:6px;font-size:12px;font-weight:600;border:1px solid var(--border);background:#fff;color:var(--text);cursor:pointer}
.status-select.done{background:var(--green);color:#fff;border-color:var(--green)}
.status-select.review{background:var(--accent2);color:#fff;border-color:var(--accent2)}
.status-select.important{background:var(--red);color:#fff;border-color:var(--red)}

.note-section{background:#fffef5;border:1px dashed var(--accent2);border-radius:8px;padding:14px 16px;margin-top:14px}
.note-section .note-label{font-size:12px;color:var(--accent2);font-weight:700;text-transform:uppercase;margin-bottom:6px;display:flex;align-items:center;gap:6px}
.note-textarea{width:100%;min-height:90px;border:1px solid var(--border);background:#fff;color:var(--text);border-radius:6px;padding:8px 10px;font-family:inherit;font-size:13.5px;line-height:1.6;resize:vertical}
.note-textarea:focus{outline:none;border-color:var(--accent2)}
.note-hint{font-size:11px;color:var(--muted);font-style:italic;margin-top:4px}

/* Drawer — fullscreen modal */
.drawer{position:fixed;inset:0;width:100vw;height:100vh;background:var(--bg);overflow-y:auto;z-index:1000;opacity:0;visibility:hidden;transition:opacity 0.25s,visibility 0.25s}
.drawer.open{opacity:1;visibility:visible}
.drawer-overlay{display:none}
.drawer-inner{max-width:1280px;margin:0 auto;padding:0 32px;min-height:100%}
.drawer-head{padding:24px 0 18px;border-bottom:2px solid var(--accent);position:sticky;top:0;background:var(--bg);z-index:10;margin-bottom:8px}
.drawer-head .close{position:absolute;top:16px;right:0;background:#fff;color:var(--text);border:1px solid var(--border);width:42px;height:42px;border-radius:50%;cursor:pointer;font-size:22px;display:flex;align-items:center;justify-content:center;box-shadow:var(--shadow);transition:all 0.15s}
.drawer-head .close:hover{background:var(--red);color:#fff;border-color:var(--red);transform:rotate(90deg)}
.drawer-head h2{margin:0;font-size:24px;padding-right:60px;color:var(--accent);font-weight:700}
.drawer-head .meta{color:var(--muted);font-size:14px;margin-top:8px;display:flex;flex-wrap:wrap;gap:14px}
.drawer-head .actions{display:flex;gap:8px;margin-top:14px;flex-wrap:wrap}
.btn{background:var(--accent);color:#0f172a;border:none;padding:7px 12px;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;gap:4px;transition:opacity 0.15s}
.btn:hover{opacity:0.85}
.btn.secondary{background:var(--card);color:var(--text);border:1px solid var(--border)}
.btn.studied{background:var(--green);color:#fff}

.drawer-body{padding:0 0 48px}
.tabs{display:flex;gap:0;border-bottom:1px solid var(--border);margin:0 0 18px;padding:0;overflow-x:auto;flex-wrap:nowrap;position:sticky;top:138px;background:var(--bg);z-index:9}
.tab{padding:12px 18px;background:transparent;border:none;color:var(--muted);cursor:pointer;font-size:14px;border-bottom:3px solid transparent;font-weight:600;white-space:nowrap}
.tab:hover{color:var(--accent);background:var(--card2)}
.tab.active{color:var(--accent);border-bottom-color:var(--accent);background:var(--card)}
.tab .count{background:var(--card2);color:var(--text);padding:1px 6px;border-radius:8px;font-size:11px;margin-left:4px;font-weight:600}
.tab-panel{display:none}
.tab-panel.active{display:block}

.summary-block{background:var(--card);border-radius:8px;padding:14px 16px;margin-bottom:10px;white-space:pre-wrap;font-size:13.5px;line-height:1.65;border:1px solid var(--border);box-shadow:var(--shadow)}
.summary-block .label{font-size:11px;color:var(--accent);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;font-weight:700}
.keywords{display:flex;flex-wrap:wrap;gap:5px;margin-top:8px}
.keyword{background:rgba(0,133,63,0.08);color:var(--accent);padding:3px 9px;border-radius:11px;font-size:12px;border:1px solid rgba(0,133,63,0.25);font-weight:500}

.dieu-list{display:flex;flex-direction:column;gap:5px}
.chuong-header{font-size:12px;color:var(--accent2);text-transform:uppercase;margin:14px 0 4px;font-weight:700;letter-spacing:0.5px;border-bottom:1px dashed var(--border);padding-bottom:4px}
.chuong-header:first-child{margin-top:0}
.dieu-item{background:var(--card);border-radius:6px;border:1px solid var(--border);overflow:hidden}
.dieu-head{padding:8px 12px;cursor:pointer;display:flex;justify-content:space-between;align-items:center;gap:8px;font-size:13px;transition:background 0.15s}
.dieu-head:hover{background:var(--card2)}
.dieu-num{font-weight:700;color:var(--accent);font-family:Consolas,monospace;min-width:60px}
.dieu-title{flex:1;font-weight:500}
.dieu-toggle{color:var(--muted);transition:transform 0.2s;font-size:11px}
.dieu-item.expanded .dieu-toggle{transform:rotate(90deg)}
.dieu-body{display:none;padding:0 14px 14px;border-top:1px solid var(--border);white-space:pre-wrap;font-size:13.5px;color:var(--text);line-height:1.85;background:rgba(0,133,63,0.025)}
.dieu-item.expanded .dieu-body{display:block;padding-top:10px}

/* Keynotes - grouped by topic with color coding */
.kn-group{margin-bottom:20px}
.kn-group-header{display:flex;align-items:center;gap:10px;margin:0 0 10px;padding:10px 14px;border-radius:8px;font-weight:700;font-size:14px;color:#fff;box-shadow:var(--shadow)}
.kn-group-header .kn-count{margin-left:auto;background:rgba(255,255,255,0.25);padding:2px 10px;border-radius:10px;font-size:12px}
.kn-group-I .kn-group-header{background:linear-gradient(90deg,var(--blue),transparent)}
.kn-group-II .kn-group-header{background:linear-gradient(90deg,var(--green),transparent)}
.kn-group-III .kn-group-header{background:linear-gradient(90deg,var(--purple),transparent)}
.kn-group-IV .kn-group-header{background:linear-gradient(90deg,var(--red),transparent)}
.kn-group-V .kn-group-header{background:linear-gradient(90deg,var(--accent2),transparent)}
.kn-group-VI .kn-group-header{background:linear-gradient(90deg,var(--indigo),transparent)}
.kn-group-VII .kn-group-header{background:linear-gradient(90deg,var(--pink),transparent)}
.kn-group-VIII .kn-group-header{background:linear-gradient(90deg,var(--teal),transparent)}

.kn-list{display:grid;grid-template-columns:1fr;gap:10px}
@media (min-width:900px){.kn-list{grid-template-columns:1fr 1fr}}
@media (min-width:1400px){.kn-list{grid-template-columns:1fr 1fr 1fr}}
.kn-card{background:var(--card);border-radius:8px;padding:12px 14px;font-size:13.5px;line-height:1.6;border:1px solid var(--border);position:relative;white-space:pre-wrap;transition:border-color 0.15s;box-shadow:var(--shadow)}
.kn-card:hover{border-color:var(--accent)}
.kn-card .kn-num{position:absolute;top:-8px;left:10px;background:var(--bg);color:var(--accent);font-weight:700;padding:0 8px;font-size:11px;font-family:Consolas,monospace;border:1px solid var(--border);border-radius:3px}
.kn-card .kn-source{margin-top:8px;padding-top:6px;border-top:1px dashed var(--border);font-size:10.5px;color:var(--muted);font-style:italic}
.kn-card .kn-source a{color:var(--accent);text-decoration:none}
.kn-card .kn-source a:hover{text-decoration:underline}
.kn-group-I .kn-card{border-left:3px solid var(--blue)}
.kn-group-II .kn-card{border-left:3px solid var(--green)}
.kn-group-III .kn-card{border-left:3px solid var(--purple)}
.kn-group-IV .kn-card{border-left:3px solid var(--red)}
.kn-group-V .kn-card{border-left:3px solid var(--accent2)}
.kn-group-VI .kn-card{border-left:3px solid var(--indigo)}
.kn-group-VII .kn-card{border-left:3px solid var(--pink)}
.kn-group-VIII .kn-card{border-left:3px solid var(--teal)}

/* Inline highlights inside keynote text */
.kn-card .num-hl{background:rgba(184,134,11,0.15);color:#8a6508;padding:1px 6px;border-radius:4px;font-weight:600;font-family:Consolas,monospace;font-size:0.92em;border:1px solid rgba(184,134,11,0.25)}
.kn-card .dieu-link{background:rgba(0,133,63,0.1);color:var(--accent);padding:1px 6px;border-radius:4px;font-weight:600;font-size:0.92em;cursor:pointer;border-bottom:1px dashed var(--accent);transition:all 0.15s}
.kn-card .dieu-link:hover{background:var(--accent);color:#fff}
.kn-card .vb-link{background:rgba(107,33,168,0.1);color:var(--purple);padding:1px 6px;border-radius:4px;font-weight:600;font-size:0.92em;cursor:pointer;border-bottom:1px dashed var(--purple);transition:all 0.15s}
.kn-card .vb-link:hover{background:var(--purple);color:#fff}
.kn-card .dieu-link.unknown,.kn-card .vb-link.unknown{cursor:default;border-bottom:none;opacity:0.6}
.kn-card .dieu-link.unknown:hover,.kn-card .vb-link.unknown:hover{background:rgba(107,33,168,0.08);color:inherit}
.kn-card strong{color:var(--accent);font-weight:700}

/* Flashcard mode */
.fc-stage{display:flex;flex-direction:column;align-items:center;gap:14px;padding:10px 0}
.fc-progress{width:100%;display:flex;align-items:center;gap:10px;font-size:12px;color:var(--muted)}
.fc-progress .bar{flex:1;height:6px;background:var(--card2);border-radius:3px;overflow:hidden}
.fc-progress .fill{height:100%;background:linear-gradient(90deg,var(--accent),var(--accent2));transition:width 0.3s}
.fc-nav-wrap{position:relative;width:100%;max-width:800px;display:flex;align-items:center;gap:8px}
.fc-nav-arrow{flex:0 0 auto;width:48px;height:48px;border-radius:50%;border:1px solid var(--border);background:#fff;color:var(--accent);font-size:22px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all 0.15s;box-shadow:var(--shadow)}
.fc-nav-arrow:hover:not(:disabled){background:var(--accent);color:#fff;transform:scale(1.08);box-shadow:var(--shadow-hover)}
.fc-nav-arrow:disabled{opacity:0.3;cursor:not-allowed}
.fc-card-wrap{flex:1;perspective:1000px;min-height:340px;cursor:pointer}
.fc-card{position:relative;width:100%;min-height:340px;transition:transform 0.55s;transform-style:preserve-3d}
.fc-card.flipped{transform:rotateY(180deg)}
.fc-face{position:absolute;inset:0;backface-visibility:hidden;background:#fff;border:1px solid var(--border);border-radius:14px;padding:24px;display:flex;flex-direction:column;box-shadow:var(--shadow);overflow-y:auto}
.fc-face .fc-badge{display:inline-block;font-size:10px;padding:3px 9px;border-radius:10px;background:rgba(0,133,63,0.1);color:var(--accent);font-weight:700;text-transform:uppercase;margin-bottom:10px;align-self:flex-start}
.fc-face .fc-roman{font-size:11px;color:var(--muted);margin-bottom:6px;font-family:Consolas,monospace}
.fc-face .fc-front-text{font-size:18px;font-weight:600;line-height:1.55;color:var(--text);margin:auto 0;text-align:center;padding:0 10px}
.fc-face.back{transform:rotateY(180deg);background:linear-gradient(135deg,#f9fbf8,#eef5eb)}
.fc-face.back .fc-back-title{font-size:14px;color:var(--accent);font-weight:700;margin-bottom:8px}
.fc-face.back .fc-back-content{font-size:14px;line-height:1.75;color:var(--text);white-space:pre-wrap}
.fc-face.back .fc-back-quote{margin-top:12px;padding:10px 12px;background:rgba(0,133,63,0.05);border-left:3px solid var(--accent);border-radius:0 6px 6px 0;font-size:12.5px;font-style:italic;color:var(--muted);line-height:1.65}
.fc-face.back .fc-back-src{margin-top:10px;padding-top:6px;border-top:1px dashed var(--border);font-size:10.5px;color:var(--muted)}
.fc-face.back .fc-back-src a{color:var(--accent);text-decoration:none}
.fc-hint{font-size:12px;color:var(--muted);text-align:center;margin-top:8px}
.fc-rate{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;width:100%;max-width:680px;margin-top:10px}
.fc-rate-btn{padding:12px 8px;border:1px solid var(--border);background:#fff;color:var(--text);border-radius:8px;cursor:pointer;font-size:13px;font-weight:600;display:flex;flex-direction:column;gap:2px;align-items:center;transition:all 0.15s;box-shadow:var(--shadow)}
.fc-rate-btn:hover{transform:translateY(-2px);box-shadow:var(--shadow-hover)}
.fc-rate-btn .emo{font-size:22px}
.fc-rate-btn .label{font-size:12px}
.fc-rate-btn .interval{font-size:10px;color:var(--muted);font-weight:500}
.fc-rate-btn.again{border-color:var(--red);color:var(--red)}
.fc-rate-btn.again:hover{background:var(--red);color:#fff}
.fc-rate-btn.hard{border-color:var(--accent2);color:var(--accent2)}
.fc-rate-btn.hard:hover{background:var(--accent2);color:#fff}
.fc-rate-btn.good{border-color:var(--accent);color:var(--accent)}
.fc-rate-btn.good:hover{background:var(--accent);color:#fff}
.fc-rate-btn.easy{border-color:var(--teal);color:var(--teal)}
.fc-rate-btn.easy:hover{background:var(--teal);color:#fff}
.fc-controls{display:flex;gap:8px;justify-content:space-between;width:100%;max-width:680px;margin-top:8px;font-size:12px}
.fc-controls button{font-size:12px;padding:5px 12px}

.fc-mode-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}

/* Quiz mode (modal) */
.quiz-overlay{display:none;position:fixed;inset:0;background:rgba(15,30,20,0.5);z-index:2000;overflow-y:auto;padding:24px}
.quiz-overlay.show{display:block}
.quiz-modal{max-width:780px;margin:0 auto;background:var(--bg2);border-radius:14px;padding:24px;min-height:80vh;position:relative;box-shadow:0 12px 48px rgba(0,0,0,0.25);border:1px solid var(--border)}
.quiz-close{position:absolute;top:14px;right:14px;background:transparent;color:var(--text);border:1px solid var(--border);width:34px;height:34px;border-radius:50%;cursor:pointer;font-size:18px}
.quiz-close:hover{background:var(--card)}
.quiz-header{border-bottom:1px solid var(--border);padding-bottom:14px;margin-bottom:18px}
.quiz-header h2{margin:0;font-size:22px;color:var(--accent)}
.quiz-header .quiz-sub{color:var(--muted);margin-top:6px;font-size:14px}
.quiz-setup{display:flex;flex-direction:column;gap:14px}
.quiz-setup .row{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.quiz-setup label{font-size:13px;color:var(--muted);margin-right:8px}
.quiz-setup select, .quiz-setup input[type=number]{background:var(--card);border:1px solid var(--border);color:var(--text);padding:6px 10px;border-radius:6px;font-size:13px}
.quiz-mode-btns{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px}
.quiz-mode-btn{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:14px;cursor:pointer;text-align:center;transition:all 0.15s}
.quiz-mode-btn:hover{border-color:var(--accent);transform:translateY(-2px)}
.quiz-mode-btn .icon{font-size:24px;display:block;margin-bottom:6px}
.quiz-mode-btn .name{font-weight:600;font-size:14px;color:var(--text)}
.quiz-mode-btn .desc{font-size:11px;color:var(--muted);margin-top:4px}

.quiz-progress{display:flex;align-items:center;gap:10px;font-size:13px;color:var(--muted);margin-bottom:14px}
.quiz-progress .bar{flex:1;height:8px;background:var(--card);border-radius:4px;overflow:hidden}
.quiz-progress .fill{height:100%;background:linear-gradient(90deg,var(--accent),var(--green));transition:width 0.3s}
.quiz-question{background:var(--card);border-radius:10px;padding:16px 18px;margin-bottom:14px;border-left:3px solid var(--accent)}
.quiz-question .q-meta{font-size:11px;color:var(--muted);margin-bottom:6px;display:flex;gap:8px;flex-wrap:wrap}
.quiz-question .q-text{font-size:15px;line-height:1.6;font-weight:500}
.quiz-options{display:flex;flex-direction:column;gap:8px;margin-bottom:14px}
.quiz-option{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:12px 14px;cursor:pointer;font-size:14px;transition:all 0.15s;display:flex;gap:10px;box-shadow:var(--shadow)}
.quiz-option:hover{border-color:var(--accent);background:var(--card2)}
.quiz-option.selected{border-color:var(--accent);background:rgba(0,133,63,0.08)}
.quiz-option.correct{border-color:var(--green);background:rgba(0,133,63,0.18)}
.quiz-option.wrong{border-color:var(--red);background:rgba(198,40,40,0.12)}
.quiz-option .letter{font-weight:700;color:var(--muted);min-width:20px}
.quiz-option.correct .letter{color:var(--green)}
.quiz-option.wrong .letter{color:var(--red)}
.quiz-explain{background:rgba(0,133,63,0.06);border-left:3px solid var(--accent);padding:12px 14px;border-radius:0 6px 6px 0;margin-bottom:14px;font-size:13.5px;line-height:1.6;display:none}
.quiz-explain.show{display:block}
.quiz-explain .label{font-size:11px;color:var(--accent);text-transform:uppercase;font-weight:700;margin-bottom:4px}
.quiz-explain .quote{font-style:italic;color:var(--muted)}
.quiz-controls{display:flex;gap:8px;justify-content:space-between;align-items:center;flex-wrap:wrap}
.quiz-result{text-align:center;padding:28px 16px}
.quiz-result .score{font-size:48px;font-weight:700;color:var(--accent)}
.quiz-result .pct{font-size:18px;color:var(--muted);margin-top:6px}
.quiz-result .grade{font-size:22px;margin-top:14px;font-weight:600}
.quiz-result .review-btns{margin-top:24px;display:flex;gap:8px;justify-content:center;flex-wrap:wrap}

/* === ÔN TẬP NHANH section (separate) === */
.ontap-section{background:linear-gradient(135deg,#fff8e6 0%,#fffdf5 100%);border:2px solid var(--accent2);border-radius:14px;padding:20px 24px;margin:14px 0;box-shadow:0 4px 18px rgba(184,134,11,0.12)}
.ontap-section h2{margin:0 0 6px;font-size:20px;color:var(--accent2);display:flex;align-items:center;gap:10px}
.ontap-section .ontap-sub{color:var(--muted);font-size:13px;margin-bottom:14px}
.ontap-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px;margin-top:12px}
.ontap-card{background:#fff;border:1px solid var(--border);border-left:4px solid var(--accent2);border-radius:10px;padding:14px 16px;cursor:pointer;transition:all 0.2s;box-shadow:var(--shadow)}
.ontap-card:hover{transform:translateY(-2px);box-shadow:var(--shadow-hover);border-left-color:var(--accent)}
.ontap-card .ot-title{font-size:14.5px;font-weight:700;color:var(--text);margin-bottom:4px;line-height:1.4}
.ontap-card .ot-code{font-family:Consolas,monospace;font-size:11px;color:var(--accent);margin-bottom:6px}
.ontap-card .ot-stats{display:flex;gap:10px;font-size:12px;color:var(--muted);margin-top:8px}
.ontap-card .ot-stats .v{color:var(--accent2);font-weight:700}
.ontap-quick-btns{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}
.ontap-quick-btn{background:var(--accent2);color:#fff;border:none;padding:8px 14px;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600;transition:opacity 0.15s}
.ontap-quick-btn:hover{opacity:0.85}
.ontap-quick-btn.alt{background:var(--accent)}
.ontap-quick-btn.review{background:var(--red)}

/* ÔN TẬP NHANH quiz modal-specific extras */
.otn-mode-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin-top:14px}
.otn-mode-btn{background:#fff;border:2px solid var(--border);border-radius:10px;padding:18px 14px;cursor:pointer;text-align:center;transition:all 0.2s;box-shadow:var(--shadow)}
.otn-mode-btn:hover{border-color:var(--accent2);transform:translateY(-2px);box-shadow:var(--shadow-hover)}
.otn-mode-btn .icon{font-size:30px;display:block;margin-bottom:8px}
.otn-mode-btn .name{font-weight:700;font-size:15px;color:var(--text)}
.otn-mode-btn .desc{font-size:11.5px;color:var(--muted);margin-top:4px;line-height:1.4}
.otn-set-select{margin-top:14px;padding:14px;background:rgba(0,133,63,0.04);border-radius:8px;border:1px solid var(--border)}
.otn-set-select label{display:block;font-size:13px;font-weight:600;color:var(--accent);margin-bottom:6px}
.otn-set-checks{display:flex;flex-direction:column;gap:6px}
.otn-set-checks label{display:flex;align-items:center;gap:8px;font-weight:500;font-size:13px;color:var(--text);cursor:pointer;padding:6px 10px;border-radius:6px;transition:background 0.1s}
.otn-set-checks label:hover{background:rgba(0,133,63,0.06)}
.otn-set-checks input[type=checkbox]{width:16px;height:16px;accent-color:var(--accent2)}
.otn-keyhints{margin-top:14px;padding:10px 14px;background:rgba(184,134,11,0.08);border-left:3px solid var(--accent2);border-radius:0 6px 6px 0;font-size:12.5px;color:var(--muted);line-height:1.7}
.otn-keyhints kbd{background:#fff;border:1px solid var(--border);border-bottom-width:2px;border-radius:4px;padding:1px 7px;font-family:Consolas,monospace;font-size:11px;color:var(--text);font-weight:600}
.otn-mode-badge{display:inline-block;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px}
.otn-mode-badge.practice{background:rgba(0,133,63,0.15);color:var(--accent)}
.otn-mode-badge.exam{background:rgba(198,40,40,0.15);color:var(--red)}
.otn-mode-badge.review{background:rgba(184,134,11,0.15);color:var(--accent2)}

/* === ÔN TẬP NHANH — Card buttons === */
.ontap-card .ot-actions{display:flex;gap:6px;margin-top:10px;flex-wrap:wrap}
.ontap-card .ot-btn{flex:1;padding:8px 10px;border-radius:6px;border:1px solid var(--border);background:#fff;color:var(--text);font-size:12.5px;font-weight:600;cursor:pointer;transition:all 0.15s;text-align:center}
.ontap-card .ot-btn:hover{transform:translateY(-1px);box-shadow:var(--shadow)}
.ontap-card .ot-btn.read{background:var(--accent);color:#fff;border-color:var(--accent)}
.ontap-card .ot-btn.read:hover{background:#006B3F}
.ontap-card .ot-btn.quiz{background:var(--accent2);color:#fff;border-color:var(--accent2)}
.ontap-card .ot-btn.quiz:hover{background:#9a7009}

/* === ON_TAP READER — fullscreen modal === */
.otr-overlay{display:none;position:fixed;inset:0;background:rgba(15,30,20,0.55);z-index:2100;overflow-y:auto;padding:16px}
.otr-overlay.show{display:block}
.otr-modal{max-width:1280px;margin:0 auto;background:var(--bg);border-radius:14px;min-height:90vh;position:relative;box-shadow:0 16px 56px rgba(0,0,0,0.3);border:1px solid var(--border);overflow:hidden;display:flex;flex-direction:column}
.otr-head{position:sticky;top:0;background:linear-gradient(135deg,#00853F 0%,#006B3F 100%);color:#fff;padding:16px 24px;border-bottom:3px solid var(--accent2);z-index:10;display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.otr-head .otr-icon{font-size:28px}
.otr-head .otr-info{flex:1;min-width:200px}
.otr-head h2{margin:0;font-size:18px;font-weight:700;color:#fff;line-height:1.3}
.otr-head .otr-code{font-family:Consolas,monospace;font-size:12px;color:rgba(255,255,255,0.85);margin-top:2px}
.otr-head .otr-actions{display:flex;gap:8px;flex-wrap:wrap}
.otr-head .otr-btn{padding:7px 14px;border-radius:6px;background:rgba(255,255,255,0.18);color:#fff;border:1px solid rgba(255,255,255,0.3);cursor:pointer;font-size:13px;font-weight:600;text-decoration:none;backdrop-filter:blur(4px);transition:all 0.15s}
.otr-head .otr-btn:hover{background:rgba(255,255,255,0.3)}
.otr-head .otr-btn.gold{background:var(--accent2);border-color:var(--accent2)}
.otr-head .otr-btn.gold:hover{background:#9a7009}
.otr-head .otr-close{width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,0.15);color:#fff;border:1px solid rgba(255,255,255,0.25);cursor:pointer;font-size:20px;line-height:1;flex-shrink:0;transition:all 0.15s}
.otr-head .otr-close:hover{background:var(--red);border-color:var(--red);transform:rotate(90deg)}

.otr-body{display:grid;grid-template-columns:260px 1fr;gap:0;flex:1;overflow:hidden}
@media (max-width:900px){.otr-body{grid-template-columns:1fr}.otr-toc-wrap{display:none}}

.otr-toc-wrap{background:#fafdf9;border-right:1px solid var(--border);overflow-y:auto;max-height:calc(90vh - 80px);padding:16px 0}
.otr-toc-header{padding:0 16px 10px;font-size:11px;text-transform:uppercase;letter-spacing:0.6px;color:var(--accent);font-weight:700;border-bottom:1px dashed var(--border);margin-bottom:8px}
.otr-toc-list{list-style:none;margin:0;padding:0}
.otr-toc-list a{display:block;padding:6px 16px 6px 20px;color:var(--text);text-decoration:none;font-size:13px;border-left:3px solid transparent;transition:all 0.15s;line-height:1.4}
.otr-toc-list a:hover{background:rgba(0,133,63,0.06);color:var(--accent);border-left-color:rgba(0,133,63,0.3)}
.otr-toc-list a.active{background:rgba(0,133,63,0.1);color:var(--accent);border-left-color:var(--accent);font-weight:600}
.otr-toc-list a.h3{padding-left:32px;font-size:12.5px;color:var(--muted)}
.otr-toc-list a.h3:hover,.otr-toc-list a.h3.active{color:var(--accent)}

.otr-content-wrap{overflow-y:auto;max-height:calc(90vh - 80px);padding:24px 36px 60px;background:#fff;scroll-behavior:smooth}
.otr-content{max-width:880px;margin:0 auto;font-size:14.5px;line-height:1.78;color:var(--text)}
.otr-content h1{font-size:26px;color:var(--accent);border-bottom:3px solid var(--accent);padding-bottom:10px;margin:0 0 18px;font-weight:700}
.otr-content h2{font-size:20px;color:var(--accent);margin:32px 0 12px;padding:10px 14px;background:linear-gradient(90deg,rgba(0,133,63,0.08),transparent);border-left:4px solid var(--accent);border-radius:0 8px 8px 0;font-weight:700;scroll-margin-top:80px}
.otr-content h3{font-size:16.5px;color:var(--text);margin:22px 0 10px;font-weight:700;padding-left:10px;border-left:3px solid var(--accent2);scroll-margin-top:80px}
.otr-content p{margin:0 0 12px}
.otr-content ul,.otr-content ol{margin:8px 0 14px 0;padding-left:28px}
.otr-content li{margin-bottom:5px}
.otr-content li::marker{color:var(--accent2)}
.otr-content strong{color:var(--accent);font-weight:700}
.otr-content em{color:var(--muted);font-style:italic}
.otr-content code{background:rgba(0,133,63,0.08);color:var(--accent);padding:2px 7px;border-radius:4px;font-family:Consolas,monospace;font-size:13px;font-weight:600}
.otr-content blockquote{margin:14px 0;padding:12px 18px;background:linear-gradient(90deg,rgba(184,134,11,0.08),rgba(184,134,11,0.02));border-left:4px solid var(--accent2);border-radius:0 8px 8px 0;color:var(--text);font-size:14px}
.otr-content blockquote p{margin:0}
.otr-content blockquote p+p{margin-top:6px}
.otr-content table{border-collapse:collapse;width:100%;margin:16px 0;font-size:13.5px;border-radius:8px;overflow:hidden;box-shadow:var(--shadow)}
.otr-content table th{background:var(--accent);color:#fff;padding:10px 12px;text-align:left;font-weight:700;font-size:13px}
.otr-content table td{padding:8px 12px;border-bottom:1px solid var(--border);vertical-align:top;background:#fff}
.otr-content table tr:nth-child(even) td{background:#fafdf9}
.otr-content table tr:hover td{background:rgba(0,133,63,0.05)}
.otr-content a{color:var(--accent);text-decoration:none;font-weight:500;border-bottom:1px dashed var(--accent)}
.otr-content a:hover{border-bottom-style:solid}
.otr-content hr{border:none;border-top:2px dashed var(--border);margin:24px 0}
.otr-content pre{background:#f3f7f1;padding:14px 18px;border-radius:8px;overflow-x:auto;font-size:12.5px;line-height:1.6;border:1px solid var(--border)}
/* Highlight checkboxes from "checklist" lists */
.otr-content input[type=checkbox]{margin-right:8px;width:14px;height:14px;accent-color:var(--accent);vertical-align:middle}
/* Section anchor link visible on hover */
.otr-content h2:hover::after,.otr-content h3:hover::after{content:" 🔗";font-size:0.7em;color:var(--muted);opacity:0.6}

/* Floating "back to top" inside reader */
.otr-totop{position:absolute;bottom:24px;right:24px;width:42px;height:42px;border-radius:50%;background:var(--accent);color:#fff;border:none;cursor:pointer;font-size:20px;box-shadow:0 4px 14px rgba(0,133,63,0.4);display:none;align-items:center;justify-content:center;transition:transform 0.15s;z-index:5}
.otr-totop:hover{transform:translateY(-2px)}
.otr-totop.show{display:flex}

/* Reference tables */
.ref-section{background:var(--card);border-radius:12px;padding:20px;margin:14px 0}
.ref-section h2{margin-top:0;font-size:18px}
.ref-tabs{display:flex;gap:4px;border-bottom:1px solid var(--border);margin-bottom:14px;flex-wrap:wrap}
.ref-tab{padding:8px 14px;background:transparent;border:none;color:var(--muted);cursor:pointer;font-size:13px;border-bottom:2px solid transparent;font-weight:500}
.ref-tab.active{color:var(--accent);border-bottom-color:var(--accent)}
.ref-panel{display:none;max-height:600px;overflow-y:auto}
.ref-panel.active{display:block}
.ref-table{width:100%;border-collapse:collapse;font-size:13px}
.ref-table th{position:sticky;top:0;background:var(--accent);padding:10px 10px;text-align:left;border-bottom:2px solid var(--accent);font-size:12px;text-transform:uppercase;color:#fff;z-index:1;font-weight:700}
.ref-table td{padding:8px 10px;border-bottom:1px solid var(--border);vertical-align:top}
.ref-table tr:hover{background:rgba(0,133,63,0.04)}
.ref-table .val{font-family:Consolas,monospace;color:var(--accent2);font-weight:700;white-space:nowrap;background:rgba(184,134,11,0.08);padding:2px 6px;border-radius:3px}
.ref-table .code{font-family:Consolas,monospace;color:var(--accent);font-size:11px}
.ref-table .roman-link{color:var(--accent);cursor:pointer;text-decoration:none;font-weight:600}
.ref-table .roman-link:hover{text-decoration:underline}
.ref-search{padding:8px 12px;background:var(--bg2);border:1px solid var(--border);border-radius:6px;color:var(--text);width:100%;font-size:13px;margin-bottom:10px}

/* Reading guide section */
.rg-chain{background:#fff;border:1px solid var(--border);border-radius:12px;margin-bottom:14px;overflow:hidden;box-shadow:var(--shadow)}
.rg-chain-head{padding:14px 18px;background:linear-gradient(90deg,rgba(0,133,63,0.08),transparent);border-bottom:1px solid var(--border);cursor:pointer;display:flex;align-items:center;gap:10px}
.rg-chain-head:hover{background:linear-gradient(90deg,rgba(0,133,63,0.14),transparent)}
.rg-chain-head h3{margin:0;font-size:15px;color:var(--accent);flex:1;font-weight:700}
.rg-chain-head .rg-toggle{color:var(--muted);transition:transform 0.2s}
.rg-chain.expanded .rg-toggle{transform:rotate(90deg)}
.rg-chain-why{font-size:12.5px;color:var(--muted);font-style:italic;padding:0 18px 8px}
.rg-chain-stats{font-size:11px;color:var(--accent2);padding:0 18px 10px;font-weight:600}
.rg-chain-body{display:none;padding:14px 18px;background:rgba(0,133,63,0.02)}
.rg-chain.expanded .rg-chain-body{display:block}
.rg-step{background:#fff;border:1px solid var(--border);border-radius:8px;padding:12px 14px;margin-bottom:10px;border-left:3px solid var(--accent)}
.rg-step .rg-step-head{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;margin-bottom:6px}
.rg-step .rg-step-id{font-family:Consolas,monospace;font-weight:700;color:var(--accent);font-size:13px;background:rgba(0,133,63,0.08);padding:2px 8px;border-radius:4px}
.rg-step .rg-step-name{font-weight:600;font-size:14px;flex:1}
.rg-step .rg-step-code{font-family:Consolas,monospace;font-size:11px;color:var(--muted)}
.rg-step .rg-step-stats{font-size:11px;color:var(--muted);margin:4px 0 8px;display:flex;gap:10px;flex-wrap:wrap}
.rg-step .rg-step-stats .hot{color:var(--red);font-weight:600}
.rg-step .rg-hint{font-size:12.5px;line-height:1.7;padding:8px 10px;background:rgba(184,134,11,0.06);border-left:2px solid var(--accent2);border-radius:0 4px 4px 0;margin-top:6px;color:var(--text)}
.rg-step .rg-hint .lbl{color:var(--accent2);font-weight:700;font-size:11px;text-transform:uppercase;margin-right:6px}
.rg-step .rg-open{font-size:12px;color:var(--accent);cursor:pointer;text-decoration:none;font-weight:600;margin-top:6px;display:inline-block}
.rg-step .rg-open:hover{text-decoration:underline}

.rg-intro{background:linear-gradient(135deg,rgba(0,133,63,0.06),rgba(184,134,11,0.05));border-radius:10px;padding:14px 18px;margin-bottom:14px;font-size:13.5px;line-height:1.7}

/* Markdown rendered output (reading guide) */
.rg-rendered-md{background:#fff;border:1px solid var(--border);border-radius:10px;padding:24px 28px;line-height:1.75;max-height:75vh;overflow-y:auto;box-shadow:var(--shadow)}
.rg-rendered-md h1{font-size:22px;color:var(--accent);border-bottom:2px solid var(--accent);padding-bottom:8px;margin:0 0 14px}
.rg-rendered-md h2{font-size:18px;color:var(--accent);margin:24px 0 10px;padding-top:16px;border-top:1px dashed var(--border)}
.rg-rendered-md h2:first-of-type{border-top:none;padding-top:0}
.rg-rendered-md h3{font-size:15px;color:var(--text);margin:16px 0 8px;font-weight:700}
.rg-rendered-md p{margin:0 0 10px}
.rg-rendered-md ul,.rg-rendered-md ol{margin:0 0 12px 0;padding-left:24px}
.rg-rendered-md li{margin-bottom:4px;font-size:13.5px}
.rg-rendered-md strong{color:var(--accent);font-weight:700}
.rg-rendered-md em{color:var(--muted);font-style:italic}
.rg-rendered-md code{background:rgba(0,133,63,0.08);color:var(--accent);padding:2px 6px;border-radius:3px;font-family:Consolas,monospace;font-size:12.5px}
.rg-rendered-md blockquote{margin:10px 0;padding:8px 14px;background:rgba(184,134,11,0.06);border-left:3px solid var(--accent2);border-radius:0 6px 6px 0;color:var(--text)}
.rg-rendered-md blockquote p{margin:0}
.rg-rendered-md table{border-collapse:collapse;width:100%;margin:10px 0;font-size:12.5px}
.rg-rendered-md table th{background:var(--accent);color:#fff;padding:8px 10px;text-align:left;font-weight:700}
.rg-rendered-md table td{padding:6px 10px;border-bottom:1px solid var(--border);vertical-align:top}
.rg-rendered-md table tr:hover{background:rgba(0,133,63,0.04)}
.rg-rendered-md a{color:var(--accent);text-decoration:none;font-weight:500}
.rg-rendered-md a:hover{text-decoration:underline}
.rg-rendered-md pre{background:#f3f7f1;padding:10px 14px;border-radius:6px;overflow-x:auto;font-size:12px}
.rg-rendered-md hr{border:none;border-top:1px dashed var(--border);margin:16px 0}

/* Concepts tab */
.cc-list{display:grid;grid-template-columns:1fr;gap:10px}
@media (min-width:900px){.cc-list{grid-template-columns:1fr 1fr}}
@media (min-width:1400px){.cc-list{grid-template-columns:1fr 1fr 1fr}}
.cc-card{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:12px 14px;border-left:4px solid var(--purple);transition:border-color 0.15s}
.cc-card:hover{border-color:var(--accent)}
.cc-card .cc-head{display:flex;justify-content:space-between;align-items:baseline;gap:8px;margin-bottom:6px;flex-wrap:wrap}
.cc-card .cc-term{font-size:15px;font-weight:700;color:var(--purple);line-height:1.3}
.cc-card .cc-source{font-size:10px;color:var(--muted);font-family:Consolas,monospace;padding:2px 7px;background:rgba(107,33,168,0.08);border-radius:4px;cursor:pointer;border:1px solid transparent;transition:all 0.15s}
.cc-card .cc-source:hover{border-color:var(--purple);color:var(--purple)}
.cc-card .cc-source.unknown{cursor:default}
.cc-card .cc-source.unknown:hover{border-color:transparent;color:var(--muted)}
.cc-card .cc-def{font-size:13.5px;color:var(--text);line-height:1.6;white-space:pre-wrap}
.cc-card .cc-def strong{color:var(--accent);font-weight:700}
.cc-search{margin-bottom:12px;padding:8px 12px;background:var(--card);border:1px solid var(--border);border-radius:6px;color:var(--text);width:100%;font-size:13px}
.cc-search:focus{outline:none;border-color:var(--accent)}
.cc-source-tag{font-size:10px;padding:1px 6px;border-radius:8px;font-weight:600;text-transform:uppercase}
.cc-source-tag.law{background:rgba(0,133,63,0.12);color:var(--accent);border:1px solid rgba(0,133,63,0.25)}
.cc-source-tag.ontap{background:rgba(184,134,11,0.12);color:var(--accent2);border:1px solid rgba(184,134,11,0.25)}

/* Thresholds tab */
.th-summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px;margin-bottom:14px}
.th-summary-cell{background:var(--card);border-radius:6px;padding:8px 10px;border-left:3px solid var(--accent2);font-size:12px;box-shadow:var(--shadow)}
.th-summary-cell .v{font-size:18px;font-weight:700;color:var(--accent2);font-family:Consolas,monospace}
.th-summary-cell .l{font-size:11px;color:var(--muted);text-transform:uppercase}
.th-list{display:grid;grid-template-columns:1fr;gap:8px}
.th-card{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:12px 14px;border-left:4px solid var(--yellow)}
.th-card .th-head{display:flex;flex-wrap:wrap;gap:8px;align-items:baseline;margin-bottom:6px}
.th-card .th-val{font-size:17px;font-weight:700;color:var(--accent2);font-family:Consolas,monospace;background:rgba(184,134,11,0.1);padding:2px 10px;border-radius:6px;border:1px solid rgba(184,134,11,0.2)}
.th-card .th-type{font-size:11px;color:var(--accent);padding:1px 8px;background:rgba(0,133,63,0.08);border-radius:9px;text-transform:uppercase;font-weight:600}
.th-card .th-ref{font-size:12px;color:var(--muted);font-family:Consolas,monospace;cursor:pointer;border-bottom:1px dashed var(--muted);transition:all 0.15s}
.th-card .th-ref:hover{color:var(--accent);border-bottom-color:var(--accent)}
.th-card .th-desc{font-size:13px;color:var(--text);margin:4px 0 6px}
.th-card .th-quote{font-size:13px;color:var(--text);font-style:italic;padding:8px 12px;background:rgba(0,133,63,0.04);border-left:2px solid var(--accent);border-radius:0 4px 4px 0;line-height:1.6}
.th-card .th-quote::before{content:'"';color:var(--accent);font-weight:700}
.th-card .th-quote::after{content:'"';color:var(--accent);font-weight:700}

/* Inline popover for click on Điều */
.dieu-popover{margin-top:10px;background:#f9fbf8;border:1px solid var(--accent);border-radius:6px;padding:12px 14px;font-size:13px;line-height:1.65;white-space:pre-wrap;animation:slideIn 0.2s ease;box-shadow:0 4px 12px rgba(0,133,63,0.1)}
.dieu-popover .pop-head{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:8px;padding-bottom:6px;border-bottom:1px dashed var(--border);font-size:12px}
.dieu-popover .pop-head .pop-title{color:var(--accent);font-weight:700;font-family:Consolas,monospace}
.dieu-popover .pop-head .pop-close{background:transparent;color:var(--muted);border:none;cursor:pointer;font-size:14px;padding:0 4px}
.dieu-popover .pop-head .pop-close:hover{color:var(--red)}
.dieu-popover .pop-source{font-size:11px;color:var(--muted);margin-top:8px;padding-top:6px;border-top:1px dashed var(--border);font-style:italic}
.dieu-popover .pop-source a{color:var(--accent);text-decoration:none}
@keyframes slideIn{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:translateY(0)}}

/* Mindmap */
.mindmap-container{background:#fff;border-radius:12px;padding:20px;min-height:400px;position:relative;overflow-x:auto}
.mindmap-container .mm-loading{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#64748b;font-size:13px}
.mindmap-container .mermaid{font-family:inherit}
.mindmap-toolbar{display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap;align-items:center}
.mm-info{font-size:12px;color:var(--muted);font-style:italic;padding:8px;background:rgba(56,189,248,0.05);border-left:2px solid var(--accent);border-radius:0 4px 4px 0;margin-bottom:10px}

/* Questions */
.q-list{display:flex;flex-direction:column;gap:10px}
.q-item{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:12px 14px;font-size:13.5px}
.q-item .q-header{font-size:11px;color:var(--muted);margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px}
.q-item .q-id{color:var(--accent);font-weight:600;font-family:Consolas,monospace}
.q-item .q-mang{color:var(--muted);font-size:11px}
.q-item .q-text{font-weight:500;margin-bottom:8px;line-height:1.55}
.q-options{display:flex;flex-direction:column;gap:4px;margin-bottom:8px}
.q-option{padding:6px 10px;border-radius:4px;background:rgba(0,133,63,0.04);display:flex;gap:8px;align-items:flex-start;font-size:13px;line-height:1.5;border:1px solid var(--border)}
.q-option .q-letter{font-weight:700;color:var(--muted);min-width:18px}
.q-option.correct{background:rgba(0,133,63,0.15);border-left:3px solid var(--green);border-color:var(--green)}
.q-option.correct .q-letter{color:var(--green)}
.q-ref{font-size:11px;color:var(--muted);font-style:italic;border-top:1px dashed var(--border);padding-top:6px;margin-top:6px}
.q-ref strong{color:var(--accent2)}

.empty{text-align:center;padding:48px 24px;color:var(--muted);font-size:14px}
.note{font-size:12px;color:var(--text);font-style:italic;margin-top:8px;padding:10px;background:rgba(184,134,11,0.08);border-left:3px solid var(--accent2);border-radius:0 4px 4px 0}

@media (max-width:640px){
  .docs-grid{grid-template-columns:1fr}
  header h1{font-size:22px}
  .drawer{width:100%}
}
</style>
</head>
<body>
<header>
<div class="container">
<h1>🎓 Ôn tập 39 văn bản pháp lý — Hội thi CĐS Ngân hàng</h1>
<div class="subtitle">Hệ thống học theo 8 chủ đề BTC · Trích nguyên văn từ master CSV + ON_TAP NHOM + 400 câu BTC · Click card để xem chi tiết, click Điều để xem nguyên văn</div>
<div class="stats">
<div class="stat"><div class="stat-value" id="stat-total">0</div><div class="stat-label">Văn bản</div></div>
<div class="stat"><div class="stat-value" id="stat-dieus">0</div><div class="stat-label">Tổng Điều</div></div>
<div class="stat"><div class="stat-value" id="stat-concepts">0</div><div class="stat-label">Khái niệm</div></div>
<div class="stat"><div class="stat-value" id="stat-thresholds">0</div><div class="stat-label">Ngưỡng số liệu</div></div>
<div class="stat"><div class="stat-value" id="stat-keynotes">0</div><div class="stat-label">Keynotes</div></div>
<div class="stat"><div class="stat-value" id="stat-questions">0</div><div class="stat-label">Câu hỏi BTC</div></div>
<div class="stat"><div class="stat-value" id="stat-studied">0</div><div class="stat-label">Đã học</div></div>
</div>
<div style="margin-top:16px;display:flex;gap:8px;flex-wrap:wrap">
<button class="btn" style="font-size:14px;padding:10px 18px" onclick="openQuiz()">🎯 Luyện thi (Quiz)</button>
<button class="btn" style="font-size:14px;padding:10px 18px;background:var(--accent2);color:#fff" onclick="openFlashcards()">📇 Flashcards</button>
<button class="btn secondary" style="font-size:14px;padding:10px 18px;background:rgba(255,255,255,0.1);color:#fff;border:1px solid rgba(255,255,255,0.2)" onclick="document.getElementById('ref-section').scrollIntoView({behavior:'smooth'})">📋 Bảng tra cứu</button>
</div>
</div>
</header>

<main class="container">

<section>
<h2>💡 Mẹo ôn tập</h2>
<div class="tips-grid">
<div class="tip-card"><h3>1. Click chủ đề BTC</h3><p>Click vào chip "I" đến "VIII" để xem "Bức tranh 1 trang" của chủ đề + lọc các VB liên quan.</p></div>
<div class="tip-card"><h3>2. Tab "🎯 Keynotes"</h3><p>Mỗi VB có 5-25 keynotes verbatim từ 8 file ON_TAP — đây là điểm hay hỏi nhất trong đề.</p></div>
<div class="tip-card"><h3>3. Tab "❓ Câu hỏi BTC"</h3><p>170+ câu trong 400 câu BTC đã được map sang VB cụ thể, kèm đáp án + reference Điều khoản.</p></div>
<div class="tip-card"><h3>4. Tab "📑 Mục lục Điều"</h3><p>1400+ Điều nguyên văn — click từng Điều để bung xem chi tiết, phục vụ tra cứu nhanh.</p></div>
<div class="tip-card"><h3>5. Đánh dấu Đã học</h3><p>Nút ⭐ ở góc drawer — tiến độ lưu localStorage. Mục tiêu: 39/39 trước thi.</p></div>
<div class="tip-card"><h3>6. Combo nên dùng</h3><p>1. Click chủ đề → đọc Bức tranh 1 trang → 2. Click VB từng cái → đọc Tóm tắt → 3. Tab Keynotes → 4. Tab Câu hỏi → 5. Tab Mục lục Điều khi cần tra cụ thể.</p></div>
</div>
</section>

<section id="ontap-nhanh-section" class="ontap-section">
<h2>⚡ ÔN TẬP NHANH — Trắc nghiệm từ file ON_TAP cá nhân <span style="font-size:11px;background:var(--red);color:#fff;padding:2px 8px;border-radius:10px;font-weight:600">MỚI</span></h2>
<div class="ontap-sub">Bộ câu trắc nghiệm xây từ phần "Câu hỏi tự kiểm tra" trong các file ON_TAP do bạn tổng hợp. Hoàn toàn TÁCH RIÊNG với hệ thống quiz chính.</div>
<div id="ontap-grid" class="ontap-grid"></div>
<div class="ontap-quick-btns">
<button class="ontap-quick-btn" onclick="openOntapNhanh('practice')">📚 Ôn tập (xem đáp án ngay)</button>
<button class="ontap-quick-btn alt" onclick="openOntapNhanh('exam')">🎯 Thi (đếm điểm cuối)</button>
<button class="ontap-quick-btn review" onclick="openOntapNhanh('wrong')">🔁 Làm lại câu sai</button>
</div>
<div class="otn-keyhints">
⌨️ <strong>Phím tắt:</strong>
<kbd>A</kbd><kbd>B</kbd><kbd>C</kbd><kbd>D</kbd> chọn đáp án ·
<kbd>1</kbd><kbd>2</kbd><kbd>3</kbd><kbd>4</kbd> chọn đáp án ·
<kbd>Space</kbd> / <kbd>→</kbd> / <kbd>Enter</kbd> câu tiếp ·
<kbd>←</kbd> câu trước ·
<kbd>Esc</kbd> đóng
</div>
</section>

<section id="reading-guide-section">
<h2>📖 Thứ tự đọc + Lưu ý từng VB <button class="btn secondary" style="font-size:12px;padding:5px 10px;margin-left:10px" onclick="toggleReadingGuide()" id="rg-toggle-btn">Mở rộng ▼</button></h2>
<div id="rg-content" style="display:none">
<div class="rg-intro" id="rg-rendered">⏳ Đang tải nội dung từ <code>HUONG_DAN_DOC.md</code>...</div>
</div>
</section>

<section>
<div class="filter-bar">
<div class="filter-row">
<input id="search" type="text" placeholder="🔍 Tìm theo tên, số hiệu, từ khóa, keynote…">
<div class="chip-group" id="cat-chips"></div>
</div>
<div class="filter-row" style="margin-top:8px">
<span style="font-size:12px;color:var(--muted)">Chủ đề BTC (click để xem Bức tranh 1 trang):</span>
<div class="chip-group" id="topic-chips"></div>
<button class="chip" id="reset-btn" style="margin-left:auto;background:transparent;color:var(--muted)">↺ Reset</button>
</div>
<div class="filter-row" style="margin-top:8px">
<span style="font-size:12px;color:var(--muted)">Trạng thái:</span>
<div class="chip-group" id="status-chips"></div>
</div>
</div>
<div class="topic-overview-card" id="topic-overview">
<h3 id="to-title"></h3>
<div class="content" id="to-content"></div>
</div>
</section>

<section>
<h2>📚 Danh sách văn bản <span class="badge-count" id="visible-count">0</span></h2>
<div class="docs-grid" id="docs-grid"></div>
<div class="empty" id="empty-msg" style="display:none">Không tìm thấy văn bản nào khớp.</div>
</section>

<section id="ref-section">
<h2>📋 Bảng tra cứu — Cheat sheet ôn nhanh</h2>
<div class="ref-section">
<div class="ref-tabs">
<button class="ref-tab active" data-rtab="thresholds">📊 Ngưỡng số liệu (548)</button>
<button class="ref-tab" data-rtab="hieuluc">📅 Ngày hiệu lực</button>
<button class="ref-tab" data-rtab="phat">💰 Mức phạt</button>
<button class="ref-tab" data-rtab="thoigian">⏱️ Ngưỡng thời gian</button>
<button class="ref-tab" data-rtab="concepts">🔑 Khái niệm (214)</button>
</div>
<input type="text" class="ref-search" id="ref-search" placeholder="🔍 Tìm trong bảng…" oninput="filterRefTable(this.value)">
<div class="ref-panel active" id="rpanel-thresholds"></div>
<div class="ref-panel" id="rpanel-hieuluc"></div>
<div class="ref-panel" id="rpanel-phat"></div>
<div class="ref-panel" id="rpanel-thoigian"></div>
<div class="ref-panel" id="rpanel-concepts"></div>
</div>
</section>

</main>

<!-- Quiz modal -->
<div class="quiz-overlay" id="quiz-overlay">
<div class="quiz-modal">
<button class="quiz-close" onclick="closeQuiz()">×</button>
<div id="quiz-content"></div>
</div>
</div>

<!-- Flashcard modal -->
<div class="quiz-overlay" id="fc-overlay">
<div class="quiz-modal">
<button class="quiz-close" onclick="closeFlashcards()">×</button>
<div id="fc-content"></div>
</div>
</div>

<!-- ÔN TẬP NHANH modal (separate from main quiz) -->
<div class="quiz-overlay" id="otn-overlay">
<div class="quiz-modal">
<button class="quiz-close" onclick="closeOntapNhanh()">×</button>
<div id="otn-content"></div>
</div>
</div>

<!-- ON_TAP READER modal — beautiful MD viewer with TOC -->
<div class="otr-overlay" id="otr-overlay">
<div class="otr-modal" id="otr-modal">
<div class="otr-head" id="otr-head">
<span class="otr-icon">📘</span>
<div class="otr-info">
<h2 id="otr-title">Đang tải...</h2>
<div class="otr-code" id="otr-code"></div>
</div>
<div class="otr-actions">
<button class="otr-btn gold" id="otr-quiz-btn">✍️ Làm trắc nghiệm</button>
<button class="otr-btn" onclick="otrCopyLink()">🔗 Sao chép link</button>
</div>
<button class="otr-close" onclick="closeOntapReader()" title="Đóng (Esc)">×</button>
</div>
<div class="otr-body">
<aside class="otr-toc-wrap" id="otr-toc-wrap">
<div class="otr-toc-header">📑 Mục lục</div>
<ul class="otr-toc-list" id="otr-toc"></ul>
</aside>
<div class="otr-content-wrap" id="otr-content-wrap">
<article class="otr-content" id="otr-content">⏳ Đang render markdown...</article>
<button class="otr-totop" id="otr-totop" onclick="document.getElementById('otr-content-wrap').scrollTo({top:0,behavior:'smooth'})" title="Lên đầu trang">↑</button>
</div>
</div>
</div>
</div>

<div class="drawer-overlay" id="overlay" onclick="closeDrawer()"></div>
<div class="drawer" id="drawer">
<div class="drawer-inner">
<div class="drawer-head">
<button class="close" onclick="closeDrawer()" title="Đóng (Esc)">×</button>
<h2 id="d-title"></h2>
<div class="meta" id="d-meta"></div>
<div class="actions" id="d-actions"></div>
</div>
<div class="drawer-body">
<div class="tabs" id="tabs">
<button class="tab active" data-tab="summary">📝 Tóm tắt</button>
<button class="tab" data-tab="concepts">🔑 Khái niệm <span class="count" id="cnt-cc">0</span></button>
<button class="tab" data-tab="thresholds">📊 Ngưỡng <span class="count" id="cnt-th">0</span></button>
<button class="tab" data-tab="keynotes">🎯 Keynotes <span class="count" id="cnt-kn">0</span></button>
<button class="tab" data-tab="questions">❓ Câu hỏi <span class="count" id="cnt-q">0</span></button>
<button class="tab" data-tab="toc">📑 Mục lục Điều <span class="count" id="cnt-d">0</span></button>
<button class="tab" data-tab="mindmap">🧠 Mindmap</button>
<button class="tab" data-tab="new">🆕 Điểm mới</button>
<button class="tab" data-tab="links">🔗 Liên kết</button>
</div>
<div class="tab-panel active" id="panel-summary"></div>
<div class="tab-panel" id="panel-concepts"></div>
<div class="tab-panel" id="panel-thresholds"></div>
<div class="tab-panel" id="panel-mindmap"></div>
<div class="tab-panel" id="panel-keynotes"></div>
<div class="tab-panel" id="panel-questions"></div>
<div class="tab-panel" id="panel-toc"></div>
<div class="tab-panel" id="panel-new"></div>
<div class="tab-panel" id="panel-links"></div>
</div>
</div>
</div>

<script>
const DATA = __DATA_JSON__;
const STORAGE_KEY = 'cds_studied_docs';      // legacy
const FILE_STATE_KEY = 'cds_file_states';    // new: {stt: {status, note}}

function loadFileStates(){
  try{
    const raw = JSON.parse(localStorage.getItem(FILE_STATE_KEY) || '{}');
    // Migrate legacy 'studied' Set
    const legacy = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    if(legacy.length){
      legacy.forEach(stt => { if(!raw[stt]) raw[stt] = {status:'done', note:''}; });
      localStorage.setItem(FILE_STATE_KEY, JSON.stringify(raw));
      localStorage.removeItem(STORAGE_KEY);
    }
    return raw;
  }catch(e){ return {}; }
}
function saveFileStates(){ localStorage.setItem(FILE_STATE_KEY, JSON.stringify(fileStates)); }
let fileStates = loadFileStates();
function getStatus(stt){ return (fileStates[stt]||{}).status || ''; }
function getNote(stt){ return (fileStates[stt]||{}).note || ''; }
function setDocStatus(stt, status){
  fileStates[stt] = fileStates[stt] || {};
  if(status) fileStates[stt].status = status;
  else delete fileStates[stt].status;
  saveFileStates();
}
function setDocNote(stt, note){
  fileStates[stt] = fileStates[stt] || {};
  if(note && note.trim()) fileStates[stt].note = note.trim();
  else delete fileStates[stt].note;
  saveFileStates();
}
// Legacy alias for code that still uses 'studied'
const studied = {
  has: s => getStatus(s) === 'done',
  add: s => setDocStatus(s, 'done'),
  delete: s => setDocStatus(s, ''),
  get size(){ return Object.values(fileStates).filter(v=>v.status==='done').length; }
};

let activeCategory = null, activeTopic = null, activeStatus = null, searchTerm = '';

const TOPIC_NAMES = DATA.topics;
const TOPIC_OVERVIEWS = DATA.topic_overviews || {};
const docs = DATA.docs;

// Build code -> doc map for keynote click navigation
const codeToDoc = {};
docs.forEach(d => {
  codeToDoc[d.code] = d;
  // Also map by simpler patterns: "14/2022" -> doc
  const m = (d.code||'').match(/^(\d+)[\/\.\-](\d{4})/);
  if(m){
    codeToDoc[m[1]+'/'+m[2]] = d;
    codeToDoc[m[1]+'.'+m[2]] = d;
    codeToDoc[m[1]+'-'+m[2]] = d;
  }
});
const sttToDoc = {};
docs.forEach(d => sttToDoc[d.stt] = d);

function init(){
  document.getElementById('stat-total').textContent = docs.length;
  document.getElementById('stat-dieus').textContent = docs.reduce((s,d)=>s+(d.structure?d.structure.total_dieus:0),0);
  document.getElementById('stat-concepts').textContent = docs.reduce((s,d)=>s+(d.concepts?d.concepts.length:0),0);
  document.getElementById('stat-thresholds').textContent = docs.reduce((s,d)=>s+(d.thresholds?d.thresholds.length:0),0);
  document.getElementById('stat-keynotes').textContent = docs.reduce((s,d)=>s+(d.keynotes?d.keynotes.length:0),0);
  document.getElementById('stat-questions').textContent = docs.reduce((s,d)=>s+(d.questions?d.questions.length:0),0);
  updateStudiedStat();

  const cats = [...new Set(docs.map(d=>d.section))];
  document.getElementById('cat-chips').innerHTML = cats.map(c=>`<button class="chip" data-cat="${escapeAttr(c)}">${escapeHtml(c)} <span style="opacity:0.6">(${docs.filter(d=>d.section===c).length})</span></button>`).join('');

  document.getElementById('topic-chips').innerHTML = Object.entries(TOPIC_NAMES).map(([k,v])=>{
    const n = docs.filter(d=>(d.topics_main||[]).includes(k)||(d.topics_secondary||[]).includes(k)).length;
    return `<button class="chip topic-chip" data-topic="${k}"><span class="topic-badge main topic-${k}" style="margin-right:6px;display:inline-block">${k}</span>${escapeHtml((v.split('. ')[1]||v).split(' – ')[0])} <span style="opacity:0.6">(${n})</span></button>`;
  }).join('');

  document.getElementById('cat-chips').addEventListener('click', e=>{
    const btn = e.target.closest('.chip');
    if(btn){ activeCategory = (activeCategory===btn.dataset.cat)?null:btn.dataset.cat; renderChips(); renderDocs(); }
  });
  document.getElementById('topic-chips').addEventListener('click', e=>{
    const btn = e.target.closest('.chip');
    if(btn){
      activeTopic = (activeTopic===btn.dataset.topic) ? null : btn.dataset.topic;
      renderChips();
      renderDocs();
      showTopicOverview();
    }
  });
  document.getElementById('search').addEventListener('input', e=>{ searchTerm=e.target.value.toLowerCase().trim(); renderDocs(); });
  document.getElementById('reset-btn').addEventListener('click', ()=>{
    activeCategory=null;activeTopic=null;activeStatus=null;searchTerm='';
    document.getElementById('search').value=''; renderChips(); renderStatusChips(); renderDocs(); showTopicOverview();
  });

  document.querySelectorAll('.tab').forEach(t=>{
    t.addEventListener('click', ()=>{
      document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach(x=>x.classList.remove('active'));
      t.classList.add('active');
      const panel = document.getElementById('panel-'+t.dataset.tab);
      panel.classList.add('active');
      // Lazy render mindmap when tab is activated
      if(t.dataset.tab === 'mindmap' && _currentDrawerStt && !panel.dataset.rendered){
        const d = sttToDoc[_currentDrawerStt];
        if(d){ renderMindmap(d); panel.dataset.rendered = '1'; }
      }
    });
  });

  document.addEventListener('keydown', e=>{
    // ON_TAP reader modal — its own handler
    if(document.getElementById('otr-overlay').classList.contains('show')){
      otrKeyHandler(e);
      return;
    }
    // Ôn tập nhanh modal has its own keyboard handler — skip global Esc only
    if(document.getElementById('otn-overlay').classList.contains('show')){
      otnKeyHandler(e);
      return;
    }
    if(e.key==='Escape'){
      if(document.getElementById('fc-overlay').classList.contains('show')) closeFlashcards();
      else if(document.getElementById('quiz-overlay').classList.contains('show')) closeQuiz();
      else closeDrawer();
    }
  });
  renderDocs();
  renderRefTables();
  renderStatusChips();
  renderOntapNhanhGrid();
}

function renderChips(){
  document.querySelectorAll('#cat-chips .chip').forEach(c=>c.classList.toggle('active', c.dataset.cat===activeCategory));
  document.querySelectorAll('#topic-chips .chip').forEach(c=>c.classList.toggle('active', c.dataset.topic===activeTopic));
}

function showTopicOverview(){
  const card = document.getElementById('topic-overview');
  if(activeTopic && TOPIC_OVERVIEWS[activeTopic]){
    document.getElementById('to-title').textContent = '📍 ' + TOPIC_NAMES[activeTopic];
    document.getElementById('to-content').textContent = TOPIC_OVERVIEWS[activeTopic];
    card.classList.add('show');
  } else {
    card.classList.remove('show');
  }
}

function matches(d){
  if(activeCategory && d.section !== activeCategory) return false;
  if(activeTopic){
    const all = [...(d.topics_main||[]), ...(d.topics_secondary||[])];
    if(!all.includes(activeTopic)) return false;
  }
  if(activeStatus){
    const s = getStatus(d.stt);
    if(activeStatus === 'none' && s) return false;
    if(activeStatus === 'has-note' && !getNote(d.stt)) return false;
    if(['done','review','important'].includes(activeStatus) && s !== activeStatus) return false;
  }
  if(searchTerm){
    const knText = (d.keynotes||[]).map(k=>k.text).join(' ');
    const qText = (d.questions||[]).map(q=>q.question).join(' ');
    const note = getNote(d.stt);
    const hay = [d.short_name,d.full_name,d.code,d.keywords,d.summary,d.roman_id,knText,qText,note].join(' ').toLowerCase();
    if(!hay.includes(searchTerm)) return false;
  }
  return true;
}

function renderDocs(){
  const grid = document.getElementById('docs-grid');
  const visible = docs.filter(matches);
  document.getElementById('visible-count').textContent = visible.length;
  document.getElementById('empty-msg').style.display = visible.length?'none':'block';
  grid.innerHTML = visible.map(d=>{
    const mainT = (d.topics_main||[]).map(t=>`<span class="topic-badge main topic-${t}" title="${escapeAttr(TOPIC_NAMES[t]||t)}">${t}</span>`).join('');
    const secT = (d.topics_secondary||[]).map(t=>`<span class="topic-badge sec topic-${t}" title="${escapeAttr(TOPIC_NAMES[t]||t)}">${t}</span>`).join('');
    const status = getStatus(d.stt);
    const hasNote = !!getNote(d.stt);
    const nK = (d.keynotes||[]).length, nQ = (d.questions||[]).length, nD = d.structure?d.structure.total_dieus:0;
    const nC = (d.concepts||[]).length, nT = (d.thresholds||[]).length;
    return `<div class="doc-card ${status?'s-'+status:''}" onclick="openDoc(${d.stt})" style="position:relative">
      ${hasNote?`<span class="has-note" title="Có ghi chú">📝</span>`:''}
      <div class="head"><span class="roman-id">${d.roman_id}</span><span class="cat-icon" title="${escapeAttr(d.category)}">${d.category_icon}</span></div>
      <div class="title">${escapeHtml(d.short_name)}</div>
      <div class="code">${escapeHtml(d.code)} · ${d.date}</div>
      <div class="topics">${mainT}${secT}</div>
      <div class="metrics">
        <span class="metric ${nC?'has':''}">🔑 ${nC}</span>
        <span class="metric ${nT?'has':''}">📊 ${nT}</span>
        <span class="metric ${nK?'has':''}">🎯 ${nK}</span>
        <span class="metric ${nQ?'has-q':''}">❓ ${nQ}</span>
        <span class="metric">📑 ${nD}</span>
      </div>
    </div>`;
  }).join('');
}

function openDoc(stt){
  const d = docs.find(x=>x.stt===stt);
  if(!d) return;
  document.getElementById('d-title').innerHTML = `${d.roman_id} — ${escapeHtml(d.short_name)}`;
  document.getElementById('d-meta').innerHTML = `<span>${d.category_icon} <strong>${escapeHtml(d.category)}</strong> ${escapeHtml(d.code)}</span><span>📅 ${d.date}</span><span>${d.structure?d.structure.total_dieus+' Điều':'Không có cấu trúc Điều'}</span>`;
  const isStudied = studied.has(d.stt);
  // Count auto-gen questions + flashcards for this doc
  const docAutoQs = (PRACTICE.questions||[]).filter(q => q.doc_stt === d.stt);
  const docFcCount = (d.concepts||[]).length + (d.thresholds||[]).length;
  const curStatus = getStatus(d.stt);
  document.getElementById('d-actions').innerHTML = `
    <select class="status-select ${curStatus}" onchange="onStatusChange(${d.stt}, this.value)" id="status-select">
      <option value="" ${!curStatus?'selected':''}>📋 Chưa học</option>
      <option value="done" ${curStatus==='done'?'selected':''}>✓ Đã học</option>
      <option value="review" ${curStatus==='review'?'selected':''}>🔄 Cần học lại</option>
      <option value="important" ${curStatus==='important'?'selected':''}>⭐ Quan trọng</option>
    </select>
    <button class="btn" style="background:var(--accent2);color:#fff" onclick="startStudyFlow(${d.stt})">🎓 Học + Luyện ${docAutoQs.length} câu</button>
    <button class="btn" style="background:var(--purple);color:#fff" onclick="startFcForDoc(${d.stt})">📇 Flashcard VB này (${docFcCount} thẻ)</button>
    <button class="btn secondary" onclick="toggleNoteSection()">📝 ${getNote(d.stt)?'Sửa ghi chú':'Thêm ghi chú'}</button>
    ${d.word_file ? `<a class="btn secondary" href="${escapeAttr('TAI LIEU THAM KHAO/'+d.word_file)}" target="_blank">📄 Mở file</a>`:''}
    ${d.md_file ? `<a class="btn secondary" href="${escapeAttr('vcb_cds_202605/van_ban/'+d.md_file)}" target="_blank">📝 MD</a>`:''}
    ${d.source_url ? `<a class="btn secondary" href="${escapeAttr(d.source_url)}" target="_blank">🌐 Nguồn</a>`:''}
  `;

  // Tab counts
  document.getElementById('cnt-cc').textContent = (d.concepts||[]).length;
  document.getElementById('cnt-th').textContent = (d.thresholds||[]).length;
  document.getElementById('cnt-kn').textContent = (d.keynotes||[]).length;
  document.getElementById('cnt-q').textContent = (d.questions||[]).length;
  document.getElementById('cnt-d').textContent = d.structure?d.structure.total_dieus:0;

  // Tab: Summary (with personal note section)
  const curNote = getNote(d.stt);
  document.getElementById('panel-summary').innerHTML = `
    <div class="note-section" id="note-section" style="display:${curNote?'block':'none'}">
      <div class="note-label">📝 Ghi chú cá nhân (lưu trong trình duyệt)</div>
      <textarea class="note-textarea" id="note-textarea" oninput="onNoteChange(${d.stt}, this.value)" placeholder="Ghi chú gì đó về VB này — chỗ khó nhớ, cần tra cứu lại, liên hệ với VB khác...">${escapeHtml(curNote)}</textarea>
      <div class="note-hint">Tự động lưu mỗi khi gõ · Hiển thị 📝 trên card · Filter "Có ghi chú" để xem lại</div>
    </div>
    <div class="summary-block"><div class="label">Tên đầy đủ</div><div>${escapeHtml(d.full_name)}</div></div>
    <div class="summary-block"><div class="label">⭐ Nội dung chính (trích từ master_documents.csv)</div><div>${escapeHtml(d.summary||'')}</div></div>
    <div class="summary-block"><div class="label">🏷️ Từ khóa chính</div><div class="keywords">${(d.keywords||'').split(';').filter(s=>s.trim()).map(k=>`<span class="keyword">${escapeHtml(k.trim())}</span>`).join('')}</div></div>
    <div class="summary-block"><div class="label">📊 Chủ đề BTC</div><div>
      <strong>Chính:</strong> ${(d.topics_main||[]).map(t=>`<span class="topic-badge main topic-${t}">${t} ${escapeHtml((TOPIC_NAMES[t]||'').split('. ')[1]||'')}</span>`).join(' ')}<br>
      <strong>Phụ:</strong> ${(d.topics_secondary||[]).map(t=>`<span class="topic-badge sec topic-${t}">${t} ${escapeHtml((TOPIC_NAMES[t]||'').split('. ')[1]||'')}</span>`).join(' ')||'<em style="color:var(--muted)">không</em>'}
    </div></div>
  `;

  // Tab: Keynotes — grouped by source topic with inline highlights
  const kns = d.keynotes||[];
  if(kns.length){
    // Group by topic
    const byTopic = {};
    kns.forEach(kn=>{ (byTopic[kn.topic] = byTopic[kn.topic]||[]).push(kn); });
    const order = ['I','II','III','IV','V','VI','VII','VIII'];
    const groupsHtml = order.filter(t=>byTopic[t]).map(t=>{
      const items = byTopic[t].map((kn,i)=>{
        const srcFile = ONTAP_FILES[kn.topic] || '';
        const srcPath = srcFile ? `vcb_cds_202605/${srcFile}` : '';
        return `<div class="kn-card">
          <span class="kn-num">#${i+1}</span>
          <div>${highlightKeynote(kn.text, d.stt)}</div>
          ${srcFile?`<div class="kn-source">📖 Trích từ <a href="${escapeAttr(srcPath)}" target="_blank">${escapeHtml(srcFile)}</a></div>`:''}
        </div>`;
      }).join('');
      return `<div class="kn-group kn-group-${t}">
        <div class="kn-group-header">📘 Nhóm ${t}. ${escapeHtml((TOPIC_NAMES[t]||'').split('. ')[1]||'')}<span class="kn-count">${byTopic[t].length} điểm</span></div>
        <div class="kn-list">${items}</div>
      </div>`;
    }).join('');
    document.getElementById('panel-keynotes').innerHTML = `
      <div class="note">🎯 <strong>${kns.length} điểm trọng yếu</strong> — verbatim từ 8 file ON_TAP_NHOM. Group theo chủ đề BTC. <span style="color:var(--yellow)">Số liệu/ngày</span> · <span style="color:var(--accent)">Điều khoản</span> · <span style="color:var(--purple)">Văn bản dẫn chiếu</span> được highlight.</div>
      ${groupsHtml}
    `;
  } else {
    document.getElementById('panel-keynotes').innerHTML = `<div class="empty">📭 Chưa có keynote nào extract được cho VB này. Thêm vào file ON_TAP_NHOM_*.md tương ứng để hiện ở đây.</div>`;
  }

  // Tab: Concepts — verbatim definitions from "Giải thích từ ngữ" + ON_TAP Bản đồ thuật ngữ
  const ccs = d.concepts || [];
  if(ccs.length){
    const cardsHtml = ccs.map((c, idx)=>{
      const sourceTag = c.source_type === 'law' ? '<span class="cc-source-tag law">Luật</span>' : '<span class="cc-source-tag ontap">ON TẬP</span>';
      // Try to link source_dieu
      let srcEl;
      const dnumMatch = (c.source_dieu||'').match(/Điều\s+(\d+[a-z]?)/);
      const dnum = dnumMatch ? dnumMatch[1] : '';
      const hasArticle = dnum && d.structure && d.structure.dieus && d.structure.dieus.some(x=>x.number===dnum);
      if(hasArticle){
        srcEl = `<span class="cc-source" data-doc="${d.stt}" data-dieu="${dnum}" onclick="event.stopPropagation();document.dispatchEvent(new MouseEvent('click',{bubbles:true})); showDieuPopover(this.closest('.cc-card'), ${d.stt}, '${dnum}');">${escapeHtml(c.source_dieu||'')}</span>`;
      } else {
        srcEl = `<span class="cc-source unknown">${escapeHtml(c.source_dieu||'(không rõ nguồn)')}</span>`;
      }
      // For the definition, apply minimal highlight (numbers + Điều refs)
      const defHtml = highlightKeynote(c.definition || c.full_text || '', d.stt);
      return `<div class="cc-card" data-idx="${idx}">
        <div class="cc-head">
          <div class="cc-term">${escapeHtml(c.term)} ${sourceTag}</div>
          ${srcEl}
        </div>
        <div class="cc-def">${defHtml}</div>
      </div>`;
    }).join('');
    document.getElementById('panel-concepts').innerHTML = `
      <div class="note">🔑 <strong>${ccs.length} khái niệm</strong> verbatim từ Điều "Giải thích từ ngữ" trong VB + ON_TAP "Bản đồ thuật ngữ" của bạn. Search nhanh phía dưới. Click "Điều X" trong định nghĩa để xem toàn văn.</div>
      <input type="text" class="cc-search" placeholder="🔍 Tìm trong khái niệm (vd: dữ liệu, eKYC, PEP, sandbox...)" oninput="filterConcepts(this.value)">
      <div class="cc-list" id="cc-list">${cardsHtml}</div>
    `;
  } else {
    document.getElementById('panel-concepts').innerHTML = `<div class="empty">📭 VB này không có Điều "Giải thích từ ngữ" hoặc chưa extract được khái niệm.</div>`;
  }

  // Tab: Thresholds — verbatim ngưỡng số liệu từ thresholds_full.csv
  const ths = d.thresholds || [];
  if(ths.length){
    // Group by loai_so_lieu type
    const byType = {};
    ths.forEach(th=>{(byType[th.loai] = byType[th.loai]||[]).push(th);});
    // Quick summary
    const summaryHtml = Object.entries(byType).map(([type,items])=>{
      return `<div class="th-summary-cell"><div class="v">${items.length}</div><div class="l">${escapeHtml(type)}</div></div>`;
    }).join('');
    // Cards
    const cardsHtml = ths.map(th=>{
      const dieuRaw = (th.dieu_khoan||'').trim();
      const dnumMatch = dieuRaw.match(/Đ\.?\s*(\d+[a-z]?)/);
      const dnum = dnumMatch ? dnumMatch[1] : '';
      const hasNumber = !!dnum;  // CSV has actual Điều number
      // Check if Điều exists in extracted structure
      const hasArticle = hasNumber && d.structure && d.structure.dieus && d.structure.dieus.some(x=>x.number===dnum);
      let refHtml;
      if(hasArticle){
        refHtml = `<span class="th-ref" data-doc="${d.stt}" data-dieu="${dnum}">📍 ${escapeHtml(dieuRaw)}</span>`;
      } else if(hasNumber){
        refHtml = `<span class="th-ref unknown" title="Điều ${dnum} không có trong cấu trúc trích xuất">📍 ${escapeHtml(dieuRaw)}</span>`;
      } else {
        refHtml = `<span class="th-ref unknown" title="CSV không có số Điều cụ thể">—</span>`;
      }
      return `<div class="th-card">
        <div class="th-head">
          <span class="th-val">${escapeHtml(th.gia_tri||'')}</span>
          <span class="th-type">${escapeHtml(th.loai||'')}</span>
          ${refHtml}
          <span style="font-size:10px;color:var(--muted);margin-left:auto">Nhóm ${escapeHtml(th.topic||'')}</span>
        </div>
        <div class="th-desc">${escapeHtml(th.mo_ta||'')}</div>
        <div class="th-quote">${escapeHtml(th.quote||'')}</div>
        <div style="font-size:10.5px;color:var(--muted);margin-top:6px;font-style:italic;padding-top:4px;border-top:1px dashed var(--border)">📖 Trích từ <code style="font-family:Consolas,monospace">thresholds_full.csv</code>${th.line?`, dòng ${escapeHtml(th.line)}`:''}</div>
      </div>`;
    }).join('');
    document.getElementById('panel-thresholds').innerHTML = `
      <div class="note">📊 <strong>${ths.length} ngưỡng số liệu</strong> verbatim từ <code>thresholds_full.csv</code> với <strong>trích dẫn nguyên văn</strong> từ văn bản gốc. Click vào "📍 Đ.X K.Y" để xem toàn văn Điều đó.</div>
      <div class="th-summary">${summaryHtml}</div>
      <div class="th-list">${cardsHtml}</div>
    `;
  } else {
    document.getElementById('panel-thresholds').innerHTML = `<div class="empty">📭 Chưa có ngưỡng số liệu nào extract được cho VB này.</div>`;
  }

  // Tab: Mindmap — placeholder, render lazy on tab click
  const mmPanel = document.getElementById('panel-mindmap');
  mmPanel.innerHTML = `<div class="mm-info">🧠 Click tab "🧠 Mindmap" để xem mindmap (lazy-loaded khi cần).</div>`;
  mmPanel.dataset.rendered = '';

  // Tab: Questions
  const qs = d.questions||[];
  if(qs.length){
    document.getElementById('panel-questions').innerHTML = `
      <div class="note">❓ ${qs.length} câu hỏi từ Bộ 400 câu BTC liên quan VB này. Đáp án đúng được highlight xanh.</div>
      <div class="q-list">${qs.map(q=>{
        const opts = Object.entries(q.options).map(([k,v])=>{
          const isCorrect = q.answer===k;
          return `<div class="q-option ${isCorrect?'correct':''}"><span class="q-letter">${k}.</span><span>${escapeHtml(v)}</span></div>`;
        }).join('');
        return `<div class="q-item">
          <div class="q-header"><span class="q-id">Câu ${q.q_id}</span><span class="q-mang">${escapeHtml(q.mang||'')}</span></div>
          <div class="q-text">${escapeHtml(q.question)}</div>
          <div class="q-options">${opts}</div>
          ${q.reference?`<div class="q-ref"><strong>Tham chiếu:</strong> ${escapeHtml(q.reference)}${q.dieu_khoan?' · '+escapeHtml(q.dieu_khoan):''}</div>`:''}
        </div>`;
      }).join('')}</div>
    `;
  } else {
    document.getElementById('panel-questions').innerHTML = `<div class="empty">📭 Chưa map được câu hỏi nào trong 400 câu BTC cho VB này.<br><span style="font-size:12px">(Có thể câu hỏi liên quan dùng tên VB khác — kiểm tra <code>van_ban_tham_chieu</code> trong 400_cau_hoi.csv)</span></div>`;
  }

  // Tab: ToC
  if(d.structure && d.structure.dieus.length){
    let cur = '';
    let h = '<div class="dieu-list">';
    d.structure.dieus.forEach((dieu,idx)=>{
      if(dieu.chuong && dieu.chuong !== cur){
        cur = dieu.chuong;
        h += `<div class="chuong-header">${escapeHtml(cur)}</div>`;
      }
      h += `<div class="dieu-item" id="dieu-${d.stt}-${idx}">
        <div class="dieu-head" onclick="toggleDieu(${d.stt},${idx})">
          <span class="dieu-num">Điều ${dieu.number}</span>
          <span class="dieu-title">${escapeHtml(dieu.title)}</span>
          <span class="dieu-toggle">▶</span>
        </div>
        <div class="dieu-body">${escapeHtml(cleanLawText(dieu.text))}</div>
      </div>`;
    });
    h += '</div>';
    document.getElementById('panel-toc').innerHTML = h;
  } else {
    document.getElementById('panel-toc').innerHTML = `<div class="empty">📭 Văn bản này không có cấu trúc Điều rõ rệt (thường là Nghị quyết / Quyết định chương trình / Chỉ thị). Mở file gốc để đọc.</div>`;
  }

  // Tab: New
  document.getElementById('panel-new').innerHTML = `
    <div class="summary-block"><div class="label">📌 Văn bản cha / liên quan</div><div>${escapeHtml(d.parent||'(không có)')}</div></div>
    <div class="summary-block"><div class="label">🆕 Điểm mới so với VB cha</div><div>${escapeHtml(d.whats_new||'(văn bản tiên phong / không có thay đổi cụ thể)')}</div></div>
  `;

  // Tab: Links
  const nhomMap = {'I':'DU_LIEU','II':'KHACH_HANG','III':'CONG_NGHE','IV':'PHAP_LY','V':'AN_TOAN','VI':'QUAN_TRI','VII':'NHAN_LUC','VIII':'UNG_DUNG'};
  document.getElementById('panel-links').innerHTML = `
    <div class="summary-block"><div class="label">📂 File trong project</div><div>
      ${d.word_file ? `📄 <a href="${escapeAttr('TAI LIEU THAM KHAO/'+d.word_file)}" target="_blank" style="color:var(--accent)">${escapeHtml(d.word_file)}</a>`:'(không có)'}<br>
      ${d.md_file ? `📝 <a href="${escapeAttr('vcb_cds_202605/van_ban/'+d.md_file)}" target="_blank" style="color:var(--accent)">vcb_cds_202605/van_ban/${escapeHtml(d.md_file)}</a>`:''}
    </div></div>
    <div class="summary-block"><div class="label">🌐 Nguồn gốc</div><div>${d.source_url?`<a href="${escapeAttr(d.source_url)}" target="_blank" style="color:var(--accent);word-break:break-all">${escapeHtml(d.source_url)}</a>`:'(không có)'}</div></div>
    <div class="summary-block"><div class="label">📊 File ôn tập theo chủ đề</div><div>
      ${(d.topics_main||[]).concat(d.topics_secondary||[]).map(t=>`<a href="${escapeAttr('vcb_cds_202605/ON_TAP_NHOM_'+t+'_'+nhomMap[t]+'.md')}" target="_blank" style="display:block;color:var(--accent);margin:4px 0">📘 ${escapeHtml(TOPIC_NAMES[t]||t)}</a>`).join('')}
    </div></div>
  `;

  _currentDrawerStt = stt;
  document.getElementById('drawer').classList.add('open');
  document.getElementById('overlay').classList.add('show');
  document.body.style.overflow = 'hidden';
  document.querySelector('.tab').click();
}

function closeDrawer(){
  document.getElementById('drawer').classList.remove('open');
  document.getElementById('overlay').classList.remove('show');
  document.body.style.overflow = '';
}

function toggleDieu(stt,idx){ document.getElementById(`dieu-${stt}-${idx}`).classList.toggle('expanded'); }

function toggleStudied(stt, btn){
  // legacy — kept for compatibility, status select is preferred
  if(studied.has(stt)){ setDocStatus(stt,''); if(btn) btn.textContent='☆ Đánh dấu đã học'; }
  else { setDocStatus(stt,'done'); if(btn) btn.textContent='✓ Đã học'; }
  updateStudiedStat(); renderDocs(); renderStatusChips();
}

function onStatusChange(stt, status){
  setDocStatus(stt, status);
  const sel = document.getElementById('status-select');
  if(sel){ sel.classList.remove('done','review','important'); if(status) sel.classList.add(status); }
  updateStudiedStat(); renderDocs(); renderStatusChips();
}

function toggleNoteSection(){
  const el = document.getElementById('note-section');
  if(el) el.style.display = el.style.display === 'none' ? 'block' : 'none';
  if(el && el.style.display === 'block') document.getElementById('note-textarea')?.focus();
}

function onNoteChange(stt, val){
  setDocNote(stt, val);
  renderDocs();  // refresh card to show 📝 indicator
}

function updateStudiedStat(){
  const done = Object.values(fileStates).filter(v=>v.status==='done').length;
  const review = Object.values(fileStates).filter(v=>v.status==='review').length;
  document.getElementById('stat-studied').textContent = `${done}/${docs.length}${review?` · 🔄${review}`:''}`;
}

function renderStatusChips(){
  const el = document.getElementById('status-chips');
  if(!el) return;
  const counts = {done:0, review:0, important:0, '':0};
  docs.forEach(d => { counts[getStatus(d.stt)||'']++; });
  const noteCount = docs.filter(d => getNote(d.stt)).length;
  const chips = [
    {k:'', label:'📋 Chưa học', n:counts['']},
    {k:'done', label:'✓ Đã học', n:counts.done},
    {k:'review', label:'🔄 Cần học lại', n:counts.review},
    {k:'important', label:'⭐ Quan trọng', n:counts.important},
    {k:'has-note', label:'📝 Có ghi chú', n:noteCount},
  ];
  el.innerHTML = chips.filter(c=>c.n>0||c.k!=='').map(c=>`<button class="chip ${activeStatus===c.k?'active':''}" onclick="toggleStatusFilter('${c.k}')">${c.label} <span style="opacity:0.6">(${c.n})</span></button>`).join('');
}

function toggleStatusFilter(k){
  activeStatus = (activeStatus === k) ? null : k;
  renderStatusChips(); renderDocs();
}

function escapeHtml(s){ if(s==null) return ''; return String(s).replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function escapeAttr(s){return escapeHtml(s);}

// Clean Vietnamese law text: fix mid-sentence line breaks from PDF extraction
// Heuristic: \n+ between fragments → space if continuation; preserve if true paragraph
function cleanLawText(text){
  if(!text) return '';
  let s = String(text);
  // Step 1: Join lines that end mid-sentence (no terminator + next starts lowercase or punctuation)
  // Match: any char that's NOT [.;:!?] followed by \n+ followed by lowercase Vietnamese letter / comma / etc
  // Vietnamese lowercase range: a-z + special chars
  const viLower = 'a-zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ';
  // Join if line ends with NOT-terminator and next starts with: lowercase, comma, semicolon, openparen
  const joinRe = new RegExp(`([^.!?;:\\n])\\n+([${viLower},;\\)\\(])`, 'g');
  s = s.replace(joinRe, '$1 $2');
  // Also join after explicit colon if next isn't a numbered item
  // (handles "sau đây:\n1. ..." - this stays; "trong đó:\n các trường hợp" - this joins)
  // Actually we want : followed by \n + lowercase to STAY as paragraph break
  // Default behavior is OK now
  // Step 2: Collapse 3+ \n to 2
  s = s.replace(/\n{3,}/g, '\n\n');
  // Step 3: Trim spaces around \n
  s = s.replace(/[ \t]+\n/g, '\n').replace(/\n[ \t]+/g, '\n');
  return s.trim();
}

// Map topic letter to ON_TAP filename for citation
const ONTAP_FILES = {
  'I':'ON_TAP_NHOM_I_DU_LIEU.md',
  'II':'ON_TAP_NHOM_II_KHACH_HANG.md',
  'III':'ON_TAP_NHOM_III_CONG_NGHE.md',
  'IV':'ON_TAP_NHOM_IV_PHAP_LY.md',
  'V':'ON_TAP_NHOM_V_AN_TOAN.md',
  'VI':'ON_TAP_NHOM_VI_QUAN_TRI.md',
  'VII':'ON_TAP_NHOM_VII_NHAN_LUC.md',
  'VIII':'ON_TAP_NHOM_VIII_UNG_DUNG.md',
};

// Highlight keynote text with CLICKABLE links to Điều/VB content.
// Track VB context as we scan left-to-right: each Luật/NĐ/TT/QĐ ref updates the current
// context for subsequent "Điều N" mentions.
function highlightKeynote(text, currentStt){
  // Tokenize text into [VB ref | Điều ref | Number-with-unit | Date | Code] segments
  let tokens = [];
  const vbRegex = /\b(Luật|Nghị định|NĐ|Thông tư|TT|Quyết định|QĐ|Chỉ thị|CT|Nghị quyết|NQ)\s+(\d+(?:[\/\.-]\d+)+(?:[\/\.-][\w\-]+)?)/g;
  const dieuRegex = /(Điều\s+\d+[a-z]?(?:\.\d+)?(?:\s*Khoản\s+\d+)?(?:\s*Điểm\s+\w)?)/g;
  // Codes: 14/2022/QH15 etc.
  const codeRegex = /\b(\d+[\/\.-]\d{4}(?:[\/\.-][\w\-]+)?)\b/g;
  // Dates: 01/07/2025
  const dateRegex = /\b(\d{1,2}\/\d{1,2}\/\d{4})\b/g;
  // Numbers with units (essential exam values): "5 năm", "72 giờ", "30%", "400 triệu", "10 lần", "5G"
  const numUnitRegex = /\b(\d+(?:[,.]\d+)?)\s*(năm|tháng|ngày|giờ|phút|giây|lần|tỷ|triệu|nghìn|đồng|VND|VNĐ|USD|G)\b/gi;
  // Percentages
  const pctRegex = /\b(\d+(?:[,.]\d+)?%)/g;
  // Comparison thresholds
  const cmpRegex = /(≥|>=|<=|≤|>|<)\s*(\d+(?:\.\d+)?%?)/g;

  let segs = [];
  let m;
  vbRegex.lastIndex = 0;
  while((m = vbRegex.exec(text)) !== null){
    const fullMatch = m[0], code = m[2];
    let d = codeToDoc[code];
    if(!d){
      const m2 = code.match(/^(\d+)[\/\.\-](\d{4})/);
      if(m2) d = codeToDoc[m2[1]+'/'+m2[2]];
    }
    segs.push({start: m.index, end: m.index + fullMatch.length, type: 'vb', text: fullMatch, doc: d});
  }
  dieuRegex.lastIndex = 0;
  while((m = dieuRegex.exec(text)) !== null){
    segs.push({start: m.index, end: m.index + m[0].length, type: 'dieu', text: m[0]});
  }
  // Numbers + dates + percentages — only highlight in safe, non-overlapping positions
  for(const re of [dateRegex, numUnitRegex, pctRegex, cmpRegex, codeRegex]){
    re.lastIndex = 0;
    while((m = re.exec(text)) !== null){
      segs.push({start: m.index, end: m.index + m[0].length, type: 'num', text: m[0]});
    }
  }

  // Remove overlaps (prefer vb > dieu > num)
  segs.sort((a,b)=> a.start-b.start || ({'vb':0,'dieu':1,'num':2}[a.type] - {'vb':0,'dieu':1,'num':2}[b.type]));
  const filtered = [];
  let lastEnd = -1;
  for(const s of segs){
    if(s.start >= lastEnd){
      filtered.push(s);
      lastEnd = s.end;
    }
  }

  // Walk text, render with context tracking
  let out = '';
  let pos = 0;
  let lastVbStt = currentStt;  // default: current doc
  for(const s of filtered){
    out += escapeHtml(text.substring(pos, s.start));
    if(s.type === 'vb'){
      if(s.doc){
        lastVbStt = s.doc.stt;  // update context
        out += `<a class="vb-link" data-doc="${s.doc.stt}">${escapeHtml(s.text)}</a>`;
      } else {
        out += `<span class="vb-link unknown">${escapeHtml(s.text)}</span>`;
      }
    } else if(s.type === 'dieu'){
      const dnum = (s.text.match(/Điều\s+(\d+[a-z]?)/)||[])[1];
      // Only link if we have a known VB context AND the Điều exists in that doc
      const targetDoc = sttToDoc[lastVbStt];
      let hasArticle = false;
      if(targetDoc && targetDoc.structure && targetDoc.structure.dieus){
        hasArticle = targetDoc.structure.dieus.some(dd => dd.number === dnum);
      }
      if(hasArticle){
        out += `<a class="dieu-link" data-doc="${lastVbStt}" data-dieu="${dnum}">${escapeHtml(s.text)}</a>`;
      } else {
        out += `<span class="dieu-link unknown">${escapeHtml(s.text)}</span>`;
      }
    } else { // num
      out += `<span class="num-hl">${escapeHtml(s.text)}</span>`;
    }
    pos = s.end;
  }
  out += escapeHtml(text.substring(pos));
  // Bold (after escaping) — find \*\* in original positions
  out = out.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  return out;
}

// Show Điều text inline below the keynote card
function showDieuPopover(cardEl, docStt, dieuNum){
  // Remove existing popover in this card
  const existing = cardEl.querySelector('.dieu-popover');
  if(existing){ existing.remove(); return; }
  // Remove popovers from OTHER cards (only one open at a time)
  document.querySelectorAll('.dieu-popover').forEach(p=>p.remove());
  const d = sttToDoc[docStt];
  if(!d || !d.structure || !d.structure.dieus) return;
  const dieu = d.structure.dieus.find(x => x.number === dieuNum);
  if(!dieu) return;
  const wordPath = d.word_file ? 'TAI LIEU THAM KHAO/' + d.word_file : null;
  const mdPath = d.md_file ? 'vcb_cds_202605/van_ban/' + d.md_file : null;
  const pop = document.createElement('div');
  pop.className = 'dieu-popover';
  pop.innerHTML = `
    <div class="pop-head">
      <span class="pop-title">${d.roman_id} — ${escapeHtml(d.short_name)} → Điều ${dieu.number}. ${escapeHtml(dieu.title)}</span>
      <button class="pop-close" onclick="this.closest('.dieu-popover').remove()">×</button>
    </div>
    <div>${escapeHtml(cleanLawText(dieu.text))}</div>
    <div class="pop-source">
      ${dieu.chuong ? '📑 '+escapeHtml(dieu.chuong)+' · ' : ''}
      📖 Trích nguyên văn từ ${mdPath ? `<a href="${escapeAttr(mdPath)}" target="_blank">${escapeHtml(d.md_file||'')}</a>`:'(?)'} ·
      ${wordPath ? `<a href="${escapeAttr(wordPath)}" target="_blank">📄 Mở file Word</a> · ` : ''}
      <a href="#" onclick="event.preventDefault(); openDoc(${docStt})">🔍 VB ${d.roman_id}</a>
    </div>
  `;
  cardEl.appendChild(pop);
  pop.scrollIntoView({behavior:'smooth', block:'nearest'});
}

// Click delegation for keynote/threshold/question links — ALWAYS show something
document.addEventListener('click', function(e){
  // Điều link (in keynote/threshold/question)
  const dlink = e.target.closest('.dieu-link, .th-ref');
  if(dlink){
    e.preventDefault();
    e.stopPropagation();
    const docStt = parseInt(dlink.dataset.doc);
    const dieuNum = dlink.dataset.dieu;
    const isUnknown = dlink.classList.contains('unknown');
    const card = dlink.closest('.kn-card') || dlink.closest('.q-item') || dlink.closest('.summary-block') || dlink.closest('.th-card');
    if(card){
      if(isUnknown || !docStt || !dieuNum){
        showFallbackPopover(card, dlink.textContent.trim());
      } else {
        showDieuPopover(card, docStt, dieuNum);
      }
    }
    return;
  }
  // VB link
  const vlink = e.target.closest('.vb-link');
  if(vlink && !vlink.classList.contains('unknown')){
    e.preventDefault();
    e.stopPropagation();
    const docStt = parseInt(vlink.dataset.doc);
    if(docStt && docStt !== getCurrentDrawerStt()){
      openDoc(docStt);
    }
  }
});

function showFallbackPopover(cardEl, refText){
  document.querySelectorAll('.dieu-popover').forEach(p=>p.remove());
  const pop = document.createElement('div');
  pop.className = 'dieu-popover';
  pop.innerHTML = `
    <div class="pop-head">
      <span class="pop-title">📭 ${escapeHtml(refText)}</span>
      <button class="pop-close" onclick="this.closest('.dieu-popover').remove()">×</button>
    </div>
    <div style="color:var(--muted);font-style:italic">Điều khoản này không tìm thấy trong cấu trúc đã trích xuất của VB hiện tại. Có thể:
    <ul style="margin:8px 0 0 0;padding-left:20px">
      <li>VB này không có cấu trúc Điều rõ rệt (vd: Nghị quyết, Quyết định chương trình)</li>
      <li>Điều khoản thuộc một VB khác (đọc kỹ context xung quanh keynote)</li>
      <li>Định dạng số Điều không khớp (vd: Điều 21a vs 21)</li>
    </ul>
    Hãy mở file gốc ở tab "🔗 Liên kết" để tra cứu trực tiếp.</div>
  `;
  cardEl.appendChild(pop);
  pop.scrollIntoView({behavior:'smooth', block:'nearest'});
}

let _currentDrawerStt = null;
function getCurrentDrawerStt(){return _currentDrawerStt;}

// Render Mermaid mindmap for a document — called lazily when tab is clicked
let mermaidLoaded = false;
let mmCounter = 0;

function renderMindmap(d){
  const panel = document.getElementById('panel-mindmap');
  const summary = (d.summary||'').split(/\n+/).map(l=>l.replace(/^\d+\)\s*/,'').trim()).filter(l=>l.length>5);
  const knByTopic = {};
  (d.keynotes||[]).forEach(kn=>{(knByTopic[kn.topic]=knByTopic[kn.topic]||[]).push(kn.text);});
  const kwds = (d.keywords||'').split(';').map(k=>k.trim()).filter(k=>k);

  // Aggressive sanitization — Mermaid mindmap text rules are strict
  function san(s, max){
    if(!s) return '';
    // Remove ALL chars that confuse Mermaid: () [] {} : ; # " ` ! ? & < > / | * ~
    s = String(s)
      .replace(/[\x00-\x1f]+/g,' ')  // control chars
      .replace(/[\(\)\[\]\{\}"`#:;<>&|*~!?\\\/]/g,' ')
      .replace(/[–—]/g,'-')   // en/em dash → hyphen
      .replace(/[‘’“”]/g,'')  // smart quotes
      .replace(/\s+/g,' ')
      .trim();
    if(s.length>max) s = s.substring(0,max).trim()+'...';
    return s || '...';
  }
  function escId(s){return san(s, 80);}

  // Build mindmap markup — use shape syntax `[text]` to wrap multi-word nodes safely
  let mm = 'mindmap\n';
  mm += `  root((${san(d.roman_id+' '+d.short_name, 50)}))\n`;
  if(summary.length){
    mm += `    Tom tat\n`;
    summary.slice(0,5).forEach((s,i)=>{
      mm += `      ${i+1}. ${san(s, 70)}\n`;
    });
  }
  if(kwds.length){
    mm += `    Tu khoa\n`;
    kwds.slice(0,6).forEach(k=>{
      mm += `      ${san(k, 30)}\n`;
    });
  }
  if(Object.keys(knByTopic).length){
    mm += `    Keynotes\n`;
    ['I','II','III','IV','V','VI','VII','VIII'].forEach(t=>{
      if(knByTopic[t] && knByTopic[t].length){
        const name = san((TOPIC_NAMES[t]||t).split('. ')[1]||t, 30);
        mm += `      Nhom ${t} - ${name}\n`;
        knByTopic[t].slice(0,2).forEach(kn=>{
          mm += `        ${san(kn, 60)}\n`;
        });
      }
    });
  }
  if(d.structure && d.structure.total_dieus){
    mm += `    Cau truc\n`;
    if(d.structure.chuongs && d.structure.chuongs.length){
      mm += `      ${d.structure.chuongs.length} Chuong\n`;
    }
    mm += `      ${d.structure.total_dieus} Dieu\n`;
  }
  if(d.parent){
    mm += `    Lien quan\n`;
    mm += `      ${san(d.parent.split('|')[0], 70)}\n`;
  }
  if((d.questions||[]).length){
    mm += `    Cau hoi BTC: ${d.questions.length}\n`;
    const mangs = {};
    d.questions.forEach(q=>{
      const m = san((q.mang||'').split('.')[0].trim(), 20);
      if(m) mangs[m] = (mangs[m]||0) + 1;
    });
    Object.entries(mangs).slice(0,4).forEach(([m,c])=>{
      mm += `      ${m}: ${c} cau\n`;
    });
  }

  mmCounter++;
  const uid = 'mm-' + d.stt + '-' + mmCounter;
  panel.innerHTML = `
    <div class="mm-info">🧠 Mindmap tự sinh từ master CSV + ON_TAP_NHOM. Cần internet lần đầu để load Mermaid CDN (~700KB), sau đó cache.</div>
    <div class="mindmap-toolbar">
      <button class="btn secondary" onclick="toggleEl('${uid}-debug')">🔧 Toggle markup</button>
      <span style="font-size:12px;color:var(--muted);margin-left:auto">Mindmap khá to — kéo ngang để xem</span>
    </div>
    <div class="mindmap-container" id="${uid}-container">
      <div class="mm-loading" id="${uid}-load">⏳ Đang tải Mermaid…</div>
    </div>
    <pre id="${uid}-debug" style="display:none;background:var(--card);padding:12px;border-radius:6px;font-size:11px;color:var(--muted);max-height:300px;overflow:auto;margin-top:8px;white-space:pre-wrap">${escapeHtml(mm)}</pre>
  `;

  ensureMermaid().then(async ()=>{
    const container = document.getElementById(uid+'-container');
    const loader = document.getElementById(uid+'-load');
    if(!container) return;
    try{
      // Use the mermaid.render API which returns SVG directly — more reliable than mermaid.run
      const renderId = uid + '-render';
      const result = await window.mermaid.render(renderId, mm);
      // mermaid.render returns {svg, bindFunctions} in v10
      container.innerHTML = result.svg || result;
      if(result.bindFunctions) result.bindFunctions(container);
    }catch(err){
      console.error('Mermaid render error', err);
      if(loader){
        loader.innerHTML = `⚠️ Lỗi render mindmap.<br><small style="color:var(--muted)">${escapeHtml(String(err.message||err))}</small>`;
      }
      document.getElementById(uid+'-debug').style.display='block';
    }
  }).catch(err=>{
    const loader = document.getElementById(uid+'-load');
    if(loader){
      loader.innerHTML = '⚠️ Không tải được Mermaid CDN. Kiểm tra internet / firewall.<br><small>'+escapeHtml(String(err.message||err))+'</small>';
    }
    document.getElementById(uid+'-debug').style.display='block';
  });
}

function toggleEl(id){
  const el = document.getElementById(id);
  if(!el) return;
  el.style.display = el.style.display === 'block' ? 'none' : 'block';
}

// Quick filter inside Concepts tab
function filterConcepts(term){
  const t = (term||'').toLowerCase().trim();
  document.querySelectorAll('#cc-list .cc-card').forEach(card=>{
    const hay = card.textContent.toLowerCase();
    card.style.display = (!t || hay.includes(t)) ? '' : 'none';
  });
}

// ============================================================
// Reading guide (HUONG_DAN_DOC.md)
// ============================================================
const READING_GUIDE_MD = DATA.reading_guide_md || '';
let readingGuideRendered = false;
let markedLoaded = false;

function loadMarkedJs(){
  if(window.marked) return Promise.resolve();
  if(markedLoaded) return Promise.resolve();
  return new Promise((resolve, reject)=>{
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/marked@11/marked.min.js';
    script.onload = ()=>{ markedLoaded = true; resolve(); };
    script.onerror = ()=>reject(new Error('Failed to load marked.js'));
    document.head.appendChild(script);
  });
}

function toggleReadingGuide(){
  const content = document.getElementById('rg-content');
  const btn = document.getElementById('rg-toggle-btn');
  const showing = content.style.display !== 'none';
  if(showing){
    content.style.display = 'none';
    btn.textContent = 'Mở rộng ▼';
  } else {
    content.style.display = 'block';
    btn.textContent = 'Thu gọn ▲';
    if(!readingGuideRendered) renderReadingGuide();
  }
}

function renderReadingGuide(){
  const target = document.getElementById('rg-rendered');
  if(!READING_GUIDE_MD){
    target.innerHTML = `<div class="empty">📭 Không tìm thấy <code>HUONG_DAN_DOC.md</code>. Chạy <code>python tools/04_reading_guide.py</code> để tạo.</div>`;
    return;
  }
  // Use marked.js for rendering (load lazy)
  loadMarkedJs().then(()=>{
    try{
      const html = window.marked.parse(READING_GUIDE_MD, {gfm:true, breaks:false});
      target.innerHTML = `<div class="rg-rendered-md">${html}</div>`;
      readingGuideRendered = true;
      // Process internal links so they open VBs
      target.querySelectorAll('a').forEach(a=>{
        const href = a.getAttribute('href') || '';
        if(href.startsWith('http')) a.setAttribute('target','_blank');
      });
    }catch(e){
      target.innerHTML = `<pre style="white-space:pre-wrap;font-size:12px;color:var(--muted)">${escapeHtml(READING_GUIDE_MD)}</pre>`;
    }
  }).catch(err=>{
    // Fallback: show raw MD as preformatted text
    target.innerHTML = `<div style="font-size:12px;color:var(--muted);margin-bottom:10px">⚠️ Không tải được marked.js (cần internet lần đầu). Hiển thị raw MD:</div><pre style="white-space:pre-wrap;font-size:12px;background:#fff;padding:14px;border-radius:6px;border:1px solid var(--border);max-height:60vh;overflow-y:auto;line-height:1.6">${escapeHtml(READING_GUIDE_MD)}</pre>`;
  });
}

// ============================================================
// Reference tables (cheat sheet)
// ============================================================
function renderRefTables(){
  // Collect all thresholds
  const allThs = [];
  docs.forEach(d => (d.thresholds||[]).forEach(th => allThs.push({...th, doc: d})));

  // Helper to render a table
  function tableHtml(rows){
    if(!rows.length) return '<div class="empty">Không có dữ liệu.</div>';
    return `<table class="ref-table"><thead><tr>
      <th>VB</th><th>Điều</th><th>Giá trị</th><th>Loại</th><th>Mô tả</th><th>Nhóm</th>
    </tr></thead><tbody>${rows.map(th=>`<tr>
      <td><a class="roman-link" onclick="openDoc(${th.doc.stt})">${th.doc.roman_id}</a><br><span style="font-size:11px;color:var(--muted)">${escapeHtml(th.doc.short_name)}</span></td>
      <td class="code">${escapeHtml(th.dieu_khoan||'—')}</td>
      <td class="val">${escapeHtml(th.gia_tri||'')}</td>
      <td><span style="font-size:11px;color:var(--accent)">${escapeHtml(th.loai||'')}</span></td>
      <td>${escapeHtml(th.mo_ta||'')}<br><span style="font-size:11px;color:var(--muted);font-style:italic">"${escapeHtml((th.quote||'').substring(0,200))}${(th.quote||'').length>200?'...':''}"</span></td>
      <td style="text-align:center;font-size:11px;color:var(--muted)">${escapeHtml(th.topic||'')}</td>
    </tr>`).join('')}</tbody></table>`;
  }

  document.getElementById('rpanel-thresholds').innerHTML = tableHtml(allThs);
  // Hiệu lực
  const hl = allThs.filter(th => /hiệu lực/i.test(th.loai||''));
  document.getElementById('rpanel-hieuluc').innerHTML = tableHtml(hl);
  // Mức phạt
  const phat = allThs.filter(th => /phạt|tiền phạt/i.test(th.loai||''));
  document.getElementById('rpanel-phat').innerHTML = tableHtml(phat);
  // Ngưỡng thời gian
  const tg = allThs.filter(th => /ngưỡng thời gian|thời hạn|thời gian/i.test(th.loai||''));
  document.getElementById('rpanel-thoigian').innerHTML = tableHtml(tg);
  // Concepts table
  const allCs = [];
  docs.forEach(d => (d.concepts||[]).forEach(c => allCs.push({...c, doc: d})));
  document.getElementById('rpanel-concepts').innerHTML = `<table class="ref-table"><thead><tr>
    <th>VB</th><th>Nguồn</th><th>Thuật ngữ</th><th>Định nghĩa (verbatim)</th>
  </tr></thead><tbody>${allCs.map(c=>`<tr>
    <td><a class="roman-link" onclick="openDoc(${c.doc.stt})">${c.doc.roman_id}</a><br><span style="font-size:11px;color:var(--muted)">${escapeHtml(c.doc.short_name)}</span></td>
    <td class="code">${escapeHtml(c.source_dieu||'')}</td>
    <td style="color:var(--purple);font-weight:600">${escapeHtml(c.term||'')}</td>
    <td>${escapeHtml((c.definition||'').substring(0,400))}${(c.definition||'').length>400?'...':''}</td>
  </tr>`).join('')}</tbody></table>`;

  // Wire ref-tabs
  document.querySelectorAll('.ref-tab').forEach(t=>{
    t.addEventListener('click', ()=>{
      document.querySelectorAll('.ref-tab').forEach(x=>x.classList.remove('active'));
      document.querySelectorAll('.ref-panel').forEach(x=>x.classList.remove('active'));
      t.classList.add('active');
      document.getElementById('rpanel-'+t.dataset.rtab).classList.add('active');
      document.getElementById('ref-search').value='';
      filterRefTable('');
    });
  });
}

function filterRefTable(term){
  const t = (term||'').toLowerCase().trim();
  document.querySelectorAll('.ref-panel.active .ref-table tbody tr').forEach(tr=>{
    const hay = tr.textContent.toLowerCase();
    tr.style.display = (!t || hay.includes(t)) ? '' : 'none';
  });
}

// ============================================================
// ÔN TẬP NHANH (separate quiz module from ON_TAP markdown files)
// ============================================================
const ONTAP_NHANH = DATA.ontap_nhanh || {sets:[]};
const OTN_HISTORY_KEY = 'cds_ontap_nhanh_history';
let otnState = null;

function loadOtnHistory(){
  try{ return JSON.parse(localStorage.getItem(OTN_HISTORY_KEY) || '{}'); }catch(e){return {};}
}
function saveOtnHistory(h){ localStorage.setItem(OTN_HISTORY_KEY, JSON.stringify(h)); }

function renderOntapNhanhGrid(){
  const grid = document.getElementById('ontap-grid');
  if(!grid) return;
  const sets = ONTAP_NHANH.sets || [];
  const history = loadOtnHistory();
  grid.innerHTML = sets.map(s=>{
    const total = s.questions.length;
    let seen = 0, correct = 0;
    s.questions.forEach((q, i) => {
      const id = s.id + ':' + i;
      if(history[id]){ seen++; if(history[id].correct) correct++; }
    });
    const pct = seen ? Math.round(correct*100/seen) : 0;
    const hasContent = !!(s.content_md && s.content_md.trim());
    return `<div class="ontap-card">
      <div class="ot-title">${escapeHtml(s.title)}</div>
      <div class="ot-code">${escapeHtml(s.code||'')}</div>
      <div class="ot-stats">
        <span><span class="v">${total}</span> câu trắc nghiệm</span>
        <span>Đã làm: <span class="v">${seen}</span></span>
        <span>Đúng: <span class="v">${correct}</span> (${pct}%)</span>
      </div>
      <div class="ot-actions">
        ${hasContent?`<button class="ot-btn read" onclick="openOntapReader('${s.id}')">📖 Đọc nội dung</button>`:''}
        <button class="ot-btn quiz" onclick="openOntapNhanh('practice','${s.id}')">✍️ Trắc nghiệm</button>
      </div>
    </div>`;
  }).join('');
}

function openOntapNhanh(mode, setId){
  document.getElementById('otn-overlay').classList.add('show');
  document.body.style.overflow='hidden';
  showOtnSetup(mode || 'practice', setId || '');
}

function closeOntapNhanh(){
  document.getElementById('otn-overlay').classList.remove('show');
  document.body.style.overflow='';
  otnState = null;
  renderOntapNhanhGrid();
}

function showOtnSetup(mode, presetSetId){
  otnState = null;
  const sets = ONTAP_NHANH.sets || [];
  const history = loadOtnHistory();
  const totalAll = sets.reduce((acc,s)=>acc+s.questions.length, 0);
  const wrongIds = Object.keys(history).filter(id => !history[id].correct);

  const setOptions = sets.map(s=>{
    const checked = (!presetSetId || presetSetId === s.id) ? 'checked' : '';
    return `<label><input type="checkbox" class="otn-set-cb" value="${escapeAttr(s.id)}" ${checked}> ${escapeHtml(s.title)} <span style="color:var(--muted);font-size:12px">(${s.questions.length} câu)</span></label>`;
  }).join('');

  document.getElementById('otn-content').innerHTML = `
    <div class="quiz-header">
      <h2>⚡ ÔN TẬP NHANH</h2>
      <div class="quiz-sub">${escapeHtml(ONTAP_NHANH.title || 'Trắc nghiệm từ file ON_TAP')}</div>
      <div class="quiz-sub" style="margin-top:6px">
        Tổng <strong>${totalAll}</strong> câu · ${sets.length} bộ · Lịch sử: <strong>${Object.keys(history).length}</strong> câu đã làm · <strong>${wrongIds.length}</strong> câu sai
      </div>
    </div>
    <h3 style="margin:0 0 10px;font-size:15px">1) Chọn chế độ:</h3>
    <div class="otn-mode-grid">
      <div class="otn-mode-btn" onclick="startOtn('practice')">
        <span class="icon">📚</span><div class="name">Ôn tập</div>
        <div class="desc">Xem đáp án ngay sau khi chọn — phù hợp luyện trí nhớ.</div>
      </div>
      <div class="otn-mode-btn" onclick="startOtn('exam')">
        <span class="icon">🎯</span><div class="name">Thi</div>
        <div class="desc">Làm hết bài rồi mới chấm điểm — mô phỏng thi thật.</div>
      </div>
      <div class="otn-mode-btn" onclick="startOtn('wrong')">
        <span class="icon">🔁</span><div class="name">Làm câu sai</div>
        <div class="desc">Chỉ làm lại các câu đã sai trong lịch sử (${wrongIds.length}).</div>
      </div>
    </div>
    <div class="otn-set-select">
      <label>2) Chọn bộ câu hỏi (mặc định: tất cả)</label>
      <div class="otn-set-checks">
        ${setOptions}
        <label style="border-top:1px dashed var(--border);margin-top:4px;padding-top:8px">
          <input type="checkbox" id="otn-shuffle" checked> 🔀 Trộn ngẫu nhiên câu hỏi
        </label>
        <label>
          <input type="checkbox" id="otn-shuffle-opts"> 🔀 Trộn ngẫu nhiên đáp án A/B/C/D
        </label>
      </div>
    </div>
    <div class="otn-keyhints" style="margin-top:14px">
      ⌨️ Phím tắt khi làm bài:
      <kbd>A</kbd>/<kbd>B</kbd>/<kbd>C</kbd>/<kbd>D</kbd> hoặc <kbd>1</kbd>/<kbd>2</kbd>/<kbd>3</kbd>/<kbd>4</kbd> chọn ·
      <kbd>Space</kbd>/<kbd>→</kbd>/<kbd>Enter</kbd> tiếp ·
      <kbd>←</kbd> trước ·
      <kbd>R</kbd> reset câu hiện tại ·
      <kbd>Esc</kbd> đóng
    </div>
    <div style="margin-top:14px;display:flex;gap:8px;justify-content:space-between;flex-wrap:wrap">
      <button class="btn secondary" onclick="if(confirm('Reset toàn bộ lịch sử Ôn tập nhanh?')){localStorage.removeItem(OTN_HISTORY_KEY);showOtnSetup('${mode}','');}">🗑️ Reset lịch sử</button>
    </div>
  `;
}

function startOtn(mode){
  const sets = ONTAP_NHANH.sets || [];
  const checkedIds = Array.from(document.querySelectorAll('.otn-set-cb:checked')).map(cb=>cb.value);
  const shuffle = document.getElementById('otn-shuffle')?.checked;
  const shuffleOpts = document.getElementById('otn-shuffle-opts')?.checked;
  let pool = [];
  sets.filter(s => checkedIds.length===0 || checkedIds.includes(s.id)).forEach(s=>{
    s.questions.forEach((q, i)=>{
      pool.push({
        id: s.id + ':' + i,
        set_id: s.id,
        set_title: s.title,
        set_code: s.code || '',
        q: q.q,
        options: q.options,
        answer: q.answer,
        explain: q.explain || ''
      });
    });
  });
  if(mode === 'wrong'){
    const history = loadOtnHistory();
    const wrongIds = new Set(Object.keys(history).filter(id => !history[id].correct));
    pool = pool.filter(q => wrongIds.has(q.id));
    if(pool.length === 0){
      alert('🎉 Không có câu sai nào! Hãy làm chế độ Ôn tập trước.');
      return;
    }
  }
  if(pool.length === 0){
    alert('Không có câu hỏi nào — chọn ít nhất 1 bộ.');
    return;
  }
  if(shuffle) pool = pool.sort(()=>Math.random()-0.5);
  if(shuffleOpts){
    pool = pool.map(q => {
      const entries = Object.entries(q.options);
      const shuffled = [...entries].sort(()=>Math.random()-0.5);
      const newOpts = {};
      let newAnswer = q.answer;
      const letters = ['A','B','C','D','E','F'];
      shuffled.forEach(([oldLetter, text], idx)=>{
        const newLetter = letters[idx];
        newOpts[newLetter] = text;
        if(oldLetter === q.answer) newAnswer = newLetter;
      });
      return {...q, options: newOpts, answer: newAnswer};
    });
  }
  otnState = {
    mode: mode,         // 'practice' | 'exam' | 'wrong'
    questions: pool,
    idx: 0,
    answers: {},        // id -> letter
    revealed: new Set(),// in practice mode: which are revealed
    finished: false
  };
  showOtnQuestion();
}

function showOtnQuestion(){
  const s = otnState;
  if(!s) return;
  if(s.idx >= s.questions.length){ showOtnResult(); return; }
  const q = s.questions[s.idx];
  const chosen = s.answers[q.id];
  const revealed = s.mode === 'practice' ? s.revealed.has(q.id) : false;
  const pct = Math.round(((s.idx+1)/s.questions.length)*100);
  const correctCount = Object.entries(s.answers).filter(([id,let_])=>{
    const qq = s.questions.find(x=>x.id===id);
    return qq && qq.answer === let_;
  }).length;

  const modeBadge = s.mode === 'practice'
    ? '<span class="otn-mode-badge practice">📚 Ôn tập</span>'
    : s.mode === 'exam'
      ? '<span class="otn-mode-badge exam">🎯 Thi</span>'
      : '<span class="otn-mode-badge review">🔁 Câu sai</span>';

  const optsHtml = Object.entries(q.options).map(([letter, text])=>{
    let cls = 'quiz-option';
    if(revealed){
      if(letter === q.answer) cls += ' correct';
      else if(letter === chosen) cls += ' wrong';
    } else if(letter === chosen) cls += ' selected';
    return `<div class="${cls}" onclick="otnSelectAnswer('${letter}')"><span class="letter">${letter}.</span><span>${escapeHtml(text)}</span></div>`;
  }).join('');

  document.getElementById('otn-content').innerHTML = `
    <div class="quiz-progress">
      <span>${modeBadge} Câu ${s.idx+1}/${s.questions.length}</span>
      <div class="bar"><div class="fill" style="width:${pct}%"></div></div>
      <span>${s.mode==='exam'?'Đã chọn '+Object.keys(s.answers).length:correctCount+' đúng'}</span>
    </div>
    <div class="quiz-question">
      <div class="q-meta">
        <span style="color:var(--accent2);font-weight:700">${escapeHtml(q.set_code)}</span> ·
        <span>${escapeHtml(q.set_title)}</span>
      </div>
      <div class="q-text">${escapeHtml(q.q)}</div>
    </div>
    <div class="quiz-options">${optsHtml}</div>
    <div class="quiz-explain ${revealed?'show':''}" id="otn-explain">
      <div class="label">${(revealed && chosen===q.answer)?'✅ Chính xác':'❌ Đáp án đúng: '+q.answer}</div>
      <div class="quote">${escapeHtml(q.explain||'')}</div>
    </div>
    <div class="quiz-controls">
      <button class="btn secondary" onclick="otnPrev()" ${s.idx===0?'disabled style=opacity:0.4':''}>← Trước</button>
      <div style="display:flex;gap:6px">
        ${s.mode==='practice' && chosen && !revealed ? '<button class="btn" onclick="otnCheck()">✓ Kiểm tra</button>' : ''}
        ${s.mode==='practice' && revealed ? '<button class="btn" onclick="otnNext()">Tiếp →</button>' : ''}
        ${s.mode!=='practice' ? `<button class="btn" onclick="otnNext()" ${!chosen && s.idx<s.questions.length-1?'':''}>Tiếp →</button>` : ''}
        ${s.mode!=='practice' && s.idx===s.questions.length-1 ? '<button class="btn" style="background:var(--red);color:#fff" onclick="otnFinish()">🏁 Nộp bài</button>' : ''}
      </div>
      <button class="btn secondary" onclick="if(confirm('Kết thúc ngay?'))otnFinish()">⏹ Kết thúc</button>
    </div>
  `;
}

function otnSelectAnswer(letter){
  const s = otnState;
  if(!s) return;
  const q = s.questions[s.idx];
  if(s.mode==='practice' && s.revealed.has(q.id)) return;
  s.answers[q.id] = letter;
  // In exam/wrong mode, auto-advance after a brief moment? No — keep manual nav so user can review.
  showOtnQuestion();
}

function otnCheck(){
  const s = otnState;
  if(!s) return;
  const q = s.questions[s.idx];
  if(!s.answers[q.id]) return;
  s.revealed.add(q.id);
  // Save to history immediately in practice mode
  const history = loadOtnHistory();
  history[q.id] = { correct: s.answers[q.id] === q.answer, at: Date.now() };
  saveOtnHistory(history);
  showOtnQuestion();
}

function otnNext(){
  const s = otnState;
  if(!s) return;
  if(s.idx >= s.questions.length-1){
    if(s.mode!=='practice') otnFinish();
    return;
  }
  s.idx++;
  showOtnQuestion();
}

function otnPrev(){
  const s = otnState;
  if(!s) return;
  if(s.idx > 0){ s.idx--; showOtnQuestion(); }
}

function otnResetCurrent(){
  const s = otnState;
  if(!s) return;
  const q = s.questions[s.idx];
  delete s.answers[q.id];
  s.revealed.delete(q.id);
  showOtnQuestion();
}

function otnFinish(){
  const s = otnState;
  if(!s) return;
  s.finished = true;
  // Persist all answers to history (for exam/wrong modes)
  if(s.mode !== 'practice'){
    const history = loadOtnHistory();
    s.questions.forEach(q => {
      const chosen = s.answers[q.id];
      if(chosen){
        history[q.id] = { correct: chosen === q.answer, at: Date.now() };
      }
    });
    saveOtnHistory(history);
  }
  showOtnResult();
}

function showOtnResult(){
  const s = otnState;
  if(!s) return;
  const total = s.questions.length;
  const correctList = s.questions.filter(q => s.answers[q.id] === q.answer);
  const wrongList = s.questions.filter(q => s.answers[q.id] && s.answers[q.id] !== q.answer);
  const skipped = s.questions.filter(q => !s.answers[q.id]);
  const score = correctList.length;
  const pct = Math.round((score/total)*100);
  let grade = '🌟 Xuất sắc!';
  let gradeColor = 'var(--accent)';
  if(pct < 50){ grade = '📕 Cần ôn lại'; gradeColor = 'var(--red)'; }
  else if(pct < 70){ grade = '📙 Khá'; gradeColor = 'var(--accent2)'; }
  else if(pct < 90){ grade = '📗 Tốt'; gradeColor = 'var(--accent)'; }

  const reviewHtml = wrongList.length ? `
    <div style="margin-top:24px;text-align:left">
      <h3 style="color:var(--red);font-size:15px;margin:0 0 10px">❌ ${wrongList.length} câu sai — xem lại:</h3>
      ${wrongList.map((q,i)=>`
        <div style="background:rgba(198,40,40,0.05);border-left:3px solid var(--red);padding:10px 14px;border-radius:0 6px 6px 0;margin-bottom:8px;font-size:13.5px">
          <div style="font-weight:600;margin-bottom:4px">${i+1}. ${escapeHtml(q.q)}</div>
          <div style="color:var(--red)">✗ Bạn chọn: <strong>${s.answers[q.id]}.</strong> ${escapeHtml(q.options[s.answers[q.id]]||'')}</div>
          <div style="color:var(--accent)">✓ Đáp án đúng: <strong>${q.answer}.</strong> ${escapeHtml(q.options[q.answer])}</div>
          ${q.explain?`<div style="font-style:italic;color:var(--muted);margin-top:4px;font-size:12.5px">📖 ${escapeHtml(q.explain)}</div>`:''}
        </div>
      `).join('')}
    </div>
  ` : '';

  document.getElementById('otn-content').innerHTML = `
    <div class="quiz-header">
      <h2>🏁 Kết quả Ôn tập nhanh</h2>
    </div>
    <div class="quiz-result">
      <div class="score">${score}/${total}</div>
      <div class="pct">${pct}% đúng${skipped.length?` · ${skipped.length} câu bỏ qua`:''}</div>
      <div class="grade" style="color:${gradeColor}">${grade}</div>
      <div class="review-btns">
        <button class="btn" onclick="otnRetake()">🔄 Làm lại bộ này</button>
        ${wrongList.length?`<button class="btn" style="background:var(--red);color:#fff" onclick="otnRetakeWrong()">🔁 Làm lại ${wrongList.length} câu sai</button>`:''}
        <button class="btn secondary" onclick="showOtnSetup('practice','')">⚙️ Quay lại menu</button>
        <button class="btn secondary" onclick="closeOntapNhanh()">✕ Đóng</button>
      </div>
    </div>
    ${reviewHtml}
  `;
}

function otnRetake(){
  if(!otnState) return;
  otnState.idx = 0;
  otnState.answers = {};
  otnState.revealed = new Set();
  otnState.finished = false;
  // Reshuffle within the same set
  otnState.questions = [...otnState.questions].sort(()=>Math.random()-0.5);
  showOtnQuestion();
}

function otnRetakeWrong(){
  if(!otnState) return;
  const wrongList = otnState.questions.filter(q => otnState.answers[q.id] && otnState.answers[q.id] !== q.answer);
  if(wrongList.length === 0) return;
  otnState.questions = wrongList.sort(()=>Math.random()-0.5);
  otnState.idx = 0;
  otnState.answers = {};
  otnState.revealed = new Set();
  otnState.finished = false;
  showOtnQuestion();
}

// === ON_TAP READER (beautiful MD viewer) ===
let otrCurrentSetId = '';

function openOntapReader(setId){
  const set = (ONTAP_NHANH.sets||[]).find(s => s.id === setId);
  if(!set){ alert('Không tìm thấy bộ tài liệu.'); return; }
  if(!set.content_md){ alert('Chưa có nội dung MD cho bộ này — chạy lại rebuild.bat.'); return; }
  otrCurrentSetId = setId;
  document.getElementById('otr-overlay').classList.add('show');
  document.body.style.overflow = 'hidden';
  document.getElementById('otr-title').textContent = set.title;
  document.getElementById('otr-code').textContent = (set.code||'') + ' · Nguồn: ' + (set.source_md||'');
  document.getElementById('otr-quiz-btn').onclick = ()=>{
    closeOntapReader();
    setTimeout(()=>openOntapNhanh('practice', setId), 250);
  };
  // Reset scroll + render
  document.getElementById('otr-content-wrap').scrollTop = 0;
  renderOntapReaderMd(set);
}

function closeOntapReader(){
  document.getElementById('otr-overlay').classList.remove('show');
  document.body.style.overflow = '';
  otrCurrentSetId = '';
}

function renderOntapReaderMd(set){
  const target = document.getElementById('otr-content');
  const toc = document.getElementById('otr-toc');
  target.innerHTML = '⏳ Đang render markdown...';
  toc.innerHTML = '';
  loadMarkedJs().then(()=>{
    try{
      // Configure marked to support GFM tables, task lists
      const renderer = new window.marked.Renderer();
      // Inject IDs for h2/h3 so TOC links work
      const slugCounter = {};
      function slugify(txt){
        let s = txt.toLowerCase()
          .replace(/[àáạảãâầấậẩẫăằắặẳẵ]/g,'a')
          .replace(/[èéẹẻẽêềếệểễ]/g,'e')
          .replace(/[ìíịỉĩ]/g,'i')
          .replace(/[òóọỏõôồốộổỗơờớợởỡ]/g,'o')
          .replace(/[ùúụủũưừứựửữ]/g,'u')
          .replace(/[ỳýỵỷỹ]/g,'y')
          .replace(/đ/g,'d')
          .replace(/[^a-z0-9]+/g,'-')
          .replace(/^-+|-+$/g,'')
          .substring(0, 60);
        if(!s) s = 'section';
        const n = (slugCounter[s] = (slugCounter[s]||0) + 1);
        return n>1 ? s+'-'+n : s;
      }
      renderer.heading = function(text, level){
        if(level === 1 || level === 2 || level === 3){
          const plain = String(text).replace(/<[^>]+>/g,'').trim();
          const id = slugify(plain);
          return `<h${level} id="${id}">${text}</h${level}>`;
        }
        return `<h${level}>${text}</h${level}>`;
      };
      const html = window.marked.parse(set.content_md, {gfm:true, breaks:false, renderer:renderer});
      target.innerHTML = html;
      // Build TOC from h2/h3
      const headings = target.querySelectorAll('h2[id], h3[id]');
      const items = [];
      headings.forEach(h=>{
        const id = h.id;
        const text = h.textContent.replace(/\s*🔗\s*$/,'').trim();
        const lvl = h.tagName.toLowerCase();
        items.push(`<li><a href="#${id}" class="${lvl}" data-target="${id}" onclick="otrScrollTo(event,'${id}')">${escapeHtml(text)}</a></li>`);
      });
      toc.innerHTML = items.join('') || '<li style="padding:8px 16px;color:var(--muted);font-size:12px">(Không có mục lục)</li>';
      // External links open in new tab
      target.querySelectorAll('a').forEach(a=>{
        const href = a.getAttribute('href') || '';
        if(href.startsWith('http')) a.setAttribute('target','_blank');
      });
      // Scroll-spy
      attachOtrScrollSpy(headings);
    }catch(e){
      target.innerHTML = `<pre style="white-space:pre-wrap;font-size:13px;color:var(--text);background:#f5f5f5;padding:18px;border-radius:8px">${escapeHtml(set.content_md)}</pre>`;
    }
  }).catch(()=>{
    target.innerHTML = `<div style="font-size:13px;color:var(--muted);margin-bottom:10px">⚠️ Không tải được marked.js — hiển thị raw:</div><pre style="white-space:pre-wrap;font-size:13px;background:#fafafa;padding:14px;border-radius:6px;line-height:1.7">${escapeHtml(set.content_md)}</pre>`;
  });
}

function otrScrollTo(e, id){
  e.preventDefault();
  const wrap = document.getElementById('otr-content-wrap');
  const el = document.getElementById(id);
  if(!el || !wrap) return;
  wrap.scrollTo({top: el.offsetTop - 20, behavior:'smooth'});
}

function attachOtrScrollSpy(headings){
  const wrap = document.getElementById('otr-content-wrap');
  const toTop = document.getElementById('otr-totop');
  if(!wrap || !headings.length) return;
  wrap.onscroll = ()=>{
    const top = wrap.scrollTop;
    toTop.classList.toggle('show', top > 300);
    // Find current heading
    let current = null;
    for(const h of headings){
      if(h.offsetTop - 60 <= top) current = h;
      else break;
    }
    document.querySelectorAll('#otr-toc a').forEach(a=>{
      a.classList.toggle('active', current && a.dataset.target === current.id);
    });
  };
  wrap.onscroll();
}

function otrCopyLink(){
  // Generate a copy of the set's title with deep link (informational)
  const set = (ONTAP_NHANH.sets||[]).find(s => s.id === otrCurrentSetId);
  if(!set) return;
  const text = `${set.title} (${set.code||''})`;
  navigator.clipboard?.writeText(text).then(()=>{
    const btn = event.target;
    const old = btn.textContent;
    btn.textContent = '✓ Đã chép';
    setTimeout(()=>{btn.textContent = old;}, 1200);
  });
}

function otrKeyHandler(e){
  if(e.key === 'Escape'){ closeOntapReader(); return; }
  const wrap = document.getElementById('otr-content-wrap');
  if(!wrap) return;
  if(e.key === 'ArrowDown' || e.key === 'PageDown' || e.key === ' '){
    e.preventDefault();
    wrap.scrollBy({top: e.key===' '? 500 : 80, behavior:'smooth'});
  } else if(e.key === 'ArrowUp' || e.key === 'PageUp'){
    e.preventDefault();
    wrap.scrollBy({top: -80, behavior:'smooth'});
  } else if(e.key === 'Home'){
    e.preventDefault();
    wrap.scrollTo({top:0, behavior:'smooth'});
  } else if(e.key === 'End'){
    e.preventDefault();
    wrap.scrollTo({top:wrap.scrollHeight, behavior:'smooth'});
  }
}

function otnKeyHandler(e){
  const s = otnState;
  if(!s){
    // Setup screen: only Esc
    if(e.key==='Escape') closeOntapNhanh();
    return;
  }
  if(s.finished){
    if(e.key==='Escape') closeOntapNhanh();
    return;
  }
  const q = s.questions[s.idx];
  // Letter keys A/B/C/D and digit 1-4 to select
  const upper = (e.key||'').toUpperCase();
  if(['A','B','C','D','E','F'].includes(upper) && q.options[upper] !== undefined){
    e.preventDefault();
    otnSelectAnswer(upper);
    return;
  }
  const digits = {'1':'A','2':'B','3':'C','4':'D','5':'E','6':'F'};
  if(digits[e.key] && q.options[digits[e.key]] !== undefined){
    e.preventDefault();
    otnSelectAnswer(digits[e.key]);
    return;
  }
  if(e.key===' ' || e.key==='Enter' || e.key==='ArrowRight'){
    e.preventDefault();
    if(s.mode==='practice'){
      // Space in practice: if not revealed and has selection → check; else → next
      if(s.answers[q.id] && !s.revealed.has(q.id)) otnCheck();
      else otnNext();
    } else {
      otnNext();
    }
    return;
  }
  if(e.key==='ArrowLeft'){
    e.preventDefault();
    otnPrev();
    return;
  }
  if(e.key==='r' || e.key==='R'){
    e.preventDefault();
    otnResetCurrent();
    return;
  }
  if(e.key==='Escape'){
    closeOntapNhanh();
  }
}

// ============================================================
// QUIZ MODE
// ============================================================
const PRACTICE = DATA.practice || {total:0, questions:[]};
const QUIZ_PROGRESS_KEY = 'cds_quiz_history';
let quizState = null;

function loadQuizHistory(){
  try{ return JSON.parse(localStorage.getItem(QUIZ_PROGRESS_KEY) || '{}'); }catch(e){return {};}
}
function saveQuizHistory(h){ localStorage.setItem(QUIZ_PROGRESS_KEY, JSON.stringify(h)); }

function openQuiz(){
  document.getElementById('quiz-overlay').classList.add('show');
  document.body.style.overflow='hidden';
  showQuizSetup();
}

function closeQuiz(){
  document.getElementById('quiz-overlay').classList.remove('show');
  document.body.style.overflow='';
}

function showQuizSetup(){
  quizState = null;
  const allQs = PRACTICE.questions || [];
  const btcQs = [];
  docs.forEach(d => (d.questions||[]).forEach(q => btcQs.push({...q, doc_stt: d.stt, roman: d.roman_id, type:'btc', answer: q.answer, options: q.options, question: q.question, reference: q.reference})));
  const history = loadQuizHistory();
  const seen = Object.keys(history).length;
  const correct = Object.values(history).filter(h=>h.correct).length;
  document.getElementById('quiz-content').innerHTML = `
    <div class="quiz-header">
      <h2>🎯 Chế độ Luyện thi</h2>
      <div class="quiz-sub">
        Tổng kho câu hỏi: <strong>${allQs.length}</strong> auto-gen (548 ngưỡng + 213 khái niệm)
        + <strong>${btcQs.length}</strong> câu BTC.
        Mọi đáp án sai (distractors) đều là giá trị THẬT từ VB khác — không bịa.
      </div>
      <div class="quiz-sub" style="margin-top:6px">
        📊 Lịch sử: đã làm <strong>${seen}</strong> câu, đúng <strong>${correct}</strong> (${seen?Math.round(correct*100/seen):0}%)
      </div>
    </div>
    <h3 style="margin:0 0 12px;font-size:15px">Chọn chế độ:</h3>
    <div class="quiz-mode-btns">
      <div class="quiz-mode-btn" onclick="startQuiz({type:'daily', n:20})">
        <span class="icon">📅</span><div class="name">Daily 20</div><div class="desc">20 câu ngẫu nhiên/ngày</div>
      </div>
      <div class="quiz-mode-btn" onclick="startQuiz({type:'all', n:30})">
        <span class="icon">🎲</span><div class="name">Random 30</div><div class="desc">Mix tất cả loại</div>
      </div>
      <div class="quiz-mode-btn" onclick="startQuiz({type:'threshold', n:25})">
        <span class="icon">📊</span><div class="name">Chỉ Ngưỡng</div><div class="desc">25 câu số liệu</div>
      </div>
      <div class="quiz-mode-btn" onclick="startQuiz({type:'concept', n:25})">
        <span class="icon">🔑</span><div class="name">Chỉ Khái niệm</div><div class="desc">25 câu định nghĩa</div>
      </div>
      <div class="quiz-mode-btn" onclick="startQuiz({type:'btc', n:30})">
        <span class="icon">📋</span><div class="name">Chỉ câu BTC</div><div class="desc">30 câu từ 170 câu BTC matched</div>
      </div>
      <div class="quiz-mode-btn" onclick="startQuiz({type:'wrong', n:20})">
        <span class="icon">🔁</span><div class="name">Ôn câu sai</div><div class="desc">Câu đã sai lần trước</div>
      </div>
    </div>
    <div class="quiz-setup" style="margin-top:20px">
      <div class="row">
        <label>Lọc theo VB:</label>
        <select id="quiz-filter-doc" onchange="updateQuizFilter()">
          <option value="">— Tất cả 39 VB —</option>
          ${docs.map(d=>`<option value="${d.stt}">${d.roman_id} - ${escapeHtml(d.short_name)}</option>`).join('')}
        </select>
      </div>
      <div class="row">
        <label>Lọc theo chủ đề:</label>
        <select id="quiz-filter-topic" onchange="updateQuizFilter()">
          <option value="">— Tất cả 8 chủ đề —</option>
          ${Object.entries(TOPIC_NAMES).map(([k,v])=>`<option value="${k}">${escapeHtml(v)}</option>`).join('')}
        </select>
      </div>
      <div class="row">
        <button class="btn" onclick="startQuizCustom()">▶️ Bắt đầu với bộ lọc trên</button>
        <button class="btn secondary" onclick="if(confirm('Reset toàn bộ lịch sử quiz?')){localStorage.removeItem(QUIZ_PROGRESS_KEY);showQuizSetup();}">🗑️ Reset lịch sử</button>
      </div>
    </div>
  `;
}

function updateQuizFilter(){}

function startQuizCustom(){
  const docFilter = document.getElementById('quiz-filter-doc').value;
  const topicFilter = document.getElementById('quiz-filter-topic').value;
  startQuiz({type:'all', n:25, doc_stt: docFilter, topic: topicFilter});
}

function startQuiz(opts){
  let pool = [];
  const allQs = PRACTICE.questions || [];
  const btcQs = [];
  docs.forEach(d => (d.questions||[]).forEach(q => btcQs.push({
    id: 'BTC-'+q.q_id, type:'btc', doc_stt: d.stt, roman: d.roman_id,
    question: q.question, options: q.options, answer: q.answer,
    reference: q.reference, explanation: q.dieu_khoan, topic: q.mang
  })));

  if(opts.type === 'threshold') pool = allQs.filter(q=>q.type==='threshold');
  else if(opts.type === 'concept') pool = allQs.filter(q=>q.type==='concept');
  else if(opts.type === 'btc') pool = btcQs;
  else if(opts.type === 'wrong') {
    const h = loadQuizHistory();
    const wrongIds = new Set(Object.keys(h).filter(id => !h[id].correct));
    pool = [...allQs, ...btcQs].filter(q => wrongIds.has(q.id));
    if(pool.length === 0){
      alert('Chưa có câu sai nào — làm vài câu trước đã!');
      return;
    }
  }
  else pool = [...allQs, ...btcQs];

  // Apply filters
  if(opts.doc_stt) pool = pool.filter(q => String(q.doc_stt) === String(opts.doc_stt));
  if(opts.topic){
    pool = pool.filter(q => {
      if(q.topic === opts.topic) return true;
      const d = sttToDoc[q.doc_stt];
      return d && ((d.topics_main||[]).includes(opts.topic) || (d.topics_secondary||[]).includes(opts.topic));
    });
  }
  if(pool.length === 0){
    alert('Không có câu hỏi nào khớp bộ lọc này.');
    return;
  }
  // Shuffle and take N
  const shuffled = [...pool].sort(()=>Math.random()-0.5);
  const questions = shuffled.slice(0, Math.min(opts.n || 20, shuffled.length));
  quizState = {
    questions: questions,
    idx: 0,
    answers: {},  // q_id -> chosen letter
    score: 0,
    revealed: new Set(),
  };
  showQuizQuestion();
}

function showQuizQuestion(){
  const s = quizState;
  if(!s) return;
  if(s.idx >= s.questions.length){ showQuizResult(); return; }
  const q = s.questions[s.idx];
  const chosen = s.answers[q.id];
  const revealed = s.revealed.has(q.id);
  const optsHtml = Object.entries(q.options).map(([letter, text])=>{
    let cls = 'quiz-option';
    if(revealed){
      if(letter === q.answer) cls += ' correct';
      else if(letter === chosen) cls += ' wrong';
    } else if(letter === chosen) cls += ' selected';
    return `<div class="${cls}" onclick="selectAnswer('${letter}')"><span class="letter">${letter}.</span><span>${escapeHtml(text)}</span></div>`;
  }).join('');
  const pct = Math.round(((s.idx+1)/s.questions.length)*100);
  const d = sttToDoc[q.doc_stt];
  document.getElementById('quiz-content').innerHTML = `
    <div class="quiz-progress">
      <span>Câu ${s.idx+1}/${s.questions.length}</span>
      <div class="bar"><div class="fill" style="width:${pct}%"></div></div>
      <span>${s.score} đúng</span>
    </div>
    <div class="quiz-question">
      <div class="q-meta">
        <span style="color:var(--accent)">${escapeHtml(q.id||'')}</span> ·
        <span>${d?d.roman_id+' - '+escapeHtml(d.short_name):''}</span> ·
        <span>Loại: ${q.type==='threshold'?'📊 Ngưỡng':q.type==='concept'?'🔑 Khái niệm':'📋 BTC'}</span>
      </div>
      <div class="q-text">${escapeHtml(q.question)}</div>
    </div>
    <div class="quiz-options">${optsHtml}</div>
    <div class="quiz-explain ${revealed?'show':''}" id="quiz-explain">
      <div class="label">📖 Giải thích (verbatim từ VB)</div>
      <div class="quote">${escapeHtml(q.explanation||'')}</div>
      <div style="font-size:12px;color:var(--muted);margin-top:6px">Nguồn: ${escapeHtml(q.reference||'')}</div>
    </div>
    <div class="quiz-controls">
      <button class="btn secondary" onclick="prevQuestion()" ${s.idx===0?'disabled style=opacity:0.4':''}>← Trước</button>
      <div>
        ${chosen && !revealed ? '<button class="btn" onclick="checkAnswer()">✓ Kiểm tra</button>' : ''}
        ${revealed ? '<button class="btn" onclick="nextQuestion()">Tiếp →</button>' : ''}
      </div>
      <button class="btn secondary" onclick="if(confirm('Kết thúc luôn?'))showQuizResult()">⏹ Kết thúc</button>
    </div>
  `;
}

function selectAnswer(letter){
  const s = quizState;
  const q = s.questions[s.idx];
  if(s.revealed.has(q.id)) return;
  s.answers[q.id] = letter;
  showQuizQuestion();
}

function checkAnswer(){
  const s = quizState;
  const q = s.questions[s.idx];
  if(s.revealed.has(q.id)) return;
  const chosen = s.answers[q.id];
  if(!chosen) return;
  s.revealed.add(q.id);
  const isCorrect = chosen === q.answer;
  if(isCorrect) s.score++;
  // Save history
  const h = loadQuizHistory();
  h[q.id] = {correct: isCorrect, chosen, ans: q.answer, ts: Date.now()};
  saveQuizHistory(h);
  showQuizQuestion();
}

function nextQuestion(){
  quizState.idx++;
  showQuizQuestion();
}

function prevQuestion(){
  if(quizState.idx > 0){
    quizState.idx--;
    showQuizQuestion();
  }
}

// ============================================================
// Per-VB Study Flow: Detailed summary sheet → then quiz THAT doc only
// ============================================================
function startStudyFlow(stt){
  const d = sttToDoc[stt];
  if(!d) return;
  // Build a "study sheet" with everything verbatim
  const concepts = (d.concepts||[]);
  const thresholds = (d.thresholds||[]);
  const keynotes = (d.keynotes||[]);
  const dieus = ((d.structure||{}).dieus||[]);
  // Top Điều by question count
  const dieuQCount = {};
  (d.questions||[]).forEach(q=>{
    const m = (q.dieu_khoan||'').match(/Điều\s+(\d+[a-z]?)/);
    if(m) dieuQCount[m[1]] = (dieuQCount[m[1]]||0)+1;
  });
  const topDieus = Object.entries(dieuQCount).sort((a,b)=>b[1]-a[1]).slice(0,5);
  const docAutoQs = (PRACTICE.questions||[]).filter(q => q.doc_stt === stt);

  // Open quiz overlay with study mode
  document.getElementById('quiz-overlay').classList.add('show');
  document.body.style.overflow='hidden';
  document.getElementById('quiz-content').innerHTML = `
    <div class="quiz-header">
      <h2>🎓 Học kỹ: ${d.roman_id} — ${escapeHtml(d.short_name)}</h2>
      <div class="quiz-sub">${escapeHtml(d.full_name)} · ${escapeHtml(d.code)} · ${d.date}</div>
      <div class="quiz-sub" style="margin-top:6px">
        Bước 1: <strong>Đọc kỹ phần tóm tắt dưới đây</strong> · Bước 2: <strong>Click "Bắt đầu Quiz"</strong> làm ${docAutoQs.length} câu auto-gen (không trùng 400 BTC)
      </div>
    </div>
    <div style="max-height:60vh;overflow-y:auto;padding-right:8px;border:1px solid var(--border);border-radius:8px;padding:14px;background:rgba(0,0,0,0.15)">

      <h3 style="margin:0 0 8px;color:var(--accent);font-size:15px">📋 META</h3>
      <div style="font-size:13px;line-height:1.7">
        • Loại: <strong>${d.category_icon} ${escapeHtml(d.category)}</strong> · Mã: <code>${escapeHtml(d.code)}</code><br>
        • Chủ đề BTC chính: <strong>${(d.topics_main||[]).join(', ')||'—'}</strong> · Phụ: ${(d.topics_secondary||[]).join(', ')||'—'}<br>
        • Quy mô: <strong>${dieus.length} Điều</strong> · ${concepts.length} khái niệm · ${thresholds.length} ngưỡng · ${keynotes.length} keynote<br>
        • Câu BTC liên quan: <strong>${(d.questions||[]).length} câu</strong>${topDieus.length?` · Điều hay hỏi: ${topDieus.map(([n,c])=>`<strong>Đ.${n}</strong> (${c}c)`).join(', ')}`:''}
      </div>

      ${d.summary ? `<h3 style="margin:18px 0 8px;color:var(--accent);font-size:15px">⭐ NỘI DUNG CHÍNH (verbatim master CSV)</h3>
      <div style="font-size:13.5px;line-height:1.7;white-space:pre-wrap;background:var(--card);padding:10px 14px;border-radius:6px;border-left:3px solid var(--accent)">${escapeHtml(d.summary)}</div>` : ''}

      ${concepts.length ? `<h3 style="margin:18px 0 8px;color:var(--purple);font-size:15px">🔑 KHÁI NIỆM CỐT LÕI (${concepts.length})</h3>
      <div style="font-size:13px;line-height:1.65">
        ${concepts.map((c,i)=>`<div style="margin-bottom:8px;padding:8px 12px;background:rgba(168,85,247,0.07);border-radius:5px;border-left:2px solid var(--purple)">
          <strong style="color:var(--purple)">${i+1}. ${escapeHtml(c.term)}</strong>${c.source_dieu?` <span style="font-size:11px;color:var(--muted)">(${escapeHtml(c.source_dieu)})</span>`:''}<br>
          <span style="color:var(--muted)">→</span> ${escapeHtml(c.definition||'').substring(0,400)}${(c.definition||'').length>400?'...':''}
        </div>`).join('')}
      </div>` : ''}

      ${thresholds.length ? `<h3 style="margin:18px 0 8px;color:var(--yellow);font-size:15px">📊 NGƯỠNG SỐ LIỆU (${thresholds.length}) — PHẢI THUỘC</h3>
      <table style="width:100%;font-size:12.5px;border-collapse:collapse">
        <thead><tr><th style="padding:5px;text-align:left;border-bottom:1px solid var(--border);color:var(--muted)">Giá trị</th><th style="padding:5px;text-align:left;border-bottom:1px solid var(--border);color:var(--muted)">Loại</th><th style="padding:5px;text-align:left;border-bottom:1px solid var(--border);color:var(--muted)">Đ.K</th><th style="padding:5px;text-align:left;border-bottom:1px solid var(--border);color:var(--muted)">Mô tả</th></tr></thead>
        <tbody>${thresholds.map(th=>`<tr><td style="padding:5px;border-bottom:1px solid var(--border);font-weight:600;color:var(--yellow);font-family:Consolas,monospace">${escapeHtml(th.gia_tri||'')}</td><td style="padding:5px;border-bottom:1px solid var(--border);font-size:11px">${escapeHtml(th.loai||'')}</td><td style="padding:5px;border-bottom:1px solid var(--border);font-family:Consolas,monospace;font-size:11px;color:var(--accent)">${escapeHtml(th.dieu_khoan||'')}</td><td style="padding:5px;border-bottom:1px solid var(--border)">${escapeHtml(th.mo_ta||'')}</td></tr>`).join('')}</tbody>
      </table>` : ''}

      ${keynotes.length ? `<h3 style="margin:18px 0 8px;color:var(--green);font-size:15px">🎯 KEYNOTES HAY HỎI (${keynotes.length})</h3>
      <div style="font-size:13px;line-height:1.6">
        ${keynotes.slice(0,15).map((kn,i)=>`<div style="margin-bottom:6px;padding:7px 12px;background:rgba(34,197,94,0.06);border-left:2px solid var(--green);border-radius:0 4px 4px 0;white-space:pre-wrap">${highlightKeynote(kn.text, d.stt)}</div>`).join('')}
        ${keynotes.length>15?`<div style="font-size:11px;color:var(--muted);text-align:center;margin-top:6px">+ ${keynotes.length-15} keynote còn lại — xem trong drawer "🎯 Keynotes"</div>`:''}
      </div>` : ''}

      ${dieus.length ? `<h3 style="margin:18px 0 8px;color:var(--accent);font-size:15px">📚 TÓM TẮT CHI TIẾT THEO CHƯƠNG + ĐIỀU (verbatim title + preview)</h3>
      <div style="font-size:13px;line-height:1.55">
        ${(()=>{
          // Group dieus by chuong
          const groups = [];
          let cur = null;
          dieus.forEach(di=>{
            if(di.chuong !== (cur?cur.label:null)){
              cur = {label: di.chuong, items: []};
              groups.push(cur);
            }
            cur.items.push(di);
          });
          return groups.map(g=>{
            return `<div style="margin-bottom:14px">
              ${g.label?`<div style="font-weight:700;color:var(--accent2);font-size:13px;text-transform:uppercase;margin-bottom:6px;border-bottom:1px dashed var(--border);padding-bottom:3px">📘 ${escapeHtml(g.label)}</div>`:''}
              ${g.items.map(di=>{
                const preview = (di.text||'').substring(0,250).replace(/\s+/g,' ').trim();
                const isTop = topDieus.some(([n])=>n===di.number);
                return `<div style="margin-bottom:6px;padding:6px 10px;background:${isTop?'rgba(56,189,248,0.08)':'rgba(0,0,0,0.15)'};border-radius:4px;border-left:2px solid ${isTop?'var(--accent)':'var(--border)'}">
                  <div style="font-weight:600;margin-bottom:2px"><span style="color:var(--accent)">Điều ${di.number}.</span> ${escapeHtml(di.title)}${isTop?` <span style="font-size:10px;color:var(--accent2)">🔥 hot</span>`:''}</div>
                  ${preview?`<div style="color:var(--muted);font-size:12px">${escapeHtml(preview)}${(di.text||'').length>250?'…':''}</div>`:''}
                </div>`;
              }).join('')}
            </div>`;
          }).join('');
        })()}
      </div>` : ''}

      ${topDieus.length ? `<h3 style="margin:18px 0 8px;color:var(--accent);font-size:15px">🎯 5 ĐIỀU HAY HỎI NHẤT — TRÍCH DẪN ĐẦY ĐỦ</h3>
      ${topDieus.map(([n,c])=>{
        const di = dieus.find(x=>x.number===n);
        if(!di) return '';
        const mdPath = d.md_file ? 'vcb_cds_202605/van_ban/'+d.md_file : '';
        return `<div style="margin-bottom:12px;padding:12px 14px;background:var(--card);border-radius:6px;border-left:3px solid var(--accent);border:1px solid var(--border);box-shadow:var(--shadow)">
          <div style="font-weight:700;margin-bottom:6px;font-size:14px">Điều ${di.number}. ${escapeHtml(di.title)} <span style="font-size:11px;color:var(--accent2)">🔥 ${c} câu BTC</span></div>
          <div style="font-size:13px;color:var(--text);white-space:pre-wrap;line-height:1.8;background:rgba(0,133,63,0.04);padding:12px 14px;border-radius:4px;border:1px solid rgba(0,133,63,0.15)">${escapeHtml(cleanLawText(di.text||''))}</div>
          <div style="font-size:11px;color:var(--muted);margin-top:8px;font-style:italic">📖 Trích nguyên văn từ ${mdPath?`<a href="${escapeAttr(mdPath)}" target="_blank" style="color:var(--accent)">${escapeHtml(d.md_file||'')}</a>`:'(?)'}</div>
        </div>`;
      }).join('')}` : ''}

      ${d.whats_new ? `<h3 style="margin:18px 0 8px;color:var(--accent2);font-size:15px">🆕 ĐIỂM MỚI SO VỚI VB CHA</h3>
      <div style="font-size:13px;line-height:1.7;white-space:pre-wrap;padding:10px 14px;background:rgba(251,146,60,0.06);border-radius:5px">${escapeHtml(d.whats_new)}</div>` : ''}

    </div>
    <div class="quiz-controls" style="margin-top:18px">
      <button class="btn secondary" onclick="showQuizSetup()">← Về menu Quiz</button>
      <div>
        ${docAutoQs.length ? `<button class="btn" onclick="startQuiz({type:'all', n:${Math.min(docAutoQs.length, 30)}, doc_stt:${stt}})" style="background:var(--accent2);color:#fff">▶️ Bắt đầu Quiz ${Math.min(docAutoQs.length, 30)} câu (auto-gen, không trùng BTC)</button>` : '<span style="color:var(--muted);font-size:13px">Chưa có câu auto-gen cho VB này</span>'}
      </div>
      <button class="btn secondary" onclick="closeQuiz()">Đóng</button>
    </div>
  `;
}

function showQuizResult(){
  const s = quizState;
  if(!s) return;
  const total = s.questions.length;
  const answered = Object.keys(s.answers).length;
  const pct = total ? Math.round(s.score*100/total) : 0;
  let grade = '', emoji = '';
  if(pct >= 90){grade='Xuất sắc 🏆'; emoji='🎉';}
  else if(pct >= 75){grade='Tốt 👍'; emoji='💪';}
  else if(pct >= 60){grade='Khá ⚠️'; emoji='📚';}
  else {grade='Cần ôn thêm 🔁'; emoji='💪';}
  // Show wrong questions for review
  const wrong = s.questions.filter(q => s.answers[q.id] && s.answers[q.id] !== q.answer);
  const wrongList = wrong.length ? `
    <div style="margin-top:24px;text-align:left">
      <h3 style="font-size:15px;color:var(--red);margin:0 0 10px">📕 ${wrong.length} câu sai cần ôn lại:</h3>
      ${wrong.map(q=>{
        const d = sttToDoc[q.doc_stt];
        return `<div style="background:var(--card);padding:10px 14px;border-radius:6px;margin-bottom:8px;border-left:3px solid var(--red)">
          <div style="font-size:12px;color:var(--muted);margin-bottom:4px">${d?d.roman_id+' '+escapeHtml(d.short_name):''} · ${escapeHtml(q.reference||'')}</div>
          <div style="font-weight:500">${escapeHtml(q.question.substring(0,150))}${q.question.length>150?'...':''}</div>
          <div style="font-size:12px;margin-top:6px"><span style="color:var(--red)">Bạn chọn: ${s.answers[q.id]}. ${escapeHtml(q.options[s.answers[q.id]]||'')}</span></div>
          <div style="font-size:12px;color:var(--green)">Đúng: ${q.answer}. ${escapeHtml(q.options[q.answer]||'')}</div>
        </div>`;
      }).join('')}
    </div>
  ` : '<div style="margin-top:20px;color:var(--green);font-size:16px">🎉 Không có câu sai nào!</div>';
  document.getElementById('quiz-content').innerHTML = `
    <div class="quiz-result">
      <div class="score">${s.score}/${total}</div>
      <div class="pct">${pct}% · ${answered}/${total} câu đã trả lời</div>
      <div class="grade">${emoji} ${grade}</div>
      ${wrongList}
      <div class="review-btns">
        <button class="btn" onclick="showQuizSetup()">🔄 Làm bài khác</button>
        <button class="btn secondary" onclick="closeQuiz()">Đóng</button>
      </div>
    </div>
  `;
}

function ensureMermaid(){
  if(mermaidLoaded && window.mermaid) return Promise.resolve();
  if(window.mermaid){ mermaidLoaded = true; return Promise.resolve(); }
  return new Promise((resolve,reject)=>{
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js';
    script.onload = ()=>{
      try{
        window.mermaid.initialize({
          startOnLoad: false,
          theme: 'default',
          securityLevel: 'loose',
        });
        mermaidLoaded = true;
        resolve();
      }catch(e){reject(e);}
    };
    script.onerror = ()=>reject(new Error('Mermaid CDN load failed'));
    document.head.appendChild(script);
  });
}

// ============================================================
// FLASHCARDS — Anki-style spaced repetition
// ============================================================
const FC_STATE_KEY = 'cds_flashcards_state';
let fcState = null;  // current session

function loadFcStore(){
  try{ return JSON.parse(localStorage.getItem(FC_STATE_KEY) || '{}'); }catch(e){return {};}
}
function saveFcStore(s){ localStorage.setItem(FC_STATE_KEY, JSON.stringify(s)); }

// Build the full card deck from existing data (concepts + thresholds + article titles)
function buildFcDeck(){
  const deck = [];
  docs.forEach(d => {
    // Concept cards (front: term, back: definition + source)
    (d.concepts||[]).forEach((c,i)=>{
      deck.push({
        id: `cc-${d.stt}-${i}`,
        type: 'concept',
        doc_stt: d.stt,
        front: c.term,
        back_title: 'Định nghĩa pháp lý',
        back: c.definition || c.full_text || '',
        source: `${d.roman_id} ${d.short_name}, ${c.source_dieu||''}`,
        source_path: d.md_file ? 'vcb_cds_202605/van_ban/'+d.md_file : '',
      });
    });
    // Threshold cards (front: "mo_ta = ?", back: gia_tri + quote)
    (d.thresholds||[]).forEach((th,i)=>{
      if(!th.mo_ta || !th.gia_tri) return;
      deck.push({
        id: `th-${d.stt}-${i}`,
        type: 'threshold',
        doc_stt: d.stt,
        front: `${th.mo_ta} (${d.short_name}, ${th.dieu_khoan||''})`,
        back_title: 'Giá trị: ' + th.gia_tri,
        back: th.loai ? `Loại: ${th.loai}` : '',
        quote: th.quote || '',
        source: `${d.roman_id} ${d.short_name}, ${th.dieu_khoan||''} (thresholds_full.csv)`,
        source_path: 'vcb_cds_202605/thresholds_full.csv',
      });
    });
    // (Article-title flashcards removed — rote memorization of Điều numbers
    //  is "đánh đố", not real legal knowledge. Concepts + Thresholds remain.)
  });
  return deck;
}

// SRS scheduler — return next review timestamp based on rating
function srsSchedule(card, rating, prev){
  const now = Date.now();
  const day = 86400000;
  let interval, ease = (prev && prev.ease) || 2.5;
  if(rating === 'again'){
    interval = 10*60*1000;  // 10 min
    ease = Math.max(1.3, ease - 0.2);
  } else if(rating === 'hard'){
    interval = day * Math.max(1, (prev?.interval || day) / day * 1.2);
    ease = Math.max(1.3, ease - 0.15);
  } else if(rating === 'good'){
    interval = day * Math.max(2, (prev?.interval || day) / day * ease);
  } else { // easy
    interval = day * Math.max(4, (prev?.interval || day) / day * ease * 1.3);
    ease = ease + 0.15;
  }
  return {due: now + interval, interval, ease, last: now, reps: (prev?.reps||0)+1};
}

function openFlashcards(){
  document.getElementById('fc-overlay').classList.add('show');
  document.body.style.overflow='hidden';
  showFcSetup();
}

function closeFlashcards(){
  document.getElementById('fc-overlay').classList.remove('show');
  document.body.style.overflow='';
}

function showFcSetup(){
  fcState = null;
  const deck = buildFcDeck();
  const store = loadFcStore();
  const now = Date.now();
  const seen = Object.keys(store).filter(k=>store[k].last).length;
  const dueCount = deck.filter(c => store[c.id] && store[c.id].due <= now).length;
  const newCount = deck.filter(c => !store[c.id]).length;
  const starredCount = deck.filter(c => store[c.id] && store[c.id].star).length;
  const totalSrs = Object.keys(store).length;
  document.getElementById('fc-content').innerHTML = `
    <div class="quiz-header">
      <h2>📇 Flashcards · Active Recall + Spaced Repetition</h2>
      <div class="quiz-sub">
        Tổng kho: <strong>${deck.length}</strong> thẻ (khái niệm + ngưỡng + Điều) · Đã ôn: <strong>${seen}</strong> · Đã star ⭐: <strong>${starredCount}</strong>
      </div>
      <div class="quiz-sub" style="margin-top:6px">
        Cách dùng: xem mặt trước → cố nhớ đáp án → click "Lật" → chấm <strong>Lại học / Khó / Dễ / Quá dễ</strong> → thẻ sẽ tự lịch lại theo thuật toán SRS.
      </div>
    </div>
    <h3 style="margin:0 0 12px;font-size:15px">Chọn chế độ học:</h3>
    <div class="fc-mode-grid">
      <div class="quiz-mode-btn" onclick="startFc({mode:'due', n:30})">
        <span class="icon">🔔</span><div class="name">Đến hạn ôn</div><div class="desc">${dueCount} thẻ đến hạn hôm nay</div>
      </div>
      <div class="quiz-mode-btn" onclick="startFc({mode:'new', n:20})">
        <span class="icon">✨</span><div class="name">Học mới</div><div class="desc">${newCount} thẻ chưa từng học</div>
      </div>
      <div class="quiz-mode-btn" onclick="startFc({mode:'starred'})">
        <span class="icon">⭐</span><div class="name">Đã đánh dấu</div><div class="desc">${starredCount} thẻ đã star</div>
      </div>
      <div class="quiz-mode-btn" onclick="startFc({mode:'all', n:25})">
        <span class="icon">🎲</span><div class="name">Random 25</div><div class="desc">Mix tất cả</div>
      </div>
      <div class="quiz-mode-btn" onclick="startFc({mode:'concept', n:25})">
        <span class="icon">🔑</span><div class="name">Khái niệm</div><div class="desc">214 thẻ định nghĩa</div>
      </div>
      <div class="quiz-mode-btn" onclick="startFc({mode:'threshold', n:25})">
        <span class="icon">📊</span><div class="name">Ngưỡng</div><div class="desc">548 thẻ số liệu</div>
      </div>
      <div class="quiz-mode-btn" onclick="startFc({mode:'difficult', n:20})">
        <span class="icon">🔥</span><div class="name">Khó (nhiều 'lại học')</div><div class="desc">Thẻ hay sai</div>
      </div>
    </div>
    <div style="margin-top:18px;display:flex;gap:8px;flex-wrap:wrap">
      <label style="font-size:13px;color:var(--muted)">Lọc theo VB:</label>
      <select id="fc-doc-filter" style="background:#fff;border:1px solid var(--border);color:var(--text);padding:6px 10px;border-radius:6px;font-size:13px">
        <option value="">— Tất cả 39 VB —</option>
        ${docs.map(d=>`<option value="${d.stt}">${d.roman_id} - ${escapeHtml(d.short_name)}</option>`).join('')}
      </select>
      <button class="btn" onclick="startFcCustom()">▶️ Bắt đầu với bộ lọc</button>
      <button class="btn secondary" onclick="if(confirm('Reset toàn bộ tiến độ flashcard?')){localStorage.removeItem(FC_STATE_KEY);showFcSetup();}" style="margin-left:auto">🗑️ Reset</button>
    </div>
  `;
}

// Start flashcards filtered to a single VB (called from doc drawer)
function startFcForDoc(stt){
  closeDrawer();  // close VB drawer first
  document.getElementById('fc-overlay').classList.add('show');
  document.body.style.overflow='hidden';
  startFc({mode:'all', doc_stt: stt});  // all concepts + thresholds of this VB
}

function startFcCustom(){
  const docFilter = document.getElementById('fc-doc-filter').value;
  startFc({mode:'all', n: 30, doc_stt: docFilter});
}

function startFc(opts){
  const allDeck = buildFcDeck();
  const store = loadFcStore();
  const now = Date.now();
  let pool = allDeck;
  if(opts.mode === 'due') pool = pool.filter(c => store[c.id] && store[c.id].due <= now);
  else if(opts.mode === 'new') pool = pool.filter(c => !store[c.id]);
  else if(opts.mode === 'starred') pool = pool.filter(c => store[c.id] && store[c.id].star);
  else if(opts.mode === 'difficult') pool = pool.filter(c => {
    const s = store[c.id];
    return s && s.again_count && s.again_count >= 2;
  });
  else if(opts.mode === 'concept') pool = pool.filter(c => c.type === 'concept');
  else if(opts.mode === 'threshold') pool = pool.filter(c => c.type === 'threshold');
  else if(opts.mode === 'article') pool = pool.filter(c => c.type === 'article');
  if(opts.doc_stt) pool = pool.filter(c => String(c.doc_stt) === String(opts.doc_stt));
  if(pool.length === 0){
    alert('Không có thẻ nào khớp bộ lọc.');
    return;
  }
  // Shuffle, take N
  const shuffled = [...pool].sort(()=>Math.random()-0.5);
  const n = opts.n || pool.length;
  fcState = {
    cards: shuffled.slice(0, Math.min(n, shuffled.length)),
    idx: 0,
    flipped: false,
    rated: 0,
    again_count: 0,
    easy_count: 0,
  };
  showFcCard();
}

function showFcCard(){
  const s = fcState;
  if(!s){ showFcSetup(); return; }
  if(s.idx >= s.cards.length){ showFcResult(); return; }
  const c = s.cards[s.idx];
  const store = loadFcStore();
  const prev = store[c.id] || {};
  const isStarred = prev.star;
  const reps = prev.reps || 0;
  const pct = Math.round(((s.idx+1)/s.cards.length)*100);
  const typeLabel = c.type === 'concept' ? '🔑 Khái niệm' : (c.type === 'threshold' ? '📊 Ngưỡng' : '📑 Tên Điều');
  const d = sttToDoc[c.doc_stt];

  document.getElementById('fc-content').innerHTML = `
    <div class="quiz-header" style="margin-bottom:6px">
      <h2 style="font-size:18px">📇 Flashcard ${s.idx+1}/${s.cards.length}</h2>
    </div>
    <div class="fc-stage">
      <div class="fc-progress">
        <span>${s.idx+1}/${s.cards.length}</span>
        <div class="bar"><div class="fill" style="width:${pct}%"></div></div>
        <span>${s.rated} đã chấm · ${s.again_count} lại học</span>
      </div>
      <div class="fc-nav-wrap">
        <button class="fc-nav-arrow" onclick="goFcPrev()" ${s.idx===0?'disabled':''} title="Card trước (← hoặc PageUp)">←</button>
        <div class="fc-card-wrap" onclick="flipFc()">
          <div class="fc-card${s.flipped?' flipped':''}">
            <div class="fc-face">
              <span class="fc-badge">${typeLabel}</span>
              <div class="fc-roman">${d?d.roman_id+' · '+escapeHtml(d.short_name):''} · Đã học ${reps} lần${isStarred?' · ⭐':''}${prev.rating?' · '+ratingLabel(prev.rating):''}</div>
              <div class="fc-front-text">${escapeHtml(c.front)}</div>
              <div class="fc-hint">👆 Click hoặc Space để lật · ← → để chuyển thẻ</div>
            </div>
            <div class="fc-face back">
              <div class="fc-back-title">${escapeHtml(c.back_title)}</div>
              <div class="fc-back-content">${escapeHtml(cleanLawText(c.back||''))}</div>
              ${c.quote?`<div class="fc-back-quote">"${escapeHtml(c.quote)}"</div>`:''}
              <div class="fc-back-src">📖 Nguồn: ${c.source_path?`<a href="${escapeAttr(c.source_path)}" target="_blank">${escapeHtml(c.source)}</a>`:escapeHtml(c.source)}</div>
            </div>
          </div>
        </div>
        <button class="fc-nav-arrow" onclick="goFcNext()" ${s.idx>=s.cards.length-1?'disabled':''} title="Card sau (→ hoặc PageDown)">→</button>
      </div>
      ${s.flipped ? `
        <div class="fc-rate">
          <button class="fc-rate-btn again" onclick="rateFc('again')">
            <span class="emo">😵</span><span class="label">Lại học</span><span class="interval">~10 phút</span>
          </button>
          <button class="fc-rate-btn hard" onclick="rateFc('hard')">
            <span class="emo">😐</span><span class="label">Khó</span><span class="interval">~1 ngày</span>
          </button>
          <button class="fc-rate-btn good" onclick="rateFc('good')">
            <span class="emo">😊</span><span class="label">Dễ</span><span class="interval">~3 ngày</span>
          </button>
          <button class="fc-rate-btn easy" onclick="rateFc('easy')">
            <span class="emo">🎯</span><span class="label">Quá dễ</span><span class="interval">~7 ngày</span>
          </button>
        </div>
      ` : `<div style="font-size:13px;color:var(--muted)">Phím tắt: <kbd style="background:var(--card);padding:2px 6px;border-radius:3px;border:1px solid var(--border)">Space</kbd> = Lật</div>`}
      <div class="fc-controls">
        <button class="btn secondary" onclick="skipFc()">⏭️ Bỏ qua</button>
        <button class="btn secondary" onclick="toggleStarFc()">${isStarred?'⭐ Bỏ đánh dấu':'☆ Đánh dấu'}</button>
        <button class="btn secondary" onclick="openSourceFromFc()">🔍 Xem VB</button>
        <button class="btn secondary" onclick="if(confirm('Kết thúc luôn?'))showFcResult()">⏹ Kết thúc</button>
      </div>
    </div>
  `;
}

function flipFc(){
  if(!fcState) return;
  fcState.flipped = !fcState.flipped;
  showFcCard();
}

function goFcPrev(){
  if(!fcState || fcState.idx === 0) return;
  fcState.idx--;
  fcState.flipped = false;
  showFcCard();
}

function goFcNext(){
  if(!fcState) return;
  if(fcState.idx >= fcState.cards.length - 1){
    showFcResult();
    return;
  }
  fcState.idx++;
  fcState.flipped = false;
  showFcCard();
}

function ratingLabel(r){
  return {again:'😵 Lại học', hard:'😐 Khó', good:'😊 Dễ', easy:'🎯 Quá dễ'}[r] || '';
}

function rateFc(rating){
  const s = fcState;
  if(!s) return;
  const c = s.cards[s.idx];
  const store = loadFcStore();
  const prev = store[c.id] || {};
  const sched = srsSchedule(c, rating, prev);
  store[c.id] = {
    ...prev,
    ...sched,
    rating,
    again_count: (prev.again_count||0) + (rating === 'again' ? 1 : 0),
  };
  saveFcStore(store);
  s.rated++;
  if(rating === 'again') s.again_count++;
  if(rating === 'easy') s.easy_count++;
  s.idx++;
  s.flipped = false;
  showFcCard();
}

function skipFc(){
  fcState.idx++;
  fcState.flipped = false;
  showFcCard();
}

function toggleStarFc(){
  const c = fcState.cards[fcState.idx];
  const store = loadFcStore();
  const prev = store[c.id] || {};
  store[c.id] = {...prev, star: !prev.star};
  saveFcStore(store);
  showFcCard();
}

function openSourceFromFc(){
  const c = fcState.cards[fcState.idx];
  closeFlashcards();
  openDoc(c.doc_stt);
}

function showFcResult(){
  const s = fcState;
  if(!s) return;
  const pct = s.rated ? Math.round((s.rated-s.again_count)*100/s.rated) : 0;
  let grade = pct>=85?'Xuất sắc 🏆':(pct>=70?'Tốt 💪':(pct>=50?'Khá 📚':'Cần ôn thêm 🔁'));
  document.getElementById('fc-content').innerHTML = `
    <div class="quiz-result">
      <div class="score">${s.rated}/${s.cards.length}</div>
      <div class="pct">Đã chấm · ${s.again_count} lần "lại học" · ${s.easy_count} "quá dễ"</div>
      <div class="grade">${grade}</div>
      <div style="font-size:13px;color:var(--muted);margin:20px auto;max-width:480px;line-height:1.7">
        Thẻ "Lại học" sẽ quay lại trong 10 phút.
        Thẻ "Khó/Dễ/Quá dễ" lịch lại sau 1/3/7 ngày (SRS).
        Quay lại mai để ôn các thẻ đến hạn.
      </div>
      <div class="review-btns">
        <button class="btn" onclick="showFcSetup()">🔄 Học bộ khác</button>
        <button class="btn secondary" onclick="closeFlashcards()">Đóng</button>
      </div>
    </div>
  `;
}

// Keyboard shortcuts for flashcards
document.addEventListener('keydown', e=>{
  if(!document.getElementById('fc-overlay').classList.contains('show')) return;
  // Don't intercept if typing in input/select
  if(['INPUT','SELECT','TEXTAREA'].includes(document.activeElement?.tagName)) return;
  if(e.key === ' '){ e.preventDefault(); flipFc(); }
  else if(e.key === 'ArrowLeft' || e.key === 'PageUp'){ e.preventDefault(); goFcPrev(); }
  else if(e.key === 'ArrowRight' || e.key === 'PageDown'){ e.preventDefault(); goFcNext(); }
  else if(fcState && fcState.flipped){
    if(e.key === '1') rateFc('again');
    else if(e.key === '2') rateFc('hard');
    else if(e.key === '3') rateFc('good');
    else if(e.key === '4') rateFc('easy');
  }
});

init();
</script>
</body>
</html>
'''

data_json = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
html_out = HTML.replace('__DATA_JSON__', data_json)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_out)

size = os.path.getsize('index.html')
print(f'Built index.html ({size:,} bytes / {size/1024/1024:.1f} MB)')
print(f'  - {len(data["docs"])} documents')
print(f'  - {sum(len(d.get("keynotes",[])) for d in data["docs"])} keynotes')
print(f'  - {sum(len(d.get("questions",[])) for d in data["docs"])} BTC questions linked')
print(f'  - {len(data.get("topic_overviews",{}))} topic overviews')
