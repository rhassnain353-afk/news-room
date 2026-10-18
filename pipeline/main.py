import hashlib, json, os, sys, time, datetime as dt
import firebase_admin
from firebase_admin import credentials, firestore
from google.api_core.exceptions import AlreadyExists
from config import DEFAULTS, CATEGORIES
from sources import fetch_source
from dedupe import group
from trending import score
from verify import verify
from gates import check
from gemini_writer import generate, QuotaExhausted
from publisher import slugify, write_site
ROOT=os.path.join(os.path.dirname(__file__),"..","site")
def main():
    firebase_admin.initialize_app(credentials.Certificate(json.loads(os.environ["FIREBASE_SERVICE_ACCOUNT"])))
    db=firestore.client(); SITE=os.environ["SITE_URL"].rstrip("/")
    s={**DEFAULTS,**(db.document("automationSettings/main").get().to_dict() or {})}
    if not s["enabled"]: print("kill switch ON: nothing published"); return
    lock=db.document("locks/pipeline")
    @firestore.transactional
    def take(tx):
        d=lock.get(transaction=tx)
        if d.exists and d.to_dict().get("until",0)>time.time(): return False
        tx.set(lock,{"until":time.time()+900}); return True
    if not take(db.transaction()): print("another run active"); return
    run=db.collection("jobRuns").document(); st={"status":"running","startedAt":firestore.SERVER_TIMESTAMP,"processed":0,"published":0,"rejected":0,"errors":[]}
    run.set(st)
    try:
        items=[]
        for d in db.collection("sources").where("enabled","==",True).stream():
            src=d.to_dict()
            try: items+=fetch_source(src,s["maxItemsPerSource"]); d.reference.update({"lastSuccess":firestore.SERVER_TIMESTAMP,"lastError":None})
            except Exception as e: d.reference.update({"lastError":str(e)[:200]}); st["errors"].append(f"{src.get('name')}: {str(e)[:100]}")
        existing=[a.to_dict().get("headline","") for a in db.collection("articles").order_by("publishedAt",direction=firestore.Query.DESCENDING).limit(200).stream()]
        ranked=sorted(((score(c,s["weights"]),c) for c in group(items)),key=lambda x:-x[0]["score"])
        for sc,cl in ranked:
            if st["published"]>=s["maxArticlesPerRun"] or sc["score"]<s["minTrendScore"]: break
            st["processed"]+=1; lead=cl[0]; did=hashlib.sha1(lead["link"].encode()).hexdigest()[:24]
            ver=verify(cl,s["minIndependentSources"])
            base={"verification":ver,"trending":sc,"createdAt":firestore.SERVER_TIMESTAMP}
            if not ver["passed"]:
                st["rejected"]+=1
                try: db.collection("verificationReports").document(did).create({**base,"headline":lead["title"],"decision":"quarantined"})
                except AlreadyExists: pass
                continue
            try: art=generate(cl,s)
            except QuotaExhausted: st["errors"].append("Gemini quota exhausted; stopping AI work"); break
            except Exception as e: st["errors"].append(str(e)[:100]); continue
            ok,why=check(art,cl,ver,s,existing)
            now=dt.datetime.now(dt.timezone.utc)
            doc={**base,**art,"slug":slugify(art["headline"])+"-"+did[:6],"status":"published" if ok else "draft","needsReview":not ok,"gateReasons":why,
                 "publishedAt":firestore.SERVER_TIMESTAMP,"publishedAtIso":now.isoformat(),"imageUrl":"","aiGenerated":True,"revision":1}
            try: db.collection("articles").document(did).create(doc)  # create() = idempotent, never overwrites
            except AlreadyExists: continue
            if ok: st["published"]+=1; existing.append(art["headline"])
            else: st["rejected"]+=1
        pub=[]
        for a in db.collection("articles").where("status","==","published").order_by("publishedAt",direction=firestore.Query.DESCENDING).limit(500).stream():
            x=a.to_dict()
            if x.get("publishedAtIso"): pub.append(x)
        write_site(pub,SITE,ROOT)
        for r in db.collection("runRequests").where("handled","==",False).limit(10).stream(): r.reference.update({"handled":True,"runId":run.id})
        st["status"]="succeeded" if not st["errors"] else "partially_succeeded"
    except Exception as e: st["status"]="failed"; st["errors"].append(str(e)[:200])
    finally:
        st["endedAt"]=firestore.SERVER_TIMESTAMP; run.set(st); lock.delete()
    print(st["status"],st["published"],"published",st["errors"])
if __name__=="__main__": main()
