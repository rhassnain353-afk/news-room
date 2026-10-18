"""Static SEO pages. EVERY dynamic value is html-escaped; JSON-LD is made script-safe."""
import html, json, os, re, datetime as dt
E=lambda s:html.escape(str(s),quote=True)
def slugify(t): return (re.sub(r"[^a-z0-9]+","-",t.lower()).strip("-")[:70] or "story")
def _ld(o): return json.dumps(o).replace("<","\\u003c")
def article_html(a,site):
    url=f"{site}/a/{a['slug']}.html"; iso=a["publishedAtIso"]
    body="".join(f"<h2>{E(s['heading'])}</h2>"+"".join(f"<p>{E(p)}</p>" for p in s["paragraphs"]) for s in a["sections"])
    srcs="".join(f'<li><a rel="nofollow noopener" href="{E(u)}">{E(u)}</a></li>' for u in a["sources"] if u.startswith("http"))
    ld={"@context":"https://schema.org","@type":"NewsArticle","headline":a["headline"],"datePublished":iso,"dateModified":iso,"mainEntityOfPage":url,"description":a["metaDescription"]}
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self'; img-src https: data:; base-uri 'none'; form-action 'none'">
<title>{E(a['seoTitle'])}</title><meta name="description" content="{E(a['metaDescription'])}"><link rel="canonical" href="{E(url)}">
<meta property="og:type" content="article"><meta property="og:title" content="{E(a['seoTitle'])}"><meta property="og:description" content="{E(a['metaDescription'])}"><meta property="og:url" content="{E(url)}">
<link rel="stylesheet" href="../css/style.css"><script type="application/ld+json">{_ld(ld)}</script></head><body>
<header><a href="../index.html">Newsroom</a> &rsaquo; <a href="../index.html?c={E(a['category'])}">{E(a['category'])}</a></header>
<main class="wrap"><article><h1>{E(a['headline'])}</h1><p class="meta">{E(iso[:10])} &middot; AI-assisted, source-attributed</p><p><strong>{E(a['summary'])}</strong></p>{body}
<h2>Sources</h2><ul>{srcs}</ul></article><p><a href="../index.html?a={E(a['slug'])}">Open interactive version</a></p></main></body></html>'''
def write_site(arts,site,root):
    os.makedirs(f"{root}/a",exist_ok=True)
    for a in arts: open(f"{root}/a/{a['slug']}.html","w",encoding="utf-8").write(article_html(a,site))
    u="".join(f"<url><loc>{E(site)}/a/{E(a['slug'])}.html</loc><lastmod>{E(a['publishedAtIso'][:10])}</lastmod></url>" for a in arts)
    open(f"{root}/sitemap.xml","w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{E(site)}/</loc></url>{u}</urlset>')
    open(f"{root}/robots.txt","w").write(f"User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: {site}/sitemap.xml\n")
    it="".join(f"<item><title>{E(a['headline'])}</title><link>{E(site)}/a/{E(a['slug'])}.html</link><description>{E(a['summary'])}</description><guid>{E(site)}/a/{E(a['slug'])}.html</guid></item>" for a in arts[:30])
    open(f"{root}/rss.xml","w",encoding="utf-8").write(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Newsroom</title><link>{E(site)}</link><description>Latest news</description>{it}</channel></rss>')
