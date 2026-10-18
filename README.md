# Newsroom - AI News Website (Python + Firebase, Node.js NAHI chahiye)

## Folder
- site/        -> website (Cloudflare Pages ye folder serve karega), site/admin = admin panel
- pipeline/    -> Python robot jo news dhoondta, verify karta, Gemini se likhta aur publish karta hai
- .github/     -> har 30 minute ka automatic schedule (laptop band ho tab bhi chalta hai)
- firestore.rules, firestore.indexes.json -> database security

## Setup (sirf ye 8 kaam)
1. Firebase Console: naya project > Firestore Database (Production mode) + Authentication > Email/Password ON.
2. Project settings > Your apps > Web app banayein. Config ki 4 values (apiKey, authDomain, projectId, appId) sirf EK file mein paste karein: site/js/firebase-config.js
3. Firestore > Rules: firestore.rules ka poora text paste karke Publish.
4. Firestore > Indexes: firestore.indexes.json ke 2 composite indexes banayein (ya pehli error ke link par click karein).
5. Authentication > Users > Add user (apna email+password). Uska UID copy karein. Firestore mein collection "admins" banayein, Document ID = wohi UID, koi bhi field (role = admin).
6. GitHub par PRIVATE repo banayein, is folder ki saari files upload karein (.github folder samet).
   Repo > Settings > Secrets and variables > Actions:
   - Secret FIREBASE_SERVICE_ACCOUNT = Firebase Project settings > Service accounts > Generate key wali poori JSON
   - Secret GEMINI_API_KEY = Google AI Studio ki key
   - Variable SITE_URL = aapka Cloudflare link (https://xxxx.pages.dev, aakhir mein / nahi)
7. Cloudflare Pages > Connect to Git > repo chunein. Build command KHALI, Output directory = site
8. Admin: https://aapka-link/admin/ > sign in > Sources mein RSS feeds add karein (sirf wo jinki ijazat ho) > Settings mein Automation ON.
   GitHub > Actions > news-pipeline > Run workflow se pehla test chalayein.

## Security
Secrets sirf GitHub Secrets mein. Rules deny-by-default. Admin sirf admins/{uid} se. SSRF/XXE guards, quote/source fabrication gates, no innerHTML, CSP, sandboxed ads, audit log, kill switch.

## Limits
RSS sirf title/snippet deta hai, is liye articles chote hon ge. Khatarnak khabrain (maut, giraftari, ilzam) auto-publish nahi hoti, review mein jati hain. "Run now" agle 30-min tick par chalta hai. Free limits (Firebase, Gemini, GitHub Actions) khud check karein. Abhi shamil nahi: image provider, newsletter/contact form, rules emulator tests.
