import test from 'node:test';
import assert from 'node:assert/strict';
import {narrativeSummary} from '../narrative.mjs';
test('conclusion states numerator, denominator and missing texts for the selected scope',()=>{
 const text=narrativeSummary({total:4045,authors:Array(106).fill({count:1}),top10:1955,fullText:3425});
 for(const value of ['106','1.955','4.045','48,3%','620','filtros e datas'])assert.ok(text.includes(value),value);
});
test('empty scope cannot retain an earlier conclusion',()=>{
 assert.match(narrativeSummary({total:0}),/Não há registros/);
});
test('small author selection cannot imply concentration of the whole legislature',()=>{
 const text=narrativeSummary({total:5,authors:[{count:5}],top10:5,fullText:5});
 assert.match(text,/100% por construção/);assert.match(text,/não descreve a concentração/);
});
test('equal frequencies do not produce an inequality claim',()=>{
 const text=narrativeSummary({total:22,authors:Array(11).fill({count:2}),top10:20,fullText:22});
 assert.match(text,/mesma contagem/);assert.doesNotMatch(text,/forma desigual/);
});
