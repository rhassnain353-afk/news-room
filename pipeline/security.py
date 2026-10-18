"""SSRF-safe fetching + XXE-safe feed parsing. Stdlib only."""
import ipaddress, re, socket, urllib.parse, urllib.request
MAX_BYTES=2_000_000
class Blocked(Exception): pass
def check_url(url):
    p=urllib.parse.urlparse(url)
    if p.scheme not in("http","https") or not p.hostname or p.username or p.password: raise Blocked("bad url")
    if p.port not in(None,80,443): raise Blocked("bad port")
    for i in socket.getaddrinfo(p.hostname,p.port or 443):
        if not ipaddress.ip_address(i[4][0]).is_global: raise Blocked("non-public address")
    return url
class _Redir(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,h,newurl):
        check_url(newurl); return super().redirect_request(req,fp,code,msg,h,newurl)
def safe_fetch(url,timeout=10):
    check_url(url)
    req=urllib.request.Request(url,headers={"User-Agent":"NewsroomBot/1.0"})
    with urllib.request.build_opener(_Redir).open(req,timeout=timeout) as r: data=r.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES: raise Blocked("response too large")
    return data
def reject_dtd(data):
    if re.search(rb"<!\s*(DOCTYPE|ENTITY)",data,re.I): raise ValueError("DTD/entities rejected")
