import {initializeApp} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import {getFirestore,collection,query,where,orderBy,limit,getDocs} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";
import {firebaseConfig} from "./firebase-config.js";
const db=getFirestore(initializeApp(firebaseConfig));
// h(): builds DOM with textContent only (no innerHTML) => XSS-safe. Only http(s) URLs allowed in links/images.
const safe=u=>{try{const x=new URL(u,location.href);return /^https?:$/.test(x.protocol)?x.href:null}catch{return null}};
const h=(t,a={},...k)=>{const e=document.createElement(t);for(const[n,v]of Object.entries(a)){if(n==="class")e.className=v;else if(n==="href"||n==="src"){const s=safe(v);if(s)e.setAttribute(n,s)}else if(!n.startsWith("on"))e.setAttribute(n,v)}k.flat().forEach(c=>e.append(c));return e};
const ls={get:(k,d)=>{try{return JSON.parse(localStorage.getItem(k))??d}catch{return d}},set:(k,v)=>{try{localStorage.setItem(k,JSON.stringify(v))}catch{}}};
document.documentElement.dataset.theme=ls.get("theme","light");
document.getElementById("theme").onclick=()=>{const t=document.documentElement.dataset.theme==="dark"?"light":"dark";document.documentElement.dataset.theme=t;ls.set("theme",t)};
const main=document.getElementById("main"),P=new URLSearchParams(location.search);let all=[],showSaved=false;
const mins=a=>Math.max(1,Math.round(a.sections.flatMap(s=>s.paragraphs).join(" ").split(/\s+/).length/200));
function card(a){const sv=ls.get("saved",[]);return h("article",{class:"card"},h("span",{class:"meta"},a.category+" · "+mins(a)+" min"),h("h3",{},h("a",{href:"?a="+encodeURIComponent(a.slug)},a.headline)),h("p",{},a.summary),
 h("button",{onclick:null},sv.includes(a.slug)?"Unsave":"Save"))}
function wireSave(el,a){const b=el.querySelector("button");b.onclick=()=>{let s=ls.get("saved",[]);s=s.includes(a.slug)?s.filter(x=>x!==a.slug):[...s,a.slug];ls.set("saved",s);b.textContent=s.includes(a.slug)?"Unsave":"Save"}}
function list(){const q=document.getElementById("q").value.toLowerCase(),c=P.get("c"),sv=ls.get("saved",[]);
 const r=all.filter(a=>(!c||a.category===c)&&(!showSaved||sv.includes(a.slug))&&(!q||(a.headline+a.summary+(a.tags||[]).join(" ")).toLowerCase().includes(q)));
 main.replaceChildren(r.length?h("div",{class:"grid"},r.map(a=>{const e=card(a);wireSave(e,a);return e})):h("p",{},"No stories found."))}
function article(a){const url=encodeURIComponent(location.origin+location.pathname+"?a="+a.slug);
 main.replaceChildren(h("a",{href:"index.html"},"← Back"),h("h1",{},a.headline),h("p",{class:"meta"},a.category+" · "+mins(a)+" min read"),h("p",{},h("strong",{},a.summary)),
 a.sections.map(s=>[h("h2",{},s.heading),s.paragraphs.map(p=>h("p",{},p))]),h("div",{id:"ad-inarticle"}),h("h3",{},"Sources"),h("ul",{},a.sources.map(u=>h("li",{},h("a",{href:u,rel:"nofollow noopener"},u)))),
 h("p",{},"Share: ",h("a",{href:"https://twitter.com/intent/tweet?url="+url},"X")," · ",h("a",{href:"https://www.facebook.com/sharer/sharer.php?u="+url},"Facebook")," · ",h("a",{href:"https://wa.me/?text="+url},"WhatsApp")));document.title=a.seoTitle||a.headline}
async function ads(){const now=Date.now(),mob=matchMedia("(max-width:700px)").matches;
 try{(await getDocs(query(collection(db,"ads"),where("enabled","==",true)))).forEach(d=>{const a=d.data(),box=document.getElementById("ad-"+d.id);if(!box)return;
  if((a.start&&Date.parse(a.start)>now)||(a.end&&Date.parse(a.end)<now)||(mob&&a.mobile===false)||(!mob&&a.desktop===false))return;
  const inner=a.type==="html"?h("iframe",{sandbox:"allow-scripts allow-popups",referrerpolicy:"no-referrer",srcdoc:a.html||"",title:"Advertisement"}):(safe(a.imageUrl)?h("a",{href:a.linkUrl,rel:"sponsored noopener",target:"_blank"},h("img",{src:a.imageUrl,alt:a.label||"Advertisement"})):null);
  if(inner)box.replaceChildren(h("div",{class:"ad"},h("small",{},"Advertisement"),inner))})}catch{}}
(async()=>{try{
 const s=await getDocs(query(collection(db,"articles"),where("status","==","published"),orderBy("publishedAt","desc"),limit(60)));all=s.docs.map(d=>d.data());
 document.getElementById("ticker").textContent=all.length?all.slice(0,5).map(a=>a.headline).join("  •  "):"Welcome";
 const cats=[...new Set(all.map(a=>a.category))];document.getElementById("cats").replaceChildren(h("a",{href:"index.html"},h("button",{},"All")),cats.map(c=>h("a",{href:"?c="+encodeURIComponent(c)},h("button",{},c))));
 if(P.get("a")){const a=all.find(x=>x.slug===P.get("a"));a?article(a):main.replaceChildren(h("h1",{},"404 - Story not found"),h("a",{href:"index.html"},"Home"))}else list();
 document.getElementById("q").oninput=list;document.getElementById("saved").onclick=()=>{showSaved=!showSaved;list()};ads()
}catch{main.replaceChildren(h("p",{},"Could not load stories. Please try again later."))}})();
