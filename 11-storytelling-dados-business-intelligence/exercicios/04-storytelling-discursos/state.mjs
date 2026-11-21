export const defaults={from:'2019-02',to:'2023-01',kind:'Discurso',party:'',uf:'',author:'',theme:'',query:'',mode:'count',sort:'newest',aFrom:'2019-02',aTo:'2019-12',bFrom:'2020-02',bTo:'2020-12',trend:'Saúde e pandemia',voice1:'825',voice2:'5976',quality:'month'};
export function parseState(search,choices={}){
 const params=new URLSearchParams(search),state={...defaults},warnings=[];
 for(const key of Object.keys(defaults))if(params.has(key)){
  let value=params.get(key);
  const allowed=choices[key]||({mode:['count','share'],sort:['newest','oldest'],quality:['month','kind']})[key];
  if(value.length>200||(allowed&&!allowed.includes(value))||(['from','to','aFrom','aTo','bFrom','bTo'].includes(key)&&(!/^20\d{2}-(0[1-9]|1[0-2])$/.test(value)||value<'2019-02'||value>'2023-01'))){warnings.push(key);continue;}
  state[key]=value;
 }
 return {state,warnings};
}
export function serializeState(state){const p=new URLSearchParams();p.set('v','2');for(const k of Object.keys(defaults))if(state[k]!==defaults[k])p.set(k,state[k]);return p.toString();}
