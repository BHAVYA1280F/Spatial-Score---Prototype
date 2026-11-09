"""Global look and behaviour: CSS plus a small script injected into the parent page
(cursor glow, scroll progress, scroll variable, reveal-on-scroll, hover tilt)."""
import streamlit as st
import streamlit.components.v1 as components

CSS = """@import url('https://fonts.googleapis.com/css2?family=Syne:wght@500;700;800&family=Inter:wght@300;400;600&display=swap');
:root{--sy:0}
.stApp{background:radial-gradient(1100px 700px at 10% -10%,rgba(255,45,85,.22),transparent 60%),radial-gradient(900px 600px at 95% 8%,rgba(79,140,255,.18),transparent 60%),#07060d;color:#f3eefc}
header[data-testid="stHeader"]{background:transparent}
#MainMenu,footer{visibility:hidden}
.stApp,.stMarkdown,p,label,button,input,textarea{font-family:'Inter',sans-serif}
h1,h2,h3,.disp{font-family:'Syne',sans-serif!important;letter-spacing:-.02em}
.block-container{max-width:1280px;padding-top:2rem}
iframe{border-radius:18px}
[data-testid="stElementContainer"]:has(iframe[height="0"]){height:0;margin:0;overflow:hidden}
section[data-testid="stSidebar"]{background:rgba(14,12,24,.92);border-right:1px solid rgba(255,255,255,.08)}
#ss-glow{position:fixed;left:0;top:0;width:520px;height:520px;margin:-260px 0 0 -260px;border-radius:50%;pointer-events:none;z-index:1;background:radial-gradient(circle,rgba(255,45,85,.20),rgba(155,107,255,.10) 45%,transparent 70%);mix-blend-mode:screen;transition:opacity .3s}
#ss-progress{position:fixed;left:0;top:0;height:3px;width:100%;z-index:999999;transform-origin:0 50%;transform:scaleX(0);background:linear-gradient(90deg,#ff2d55,#9b6bff,#4f8cff)}
.eyebrow{font-size:.78rem;letter-spacing:.3em;text-transform:uppercase;color:#ff5c7c;margin:3rem 0 .6rem}
.lead{font-size:1.15rem;color:#b9b1d3;max-width:44rem;line-height:1.6}
.reveal{opacity:0;transform:translateY(46px) scale(.97);transition:opacity .9s cubic-bezier(.2,.8,.2,1),transform .9s cubic-bezier(.2,.8,.2,1)}
.reveal.in{opacity:1;transform:none}
.reveal.done{transition:transform .18s ease-out,opacity .3s,box-shadow .3s,border-color .3s}
.float{transform:translate3d(0,var(--py,0px),0)}
.tilt{position:relative;transform-style:preserve-3d;will-change:transform}
.tilt::after{content:"";position:absolute;inset:0;border-radius:inherit;pointer-events:none;opacity:0;transition:opacity .25s;background:radial-gradient(260px circle at var(--mx,50%) var(--my,50%),rgba(255,255,255,.22),transparent 60%)}
.tilt:hover::after{opacity:1}
.card{background:linear-gradient(160deg,rgba(255,255,255,.07),rgba(255,255,255,.02));border:1px solid rgba(255,255,255,.10);border-radius:20px;padding:1.4rem 1.5rem;backdrop-filter:blur(8px)}
.card:hover{border-color:var(--c,#ff2d55);box-shadow:0 18px 60px -18px var(--c,#ff2d55)}
.card h3{margin:.4rem 0 .3rem;font-size:1.3rem}
.card p{color:#b9b1d3;font-size:.95rem;line-height:1.55;margin:0}
.num{font-family:'Syne';font-weight:800;font-size:3.2rem;line-height:1;color:transparent;-webkit-text-stroke:1px var(--c,#ff2d55)}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:1.2rem}
.grid5{display:grid;grid-template-columns:repeat(5,1fr);gap:1rem}
.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:1.1rem}
@media(max-width:900px){.grid3,.grid4,.grid5{grid-template-columns:1fr 1fr}}
.ico{width:100%;height:76px;margin:.2rem 0 .6rem;overflow:visible}
.bp{transform-box:fill-box;transform-origin:bottom;animation:pulse 1.8s ease-in-out infinite}
.card:hover .bp{animation-duration:.55s}
.hb{transform-box:fill-box;transform-origin:left;animation:stretch 2.4s ease-in-out infinite}
.card:hover .hb{animation-duration:.8s}
.sq{transform-box:fill-box;transform-origin:center;animation:squeeze 2.2s ease-in-out infinite}
.dr{stroke-dasharray:220;stroke-dashoffset:220;animation:draw 2.6s ease-in-out infinite}
.fl{animation:floaty 3s ease-in-out infinite}
.tw{animation:twinkle 1.6s ease-in-out infinite}
.wl{animation:wallL 2.4s ease-in-out infinite}.wr{animation:wallR 2.4s ease-in-out infinite}
@keyframes pulse{0%,100%{transform:scaleY(.35)}50%{transform:scaleY(1)}}
@keyframes stretch{0%,100%{transform:scaleX(.25)}50%{transform:scaleX(1)}}
@keyframes squeeze{0%,100%{transform:scaleX(1)}50%{transform:scaleX(.55)}}
@keyframes draw{0%{stroke-dashoffset:220}60%,100%{stroke-dashoffset:0}}
@keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
@keyframes twinkle{0%,100%{opacity:.25}50%{opacity:1}}
@keyframes wallL{0%,100%{transform:translateX(0)}50%{transform:translateX(-14px)}}
@keyframes wallR{0%,100%{transform:translateX(0)}50%{transform:translateX(14px)}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes grow{from{transform:scaleY(0)}}
.band{overflow:hidden;white-space:nowrap;margin:2.5rem 0;border-top:1px solid rgba(255,255,255,.08);border-bottom:1px solid rgba(255,255,255,.08)}
.band span{display:inline-block;font-family:'Syne';font-weight:800;font-size:clamp(3rem,8vw,7rem);color:transparent;-webkit-text-stroke:1px rgba(255,255,255,.35);transform:translateX(calc(var(--sy) * -.7px));transition:color .3s}
.band.rev span{transform:translateX(calc(var(--sy) * .7px - 900px))}
.band:hover span{color:rgba(255,45,85,.9);-webkit-text-stroke-color:#ff2d55}
.score{display:flex;align-items:flex-end;gap:3px;height:130px;padding:.8rem;border-radius:18px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08)}
.score i{flex:1;min-width:2px;background:var(--c);border-radius:3px 3px 0 0;opacity:.85;transform-origin:bottom;animation:grow .7s cubic-bezier(.2,.8,.2,1) backwards;animation-delay:calc(var(--i) * 14ms);transition:transform .2s,filter .2s}
.score i:hover{transform:scaleY(1.18);filter:brightness(1.5)}.score i:hover+i,.score i:has(+ i:hover){transform:scaleY(1.08)}
.ztable{width:100%;border-collapse:collapse;font-size:.9rem}.ztable th{color:#a79fc0;font-weight:400;text-align:left;padding:.4rem .6rem;border-bottom:1px solid rgba(255,255,255,.1)}
.ztable td{padding:.45rem .6rem;border-bottom:1px solid rgba(255,255,255,.06)}.ztable tr:hover td{background:rgba(255,255,255,.05)}
.mbar{display:flex;height:14px;border-radius:7px;overflow:hidden}.mbar i{display:block}.mbar i:hover{filter:brightness(1.4)}
.stat{text-align:center}.stat b{display:block;font-family:'Syne';font-size:2.2rem}.stat span{color:#a79fc0;font-size:.8rem;letter-spacing:.2em;text-transform:uppercase}
.chips span{display:inline-block;margin:.25rem .3rem .25rem 0;padding:.3rem .8rem;border-radius:999px;border:1px solid rgba(255,255,255,.18);font-size:.85rem;transition:.25s}
.chips span:hover{background:#ff2d55;border-color:#ff2d55;transform:translateY(-3px)}
.cover{position:relative;aspect-ratio:1;margin-bottom:1.6rem}
.cover .art{position:absolute;inset:0;z-index:2;border-radius:10px;overflow:hidden;box-shadow:0 20px 50px -15px rgba(0,0,0,.8)}
.cover .art img,.cover .art svg{width:100%;height:100%;object-fit:cover;display:block}
.vinyl{position:absolute;inset:6%;z-index:1;border-radius:50%;transition:transform .8s cubic-bezier(.2,.8,.2,1)}
.vinyl i{display:block;width:100%;height:100%;border-radius:50%;background:radial-gradient(circle,#c4122f 0 11%,#111 12% 14%,transparent 15%),repeating-radial-gradient(circle,#0b0b0f 0 2px,#1b1b22 3px 4px);animation:spin 2.5s linear infinite paused}
.cover:hover .vinyl{transform:translateX(44%)}.cover:hover .vinyl i{animation-play-state:running}
.cover .meta{position:absolute;left:0;right:0;bottom:-1.5rem;z-index:3;display:flex;justify-content:space-between;align-items:center;font-size:.85rem}
.cover .meta em{font-style:normal;display:flex;gap:3px}.cover .meta em i{width:12px;height:12px;border-radius:50%;display:block}
.stButton>button,.stDownloadButton>button,a[data-testid="stPageLink-NavLink"]{border-radius:999px;border:1px solid rgba(255,255,255,.2);background:linear-gradient(90deg,#ff2d55,#9b6bff);color:#fff;transition:transform .25s,box-shadow .25s}
.stButton>button:hover,.stDownloadButton>button:hover,a[data-testid="stPageLink-NavLink"]:hover{transform:translateY(-3px) scale(1.04);box-shadow:0 12px 40px -8px #ff2d55;color:#fff}
[data-testid="stFileUploaderDropzone"]{border:1px dashed rgba(255,255,255,.3);border-radius:18px;background:rgba(255,255,255,.04);transition:.3s}
[data-testid="stFileUploaderDropzone"]:hover{border-color:#ff2d55;box-shadow:0 0 40px -10px #ff2d55}
"""

