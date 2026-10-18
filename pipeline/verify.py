import hashlib, re
from trending import domain
RISK=re.compile(r"\b(killed|dead|death toll|casualt\w*|massacre|shooting|terror\w*|explosion|arrest(ed)?|accused|alleg\w+|rape|assassinat\w+|bomb\w*)\b",re.I)
def verify(cl,min_sources=2):
    seen,doms,reasons=set(),set(),[]
    for i in cl:
        h=hashlib.sha1(i["summary"].lower().encode()).hexdigest()
        if h in seen: continue  # syndicated copy is not independent
        seen.add(h); doms.add(domain(i["link"]))
    if len(doms)<min_sources: reasons.append(f"only {len(doms)} independent source(s)")
    if any(RISK.search(i["title"]+" "+i["summary"]) for i in cl): reasons.append("high-risk topic: manual review")
    return {"independent":len(doms),"passed":not reasons,"reasons":reasons}
