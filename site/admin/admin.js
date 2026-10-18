import {initializeApp} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import {getAuth,signInWithEmailAndPassword,onAuthStateChanged,signOut} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";
import {getFirestore,doc,getDoc,setDoc,addDoc,updateDoc,deleteDoc,collection,getDocs,query,orderBy,limit,where,getCountFromServer,serverTimestamp} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";
import {firebaseConfig} from "../js/firebase-config.js";
const app=initializeApp(firebaseConfig),auth=getAuth(app),db=getFirestore(app),root=document.getElementById("app");
// All real authorization is enforced by Firestore rules (admins/{uid} doc). This UI check is only UX.
const h=(t,a={},...k)=>{const e=document.createElement(t);for(const[n,v]of Object.entries(a))if(n==="class")e.className=v;else if(!n.startsWith("on"))e.setAttribute(n,v);k.flat().forEach(c=>e.append(c));return e};
const audit=(action,target)=>addDoc(collection(db,"auditLogs"),{uid:auth.currentUser.uid,action,target,at:serverTimestamp()});
const SLOTS=["header","feed","inarticle","sidebar","footer"];
function login(msg=""){const em=h("input",{type:"email",placeholder:"Email",autocomplete:"username"}),pw=h("input",{type:"password",placeholder:"Password",autocomplete:"current-password"}),err=h("p",{},msg);
 const go=h("button",{},"Sign in");go.onclick=async()=>{try{await signInWithEmailAndPassword(auth,em.value,pw.value)}catch{err.textContent="Sign-in failed."}};
 root.replaceChildren(h("h1",{},"Admin sign-in"),em,pw,go,err)}
onAuthStateChanged(auth,async u=>{if(!u)return login();
 let ok=false;try{ok=(await getDoc(doc(db,"admins",u.uid))).exists()}catch{}
 if(!ok){await signOut(auth);return login("Not an administrator.")}panel()});
async function panel(tab="dash"){const nav=h("div",{class:"cats"},...["dash","articles","ads","sources","settings"].map(t=>{const b=h("button",{},t);b.onclick=()=>panel(t);return b}),(()=>{const b=h("button",{},"Sign out");b.onclick=()=>signOut(auth);return b})());
 const body=h("div",{});root.replaceChildren(h("h1",{},"Admin"),nav,body);
 try{await({dash,articles,ads,sources,settings}[tab])(body)}catch(e){body.textContent="Error: "+(e.code||"failed")}}
async function dash(b){const c=async(q)=>(await getCountFromServer(q)).data().count,A=collection(db,"articles");
 const [pub,rev,src]=await Promise.all([c(query(A,where("status","==","published"))),c(query(A,where("needsReview","==",true))),c(query(collection(db,"sources"),where("enabled","==",true)))]);
 const runs=await getDocs(query(collection(db,"jobRuns"),orderBy("startedAt","desc"),limit(8)));
 b.replaceChildren(h("p",{},`Published: ${pub} | Awaiting review: ${rev} | Enabled sources: ${src}`),h("h3",{},"Recent jobs"),h("ul",{},runs.docs.map(d=>{const r=d.data();return h("li",{},`${r.status} - published ${r.published||0}, rejected ${r.rejected||0} ${(r.errors||[]).join("; ")}`)})));}
async function articles(b){const s=await getDocs(query(collection(db,"articles"),orderBy("createdAt","desc"),limit(50)));
 b.replaceChildren(...s.docs.map(d=>{const a=d.data(),row=h("div",{class:"card"},h("strong",{},a.headline),h("p",{class:"meta"},`${a.status}${a.needsReview?" (needs review: "+(a.gateReasons||[]).join(", ")+")":""}`));
  const mk=(txt,fn)=>{const x=h("button",{},txt);x.onclick=async()=>{await fn();audit(txt,d.id);panel("articles")};row.append(x)};
  mk(a.status==="published"?"unpublish":"publish",()=>updateDoc(d.ref,{status:a.status==="published"?"draft":"published",needsReview:false}));
  mk("archive",()=>updateDoc(d.ref,{status:"archived"}));
  const del=h("button",{},"delete");del.onclick=async()=>{if(confirm("Delete permanently?")){await deleteDoc(d.ref);audit("delete",d.id);panel("articles")}};row.append(del);return row}))}
