document.addEventListener("DOMContentLoaded",()=>{const e=document.getElementById("subscribe-form");e&&fetch("https://cms.2077.xyz/get-csrf-token/",{credentials:"include"}).then(t=>t.json()).then(t=>{const n=t.csrfToken,o=document.createElement("input");o.type="hidden",o.name="csrfmiddlewaretoken",o.value=n,e.appendChild(o),e.addEventListener("submit",async r=>{r.preventDefault();const s=new FormData(e);try{const c=await fetch(e.action,{method:"POST",body:s,headers:{"X-CSRFToken":n},credentials:"include"}),i=document.getElementById("response-message");if(c.ok)i&&(i.textContent="Subscription successful!",i.style.color="green");else{const l=await c.json();throw new Error(l.message||"An error occurred")}}catch(c){const i=document.getElementById("response-message");i&&(i.textContent=c instanceof Error?c.message:"An error occurred. Please try again.",i.style.color="red")}})}).catch(t=>{console.error("Error fetching CSRF token:",t);const n=document.getElementById("response-message");n&&(n.textContent="An error occurred while fetching the CSRF token. Please try again.",n.style.color="red")})});const y="data-astro-transition-persist";function J(e){for(const t of document.scripts)for(const n of e.scripts)if(!n.hasAttribute("data-astro-rerun")&&(!t.src&&t.textContent===n.textContent||t.src&&t.type===n.type&&t.src===n.src)){n.dataset.astroExec="";break}}function Q(e){const t=document.documentElement,n=[...t.attributes].filter(({name:o})=>(t.removeAttribute(o),o.startsWith("data-astro-")));[...e.documentElement.attributes,...n].forEach(({name:o,value:r})=>t.setAttribute(o,r))}function Z(e){for(const t of Array.from(document.head.children)){const n=ne(t,e);n?n.remove():t.remove()}document.head.append(...e.head.children)}function ee(e,t){t.replaceWith(e);for(const n of t.querySelectorAll(`[${y}]`)){const o=n.getAttribute(y),r=e.querySelector(`[${y}="${o}"]`);r&&(r.replaceWith(n),r.localName==="astro-island"&&oe(n)&&(n.setAttribute("ssr",""),n.setAttribute("props",r.getAttribute("props"))))}}const te=()=>{const e=document.activeElement;if(e?.closest(`[${y}]`)){if(e instanceof HTMLInputElement||e instanceof HTMLTextAreaElement){const t=e.selectionStart,n=e.selectionEnd;return()=>R({activeElement:e,start:t,end:n})}return()=>R({activeElement:e})}else return()=>R({activeElement:null})},R=({activeElement:e,start:t,end:n})=>{e&&(e.focus(),(e instanceof HTMLInputElement||e instanceof HTMLTextAreaElement)&&(typeof t=="number"&&(e.selectionStart=t),typeof n=="number"&&(e.selectionEnd=n)))},ne=(e,t)=>{const n=e.getAttribute(y),o=n&&t.head.querySelector(`[${y}="${n}"]`);if(o)return o;if(e.matches("link[rel=stylesheet]")){const r=e.getAttribute("href");return t.head.querySelector(`link[rel=stylesheet][href="${r}"]`)}return null},oe=e=>{const t=e.dataset.astroTransitionPersistProps;return t==null||t==="false"},re=e=>{J(e),Q(e),Z(e);const t=te();ee(e.body,document.body),t()},ie="astro:before-preparation",se="astro:after-preparation",ae="astro:before-swap",ce="astro:after-swap",le=e=>document.dispatchEvent(new Event(e));class _ extends Event{from;to;direction;navigationType;sourceElement;info;newDocument;signal;constructor(t,n,o,r,s,c,i,l,f,u){super(t,n),this.from=o,this.to=r,this.direction=s,this.navigationType=c,this.sourceElement=i,this.info=l,this.newDocument=f,this.signal=u,Object.defineProperties(this,{from:{enumerable:!0},to:{enumerable:!0,writable:!0},direction:{enumerable:!0,writable:!0},navigationType:{enumerable:!0},sourceElement:{enumerable:!0},info:{enumerable:!0},newDocument:{enumerable:!0,writable:!0},signal:{enumerable:!0}})}}class ue extends _{formData;loader;constructor(t,n,o,r,s,c,i,l,f,u){super(ie,{cancelable:!0},t,n,o,r,s,c,i,l),this.formData=f,this.loader=u.bind(this,this),Object.defineProperties(this,{formData:{enumerable:!0},loader:{enumerable:!0,writable:!0}})}}class fe extends _{direction;viewTransition;swap;constructor(t,n){super(ae,void 0,t.from,t.to,t.direction,t.navigationType,t.sourceElement,t.info,t.newDocument,t.signal),this.direction=t.direction,this.viewTransition=n,this.swap=()=>re(this.newDocument),Object.defineProperties(this,{direction:{enumerable:!0},viewTransition:{enumerable:!0},swap:{enumerable:!0,writable:!0}})}}async function de(e,t,n,o,r,s,c,i,l){const f=new ue(e,t,n,o,r,s,window.document,c,i,l);return document.dispatchEvent(f)&&(await f.loader(),f.defaultPrevented||(le(se),f.navigationType!=="traverse"&&D({scrollX,scrollY}))),f}function me(e,t){const n=new fe(e,t);return document.dispatchEvent(n),n.swap(),n}const he=history.pushState.bind(history),T=history.replaceState.bind(history),D=e=>{history.state&&(history.scrollRestoration="manual",T({...history.state,...e},""))},x=!!document.startViewTransition,I=()=>!!document.querySelector('[name="astro-view-transitions-enabled"]'),$=(e,t)=>e.pathname===t.pathname&&e.search===t.search;let d,g,A;const q=e=>document.dispatchEvent(new Event(e)),U=()=>q("astro:page-load"),pe=()=>{let e=document.createElement("div");e.setAttribute("aria-live","assertive"),e.setAttribute("aria-atomic","true"),e.className="astro-route-announcer",document.body.append(e),setTimeout(()=>{let t=document.title||document.querySelector("h1")?.textContent||location.pathname;e.textContent=t},60)},N="data-astro-transition-persist",O="data-astro-transition",k="data-astro-transition-fallback";let F,b=0;history.state?(b=history.state.index,scrollTo({left:history.state.scrollX,top:history.state.scrollY})):I()&&(T({index:b,scrollX,scrollY},""),history.scrollRestoration="manual");async function ge(e,t){try{const n=await fetch(e,t),r=(n.headers.get("content-type")??"").split(";",1)[0].trim();return r!=="text/html"&&r!=="application/xhtml+xml"?null:{html:await n.text(),redirected:n.redirected?n.url:void 0,mediaType:r}}catch{return null}}function V(){const e=document.querySelector('[name="astro-view-transitions-fallback"]');return e?e.getAttribute("content"):"animate"}function we(){let e=Promise.resolve();for(const t of Array.from(document.scripts)){if(t.dataset.astroExec==="")continue;const n=t.getAttribute("type");if(n&&n!=="module"&&n!=="text/javascript")continue;const o=document.createElement("script");o.innerHTML=t.innerHTML;for(const r of t.attributes){if(r.name==="src"){const s=new Promise(c=>{o.onload=o.onerror=c});e=e.then(()=>s)}o.setAttribute(r.name,r.value)}o.dataset.astroExec="",t.replaceWith(o)}return e}const W=(e,t,n,o,r)=>{const s=$(t,e),c=document.title;document.title=o;let i=!1;if(e.href!==location.href&&!r)if(n.history==="replace"){const l=history.state;T({...n.state,index:l.index,scrollX:l.scrollX,scrollY:l.scrollY},"",e.href)}else he({...n.state,index:++b,scrollX:0,scrollY:0},"",e.href);if(document.title=c,A=e,s||(scrollTo({left:0,top:0,behavior:"instant"}),i=!0),r)scrollTo(r.scrollX,r.scrollY);else{if(e.hash){history.scrollRestoration="auto";const l=history.state;location.href=e.href,history.state||(T(l,""),s&&window.dispatchEvent(new PopStateEvent("popstate")))}else i||scrollTo({left:0,top:0,behavior:"instant"});history.scrollRestoration="manual"}};function ye(e){const t=[];for(const n of e.querySelectorAll("head link[rel=stylesheet]"))if(!document.querySelector(`[${N}="${n.getAttribute(N)}"], link[rel=stylesheet][href="${n.getAttribute("href")}"]`)){const o=document.createElement("link");o.setAttribute("rel","preload"),o.setAttribute("as","style"),o.setAttribute("href",n.getAttribute("href")),t.push(new Promise(r=>{["load","error"].forEach(s=>o.addEventListener(s,r)),document.head.append(o)}))}return t}async function M(e,t,n,o,r){async function s(l){function f(h){const m=h.effect;return!m||!(m instanceof KeyframeEffect)||!m.target?!1:window.getComputedStyle(m.target,m.pseudoElement).animationIterationCount==="infinite"}const u=document.getAnimations();document.documentElement.setAttribute(k,l);const p=document.getAnimations().filter(h=>!u.includes(h)&&!f(h));return Promise.allSettled(p.map(h=>h.finished))}if(r==="animate"&&!n.transitionSkipped&&!e.signal.aborted)try{await s("old")}catch{}const c=document.title,i=me(e,n.viewTransition);W(i.to,i.from,t,c,o),q(ce),r==="animate"&&(!n.transitionSkipped&&!i.signal.aborted?s("new").finally(()=>n.viewTransitionFinished()):n.viewTransitionFinished())}function be(){return d?.controller.abort(),d={controller:new AbortController}}async function j(e,t,n,o,r){const s=be();if(!I()||location.origin!==n.origin){s===d&&(d=void 0),location.href=n.href;return}const c=r?"traverse":o.history==="replace"?"replace":"push";if(c!=="traverse"&&D({scrollX,scrollY}),$(t,n)&&(e!=="back"&&n.hash||e==="back"&&t.hash)){W(n,t,o,document.title,r),s===d&&(d=void 0);return}const i=await de(t,n,e,c,o.sourceElement,o.info,s.controller.signal,o.formData,l);if(i.defaultPrevented||i.signal.aborted){s===d&&(d=void 0),i.signal.aborted||(location.href=n.href);return}async function l(a){const p=a.to.href,h={signal:a.signal};if(a.formData){h.method="POST";const w=a.sourceElement instanceof HTMLFormElement?a.sourceElement:a.sourceElement instanceof HTMLElement&&"form"in a.sourceElement?a.sourceElement.form:a.sourceElement?.closest("form");h.body=w?.attributes.getNamedItem("enctype")?.value==="application/x-www-form-urlencoded"?new URLSearchParams(a.formData):a.formData}const m=await ge(p,h);if(m===null){a.preventDefault();return}if(m.redirected){const w=new URL(m.redirected);if(w.origin!==a.to.origin){a.preventDefault();return}a.to=w}if(F??=new DOMParser,a.newDocument=F.parseFromString(m.html,m.mediaType),a.newDocument.querySelectorAll("noscript").forEach(w=>w.remove()),!a.newDocument.querySelector('[name="astro-view-transitions-enabled"]')&&!a.formData){a.preventDefault();return}const L=ye(a.newDocument);L.length&&!a.signal.aborted&&await Promise.all(L)}async function f(){if(g&&g.viewTransition){try{g.viewTransition.skipTransition()}catch{}try{await g.viewTransition.updateCallbackDone}catch{}}return g={transitionSkipped:!1}}const u=await f();if(i.signal.aborted){s===d&&(d=void 0);return}if(document.documentElement.setAttribute(O,i.direction),x)u.viewTransition=document.startViewTransition(async()=>await M(i,o,u,r));else{const a=(async()=>{await Promise.resolve(),await M(i,o,u,r,V())})();u.viewTransition={updateCallbackDone:a,ready:a,finished:new Promise(p=>u.viewTransitionFinished=p),skipTransition:()=>{u.transitionSkipped=!0,document.documentElement.removeAttribute(k)}}}u.viewTransition.updateCallbackDone.finally(async()=>{await we(),U(),pe()}),u.viewTransition.finished.finally(()=>{u.viewTransition=void 0,u===g&&(g=void 0),s===d&&(d=void 0),document.documentElement.removeAttribute(O),document.documentElement.removeAttribute(k)});try{await u.viewTransition.updateCallbackDone}catch(a){const p=a;console.log("[astro]",p.name,p.message,p.stack)}}async function H(e,t){await j("forward",A,new URL(e,location.href),t??{})}function ve(e){if(!I()&&e.state){location.reload();return}if(e.state===null)return;const t=history.state,n=t.index,o=n>b?"forward":"back";b=n,j(o,A,new URL(location.href),{},t)}const X=()=>{history.state&&(scrollX!==history.state.scrollX||scrollY!==history.state.scrollY)&&D({scrollX,scrollY})};{if(x||V()!=="none")if(A=new URL(location.href),addEventListener("popstate",ve),addEventListener("load",U),"onscrollend"in window)addEventListener("scrollend",X);else{let e,t,n,o;const r=()=>{if(o!==history.state?.index){clearInterval(e),e=void 0;return}if(t===scrollY&&n===scrollX){clearInterval(e),e=void 0,X();return}else t=scrollY,n=scrollX};addEventListener("scroll",()=>{e===void 0&&(o=history.state.index,t=scrollY,n=scrollX,e=window.setInterval(r,50))},{passive:!0})}for(const e of document.scripts)e.dataset.astroExec=""}const K=new Set,E=new WeakSet;let P,z,Y=!1;function Te(e){Y||(Y=!0,P??=e?.prefetchAll,z??=e?.defaultStrategy??"hover",Ee(),Ae(),Se(),Re())}function Ee(){for(const e of["touchstart","mousedown"])document.body.addEventListener(e,t=>{v(t.target,"tap")&&S(t.target.href,{ignoreSlowConnection:!0})},{passive:!0})}function Ae(){let e;document.body.addEventListener("focusin",o=>{v(o.target,"hover")&&t(o)},{passive:!0}),document.body.addEventListener("focusout",n,{passive:!0}),C(()=>{for(const o of document.getElementsByTagName("a"))E.has(o)||v(o,"hover")&&(E.add(o),o.addEventListener("mouseenter",t,{passive:!0}),o.addEventListener("mouseleave",n,{passive:!0}))});function t(o){const r=o.target.href;e&&clearTimeout(e),e=setTimeout(()=>{S(r)},80)}function n(){e&&(clearTimeout(e),e=0)}}function Se(){let e;C(()=>{for(const t of document.getElementsByTagName("a"))E.has(t)||v(t,"viewport")&&(E.add(t),e??=Le(),e.observe(t))})}function Le(){const e=new WeakMap;return new IntersectionObserver((t,n)=>{for(const o of t){const r=o.target,s=e.get(r);o.isIntersecting?(s&&clearTimeout(s),e.set(r,setTimeout(()=>{n.unobserve(r),e.delete(r),S(r.href)},300))):s&&(clearTimeout(s),e.delete(r))}})}function Re(){C(()=>{for(const e of document.getElementsByTagName("a"))v(e,"load")&&S(e.href)})}function S(e,t){const n=t?.ignoreSlowConnection??!1;if(ke(e,n))if(K.add(e),document.createElement("link").relList?.supports?.("prefetch")&&t?.with!=="fetch"){const o=document.createElement("link");o.rel="prefetch",o.setAttribute("href",e),document.head.append(o)}else fetch(e,{priority:"low"})}function ke(e,t){if(!navigator.onLine||!t&&G())return!1;try{const n=new URL(e,location.href);return location.origin===n.origin&&(location.pathname!==n.pathname||location.search!==n.search)&&!K.has(e)}catch{}return!1}function v(e,t){if(e?.tagName!=="A")return!1;const n=e.dataset.astroPrefetch;return n==="false"?!1:t==="tap"&&(n!=null||P)&&G()?!0:n==null&&P||n===""?t===z:n===t}function G(){if("connection"in navigator){const e=navigator.connection;return e.saveData||/2g/.test(e.effectiveType)}return!1}function C(e){e();let t=!1;document.addEventListener("astro:page-load",()=>{if(!t){t=!0;return}e()})}function Pe(){const e=document.querySelector('[name="astro-view-transitions-fallback"]');return e?e.getAttribute("content"):"animate"}function B(e){return e.dataset.astroReload!==void 0}(x||Pe()!=="none")&&(document.addEventListener("click",e=>{let t=e.target;if(e.composed&&(t=e.composedPath()[0]),t instanceof Element&&(t=t.closest("a, area")),!(t instanceof HTMLAnchorElement)&&!(t instanceof SVGAElement)&&!(t instanceof HTMLAreaElement))return;const n=t instanceof HTMLElement?t.target:t.target.baseVal,o=t instanceof HTMLElement?t.href:t.href.baseVal,r=new URL(o,location.href).origin;B(t)||t.hasAttribute("download")||!t.href||n&&n!=="_self"||r!==location.origin||e.button!==0||e.metaKey||e.ctrlKey||e.altKey||e.shiftKey||e.defaultPrevented||(e.preventDefault(),H(o,{history:t.dataset.astroHistory==="replace"?"replace":"auto",sourceElement:t}))}),document.addEventListener("submit",e=>{let t=e.target;if(t.tagName!=="FORM"||e.defaultPrevented||B(t))return;const n=t,o=e.submitter,r=new FormData(n,o),s=typeof n.action=="string"?n.action:n.getAttribute("action"),c=typeof n.method=="string"?n.method:n.getAttribute("method");let i=o?.getAttribute("formaction")??s??location.pathname;const l=o?.getAttribute("formmethod")??c??"get";if(l==="dialog"||location.origin!==new URL(i,location.href).origin)return;const f={sourceElement:o??n};if(l==="get"){const u=new URLSearchParams(r),a=new URL(i);a.search=u.toString(),i=a.toString()}else f.formData=r;e.preventDefault(),H(i,f)}),Te({prefetchAll:!0}));