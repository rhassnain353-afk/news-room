import time
from urllib.parse import urlparse
def domain(u):
    p=(urlparse(u).hostname or "").lower().split(".")
    return ".".join(p[-2:]) if len(p)>=2 else ".".join(p)
def score(cl,w,now=None):
    now=now or time.time(); n=len(cl)
    c={"recency":0.5**(max(0,now-max(i["ts"] for i in cl))/21600),
       "sources":min(len({domain(i["link"]) for i in cl}),5)/5,
       "reliability":sum(i.get("reliability",.5) for i in cl)/n,
       "growth":sum(1 for i in cl if now-i["ts"]<7200)/n,
       "category":sum(i.get("categoryWeight",.5) for i in cl)/n}
    return {"score":round(sum(c[k]*w[k] for k in c)/sum(w.values()),4),"components":c}
