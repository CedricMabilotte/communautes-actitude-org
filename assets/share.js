(function(){var box=document.querySelector("[data-share]");if(!box)return;
var url=box.dataset.url,text=box.dataset.text,st=box.querySelector("[data-status]");
function say(m,btn){st.textContent=m;if(btn){var o=btn.textContent;btn.textContent=m;setTimeout(function(){btn.textContent=o},1800)}}
var nat=box.querySelector("[data-native]");
if(navigator.share){nat.hidden=false;nat.addEventListener("click",function(){navigator.share({title:document.title,text:text,url:url}).catch(function(){})})}
box.querySelector("[data-copy]").addEventListener("click",function(ev){var b=ev.currentTarget;
  (navigator.clipboard?navigator.clipboard.writeText(url):Promise.reject()).then(function(){say("Lien copié",b)},function(){prompt("Copier le lien :",url)})});
box.querySelector("[data-mastodon]").addEventListener("click",function(ev){ev.preventDefault();var i="";
  try{i=localStorage.getItem("mastodon")||""}catch(_){}
  i=prompt("Votre instance Mastodon (ex. mastodon.social) :",i);if(!i)return;i=i.replace(/^https?:\/\//,"").replace(/\/.*$/,"");
  try{localStorage.setItem("mastodon",i)}catch(_){}
  window.open("https://"+i+"/share?text="+encodeURIComponent(text+" "+url),"_blank","noopener")});
})();