JS = """(function(){
var P=window.parent,D=P.document;if(P.__ssInit)return;P.__ssInit=true;
var glow=D.createElement('div');glow.id='ss-glow';D.body.appendChild(glow);
var bar=D.createElement('div');bar.id='ss-progress';D.body.appendChild(bar);
var cur=null;
function reset(el){if(el){el.style.transform='';}}
D.addEventListener('mousemove',function(e){
 glow.style.transform='translate('+e.clientX+'px,'+e.clientY+'px)';
 var t=e.target&&e.target.closest?e.target.closest('.tilt'):null;
 if(cur&&cur!==t)reset(cur);cur=t;
 if(t){var r=t.getBoundingClientRect(),px=(e.clientX-r.left)/r.width,py=(e.clientY-r.top)/r.height;
  t.style.setProperty('--mx',(px*100)+'%');t.style.setProperty('--my',(py*100)+'%');
  t.style.transform='perspective(900px) rotateX('+((.5-py)*14)+'deg) rotateY('+((px-.5)*16)+'deg) translateZ(14px)';}
},true);
D.addEventListener('mouseleave',function(){reset(cur);cur=null;},true);
D.addEventListener('scroll',function(e){var el=e.target;
 if(!el||!el.matches||!el.matches('[data-testid="stMain"],section.main,.main'))return;
 var st=el.scrollTop||0,mx=el.scrollHeight-el.clientHeight;
 D.documentElement.style.setProperty('--sy',st);
 par();
 bar.style.transform='scaleX('+(mx>0?st/mx:0)+')';
},true);
var io=new P.IntersectionObserver(function(es){es.forEach(function(en){
 if(en.isIntersecting&&!en.target.classList.contains('in')){en.target.classList.add('in');
  setTimeout(function(){en.target.classList.add('done');},1000);}});},{threshold:.12});
function par(){var vh=P.innerHeight;D.querySelectorAll('.float').forEach(function(n){
 var q=n.parentElement.getBoundingClientRect(),d=-(q.top+q.height/2-vh/2)*(parseFloat(n.style.getPropertyValue('--sp'))||0);
 n.style.setProperty('--py',Math.max(-60,Math.min(60,d))+'px');});}
function scan(){D.querySelectorAll('.reveal:not([data-o])').forEach(function(n){n.setAttribute('data-o','1');io.observe(n);});par();}
new P.MutationObserver(scan).observe(D.body,{childList:true,subtree:true});scan();
})();"""


def setup():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
    components.html(f"<script>{JS}</script>", height=0)
