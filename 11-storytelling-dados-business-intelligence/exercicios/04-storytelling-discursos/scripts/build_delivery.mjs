/** Generate one offline HTML from the local, pinned corpus. No network/dependencies. */
import {readFile,writeFile,mkdir,readdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=fileURLToPath(new URL('../',import.meta.url));
const read=name=>readFile(path.join(root,name),'utf8');
const assets={},modules={};
const catalog=JSON.parse(await read('data/catalog.json'));
for(const name of ['data/catalog.json','data/manifest.json','data/review-sample.json','data/assisted-review.json',...Object.values(catalog.fragments).map(f=>f.path)]){
 assets[name]=await read(name);
 JSON.parse(assets[name]); // Fail the build if any data fragment is malformed.
}
for(const name of ['REFERENCIAS.md','METODOLOGIA.md','ROTEIRO-APRESENTACAO.md'])assets[name]=await read(name);
for(const name of (await readdir(root)).filter(n=>n.endsWith('.mjs')||n==='app.js'))modules[name]=await read(name);
const payload=JSON.stringify({assets,modules}).replaceAll('<','\\u003c');
let html=await read('index.html');
const styleTag='<link rel="stylesheet" href="styles.css">',scriptTag='<script type="module" src="app.js"></script>';
if(!html.includes(styleTag)||!html.includes(scriptTag))throw new Error('Entradas CSS/JS não reconhecidas; revise o gerador.');
const css=await read('styles.css');
html=html.replace(styleTag,()=>`<style>${css}</style>`).replace(scriptTag,'');
const bootstrap=await read('scripts/offline-bootstrap.js');
html=html.replace('</body>',()=>`<script type="application/json" id="offline-payload">${payload}</script><script type="module">${bootstrap}</script></body>`);
await mkdir(path.join(root,'entrega'),{recursive:true});
await writeFile(path.join(root,'entrega/vozes-do-senado.html'),html);
console.log(`Entrega gerada: entrega/vozes-do-senado.html (${Buffer.byteLength(html)} bytes; ${Object.keys(catalog.fragments).length} fragmentos).`);
