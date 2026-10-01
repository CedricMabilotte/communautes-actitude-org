/* Carte : zoom et déplacement (boutons, Ctrl + molette, pincement, glisser, double-clic).
   Les cercles gardent une taille lisible et se rapprochent de leur position exacte quand on zoome. */
(function(){
  var fig=document.querySelector("[data-map]");if(!fig)return;
  var svg=fig.querySelector("svg"),vb0=svg.viewBox.baseVal,W=vb0.width,H=vb0.height;
  var pts=[].slice.call(svg.querySelectorAll(".pt")).map(function(p){
    var c=p.querySelector("circle.c"),h=p.querySelector("circle.halo"),t=p.querySelector("text");
    return {p:p,c:c,h:h,t:t,x0:+p.dataset.x,y0:+p.dataset.y,xd:+c.getAttribute("cx"),yd:+c.getAttribute("cy")};
  });
  var k=1,cx=W/2,cy=H/2,KMAX=24,hint=fig.querySelector("[data-maphint]");
  function clamp(){var w=W/k,h=H/k;cx=Math.min(Math.max(cx,w/2),W-w/2);cy=Math.min(Math.max(cy,h/2),H-h/2)}
  function draw(){
    clamp();var w=W/k,h=H/k;svg.setAttribute("viewBox",(cx-w/2)+" "+(cy-h/2)+" "+w+" "+h);
    var kr=Math.pow(k,.65);
    svg.style.setProperty("--kr",kr);
    if(k<=1.01){pts.forEach(function(o){o.x=o.xd;o.y=o.yd})}else if(k!==lastK){relax(kr)}
    lastK=k;
    pts.forEach(function(o){var x=o.x,y=o.y;
      o.c.setAttribute("cx",x);o.c.setAttribute("cy",y);o.h.setAttribute("cx",x);o.h.setAttribute("cy",y);
      if(o.t){o.t.setAttribute("x",x);o.t.setAttribute("y",y+.4/kr)}});
    fig.classList.toggle("zoomed",k>1.01);
    var lv=fig.querySelector("[data-zlevel]");if(lv)lv.textContent="× "+(Math.round(k*10)/10).toString().replace(".",",");
  }
  var lastK=-1,R0=parseFloat(getComputedStyle(svg).getPropertyValue("--r0"))||7.2;
  // écarte les cercles qui se chevauchent à l'échelle courante, en partant des positions exactes
  function relax(kr){
    var dark=document.documentElement.dataset.theme==="dark"||(!document.documentElement.dataset.theme&&matchMedia("(prefers-color-scheme:dark)").matches);
    var r=(dark?3.4:R0)/kr,m=2*r+.8/kr,vis=pts.filter(function(o){return !o.p.classList.contains("off")});
    vis.forEach(function(o){o.x=o.x0;o.y=o.y0});
    for(var it=0;it<60;it++){var g={};
      vis.forEach(function(o,i){var key=Math.floor(o.x/m)+","+Math.floor(o.y/m);(g[key]=g[key]||[]).push(i)});
      var moved=0;
      vis.forEach(function(a,i){var gx=Math.floor(a.x/m),gy=Math.floor(a.y/m);
        for(var ax=gx-1;ax<=gx+1;ax++)for(var ay=gy-1;ay<=gy+1;ay++){var c=g[ax+","+ay];if(!c)continue;
          c.forEach(function(j){if(j<=i)return;var b=vis[j],dx=b.x-a.x,dy=b.y-a.y,d=Math.hypot(dx,dy);
            if(d<m){if(d<1e-6){dx=Math.cos(i+j);dy=Math.sin(i+j);d=1}var p=(m-d)/2,ux=dx/d,uy=dy/d;a.x-=ux*p;a.y-=uy*p;b.x+=ux*p;b.y+=uy*p;moved++}})}});
      vis.forEach(function(o){o.x+=(o.x0-o.x)*.03;o.y+=(o.y0-o.y)*.03});
      if(!moved)break}
    pts.forEach(function(o){if(o.x==null){o.x=o.xd;o.y=o.yd}})
  }
  window.atlasMapRelax=function(){lastK=-1;draw()};
  function toSvg(clientX,clientY){var r=svg.getBoundingClientRect(),w=W/k,h=H/k;
    return [cx-w/2+(clientX-r.left)/r.width*w, cy-h/2+(clientY-r.top)/r.height*h]}
  function zoomAt(f,px,py){var nk=Math.min(KMAX,Math.max(1,k*f));if(nk===k)return;
    if(px!=null){cx=px+(cx-px)*k/nk;cy=py+(cy-py)*k/nk}k=nk;draw()}
  fig.querySelector("[data-zin]").addEventListener("click",function(){zoomAt(1.6)});
  fig.querySelector("[data-zout]").addEventListener("click",function(){zoomAt(1/1.6)});
  fig.querySelector("[data-zreset]").addEventListener("click",function(){k=1;cx=W/2;cy=H/2;draw()});
  var hintT;
  svg.addEventListener("wheel",function(ev){
    if(!(ev.ctrlKey||ev.metaKey)){if(hint){hint.hidden=false;clearTimeout(hintT);hintT=setTimeout(function(){hint.hidden=true},1400)}return}
    ev.preventDefault();var p=toSvg(ev.clientX,ev.clientY);zoomAt(Math.exp(-ev.deltaY*.0025),p[0],p[1])},{passive:false});
  svg.addEventListener("dblclick",function(ev){ev.preventDefault();var p=toSvg(ev.clientX,ev.clientY);zoomAt(ev.shiftKey?1/2:2,p[0],p[1])});
  // glisser et pincer
  var ptrs={},start=null,moved=false;
  svg.addEventListener("pointerdown",function(ev){ptrs[ev.pointerId]=[ev.clientX,ev.clientY];moved=false;
    var ids=Object.keys(ptrs);
    if(ids.length===1)start={x:ev.clientX,y:ev.clientY,cx:cx,cy:cy};
    if(ids.length===2){var a=ptrs[ids[0]],b=ptrs[ids[1]];start={d:Math.hypot(a[0]-b[0],a[1]-b[1]),k:k,m:toSvg((a[0]+b[0])/2,(a[1]+b[1])/2)}}});
  svg.addEventListener("pointermove",function(ev){if(!ptrs[ev.pointerId]||!start)return;ptrs[ev.pointerId]=[ev.clientX,ev.clientY];
    var ids=Object.keys(ptrs),r=svg.getBoundingClientRect();
    if(ids.length===2&&start.d){var a=ptrs[ids[0]],b=ptrs[ids[1]],d=Math.hypot(a[0]-b[0],a[1]-b[1]);
      var nk=Math.min(KMAX,Math.max(1,start.k*d/start.d));cx=start.m[0]+(cx-start.m[0])*k/nk;cy=start.m[1]+(cy-start.m[1])*k/nk;k=nk;moved=true;draw();return}
    if(k<=1.01)return;
    var dx=ev.clientX-start.x,dy=ev.clientY-start.y;if(Math.abs(dx)+Math.abs(dy)>4){moved=true;svg.setPointerCapture&&svg.setPointerCapture(ev.pointerId)}
    if(moved){cx=start.cx-dx/r.width*W/k;cy=start.cy-dy/r.height*H/k;draw()}});
  function up(ev){delete ptrs[ev.pointerId];var ids=Object.keys(ptrs);
    if(ids.length===1){var a=ptrs[ids[0]];start={x:a[0],y:a[1],cx:cx,cy:cy}}else if(!ids.length)start=null}
  svg.addEventListener("pointerup",up);svg.addEventListener("pointercancel",up);
  svg.addEventListener("click",function(ev){if(moved){ev.preventDefault();ev.stopPropagation();moved=false}},true);
  // zoom sur une sélection (appelé par le filtre)
  window.atlasMapFit=function(uids){
    if(!uids||!uids.length||uids.length===pts.length){k=1;cx=W/2;cy=H/2;draw();return}
    var xs=[],ys=[];pts.forEach(function(o){if(uids.indexOf(o.p.dataset.uid)>-1){xs.push(o.x0);ys.push(o.y0)}});
    if(!xs.length)return;var x0=Math.min.apply(0,xs),x1=Math.max.apply(0,xs),y0=Math.min.apply(0,ys),y1=Math.max.apply(0,ys);
    var w=Math.max(x1-x0,W/14)*1.5,h=Math.max(y1-y0,H/14)*1.5;k=Math.min(KMAX,Math.max(1,Math.min(W/w,H/h)));cx=(x0+x1)/2;cy=(y0+y1)/2;draw()};
  draw();
})();
