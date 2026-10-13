// Embedded only in the generated delivery. Keep normal HTTP development unchanged.
const payloadNode=document.getElementById('offline-payload');
const {assets,modules}=JSON.parse(payloadNode.textContent);
payloadNode.remove();
const base=new URL('.',location.href),nativeFetch=window.fetch.bind(window);
const mime=name=>name.endsWith('.json')?'application/json':'text/markdown;charset=utf-8';
function assetKey(input){
 const url=new URL(input instanceof Request?input.url:input,location.href);
 if(url.origin!==base.origin||!url.pathname.startsWith(base.pathname))return null;
 return decodeURIComponent(url.pathname.slice(base.pathname.length));
}
window.fetch=async(input,init)=>{
 const key=assetKey(input);
 if(Object.hasOwn(assets,key))return new Response(assets[key],{status:200,headers:{'Content-Type':mime(key)}});
 return nativeFetch(input,init);
};
const urls=new Map();
function moduleURL(name){
 if(urls.has(name))return urls.get(name);
 if(!Object.hasOwn(modules,name))throw new Error(`Módulo ausente na entrega: ${name}`);
 const source=modules[name].replace(/(from\s*['"])\.\/([^'"]+)(['"])/g,(_,before,dependency,after)=>before+moduleURL(dependency)+after);
 const url=URL.createObjectURL(new Blob([source],{type:'text/javascript'}));
 urls.set(name,url);return url;
}
// Delegation also handles the audit download link created after opening the sample.
document.addEventListener('click',event=>{
 const link=event.target.closest('a[href]');
 if(!link||link.getAttribute('href').startsWith('#'))return;
 const key=assetKey(link.href);
 if(!Object.hasOwn(assets,key))return;
 event.preventDefault();
 const url=URL.createObjectURL(new Blob([assets[key]],{type:mime(key)}));
 const download=document.createElement('a');download.href=url;download.download=key.split('/').pop();download.click();
 setTimeout(()=>URL.revokeObjectURL(url),10000);
});
await import(moduleURL('app.js'));
if(location.protocol==='file:'){
 const share=document.getElementById('share');share.disabled=true;
 document.getElementById('share-status').textContent='Arquivo offline: compartilhe este HTML. Um endereço file:// não é acessível por outras pessoas. Exporte o ZIP para preservar os filtros.';
}
