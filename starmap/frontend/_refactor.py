#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Refactor index.html to match the wireframe layout:
- Top bar: logo + search + icons + 24h toggle
- Left 40%: info bar + search + scene tags + route + spots + user shares
- Right 60%: map with popup cards
- Settings panel: click toggle (not hover)
"""

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ============================================================
# STEP 1: Replace the entire <style> block
# ============================================================
style_start = html.find("<style>")
style_end = html.find("</style>") + len("</style>")
old_style = html[style_start:style_end]

new_style = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#f5f5f0;--surface:#fff;--surface2:#f0f0eb;--surface3:#e8e8e3;
  --border:#e0ddd5;--border2:#d0cdc5;
  --text:#1a1a1a;--text2:#666;--text3:#999;
  --primary:#2a6df0;--primary-soft:rgba(42,109,240,.1);--primary-glow:rgba(42,109,240,.25);
  --green:#22c55e;--green-soft:rgba(34,197,94,.1);
  --yellow:#f59e0b;--yellow-soft:rgba(245,158,11,.1);
  --red:#ef4444;--red-soft:rgba(239,68,68,.1);
  --purple:#8b5cf6;--purple-soft:rgba(139,92,246,.1);
  --orange:#f97316;--orange-soft:rgba(249,115,22,.1);
  --r:12px;--r-sm:8px;--r-lg:18px;
  --shadow-sm:0 1px 3px rgba(0,0,0,.08);
  --shadow-md:0 4px 12px rgba(0,0,0,.1);
  --shadow-lg:0 12px 32px rgba(0,0,0,.15);
  --topbar-bg:#1e1e2e;--topbar-text:#e0e0e0;--topbar-text2:#888;
  --topbar-border:rgba(255,255,255,.08);
}
body{background:var(--bg);color:var(--text);font-family:'Inter','Noto Sans SC',-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif;height:100vh;overflow:hidden;display:flex;flex-direction:column;-webkit-font-smoothing:antialiased;letter-spacing:-.012em;font-size:14px;font-weight:400}

/* ── topbar ── */
.topbar{height:52px;background:var(--topbar-bg);display:flex;align-items:center;padding:0 20px;gap:12px;z-index:1000;flex-shrink:0}
.logo{font-size:15px;font-weight:700;letter-spacing:-.4px;color:#fff;white-space:nowrap;display:flex;align-items:center;gap:8px}
.logo-dot{width:8px;height:8px;border-radius:50%;background:var(--green);flex-shrink:0}
.search-wrap{flex:0 1 280px;position:relative}
.search-wrap input{width:100%;padding:7px 34px 7px 14px;border-radius:8px;border:1px solid var(--topbar-border);background:rgba(255,255,255,.08);color:#fff;font-size:13px;outline:none;transition:all .2s;font-family:inherit}
.search-wrap input::placeholder{color:rgba(255,255,255,.3)}
.search-wrap input:focus{border-color:rgba(255,255,255,.2);background:rgba(255,255,255,.12)}
.search-icon{position:absolute;right:10px;top:50%;transform:translateY(-50%);color:rgba(255,255,255,.3);cursor:pointer;font-size:15px;user-select:none;line-height:1}
#searchDrop{position:absolute;top:calc(100% + 6px);left:0;right:0;background:#fff;border:1px solid var(--border);border-radius:var(--r);max-height:300px;overflow-y:auto;z-index:2000;display:none;box-shadow:var(--shadow-lg)}
.sr-item{padding:10px 14px;cursor:pointer;border-bottom:1px solid var(--border);transition:background .12s;display:flex;align-items:center;gap:10px}
.sr-item:last-child{border-bottom:none}
.sr-item:hover,.sr-item.sel{background:var(--surface2)}
.sr-name{font-size:13px;font-weight:600;color:var(--text)}
.sr-addr{font-size:11px;color:var(--text3);margin-top:2px}

/* topbar icons */
.topbar-right{display:flex;gap:4px;align-items:center;margin-left:auto}
.icon-btn{width:34px;height:34px;border:1px solid var(--topbar-border);border-radius:8px;background:rgba(255,255,255,.06);color:var(--topbar-text2);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:14px;position:relative;flex-shrink:0;user-select:none;transition:all .15s}
.icon-btn:hover{background:rgba(255,255,255,.12);color:var(--topbar-text)}
.icon-btn:active{transform:scale(.93)}
.icon-btn.active{border-color:var(--primary);color:var(--primary);background:rgba(42,109,240,.15)}
.topbar-label{font-size:12px;color:var(--topbar-text2);margin-left:4px;white-space:nowrap}

/* toggle in topbar */
.toggle{width:36px;height:20px;border-radius:10px;background:rgba(255,255,255,.15);cursor:pointer;position:relative;transition:background .25s;border:0;flex-shrink:0}
.toggle.on{background:var(--green)}
.toggle::after{content:"";position:absolute;width:14px;height:14px;border-radius:50%;background:#fff;top:3px;left:3px;transition:left .25s;box-shadow:0 1px 3px rgba(0,0,0,.2)}
.toggle.on::after{left:19px}

/* dropdown menus */
.hov-wrap{position:relative}
.hov-bridge{position:absolute;top:100%;left:0;right:0;height:8px;z-index:2999}
.hov-wrap .hov-drop{position:absolute;top:calc(100% + 4px);right:0;background:#fff;border:1px solid var(--border);border-radius:var(--r);padding:6px;z-index:3000;display:none!important;box-shadow:var(--shadow-lg);min-width:230px;max-height:80vh;overflow-y:auto}
.hov-wrap.open .hov-bridge,.hov-wrap.open .hov-drop{display:block!important}
.dd-title{font-size:10px;font-weight:600;color:var(--text3);text-transform:uppercase;letter-spacing:.8px;margin-bottom:6px;padding:2px 8px}
.dd-item{display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:8px;cursor:pointer;font-size:13px;font-weight:400;transition:background .12s;color:var(--text);position:relative}
.dd-item:hover{background:var(--surface2)}
.dd-arrow{margin-left:auto;color:var(--text3);font-size:12px}
.dd-sep{height:1px;background:var(--border);margin:4px 0}
.dd-row{display:flex;justify-content:space-between;align-items:center;padding:8px 10px;gap:10px;border-radius:8px}
.dd-row:hover{background:var(--surface2)}
.dd-label{font-size:13px;font-weight:400}
.dd-btn{width:100%;padding:7px 8px;border-radius:8px;border:none;background:var(--surface2);color:var(--text2);cursor:pointer;font-size:12px;font-weight:400;margin-top:4px;transition:background .15s;text-align:left;font-family:inherit}
.dd-btn:hover{background:var(--surface3)}
.dd-btn.danger{color:var(--red)}
.submenu{position:absolute;right:calc(100% + 8px);top:0;background:#fff;border:1px solid var(--border);border-radius:var(--r);padding:6px;min-width:170px;box-shadow:var(--shadow-lg);display:none;z-index:4000}
.dd-item:hover>.submenu{display:block}
.user-info-row{display:flex;align-items:center;gap:12px;padding:8px 8px 12px;border-bottom:1px solid var(--border);margin-bottom:6px}
.avatar{width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,var(--primary),var(--purple));display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:700;flex-shrink:0;overflow:hidden;color:#fff}
.avatar img{width:100%;height:100%;object-fit:cover;border-radius:50%}
.user-name{font-size:14px;font-weight:600}
.user-email{font-size:11px;color:var(--text3);margin-top:2px}

/* ── layout ── */
.main{flex:1;display:flex;overflow:hidden;position:relative}
#map{flex:1;height:100%;min-width:0;order:2}

/* ── left panel ── */
#sidePanel{width:40%;min-width:340px;max-width:480px;background:var(--surface);border-right:1px solid var(--border);display:flex;flex-direction:column;overflow:hidden;flex-shrink:0;order:1;transition:width .3s ease;position:relative}
#sidePanel.collapsed{width:0;min-width:0;border-right:none}
#panelTab{position:absolute;right:-24px;top:50%;transform:translateY(-50%);width:24px;height:48px;background:var(--surface);border:1px solid var(--border);border-left:none;border-radius:0 8px 8px 0;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:10px;color:var(--text3);z-index:10;opacity:0;transition:opacity .2s}
#sidePanel:hover #panelTab,#panelTab:hover{opacity:1}

/* info bar */
.info-bar{padding:10px 16px;background:var(--surface2);border-bottom:1px solid var(--border);display:flex;align-items:center;gap:8px;flex-shrink:0;font-size:12px;color:var(--text2)}
.info-bar svg{flex-shrink:0}

/* left panel search */
.lp-search{padding:12px 16px 8px;flex-shrink:0}
.lp-search-input{width:100%;padding:9px 14px;border-radius:8px;border:1px solid var(--border);background:var(--surface);color:var(--text);font-size:13px;outline:none;transition:border-color .2s;font-family:inherit}
.lp-search-input:focus{border-color:var(--primary)}
.lp-search-input::placeholder{color:var(--text3)}

/* scene tags */
.scene-tags{padding:0 16px 12px;display:flex;flex-wrap:wrap;gap:6px;flex-shrink:0}
.scene-tag{padding:6px 14px;border-radius:6px;border:1px solid var(--border);background:var(--surface);color:var(--text2);font-size:12px;font-weight:500;cursor:pointer;transition:all .15s;font-family:inherit}
.scene-tag:hover{border-color:var(--primary);color:var(--primary)}
.scene-tag.on{border-color:var(--primary);color:#fff;background:var(--primary)}

/* scrollable content */
.lp-scroll{flex:1;overflow-y:auto;padding:0 16px 24px}

/* section titles */
.sec-title{font-size:14px;font-weight:700;color:var(--text);margin:16px 0 10px;display:flex;align-items:center;gap:6px}

/* route timeline */
.route-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);overflow:hidden;margin-bottom:12px}
.route-item{display:flex;align-items:flex-start;gap:10px;padding:10px 14px;border-bottom:1px solid var(--surface2);font-size:13px}
.route-item:last-child{border-bottom:none}
.route-time{font-weight:700;color:var(--text);white-space:nowrap;min-width:42px;font-variant-numeric:tabular-nums}
.route-name{font-weight:600;color:var(--text)}
.route-tag{font-size:11px;color:var(--orange);font-weight:500}
.route-dur{font-size:12px;color:var(--text3);margin-left:auto;white-space:nowrap}

/* spot list */
.spot-card{display:flex;align-items:center;gap:12px;padding:12px;background:var(--surface);border:1px solid var(--border);border-radius:var(--r);margin-bottom:8px;cursor:pointer;transition:all .15s}
.spot-card:hover{border-color:var(--primary);box-shadow:var(--shadow-sm)}
.spot-thumb{width:64px;height:48px;border-radius:6px;background:var(--surface2);flex-shrink:0;overflow:hidden;display:flex;align-items:center;justify-content:center}
.spot-thumb img{width:100%;height:100%;object-fit:cover}
.spot-thumb svg{color:var(--text3)}
.spot-info{flex:1;min-width:0}
.spot-name{font-size:13px;font-weight:600;color:var(--text)}
.spot-stars{font-size:11px;color:var(--yellow);margin-top:2px}
.spot-score{font-size:14px;font-weight:700;color:var(--text2);flex-shrink:0}

/* user shares */
.share-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin-bottom:12px}
.share-item{border-radius:var(--r);overflow:hidden;background:var(--surface2);aspect-ratio:4/3;position:relative;cursor:pointer}
.share-item img{width:100%;height:100%;object-fit:cover}
.share-item-label{position:absolute;bottom:0;left:0;right:0;padding:6px 8px;background:linear-gradient(transparent,rgba(0,0,0,.5));color:#fff;font-size:11px;font-weight:500}
.share-item-likes{position:absolute;bottom:6px;right:8px;color:#fff;font-size:11px;display:flex;align-items:center;gap:3px}

/* ── map popup card ── */
.map-popup{background:#fff;border-radius:var(--r);padding:14px;min-width:240px;max-width:300px;box-shadow:var(--shadow-lg);border:1px solid var(--border)}
.map-popup-title{font-size:14px;font-weight:700;margin-bottom:10px;color:var(--text)}
.map-popup-img{width:100%;height:120px;border-radius:8px;object-fit:cover;margin-bottom:10px;background:var(--surface2)}
.map-popup-row{font-size:12px;color:var(--text2);margin-bottom:4px}
.map-popup-row b{color:var(--text);font-weight:600}

/* ── old panel stuff (keep for data cards) ── */
.panel-header{padding:12px 16px 10px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:8px;flex-shrink:0;display:none}
.panel-tabs{display:flex;gap:2px;flex:1;background:var(--surface2);border-radius:8px;padding:3px}
.ptab{flex:1;padding:5px 10px;border-radius:6px;font-size:12px;font-weight:500;cursor:pointer;color:var(--text3);transition:all .15s;border:0;background:none;white-space:nowrap;font-family:inherit}
.ptab.active{background:var(--surface);color:var(--text);box-shadow:var(--shadow-sm)}
.card-nav{display:none}
.panel-body{display:none}
#cardPages{display:flex;height:100%;transition:transform .3s ease}
.card-page{min-width:100%;width:100%;height:100%;overflow-y:auto;padding:12px;flex-shrink:0}

/* data cards (reused in popup) */
.pt-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);overflow:hidden;margin-bottom:10px;box-shadow:var(--shadow-sm)}
.pt-card-head{padding:12px 14px;display:flex;align-items:flex-start;justify-content:space-between;border-bottom:1px solid var(--surface2);gap:8px}
.pt-name{font-size:14px;font-weight:700;line-height:1.4;color:var(--text)}
.pt-coord{font-size:11px;color:var(--text3);margin-top:2px;font-variant-numeric:tabular-nums}
.pt-actions{display:flex;gap:3px;flex-shrink:0}
.pt-act{width:28px;height:28px;border-radius:6px;border:1px solid var(--border);background:none;color:var(--text3);cursor:pointer;font-size:12px;display:flex;align-items:center;justify-content:center;transition:all .15s}
.pt-act:hover{background:var(--surface2);color:var(--text2)}
.pt-act.del:hover{color:var(--red);border-color:rgba(239,68,68,.3);background:var(--red-soft)}
.pt-act.fav-on{color:var(--yellow);border-color:rgba(245,158,11,.3);background:var(--yellow-soft)}
.pt-body{padding:12px}
.data-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px}
.data-cell{background:var(--surface2);border-radius:var(--r-sm);padding:10px 12px;border:1px solid var(--border)}
.dc-label{font-size:10px;font-weight:600;color:var(--text3);text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px}
.dc-val{font-size:22px;font-weight:700;line-height:1;font-variant-numeric:tabular-nums;color:var(--text)}
.dc-sub{font-size:11px;color:var(--text3);margin-top:4px}
.dc-unit{font-size:12px;color:var(--text3);margin-left:2px;font-weight:400}
.dc-val.good{color:var(--green)}.dc-val.warn{color:var(--yellow)}.dc-val.bad{color:var(--red)}.dc-val.purple{color:var(--purple)}
.timeline{margin-bottom:10px}
.tl-label{font-size:11px;font-weight:500;color:var(--text2);margin-bottom:6px;display:flex;align-items:center;gap:5px}
.tl-bar{height:4px;border-radius:2px;background:var(--surface3);position:relative;overflow:hidden;margin-bottom:5px}
.tl-fill{height:100%;border-radius:2px;position:absolute}
.tl-sun{background:linear-gradient(90deg,var(--orange),var(--yellow))}
.tl-times{display:flex;justify-content:space-between;font-size:11px;color:var(--text3);font-variant-numeric:tabular-nums}
.bortle-bar{display:flex;gap:2px;margin:6px 0 4px}
.bortle-seg{flex:1;height:4px;border-radius:2px}
.bortle-label{font-size:11px;color:var(--text3);display:flex;justify-content:space-between}

/* ── modals ── */
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.4);backdrop-filter:blur(8px);z-index:5000;display:none;align-items:center;justify-content:center}
.modal-overlay.open{display:flex}
.modal{background:#fff;border:1px solid var(--border);border-radius:var(--r-lg);padding:28px;width:100%;max-width:400px;box-shadow:var(--shadow-lg);position:relative;max-height:90vh;overflow-y:auto}
.modal-title{font-size:18px;font-weight:700;margin-bottom:20px;color:var(--text)}
.modal-tabs{display:flex;gap:3px;margin-bottom:16px;background:var(--surface2);border-radius:8px;padding:3px}
.modal-tab{flex:1;padding:7px;border-radius:6px;border:0;background:none;color:var(--text3);cursor:pointer;font-size:13px;font-weight:500;transition:all .15s;font-family:inherit}
.modal-tab.active{background:var(--surface);color:var(--text);box-shadow:var(--shadow-sm)}
.form-group{margin-bottom:14px}
.form-label{font-size:11px;font-weight:600;color:var(--text2);margin-bottom:6px;display:block}
.form-input{width:100%;padding:10px 14px;border-radius:8px;border:1px solid var(--border);background:var(--surface);color:var(--text);font-size:14px;outline:none;transition:border-color .2s;font-family:inherit}
.form-input:focus{border-color:var(--primary)}
.form-input::placeholder{color:var(--text3)}
.form-row{display:flex;gap:8px}
.form-row .form-input{flex:1}
.send-code-btn{padding:10px 13px;border-radius:8px;border:1px solid var(--border);background:var(--surface2);color:var(--primary);cursor:pointer;font-size:12px;font-weight:600;white-space:nowrap;transition:all .15s;flex-shrink:0;font-family:inherit}
.send-code-btn:hover{background:var(--surface3)}
.send-code-btn:disabled{color:var(--text3);cursor:not-allowed}
.submit-btn{width:100%;padding:12px;border-radius:10px;border:0;background:var(--primary);color:#fff;font-size:14px;font-weight:600;cursor:pointer;margin-top:8px;transition:opacity .15s;font-family:inherit}
.submit-btn:hover{opacity:.9}
.submit-btn:active{transform:scale(.98)}
.form-error{font-size:12px;color:var(--red);margin-top:8px;min-height:16px}
.form-switch{font-size:12px;color:var(--text3);text-align:center;margin-top:12px}
.form-switch a{color:var(--primary);cursor:pointer;font-weight:500}
.modal-close{position:absolute;top:16px;right:16px;width:28px;height:28px;border-radius:50%;border:none;background:var(--surface2);color:var(--text2);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:12px;transition:all .15s}
.modal-close:hover{background:var(--surface3);color:var(--text)}
.profile-avatar-wrap{display:flex;flex-direction:column;align-items:center;margin-bottom:20px}
.profile-avatar{width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,var(--primary),var(--purple));display:flex;align-items:center;justify-content:center;font-size:34px;font-weight:700;margin-bottom:10px;overflow:hidden;flex-shrink:0;color:#fff}
.profile-avatar img{width:80px;height:80px;border-radius:50%;object-fit:cover;display:block}
.profile-avatar-hint{font-size:11px;color:var(--text3)}
.fstar{font-size:24px;cursor:pointer;opacity:.25;transition:opacity .15s;color:var(--yellow)}
.fstar.on{opacity:1}
.hist-item{display:flex;align-items:center;gap:10px;padding:10px;border-bottom:1px solid var(--surface2);cursor:pointer;font-size:13px;transition:background .12s;border-radius:8px}
.hist-item:hover{background:var(--surface2)}
.avatar-upload-wrap{position:relative;display:inline-block;cursor:pointer}
.avatar-upload-wrap:hover .avatar-overlay{opacity:1}
.avatar-overlay{position:absolute;inset:0;border-radius:50%;background:rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;opacity:0;transition:opacity .2s;font-size:10px;color:#fff;font-weight:600}
.cropper-view-box,.cropper-face{border-radius:50%}
.cropper-view-box{outline:2px solid var(--primary)}

/* share modal */
.share-row-btn{width:100%;display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:8px;border:none;background:none;color:var(--text);cursor:pointer;font-size:13px;font-family:inherit;transition:background .12s;text-align:left}
.share-row-btn:hover{background:var(--surface2)}
.share-row-icon{width:28px;height:28px;border-radius:8px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.share-row-label{flex:1;font-weight:500}
.share-row-arrow{color:var(--text3);font-size:16px;line-height:1}

/* toast */
#toast{position:fixed;bottom:32px;left:50%;transform:translateX(-50%) translateY(16px);background:#fff;border:1px solid var(--border);border-radius:20px;padding:10px 20px;font-size:13px;font-weight:500;z-index:9999;opacity:0;transition:all .3s ease;pointer-events:none;white-space:nowrap;box-shadow:var(--shadow-md);color:var(--text)}
#toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
#toast.success{color:var(--green)}
#toast.error{color:var(--red)}
.spinner{display:inline-block;width:12px;height:12px;border:1.5px solid var(--border);border-top-color:var(--primary);border-radius:50%;animation:spin .7s linear infinite;vertical-align:middle;margin-right:5px}
@keyframes spin{to{transform:rotate(360deg)}}
.empty-state{text-align:center;padding:40px 16px;color:var(--text3)}
.empty-icon{font-size:36px;margin-bottom:12px;opacity:.5}
.empty-text{font-size:13px;line-height:1.8}
::-webkit-scrollbar{width:4px;height:4px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}

/* quick grid - hidden in new layout */
#quickGrid{display:none}

/* recommend panel */
#recommendPanel{display:none}
.style-chip{padding:5px 12px;border-radius:6px;border:1px solid var(--border);background:var(--surface);color:var(--text2);font-size:12px;font-weight:500;cursor:pointer;transition:all .15s;font-family:inherit}
.style-chip:hover{border-color:var(--primary);color:var(--primary)}
.style-chip.on{border-color:var(--primary);color:#fff;background:var(--primary)}
.rec-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:12px;margin-bottom:8px;cursor:pointer;transition:all .2s}
.rec-card:hover{border-color:var(--primary);box-shadow:var(--shadow-sm)}
.rec-card-top{display:flex;align-items:flex-start;justify-content:space-between;gap:8px;margin-bottom:8px}
.rec-card-name{font-size:13px;font-weight:600;flex:1}
.rec-match{display:flex;flex-direction:column;align-items:flex-end;flex-shrink:0}
.rec-match-num{font-size:18px;font-weight:700;line-height:1}
.rec-match-label{font-size:10px;color:var(--text3);margin-top:1px}
.rec-tags{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:8px}
.rec-tag{padding:2px 8px;border-radius:10px;font-size:11px;font-weight:500}
.rec-bar{height:3px;border-radius:2px;background:var(--surface3);overflow:hidden;margin-bottom:6px}
.rec-bar-fill{height:100%;border-radius:2px;transition:width .6s ease}
.rec-reason{font-size:11px;color:var(--text3);line-height:1.5}
.rec-coord{font-size:10px;color:var(--text3);margin-top:4px;font-variant-numeric:tabular-nums}

/* night overlay - disabled in light theme */
#nightOverlay{display:none}

/* animations */
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes popIn{from{opacity:0;transform:scale(.95)}to{opacity:1;transform:scale(1)}}
@keyframes markerDrop{0%{opacity:0;transform:scale(0) translateY(-10px)}60%{transform:scale(1.15) translateY(2px)}100%{opacity:1;transform:scale(1) translateY(0)}}
@keyframes markerPulse{0%{box-shadow:0 0 0 0 rgba(42,109,240,.5)}70%{box-shadow:0 0 0 10px rgba(42,109,240,0)}100%{box-shadow:0 0 0 0 rgba(42,109,240,0)}}
body{animation:fadeIn .3s ease both}
.modal{animation:popIn .2s ease both}
.spot-card{animation:fadeUp .25s ease both}
.spot-card:nth-child(1){animation-delay:.05s}
.spot-card:nth-child(2){animation-delay:.1s}
.spot-card:nth-child(3){animation-delay:.15s}

/* leaflet overrides for light theme */
.leaflet-popup-content-wrapper{background:#fff;border-radius:var(--r);box-shadow:var(--shadow-lg);border:1px solid var(--border);padding:0}
.leaflet-popup-content{margin:0;min-width:240px}
.leaflet-popup-tip{background:#fff;border:1px solid var(--border)}
.leaflet-popup-close-button{color:var(--text3)!important;font-size:18px!important;top:8px!important;right:8px!important}
</style>"""

