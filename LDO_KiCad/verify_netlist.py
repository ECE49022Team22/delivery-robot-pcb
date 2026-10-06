"""Check actual KiCad-exported connectivity against the intended circuit."""
from pathlib import Path
import xml.etree.ElementTree as ET

p=Path(__file__).resolve().parent
root=ET.parse(p/'LDO-netlist.xml').getroot()
nets=[{(n.attrib['ref'],n.attrib['pin']) for n in net.findall('node')} for net in root.findall('./nets/net')]
expected=[
 {('C1','1'),('U1','5'),('U1','7'),('U1','8')},
 {('C2','1'),('C4','1'),('R1','1'),('U1','1'),('U1','2'),('TP1','1')},
 {('C1','2'),('C2','2'),('C3','2'),('R2','2'),('U1','4'),('U1','9')},
 {('C4','2'),('R1','2'),('R2','1'),('U1','3')},
 {('C3','1'),('U1','6')},
]
assert len(nets)==len(expected),nets
assert all(n in nets for n in expected),nets
assert {pin for net in nets for ref,pin in net if ref=='U1'}=={str(i) for i in range(1,10)}
print('PASS: five nets match intended circuit; all nine regulator pads connected correctly.')
