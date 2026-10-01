(function(){var t=document.querySelector("[data-cmp]");if(!t)return;var tb=t.tBodies[0],btns=[].slice.call(t.querySelectorAll("thead button")),cur=null,dir=-1;
[].forEach.call(tb.querySelectorAll("td.c"),function(td){var a=td.firstChild;if(window.fpPic)a.insertAdjacentHTML("afterbegin",fpPic(td.dataset.k,td.dataset.x,20,0))});
btns.forEach(function(b){b.addEventListener("click",function(){var c=b.dataset.col;dir=(cur===c)?-dir:(c==="name"?1:-1);cur=c;
  var rs=[].slice.call(tb.rows);
  rs.sort(function(a,z){if(c==="name")return dir*a.cells[0].textContent.localeCompare(z.cells[0].textContent,"fr");
    var i=+c+1,va=+a.cells[i].dataset.v,vz=+z.cells[i].dataset.v;return dir*(va-vz)||a.cells[0].textContent.localeCompare(z.cells[0].textContent,"fr")});
  rs.forEach(function(r){tb.appendChild(r)});
  btns.forEach(function(x){x.parentNode.removeAttribute("aria-sort")});b.parentNode.setAttribute("aria-sort",dir>0?"ascending":"descending")})});
var q=document.querySelector("[data-cq]"),rg=document.querySelector("[data-cr]"),cc=document.querySelector("[data-cc]");
function norm(s){return (s||"").normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase()}
function f(){var v=norm(q.value),r=rg.value,n=0;[].forEach.call(tb.rows,function(tr){var ok=(!v||tr.dataset.q.indexOf(v)>-1)&&(!r||tr.dataset.region===r);tr.hidden=!ok;if(ok)n++});cc.textContent=n+" sur "+tb.rows.length}
if(q){q.addEventListener("input",f);rg.addEventListener("change",f);f()}
})();