html = html[:style_start] + new_style + html[style_end:]
print("1. Replaced style block")

# ============================================================
# STEP 2: Replace the topbar HTML
# ============================================================
topbar_start = html.find('<!-- topbar -->')
topbar_end = html.find('<!-- modals -->')
old_topbar = html[topbar_start:topbar_end]

new_topbar = """<!-- topbar -->
<div class="topbar">
  <div class="logo"><div class="logo-dot"></div>Galaxmeet</div>
  <div class="search-wrap">
    <input id="searchInput" placeholder="\u8f93\u5165\u5730\u540d\u5373\u53ef\u641c\u7d22\u2026" autocomplete="off" spellcheck="false"/>
    <span class="search-icon" id="btnSearch">\u2315</span>
    <div id="searchDrop"></div>
  </div>
  <div class="topbar-right">
    <button class="icon-btn" id="btnLocate" title="\u5b9a\u4f4d\u5230\u6211">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><circle cx="12" cy="12" r="8" stroke-dasharray="3 2"/><line x1="12" y1="2" x2="12" y2="5"/><line x1="12" y1="19" x2="12" y2="22"/><line x1="2" y1="12" x2="5" y2="12"/><line x1="19" y1="12" x2="22" y2="12"/></svg>
    </button>
    <button class="icon-btn" id="btnLock" title="\u9501\u5b9a/\u89e3\u9501\u89c6\u89d2">
      <svg id="lockIcon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
    </button>
    <button class="icon-btn" title="\u6536\u85cf" onclick="openFavModal()">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l2.9 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l7.1-1.01L12 2z"/></svg>
    </button>
    <button class="icon-btn" title="\u5386\u53f2" onclick="openHistoryModal()">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
    </button>
    <div class="hov-wrap">
      <button class="icon-btn" title="\u8bbe\u7f6e">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
      </button>
      <div class="hov-bridge"></div>
      <div class="hov-drop" id="settingsPanel" style="min-width:220px">
        <div class="dd-title">\u663e\u793a\u8bbe\u7f6e</div>
        <div class="dd-row"><span class="dd-label">\u6e29\u5ea6 \u00b0F</span><button class="toggle" id="toggleUnit"></button></div>
        <div class="dd-row"><span class="dd-label">24\u5c0f\u65f6\u5236</span><button class="toggle on" id="toggle24h"></button></div>
        <div class="dd-row"><span class="dd-label">\u536b\u661f\u6807\u6ce8\u5c42</span><button class="toggle on" id="toggleLabel"></button></div>
        <div class="dd-sep"></div>
        <button class="dd-btn danger" id="btnClearAll">\u6e05\u7a7a\u6240\u6709\u5730\u70b9</button>
      </div>
    </div>
    <span class="topbar-label">24\u5c0f\u65f6\u5236</span>
    <button class="toggle on" id="toggle24hTopbar"></button>
    <div class="hov-wrap">
      <button class="icon-btn" id="btnUser" title="\u8d26\u53f7" style="width:34px;height:34px">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg>
      </button>
      <div class="hov-bridge"></div>
      <div class="hov-drop" id="userMenu" style="min-width:220px"></div>
    </div>
  </div>
</div>

"""

