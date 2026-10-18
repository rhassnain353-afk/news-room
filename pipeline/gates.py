import re
from dedupe import sim
CLICK=re.compile(r"(you won't believe|shocking|must see|this one trick|gone wrong)",re.I)
def check(a,cl,ver,s,existing):
    r=list(ver["reasons"])
    body=" ".join(p for x in a["sections"] for p in x["paragraphs"])
    if len(body.split())<s["minBodyWords"]: r.append("body too short")
    links={i["link"] for i in cl}
    if any(u not in links for u in a["sources"]): r.append("source not in verified cluster (possible fabrication)")
    src=" ".join(i["title"]+" "+i["summary"] for i in cl).lower()
    for q in re.findall(r'["\u201c]([^"\u201d]{12,})["\u201d]',body):
        if q.lower() not in src: r.append("quote not found in sources")
    if CLICK.search(a["headline"]): r.append("clickbait headline")
    if any(sim(a["headline"],t)>=0.6 for t in existing): r.append("duplicate of existing article")
    return (not r,r)
