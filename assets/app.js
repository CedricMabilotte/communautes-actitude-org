(function(){
  var form=document.querySelector(".filters"),list=document.querySelector("[data-rows]");
  if(!form||!list)return;
  var rows=[].slice.call(list.querySelectorAll(".row")),PAGE=50,shown=PAGE,
      pts={},count=document.querySelector("[data-count]"),empty=document.querySelector("[data-empty]"),more=document.querySelector("[data-more]"),
      sortSel=document.querySelector("[data-sort]"),
      bar=[].slice.call(document.querySelectorAll("[data-degbar] button")),map=document.querySelector("[data-map]"),tip=document.querySelector("[data-tip]");
  [].forEach.call(document.querySelectorAll(".pt"),function(p){pts[p.dataset.uid]=p});
  var degs=new Set();
  function norm(s){return (s||"").normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase()}
  var rowByUid={};rows.forEach(function(r,i){rowByUid[r.dataset.uid]=r;r._i=i;r._q=norm(r.dataset.q+" "+r.textContent);r._n=norm(r.querySelector(".n").textContent);r._e=norm(r.dataset.etats)});
  function state(){var f=new FormData(form),s={};f.forEach(function(v,k){if(v)s[k]=v});if(degs.size)s.deg=[].slice.call(degs).sort().join(",");if(sortSel&&sortSel.value!=="nom")s.tri=sortSel.value;return s}
  function sorted(){var t=sortSel?sortSel.value:"nom",rs=rows.slice();
    if(t==="deg")rs.sort(function(a,b){return (+b.dataset.deg)-(+a.dataset.deg)||a._i-b._i});
    else if(t==="etat")rs.sort(function(a,b){return a._e<b._e?-1:a._e>b._e?1:a._i-b._i});
    return rs}
  var lastKey="";
  function apply(push,keepPage){
    var s=state(),q=norm(s.q),ok=[];
    var key=JSON.stringify(s);if(key!==lastKey&&!keepPage)shown=PAGE;lastKey=key;
    var rs=sorted();rs.forEach(function(r){list.appendChild(r)});
    rs.forEach(function(r){
      var m=(!q||r._q.indexOf(q)>-1)&&(!s.region||r.dataset.region===s.region)&&(!s.fam||r.dataset.fam===s.fam)&&(!s.type||r.dataset.type===s.type)&&
        (!s.etat||("|"+r.dataset.etats+"|").indexOf("|"+s.etat+"|")>-1)&&
        (!s.eff||r.dataset.eff===s.eff)&&(!s.niv||r.dataset.niv===s.niv)&&(!degs.size||degs.has(r.dataset.deg))&&(!s.droit||r.dataset.d.indexOf(s.droit+":reconnu")>-1);
      if(pts[r.dataset.uid])pts[r.dataset.uid].classList.toggle("off",!m);
      if(m)ok.push(r);r.hidden=true});
    ok.forEach(function(r,i){if(i<shown){r.hidden=false;var f=r.querySelector("[data-fp]");if(f&&window.fpFill)fpFill(f)}});
    var n=ok.length;
    count.textContent=n+(n>1?" fiches":" fiche")+(n<rows.length?" sur "+rows.length:"");
    empty.hidden=n>0;
    if(more){var rest=n-shown;more.hidden=rest<=0;if(rest>0)more.textContent="Afficher "+Math.min(PAGE,rest)+" de plus ("+rest+" restantes)"}
    bar.forEach(function(b){b.setAttribute("aria-pressed",degs.has(b.dataset.deg)?"true":"false")});
    if(push!==false){var p=new URLSearchParams(s).toString();history.replaceState(null,"",p?"?"+p:location.pathname)}
    if(window.atlasMapRelax)atlasMapRelax();
    if(window.atlasMapFit&&!keepPage)atlasMapFit((s.etat||s.q)?ok.map(function(r){return r.dataset.uid}):null);
  }
  form.addEventListener("input",function(){apply()});form.addEventListener("change",function(){apply()});
  if(sortSel)sortSel.addEventListener("change",function(){apply()});
  if(more)more.addEventListener("click",function(){shown+=PAGE;apply(true,true)});
  bar.forEach(function(b){b.addEventListener("click",function(){var d=b.dataset.deg;degs.has(d)?degs.delete(d):degs.add(d);apply()})});
  [].forEach.call(document.querySelectorAll("[data-reset]"),function(b){b.addEventListener("click",function(){form.reset();if(sortSel)sortSel.value="nom";degs.clear();apply()})});
  // état depuis l'URL (liens partageables)
  var u=new URLSearchParams(location.search);
  u.forEach(function(v,k){if(k==="deg"){v.split(",").forEach(function(d){degs.add(d)})}else if(k==="tri"&&sortSel){sortSel.value=v}else if(form.elements[k]){form.elements[k].value=v}});
  window.addEventListener("load",function(){apply(false)});apply(false);
  // carte <-> liste
  function show(p,on){var r=rowByUid[p.dataset.uid];if(!r)return;r.classList.toggle("hl",on);p.classList.toggle("on",on);
    if(on){var c=p.querySelector("circle.c"),bb=c.getBoundingClientRect(),mb=map.getBoundingClientRect();
      var x=bb.left+bb.width/2-mb.left,y=bb.top+bb.height/2-mb.top;
      var meta=r.querySelector(".meta").textContent;
      tip.innerHTML="";var b=document.createElement("b");b.textContent=r.querySelector(".n").childNodes[0].textContent;tip.appendChild(b);tip.appendChild(document.createElement("br"));tip.appendChild(document.createTextNode(meta.split(" · ")[0]+" · degré "+r.dataset.deg));
      tip.style.left=x+"px";tip.style.top=y+"px";tip.style.display="block"}else{tip.style.display="none"}}
  Object.keys(pts).forEach(function(k){var p=pts[k];
    p.addEventListener("mouseenter",function(){show(p,true)});p.addEventListener("mouseleave",function(){show(p,false)});
    p.addEventListener("focus",function(){show(p,true)});p.addEventListener("blur",function(){show(p,false)})});
  rows.forEach(function(r){var p=pts[r.dataset.uid];if(!p)return;
    r.addEventListener("mouseenter",function(){p.classList.add("on");p.parentNode.appendChild(p)});r.addEventListener("mouseleave",function(){p.classList.remove("on")})});
})();
