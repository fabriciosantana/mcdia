import {decodeCatalog} from './analytics.mjs';
export class DataStore{
 constructor(){this.cache=new Map();this.pending=new Map();this.detailById=new Map();}
 async init(){const response=await fetch('./data/catalog.json');if(!response.ok)throw new Error(`Índice: HTTP ${response.status}`);this.catalog=await response.json();if(this.catalog.meta?.schemaVersion!==2||!Array.isArray(this.catalog.rows))throw new Error('Índice incompatível');this.rows=decodeCatalog(this.catalog);return this;}
 async month(month){
  if(this.cache.has(month))return this.cache.get(month);if(this.pending.has(month))return this.pending.get(month);
  const descriptor=this.catalog.fragments[month];if(!descriptor)return {};
  const promise=(async()=>{
   const response=await fetch('./'+descriptor.path);if(!response.ok)throw new Error(`Textos de ${month}: HTTP ${response.status}`);
   const data=await response.json();for(const[id,details]of Object.entries(data))this.detailById.set(id,details);this.cache.set(month,data);return data;
  })();this.pending.set(month,promise);
  try{return await promise;}finally{this.pending.delete(month);}
 }
 async hydrate(rows){
  const months=[...new Set(rows.filter(r=>!this.detailById.has(r.id)).map(r=>r.date.slice(0,7)))];
  // Four concurrent requests at most; retry remains possible after a failure.
  let next=0;await Promise.all(Array.from({length:Math.min(4,months.length)},async()=>{while(next<months.length)await this.month(months[next++]);}));
  return rows.map(r=>({...r,...this.detailById.get(r.id)}));
 }
}
