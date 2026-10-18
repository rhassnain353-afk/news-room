import sys,os,time,unittest
sys.path.insert(0,os.path.join(os.path.dirname(__file__),".."))
from dedupe import group; from trending import score; from verify import verify; from gates import check
from security import check_url,reject_dtd; from sources import parse_feed
from gemini_writer import validate
W={"recency":.3,"sources":.3,"reliability":.15,"growth":.1,"category":.15}
def it(t,l,s="s",ts=None): return {"title":t,"link":l,"summary":s,"ts":ts or time.time()}
class T(unittest.TestCase):
    def test_group(self):
        g=group([it("Pakistan wins cricket series against Australia","https://a.com/1"),it("Pakistan wins cricket series over Australia","https://b.com/2"),it("Gold price falls sharply today","https://c.com/3")])
        self.assertEqual(sorted(map(len,g)),[1,2])
    def test_trend(self):
        a=score([it("x","https://a.com/1"),it("x","https://b.com/1")],W); b=score([it("x","https://a.com/1")],W)
        self.assertGreater(a["score"],b["score"])
        old=score([it("x","https://a.com/1",ts=time.time()-86400*3)],W); self.assertLess(old["score"],b["score"])
    def test_verify(self):
        self.assertFalse(verify([it("a","https://a.com/1","same text"),it("a","https://b.com/1","same text")])["passed"])
        self.assertTrue(verify([it("a","https://a.com/1","one"),it("a","https://b.com/1","two")])["passed"])
        self.assertFalse(verify([it("Ten killed","https://a.com/1","one"),it("x","https://b.com/1","two")])["passed"])
    def test_gates(self):
        cl=[it("Rates cut","https://a.com/1","Bank cut rates"),it("Rates cut","https://b.com/1","Rates fall")]
        art={"headline":"Central bank cuts rates","sources":["https://a.com/1"],"sections":[{"heading":"h","paragraphs":["word "*130]}]}
        s={"minBodyWords":120}; v={"reasons":[]}
        self.assertTrue(check(art,cl,v,s,[])[0])
        art["sources"]=["https://fake.com/x"]; self.assertFalse(check(art,cl,v,s,[])[0])
        art["sources"]=["https://a.com/1"]; art["sections"][0]["paragraphs"][0]='He said "we will do something huge tomorrow" '+"w "*130
        self.assertFalse(check(art,cl,v,s,[])[0])
        art["sections"][0]["paragraphs"][0]="w "*130; self.assertFalse(check(art,cl,v,s,["Central bank cuts rates"])[0])
    def test_ssrf(self):
        for u in("http://127.0.0.1/","http://localhost/","http://169.254.169.254/","file:///etc/passwd","http://10.0.0.1:8080/","ftp://x.com"):
            with self.assertRaises(Exception): check_url(u)
    def test_xxe_and_feed(self):
        with self.assertRaises(ValueError): reject_dtd(b'<!DOCTYPE x [<!ENTITY a "b">]><rss/>')
        feed=b'<rss><channel><item><title>T</title><link>https://a.com/x</link><pubDate>Tue, 14 Nov 2023 22:13:20 GMT</pubDate></item><item><title>Bad</title><link>javascript:alert(1)</link><pubDate>Tue, 14 Nov 2023 22:13:20 GMT</pubDate></item></channel></rss>'
        self.assertEqual(len(parse_feed(feed,now=1_700_000_000)),1)
    def test_schema(self):
        with self.assertRaises(ValueError): validate({"headline":"x"})
if __name__=="__main__": unittest.main()