html = html[:topbar_start] + new_topbar + html[topbar_end:]
print("2. Replaced topbar HTML")

# ============================================================
# STEP 3: Replace the main layout (side panel + map)
# ============================================================
main_start = html.find('<!-- main -->')
main_end = html.find('<div id="toast">')
old_main = html[main_start:main_end]

new_main = """<!-- main -->
<div class="main">
  <div id="map"></div>

  <!-- left panel -->
  <div id="sidePanel">
    <div id="panelTab">\u25b6</div>

    <!-- info bar -->
    <div class="info-bar" id="infoBar">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
      <span id="infoBarText">\u5f53\u524d\u573a\u666f\uff1a\u672a\u9009\u62e9 | \u4eca\u65e5\u62cd\u6444\u6307\u6570\uff1a-- </span>
    </div>

    <!-- search in panel -->
    <div class="lp-search">
      <input class="lp-search-input" id="lpSearchInput" placeholder="\u641c\u7d22\u673a\u4f4d\u2026" autocomplete="off"/>
    </div>

    <!-- scene tags -->
    <div class="scene-tags" id="sceneTags">
      <button class="scene-tag on" data-scene="city">\u57ce\u5e02\u98ce\u5149</button>
      <button class="scene-tag" data-scene="star">\u661f\u7a7a\u94f6\u6cb3</button>
      <button class="scene-tag" data-scene="snow">\u51b0\u5ddd\u96ea\u5730</button>
      <button class="scene-tag" data-scene="ocean">\u6d77\u8fb9\u98ce\u5149</button>
    </div>

    <!-- scrollable content -->
    <div class="lp-scroll" id="lpScroll">

      <!-- route -->
      <div class="sec-title">\u63a8\u8350\u8def\u7ebf</div>
      <div class="route-card" id="routeCard">
        <div class="route-item">
          <span class="route-time">16:00</span>
          <span class="route-name">\u666f\u70b9A</span>
          <span style="flex:1"></span>
          <span style="font-size:12px;color:var(--text2)">\u66dd\u5149\u62cd\u6444</span>
          <span class="route-dur">30\u5206\u949f</span>
        </div>
        <div class="route-item">
          <span class="route-time">17:10</span>
          <span class="route-name">\u666f\u70b9B</span>
          <span class="route-tag" style="margin-left:6px">\u9ec4\u91d1\u65f6\u523b</span>
          <span style="flex:1"></span>
          <span class="route-dur">50\u5206\u949f</span>
        </div>
        <div class="route-item">
          <span class="route-time">18:30</span>
          <span class="route-name">\u666f\u70b9C</span>
          <span style="flex:1"></span>
          <span style="font-size:12px;color:var(--text2)">\u65e5\u8ff9\u62cd\u6444</span>
          <span class="route-dur">40\u5206\u949f</span>
        </div>
      </div>

      <!-- spots -->
      <div class="sec-title">\u70ed\u95e8\u666f\u70b9</div>
      <div id="spotList">
        <div class="spot-card">
          <div class="spot-thumb"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="2" width="20" height="20" rx="3"/><path d="M2 16l5-5 4 4 4-6 7 7"/></svg></div>
          <div class="spot-info"><div class="spot-name">\u666f\u70b9A</div><div class="spot-stars">\u2605\u2605\u2605\u2606\u2606</div></div>
          <div class="spot-score">\u8bc4\u5206: 84</div>
        </div>
        <div class="spot-card">
          <div class="spot-thumb"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="2" width="20" height="20" rx="3"/><path d="M2 16l5-5 4 4 4-6 7 7"/></svg></div>
          <div class="spot-info"><div class="spot-name">\u666f\u70b9B</div><div class="spot-stars">\u2605\u2605\u2605\u2606\u2606</div></div>
          <div class="spot-score">\u8bc4\u5206: 76</div>
        </div>
        <div class="spot-card">
          <div class="spot-thumb"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="2" width="20" height="20" rx="3"/><path d="M2 16l5-5 4 4 4-6 7 7"/></svg></div>
          <div class="spot-info"><div class="spot-name">\u666f\u70b9C</div><div class="spot-stars">\u2605\u2605\u2605\u2605\u2606</div></div>
          <div class="spot-score">\u8bc4\u5206: 88</div>
        </div>
      </div>

      <!-- user shares -->
      <div class="sec-title">\u7528\u6237\u5206\u4eab</div>
      <div class="share-grid" id="userShareGrid">
        <div class="share-item">
          <div style="width:100%;height:100%;background:var(--surface3);display:flex;align-items:center;justify-content:center;color:var(--text3);font-size:12px">\u7167\u72471</div>
        </div>
        <div class="share-item">
          <div style="width:100%;height:100%;background:var(--surface3);display:flex;align-items:center;justify-content:center;color:var(--text3);font-size:12px">\u7167\u72472</div>
        </div>
      </div>

    </div>

    <!-- hidden old panels for JS compatibility -->
    <div class="panel-header" style="display:none">
      <div class="panel-tabs">
        <button class="ptab active" data-tab="points">\u5730\u70b9\u4fe1\u606f</button>
        <button class="ptab" data-tab="recommend">\u667a\u80fd\u63a8\u8350</button>
      </div>
    </div>
    <div class="card-nav" id="cardNav" style="display:none">
      <button class="nav-arrow" id="navPrev">\u2039</button>
      <div style="display:flex;gap:5px;align-items:center" id="navDots"></div>
      <button class="nav-arrow" id="navNext">\u203a</button>
    </div>
    <div class="panel-body" style="display:none">
      <div id="cardPages">
        <div class="card-page" id="page-empty"></div>
      </div>
      <div id="recommendPanel" style="display:none">
        <div style="margin-bottom:14px">
          <div id="styleChips" style="display:flex;flex-wrap:wrap;gap:6px"></div>
        </div>
        <div id="recMatchCount"></div>
        <div id="recCards"></div>
      </div>
    </div>
  </div>
</div>
"""

