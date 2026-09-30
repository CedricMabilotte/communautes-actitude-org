(function(){
  var form=document.querySelector(".filters"),rows=[].slice.call(document.querySelectorAll("[data-rows] .row")),
      pts={},count=document.querySelector("[data-count]"),empty=document.querySelector("[data-empty]"),
      bar=[].slice.call(document.querySelectorAll("[data-degbar] button")),map=document.querySelector("[data-map]"),tip=document.querySelector("[data-tip]");
  if(!form)return;
  [].forEach.call(document.querySelectorAll(".pt"),function(p){pts[p.dataset.uid]=p});
  var degs=new Set();
  function norm(s){return (s||"").normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase()}
  var rowByUid={};rows.forEach(function(r){rowByUid[r.dataset.uid]=r;r._q=norm(r.dataset.q+" "+r.textContent)});
  function state(){var f=new FormData(form),s={};f.forEach(function(v,k){if(v)s[k]=v});if(degs.size)s.deg=[].slice.call(degs).sort().join(",");return s}
  function apply(push){
    var s=state(),q=norm(s.q),n=0;
    rows.forEach(function(r){
      var ok=(!q||r._q.indexOf(q)>-1)&&(!s.region||r.dataset.region===s.region)&&(!s.type||r.dataset.type===s.type)&&
        (!s.eff||r.dataset.eff===s.eff)&&(!s.niv||r.dataset.niv===s.niv)&&(!degs.size||degs.has(r.dataset.deg))&&(!s.droit||r.dataset.d.indexOf(s.droit+":reconnu")>-1);
      r.hidden=!ok;if(pts[r.dataset.uid])pts[r.dataset.uid].classList.toggle("off",!ok);if(ok)n++;
    });
    count.textContent=n+(n>1?" fiches":" fiche")+(n<rows.length?" sur "+rows.length:"");
    empty.hidden=n>0;
    bar.forEach(function(b){b.setAttribute("aria-pressed",degs.has(b.dataset.deg)?"true":"false")});
    if(push!==false){var p=new URLSearchParams(s).toString();history.replaceState(null,"",p?"?"+p:location.pathname)}
  }
  form.addEventListener("input",apply);form.addEventListener("change",apply);
  bar.forEach(function(b){b.addEventListener("click",function(){var d=b.dataset.deg;degs.has(d)?degs.delete(d):degs.add(d);apply()})});
  [].forEach.call(document.querySelectorAll("[data-reset]"),function(b){b.addEventListener("click",function(){form.reset();degs.clear();apply()})});
  // état depuis l'URL (liens partageables)
  var u=new URLSearchParams(location.search);
  u.forEach(function(v,k){if(k==="deg"){v.split(",").forEach(function(d){degs.add(d)})}else if(form.elements[k]){form.elements[k].value=v}});
  apply(false);
  // carte <-> liste
  function show(p,on){var r=rowByUid[p.dataset.uid];if(!r)return;r.classList.toggle("hl",on);p.classList.toggle("on",on);
    if(on){var c=p.querySelector("circle.c"),svg=p.ownerSVGElement,bb=svg.getBoundingClientRect(),vb=svg.viewBox.baseVal,mb=map.getBoundingClientRect();
      var x=(c.cx.baseVal.value/vb.width)*bb.width+bb.left-mb.left,y=(c.cy.baseVal.value/vb.height)*bb.height+bb.top-mb.top;
      var n=r.querySelector(".n").cloneNode(true),meta=r.querySelector(".meta").textContent;
      tip.innerHTML="";var b=document.createElement("b");b.textContent=n.childNodes[0].textContent;tip.appendChild(b);tip.appendChild(document.createElement("br"));tip.appendChild(document.createTextNode(meta.split(" · ")[0]+" · degré "+r.dataset.deg));
      tip.style.left=x+"px";tip.style.top=y+"px";tip.style.display="block"}else{tip.style.display="none"}}
  Object.keys(pts).forEach(function(k){var p=pts[k];
    p.addEventListener("mouseenter",function(){show(p,true)});p.addEventListener("mouseleave",function(){show(p,false)});
    p.addEventListener("focus",function(){show(p,true)});p.addEventListener("blur",function(){show(p,false)})});
  rows.forEach(function(r){var p=pts[r.dataset.uid];if(!p)return;
    r.addEventListener("mouseenter",function(){p.classList.add("on");p.parentNode.appendChild(p)});r.addEventListener("mouseleave",function(){p.classList.remove("on")})});
})();
