import re
STOP={"the","and","for","with","from","that","this","are","was","has","have","into","over","after","says","said"}
def tokens(t): return {w for w in re.findall(r"[a-z0-9]+",t.lower()) if len(w)>2 and w not in STOP}
def sim(a,b):
    x,y=tokens(a),tokens(b)
    return len(x&y)/len(x|y) if x and y else 0.0
def group(items,th=0.5):
    gs=[]
    for it in sorted(items,key=lambda i:-i["ts"]):
        for g in gs:
            if sim(it["title"],g[0]["title"])>=th: g.append(it); break
        else: gs.append([it])
    return gs