html = html[:main_start] + new_main + html[main_end:]
print("3. Replaced main layout HTML")

# ============================================================
# STEP 4: Add new JS for left panel features + map popup
# ============================================================
# Insert before the closing </script> tag

close_script = html.rfind("</script>")

new_js = """

// ── 24h topbar toggle sync ──
(function(){
  var tb = document.getElementById("toggle24hTopbar");
  if(!tb) return;
  tb.addEventListener("click", function(){
    CFG.h24 = !CFG.h24;
    this.classList.toggle("on", CFG.h24);
    var other = document.getElementById("toggle24h");
    if(other) other.classList.toggle("on", CFG.h24);
    renderPoints();
    updateInfoBar();
  });
})();

// ── Scene tags ──
document.querySelectorAll(".scene-tag").forEach(function(btn){
  btn.addEventListener("click", function(){
    document.querySelectorAll(".scene-tag").forEach(function(b){ b.classList.remove("on"); });
    btn.classList.add("on");
    updateSpotList();
  });
});

// ── Info bar update ──
function updateInfoBar(){
  var el = document.getElementById("infoBarText");
  if(!el) return;
  var pt = _points[_curIdx];
  if(pt && pt.data){
    var d = pt.data;
    var scoreText = d.score >= 75 ? "\\u9002\\u5408\\u5546\\u666f" : d.score >= 50 ? "\\u4e00\\u822c" : "\\u4e0d\\u9002\\u5408";
    el.textContent = "\\u5f53\\u524d\\u573a\\u666f\\uff1a" + (pt.name||"\\u672a\\u77e5") + " | \\u4eca\\u65e5\\u62cd\\u6444\\u6307\\u6570\\uff1a" + d.score + " (" + scoreText + ")";
  }
}

// ── Update spot list from points ──
function updateSpotList(){
  var container = document.getElementById("spotList");
  if(!container) return;
  if(!_points.length || !_points.some(function(p){return p.data && !p.loading && !p.err;})){
    // keep default placeholder
    return;
  }
  var items = _points.filter(function(p){return p.data && !p.loading && !p.err;});
  container.innerHTML = items.map(function(pt, i){
    var d = pt.data;
    var stars = "";
    var rating = Math.round(d.score / 20);
    for(var s=0;s<5;s++) stars += s < rating ? "\\u2605" : "\\u2606";
    return '<div class="spot-card" onclick="map.setView(['+pt.lat+','+pt.lng+'],14);showMapPopup('+i+')">' +
      '<div class="spot-thumb"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="2" width="20" height="20" rx="3"/><path d="M2 16l5-5 4 4 4-6 7 7"/></svg></div>' +
      '<div class="spot-info"><div class="spot-name">' + escH(pt.name) + '</div><div class="spot-stars">' + stars + '</div></div>' +
      '<div class="spot-score">\\u8bc4\\u5206: ' + d.score + '</div></div>';
  }).join("");
}

// ── Update route from points ──
function updateRouteCard(){
  var container = document.getElementById("routeCard");
  if(!container) return;
  var items = _points.filter(function(p){return p.data && !p.loading && !p.err;});
  if(!items.length) return;
  // Sort by golden hour times
  container.innerHTML = items.slice(0,3).map(function(pt, i){
    var d = pt.data;
    var times = ["16:00","17:10","18:30"];
    var activities = ["\\u66dd\\u5149\\u62cd\\u6444","\\u9ec4\\u91d1\\u65f6\\u523b","\\u65e5\\u8ff9\\u62cd\\u6444"];
    var durations = ["30\\u5206\\u949f","50\\u5206\\u949f","40\\u5206\\u949f"];
    if(d.goldenPM){
      var t = new Date(d.goldenPM.start);
      times[i] = String(t.getHours()).padStart(2,"0") + ":" + String(t.getMinutes()).padStart(2,"0");
    }
    var tagHtml = i === 1 ? '<span class="route-tag" style="margin-left:6px">\\u9ec4\\u91d1\\u65f6\\u523b</span>' : '';
    return '<div class="route-item">' +
      '<span class="route-time">' + times[i] + '</span>' +
      '<span class="route-name">' + escH(pt.name).substring(0,8) + '</span>' +
      tagHtml +
      '<span style="flex:1"></span>' +
      '<span style="font-size:12px;color:var(--text2)">' + activities[i] + '</span>' +
      '<span class="route-dur">' + durations[i] + '</span></div>';
  }).join("");
}

// ── Map popup for spot click ──
function showMapPopup(idx){
  var pt = _points[idx];
  if(!pt || !pt.data) return;
  var d = pt.data;
  var content = '<div class="map-popup">' +
    '<div class="map-popup-title">\\u673a\\u4f4d ' + escH(pt.name).substring(0,10) + '</div>' +
    '<div class="map-popup-img" style="display:flex;align-items:center;justify-content:center;color:var(--text3);font-size:12px">\\u62cd\\u6444\\u9884\\u89c8</div>' +
    '<div class="map-popup-row"><b>\\u671d\\u5411\\uff1a</b>' + d.srDir + '</div>' +
    '<div class="map-popup-row"><b>\\u5efa\\u8bae\\uff1a</b>' + (d.score >= 75 ? "\\u9002\\u5408\\u62cd\\u6444\\u5915\\u9633" : d.score >= 50 ? "\\u5149\\u7ebf\\u4e00\\u822c\\uff0c\\u5efa\\u8bae\\u7b49\\u5f85" : "\\u4e0d\\u5efa\\u8bae\\u62cd\\u6444") + '</div>' +
    '</div>';
  L.popup({maxWidth:300,className:''})
    .setLatLng([pt.lat, pt.lng])
    .setContent(content)
    .openOn(map);
}

// ── Override renderPoints to also update left panel ──
var _origRenderPoints = renderPoints;
renderPoints = function(){
  _origRenderPoints();
  updateInfoBar();
  updateSpotList();
  updateRouteCard();
};

// ── Also show popup when map marker is clicked ──
var _origAddPoint = addPoint;
addPoint = function(pt){
  _origAddPoint(pt);
  // After adding, update left panel
  setTimeout(function(){
    updateInfoBar();
    updateSpotList();
    updateRouteCard();
  }, 100);
};

// ── Panel search filter ──
(function(){
  var lpInput = document.getElementById("lpSearchInput");
  if(!lpInput) return;
  lpInput.addEventListener("input", function(){
    var q = this.value.trim().toLowerCase();
    var cards = document.querySelectorAll(".spot-card");
    cards.forEach(function(card){
      var name = card.querySelector(".spot-name");
      if(!name) return;
      card.style.display = (!q || name.textContent.toLowerCase().includes(q)) ? "" : "none";
    });
  });
})();

// ── Make markers clickable to show popup ──
var _origMarkerAdd = null;
(function patchMarkerClick(){
  // We'll add click handlers in the addPoint override
  var oldAddPoint2 = addPoint;
  addPoint = function(pt){
    oldAddPoint2(pt);
    var idx = _points.length - 1;
    var mk = _markers[idx];
    if(mk){
      mk.on("click", function(e){
        L.DomEvent.stopPropagation(e);
        showMapPopup(idx);
      });
    }
  };
})();

"""

html = html[:close_script] + new_js + html[close_script:]
print("4. Added new JS for left panel + map popup")

# ============================================================
# STEP 5: Fix the history button missing closing tag
# ============================================================
# The original had a missing </button> on the history icon-btn
# This was already in the original code, let's make sure it's clean

# ============================================================
# STEP 6: Write the file
# ============================================================
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\nDone! Layout refactored to match wireframe.")
print(f"File size: {len(html)} chars")
