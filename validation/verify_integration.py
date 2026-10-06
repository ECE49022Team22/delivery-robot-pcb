from pathlib import Path
import xml.etree.ElementTree as ET
p=Path(__file__).resolve().parent
old=ET.parse(p/'before-integration.xml').getroot()
new=ET.parse(p.parent/'system-netlist.xml').getroot()
def nets(root):
 return {n.attrib['name']:{(x.attrib['ref'],x.attrib['pin']) for x in n.findall('node')} for n in root.findall('./nets/net')}
a,b=nets(old),nets(new)
added={'U4','R8','R9','C24','C25','C26','C27'}
expected={k:set(v) for k,v in a.items() if k!='VDD'}
expected['+3V3']|=a['VDD']
existing={k:{n for n in v if n[0] not in added} for k,v in b.items()}
existing={k:v for k,v in existing.items() if v}
assert existing==expected, 'Existing connectivity changed beyond intended VDD/3V3 merge'
ldo={
 '+5V, 2A':{('U4','5'),('U4','7'),('U4','8'),('C24','1')},
 '+3V3':{('U4','1'),('U4','2'),('C25','1'),('C27','1'),('R8','1')},
 'GND':{('U4','4'),('U4','9'),('C24','2'),('C25','2'),('C26','2'),('R9','2')},
 'Net-(U4-FB)':{('U4','3'),('R8','2'),('R9','1'),('C27','2')},
 'Net-(U4-NR)':{('U4','6'),('C26','1')}}
assert {k:{n for n in v if n[0] in added} for k,v in b.items() if any(n[0] in added for n in v)}==ldo
assert all(('U1',pin) in b['+3V3'] for pin in ('1','19','32','48','64'))
assert ('FB2','2') in b['+3V3'] and ('FB2','1') in b['+3.3VA']
components=new.findall('./components/comp')
refs=[c.attrib['ref'] for c in components]
assert len(refs)==len(set(refs)), 'Duplicate references'
oldvalues={c.attrib['ref']:c.findtext('value') for c in old.findall('./components/comp')}
newvalues={c.attrib['ref']:c.findtext('value') for c in components if c.attrib['ref'] not in added}
assert oldvalues==newvalues,'Existing component values changed'
print('PASS: existing circuit preserved except intended VDD/3V3 merge; five LDO nets and all nine regulator pads verified; MCU supply and analog filter input powered; unique references.')