async function ads(b){const cur={};(await getDocs(collection(db,"ads"))).forEach(d=>cur[d.id]=d.data());
 b.replaceChildren(h("p",{class:"meta"},"HTML ads run in a sandboxed iframe. Ad networks need their own approval."),...SLOTS.map(id=>{const a=cur[id]||{},f={};
  const row=h("div",{class:"card"},h("strong",{},id));
  const add=(k,ph,type="text")=>{f[k]=h("input",{type,placeholder:ph,value:a[k]||""});row.append(f[k],h("br"))};
  add("label","Internal label");add("imageUrl","Image URL (https)");add("linkUrl","Destination URL (https)");add("start","Start date","date");add("end","End date","date");
  f.html=h("textarea",{placeholder:"Optional HTML snippet (sandboxed)",rows:"3"});f.html.value=a.html||"";f.enabled=h("input",{type:"checkbox"});f.enabled.checked=!!a.enabled;f.type=h("select",{},h("option",{value:"image"},"image"),h("option",{value:"html"},"html"));f.type.value=a.type||"image";
  row.append(f.html,h("br"),h("label",{},f.enabled," enabled "),f.type);const sv=h("button",{},"Save");
  sv.onclick=async()=>{const u=x=>/^https:\/\//.test(x)||x==="";if(!u(f.imageUrl.value)||!u(f.linkUrl.value))return alert("URLs must start with https://");
   await setDoc(doc(db,"ads",id),{label:f.label.value,imageUrl:f.imageUrl.value,linkUrl:f.linkUrl.value,start:f.start.value,end:f.end.value,html:f.html.value.slice(0,5000),enabled:f.enabled.checked,type:f.type.value,desktop:true,mobile:true});audit("ad-save",id);alert("Saved")};
  row.append(sv);return row}))}
async function sources(b){const s=await getDocs(collection(db,"sources")),n=h("input",{placeholder:"Name"}),u=h("input",{placeholder:"https://feed-url"}),c=h("input",{placeholder:"Category"}),add=h("button",{},"Add source");
 add.onclick=async()=>{if(!/^https:\/\//.test(u.value))return alert("https only");await addDoc(collection(db,"sources"),{name:n.value,url:u.value,category:c.value||null,type:"rss",enabled:true,reliability:0.6,categoryWeight:0.5});audit("source-add",u.value);panel("sources")};
 b.replaceChildren(n,u,c,add,...s.docs.map(d=>{const x=d.data(),r=h("div",{class:"card"},h("strong",{},x.name),h("p",{class:"meta"},`${x.url} | ${x.enabled?"on":"off"} | last error: ${x.lastError||"none"}`)),t=h("button",{},x.enabled?"disable":"enable");
  t.onclick=async()=>{await updateDoc(d.ref,{enabled:!x.enabled});audit("source-toggle",d.id);panel("sources")};r.append(t);return r}))}
async function settings(b){const r=doc(db,"automationSettings","main"),cur=(await getDoc(r)).data()||{enabled:true,maxArticlesPerRun:3,minIndependentSources:2};
 const en=h("input",{type:"checkbox"});en.checked=cur.enabled!==false;const mx=h("input",{type:"number",min:"0",max:"10",value:cur.maxArticlesPerRun}),ms=h("input",{type:"number",min:"2",max:"5",value:cur.minIndependentSources}),sv=h("button",{},"Save"),run=h("button",{},"Run now");
 sv.onclick=async()=>{await setDoc(r,{enabled:en.checked,maxArticlesPerRun:Math.min(10,+mx.value||0),minIndependentSources:Math.max(2,+ms.value||2)},{merge:true});audit("settings",""+en.checked);alert("Saved")};
 run.onclick=async()=>{await addDoc(collection(db,"runRequests"),{handled:false,by:auth.currentUser.uid,at:serverTimestamp()});alert("Requested. The next scheduled run (max ~30 min) handles it.")};
 b.replaceChildren(h("label",{},en," Automation ON (untick = kill switch; website stays up)"),h("br"),"Max articles/run ",mx,h("br"),"Min independent sources ",ms,h("br"),sv,run)}
