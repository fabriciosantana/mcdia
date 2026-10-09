"""Record the explicitly AI-assisted reading of the frozen 60-pair sample.
This is not human ground truth and must never prepopulate the human form.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sample=json.loads((ROOT/'data/review-sample.json').read_text())
# Labels and justifications from contextual reading of BOTH fields on 2026-10-09.
reviews=[
('yes','A indexação inclui saúde mental e prevenção de suicídio, embora o resumo destaque outro assunto.'),
('yes','Resumo menciona paralisação dos serviços de saúde.'),
('yes','Tributação é discutida para reforçar saúde; a indexação também menciona pandemia.'),
('yes','Pandemia e vacinação são centrais no resumo.'),
('yes','Homenagem inclui atuação direta no combate à pandemia.'),
('no','A discussão é tributária, sem assunto de saúde explícito nos campos lidos.'),
('no','Reciclagem e destinação de recursos ambientais não desenvolvem saúde nos campos lidos.'),
('yes','Regulamentação de medicamentos e Anvisa são assunto de saúde sem as palavras atuais do dicionário.'),
('no','Condecoração de direitos humanos não desenvolve saúde nos campos lidos.'),
('no','Custos de energia e transporte na Amazônia; não há assunto de saúde explícito.'),
('no','Trabalho refere-se à atuação do parlamentar, não a emprego, relações de trabalho ou economia.'),
('no','Fiscal é agente de fiscalização ambiental; não política fiscal ou tributação.'),
('yes','Preços de combustíveis, orçamento familiar e tributos são substantivos.'),
('yes','Subsídio ao gás, orçamento e política de preços são substantivos.'),
('yes','O resumo aborda agronegócio, embora a palavra acionadora trabalho tenha outro sentido.'),
('no','Combate à pandemia e vacinação sem discussão econômica explícita.'),
('no','Violência eleitoral, sem assunto econômico explícito.'),
('no','Homenagem e não violência, sem assunto econômico explícito.'),
('no','Política criminal e prevenção pela educação, sem assunto econômico explícito.'),
('no','Procedimentos de assembleias condominiais; não há assunto econômico substantivo explícito.'),
('yes','Financiamento do Fundeb e educação básica são discutidos.'),
('yes','Situação da educação e financiamento do Fundeb são discutidos.'),
('yes','Indexação registra investimento para melhorar a educação.'),
('yes','Atuação do Ministério da Educação e estabelecimentos de ensino são centrais.'),
('no','Universidade aparece apenas como filiação de pessoa presente; não há discussão educacional substantiva nos campos lidos.'),
('no','Campanhas de vacinação de adolescentes, sem discussão educacional explícita.'),
('no','Técnica cirúrgica e trajetória médica; não ensino ou política educacional explícitos.'),
('no','Reforma da previdência, sem discussão educacional explícita.'),
('no','Reforma administrativa e gasto público, sem educação explícita.'),
('no','Reformas previdenciária e tributária, regularização fundiária e fotografia; sem educação explícita.'),
('yes','Reforma previdenciária e programas do INSS são substantivos.'),
('yes','Debate previdenciário e regime de capitalização são centrais.'),
('yes','Indexação inclui concessão de benefício previdenciário e atendimento no INSS.'),
('yes','Renda de aposentados, benefícios e proteção dos idosos são substantivos.'),
('yes','O resumo discute a reforma previdenciária e a base numérica da proposta.'),
('no','Homenagem municipal e financiamento de saúde; sem previdência ou transferência social explícita.'),
('no','Liberdade de imprensa e crítica política; sem previdência ou proteção de renda explícitas.'),
('no','Incentivo tributário ao esporte não equivale a previdência ou proteção de renda.'),
('no','Regularização e infraestrutura urbana, bolsa de estudo e financiamento estudantil; fora do recorte previdência/proteção de renda adotado.'),
('no','Liberdade econômica, sem proteção de renda explícita.'),
('yes','CPI de Brumadinho refere-se à apuração do desastre de barragem.'),
('yes','Indexação explicita propostas sobre meio ambiente.'),
('yes','Política ambiental é o tema central.'),
('yes','Indexação inclui análise de meio ambiente e região amazônica.'),
('yes','Indexação descreve danos e rompimento de barragem em Brumadinho.'),
('no','Tramitação de proposta penal, sem discussão ambiental explícita.'),
('no','Reciclagem identifica a profissão de uma vítima; o assunto é violência policial e proteção social, não política ambiental.'),
('no','Violência contra mulheres, sem assunto ambiental explícito.'),
('no','Homenagens e condecorações, sem assunto ambiental explícito.'),
('no','Rastreamento de munições e homicídio, sem assunto ambiental explícito.'),
('yes','Segurança pública e atendimento a fluxos migratórios estão explícitos.'),
('yes','Criminalidade, segurança pública e armas são centrais.'),
('yes','Violência doméstica e direitos das mulheres estão explícitos.'),
('yes','Marcha de mulheres indígenas e mobilização de mulheres estão explícitas.'),
('yes','Mortes de jovens e violência são centrais.'),
('no','Aniversário de Brasília, sem direitos ou segurança explícitos.'),
('yes','Supostas ilegalidades em persecução penal e respeito à democracia constituem assunto de direitos, sem correspondência no dicionário.'),
('no','Aniversário da TV Senado, sem direitos ou segurança substantivos explícitos.'),
('no','Fomento cultural e lei de emergência cultural, fora do recorte operacional direitos/violência/segurança adotado.'),
('no','Reforma da previdência, sem direitos civis ou segurança substantivos explícitos.')]
assert len(reviews)==len(sample['items'])==60
items=[dict(key=item['key'],label=label,note=note) for item,(label,note) in zip(sample['items'],reviews)]
out={'schemaVersion':1,'datasetRevision':sample['datasetRevision'],'rulesVersion':sample['rulesVersion'],'reviewerType':'ai-assisted','reviewer':'Codex — leitura contextual assistida por IA','reviewedOn':'2026-10-09','limitations':'Revisor viu previsões; não independente; amostra balanceada por previsão e sem pesos; não é validação humana nem estimativa populacional. Rótulos podem ser contestados. Nenhuma regra foi reajustada com esta amostra.','items':items}
(ROOT/'data/assisted-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('60 leituras assistidas registradas; formulário humano permanece vazio.')
