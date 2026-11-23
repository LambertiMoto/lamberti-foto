# Prepara i dati geografici (Openpolis/ISTAT, CC-BY 4.0) per il geomarketing: confini snelliti + elenco comuni con CAP
import json, glob, os, re
SRC='/tmp/geo/src/topojson'; OUT='/home/claude/lamberti-foto/geo/v1'
def slim(path, keep):
    t=json.load(open(path)); name=list(t['objects'].keys())[0]; o=t['objects'][name]
    for g in o['geometries']: g['properties']=keep(g.get('properties') or {})
    t['objects']={'a':o}; t.pop('bbox',None)
    return t
reg=slim(f'{SRC}/limits_IT_regions.topo.json', lambda p:{'r':p['reg_istat_code_num'],'n':p['reg_name']})
prv=slim(f'{SRC}/limits_IT_provinces.topo.json', lambda p:{'p':p['prov_istat_code_num'],'s':p['prov_acr'],'n':p['prov_name'],'r':p['reg_istat_code_num']})
json.dump(reg,open(f'{OUT}/regioni.json','w'),separators=(',',':'))
json.dump(prv,open(f'{OUT}/province.json','w'),separators=(',',':'))
cj={c['codice']:c for c in json.load(open('/tmp/geo/cj/comuni.json'))}
cjn={(c['nome'].lower(),c['sigla']):c for c in cj.values()}
lista=[]; nocap=0
for f in sorted(glob.glob(f'{SRC}/limits_P_*_municipalities.topo.json')):
    t=json.load(open(f)); o=list(t['objects'].values())[0] if t.get('objects') else None
    if not o or not o.get('geometries'): continue
    pnum=None
    for g in o['geometries']:
        p=g.get('properties') or {}
        if not p.get('com_istat_code'): continue
        pnum=p['prov_istat_code_num']
        c=cj.get(p['com_istat_code']) or cjn.get((p['name'].lower(),p['prov_acr']))
        caps=(c or {}).get('cap') or []
        if not caps: nocap+=1
        lista.append([p['com_istat_code'],p['name'],p['prov_acr'],p['prov_istat_code_num'],p['reg_istat_code_num'],caps[0] if len(caps)==1 else (caps[0]+'-'+caps[-1] if caps else ''), (c or {}).get('codiceCatastale') or p.get('com_catasto_code') or ''])
    if pnum is None: continue
    t2=slim(f, lambda p:{'c':p.get('com_istat_code'),'n':p.get('name')})
    json.dump(t2,open(f'{OUT}/comuni/{pnum}.json','w'),separators=(',',':'))
lista.sort(key=lambda x:x[1])
json.dump({'v':1,'fonte':'ISTAT / Openpolis (CC-BY 4.0)','campi':['istat','nome','sigla','prov','reg','cap','catasto'],'c':lista},open(f'{OUT}/comuni.json','w'),separators=(',',':'),ensure_ascii=False)
print('comuni',len(lista),'senza cap',nocap)
