import html, re, time, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime
from security import safe_fetch, reject_dtd
def _txt(s,n): return html.unescape(re.sub(r"<[^>]*>"," ",s or "")).strip()[:n]
def _ts(s):
    try: return parsedate_to_datetime(s).timestamp()
    except Exception:
        try: return datetime.fromisoformat((s or "").replace("Z","+00:00")).timestamp()
        except Exception: return None
def parse_feed(data,limit=20,now=None):
    reject_dtd(data); now=now or time.time(); out=[]
    for e in ET.fromstring(data).iter():
        if e.tag.split("}")[-1] not in("item","entry"): continue
        def g(*ns):  # NB: Element truthiness is False when it has no children, so never use `or`
            return next((c for c in e if c.tag.split("}")[-1] in ns),None)
        t,l,d,p=g("title"),g("link"),g("description","summary"),g("pubDate","published","updated")
        link=(l.get("href") or l.text or "").strip() if l is not None else ""
        ts=_ts(p.text) if p is not None else None
        if not(link.startswith(("http://","https://")) and t is not None and ts): continue
        if ts>now+3600: continue  # bad/future timestamp
        out.append({"title":_txt(t.text,200),"summary":_txt(d.text if d is not None else "",600),"link":link[:500],"ts":ts})
        if len(out)>=limit: break
    return out
def fetch_source(src,limit=20):
    items=parse_feed(safe_fetch(src["url"]),limit)
    for i in items: i.update(reliability=src.get("reliability",0.5),category=src.get("category"),categoryWeight=src.get("categoryWeight",0.5))
    return items
