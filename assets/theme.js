(function(){var b=document.querySelector("[data-theme-toggle]");if(!b)return;
b.addEventListener("click",function(){var r=document.documentElement,cur=r.dataset.theme||(matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light"),n=cur==="dark"?"light":"dark";r.dataset.theme=n;try{localStorage.setItem("theme",n)}catch(_){}});})();
