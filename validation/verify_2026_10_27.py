"""Verify the 2026-10-27 battery monitor / interior light change against the pre-change netlist.

Usage (from the repository root):
    kicad-cli sch export netlist --format kicadxml -o /tmp/before.xml delivery_robot_1.kicad_sch   # on the parent commit
    kicad-cli sch export netlist --format kicadxml -o system-netlist.xml delivery_robot_1.kicad_sch
    python validation/verify_2026_10_27.py [before.xml] [after.xml]
"""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

repo = Path(__file__).resolve().parent.parent
before_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/tmp/before.xml')
after_path = Path(sys.argv[2]) if len(sys.argv) > 2 else repo / 'system-netlist.xml'
old = ET.parse(before_path).getroot()
new = ET.parse(after_path).getroot()


def nets(root):
    return {n.attrib['name']: {(x.attrib['ref'], x.attrib['pin']) for x in n.findall('node')}
            for n in root.findall('./nets/net')}


def pin_map(net_map):
    return {node: name for name, nodes in net_map.items() for node in nodes}


def comps(root):
    out = {}
    for c in root.findall('./components/comp'):
        fields = {f.attrib['name']: (f.text or '') for f in c.findall('./fields/field')}
        out[c.attrib['ref']] = {'value': c.findtext('value'), 'footprint': c.findtext('footprint'), **fields}
    return out


a, b = nets(old), nets(new)
pa, pb = pin_map(a), pin_map(b)
ca, cb = comps(old), comps(new)
failures = []
passes = 0


def check(cond, msg):
    global passes
    if cond:
        passes += 1
    else:
        failures.append(msg)


BM = '/Battery Monitor/'
IL = '/Interior Light/'

# Pin -> net pairs from the two connection tables
expected = {
    # Change 1: battery current monitor
    ('J23', '1'): BM + 'SH_LOAD', ('R54', '1'): BM + 'SH_LOAD',
    ('R54', '2'): BM + 'INA_INP', ('U13', '10'): BM + 'INA_INP', ('C52', '1'): BM + 'INA_INP',
    ('J23', '2'): BM + 'SH_BATT', ('R55', '1'): BM + 'SH_BATT',
    ('R55', '2'): BM + 'INA_INN', ('U13', '9'): BM + 'INA_INN', ('C52', '2'): BM + 'INA_INN',
    ('U13', '6'): '+3V3', ('C53', '1'): '+3V3', ('C53', '2'): 'GND',
    ('U13', '7'): 'GND',
    ('U13', '8'): '+12V',
    ('U13', '2'): 'GND', ('U13', '1'): 'GND',
    ('U13', '5'): 'PB6', ('U13', '4'): 'PB7',
    ('R56', '2'): 'PB6', ('R56', '1'): '+3V3',
    ('R57', '2'): 'PB7', ('R57', '1'): '+3V3',
    ('U13', '3'): 'BATT_ALERT', ('R58', '2'): 'BATT_ALERT', ('R58', '1'): '+3V3',
    ('U1', '56'): 'BATT_ALERT',
    # Change 2: interior light
    ('U1', '57'): 'LIGHT_DATA', ('R59', '1'): 'LIGHT_DATA', ('R59', '2'): 'GND', ('U14', '2'): 'LIGHT_DATA',
    ('U14', '1'): 'GND',
    ('U14', '5'): '+5V_AUX', ('C54', '1'): '+5V_AUX', ('C54', '2'): 'GND',
    ('U14', '3'): 'GND',
    ('U14', '4'): IL + 'LIGHT_DIN_BUF', ('R60', '1'): IL + 'LIGHT_DIN_BUF',
    ('R60', '2'): IL + 'LIGHT_DIN', ('J24', '2'): IL + 'LIGHT_DIN',
    ('F12', '1'): '+5V_AUX', ('F12', '2'): IL + 'LIGHT_5V',
    ('J24', '1'): IL + 'LIGHT_5V', ('C55', '1'): IL + 'LIGHT_5V', ('C56', '1'): IL + 'LIGHT_5V',
    ('C55', '2'): 'GND', ('C56', '2'): 'GND',
    ('J24', '3'): 'GND',
}
for node, net in expected.items():
    check(pb.get(node) == net, f'{node[0]} pin {node[1]}: expected {net}, got {pb.get(node)}')

# D16 is bidirectional: one pin on LIGHT_DIN, the other on GND
check({pb.get(('D16', '1')), pb.get(('D16', '2'))} == {IL + 'LIGHT_DIN', 'GND'},
      f"D16: expected LIGHT_DIN / GND, got {pb.get(('D16', '1'))} / {pb.get(('D16', '2'))}")

# Shunt-sense nets carry nothing else (in particular, no GND tie at the inputs)
exact = {
    BM + 'SH_LOAD': {('J23', '1'), ('R54', '1')},
    BM + 'SH_BATT': {('J23', '2'), ('R55', '1')},
    BM + 'INA_INP': {('R54', '2'), ('U13', '10'), ('C52', '1')},
    BM + 'INA_INN': {('R55', '2'), ('U13', '9'), ('C52', '2')},
    'BATT_ALERT': {('U13', '3'), ('R58', '2'), ('U1', '56')},
    'LIGHT_DATA': {('U1', '57'), ('R59', '1'), ('U14', '2')},
    IL + 'LIGHT_DIN_BUF': {('U14', '4'), ('R60', '1')},
    IL + 'LIGHT_5V': {('F12', '2'), ('J24', '1'), ('C55', '1'), ('C56', '1')},
}
for net, nodes in exact.items():
    check(b.get(net) == nodes, f'{net}: expected {sorted(nodes)}, got {sorted(b.get(net, ()))}')
check(b.get(IL + 'LIGHT_DIN', set()) - {('D16', '1'), ('D16', '2')} == {('R60', '2'), ('J24', '2')},
      f"{IL}LIGHT_DIN: unexpected members {sorted(b.get(IL + 'LIGHT_DIN', ()))}")

# PB6 / PB7 gained exactly U13 plus its pull-up
check(b['PB6'] - a['PB6'] == {('U13', '5'), ('R56', '2')}, f"PB6 gained {sorted(b['PB6'] - a['PB6'])}")
check(b['PB7'] - a['PB7'] == {('U13', '4'), ('R57', '2')}, f"PB7 gained {sorted(b['PB7'] - a['PB7'])}")
check(a['PB6'] <= b['PB6'] and a['PB7'] <= b['PB7'], 'PB6/PB7 lost a pre-existing pin (J8 13/14, U1 58/59)')

# No pre-existing component pin changed nets, except U1 pins 56 and 57
allowed = {('U1', '56'), ('U1', '57')}
for node, net in pa.items():
    if node in allowed:
        continue
    check(pb.get(node) == net, f'pre-existing {node[0]} pin {node[1]} moved: {net} -> {pb.get(node)}')
check(pa[('U1', '56')].startswith('unconnected-') and pa[('U1', '57')].startswith('unconnected-'),
      'U1 pins 56/57 were not no-connect in the baseline')

# No net lost a pre-existing pin (the two U1 no-connect nets are the only ones allowed to vanish)
for net, nodes in a.items():
    if nodes <= allowed:
        continue
    check(nodes <= b.get(net, set()), f'net {net} lost {sorted(nodes - b.get(net, set()))}')

# Pre-existing parts unchanged (value, footprint, Manufacturer, MPN)
for ref, f in ca.items():
    g = cb.get(ref)
    check(g is not None, f'{ref} missing')
    if g:
        for k in ('value', 'footprint', 'Manufacturer', 'MPN'):
            check(f.get(k) == g.get(k), f'{ref} {k} changed: {f.get(k)!r} -> {g.get(k)!r}')

# New references: exactly the 18 parts, unique, Manufacturer and MPN filled, footprints as specified
new_parts = {
    'U13': 'Package_SO:TSSOP-10_3x3mm_P0.5mm',
    'J23': 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MPT-0,5-2-2.54_1x02_P2.54mm_Horizontal',
    'U14': 'Package_TO_SOT_SMD:SOT-23-5',
    'J24': 'Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical',
    'F12': 'Fuse:Fuse_1812_4532Metric',
    'D16': 'Diode_SMD:D_SOD-323',
    **{f'R{n}': 'Resistor_SMD:R_0805_2012Metric' for n in range(54, 61)},
    **{f'C{n}': 'Capacitor_SMD:C_0805_2012Metric' for n in range(52, 57)},
}
refs = [c.attrib['ref'] for c in new.findall('./components/comp')]
check(len(refs) == len(set(refs)), 'duplicate references in the new netlist')
added = set(cb) - set(ca)
check(added == set(new_parts), f'added parts {sorted(added)} != expected {sorted(new_parts)}')
for ref, fp in new_parts.items():
    g = cb.get(ref, {})
    check(bool(g.get('Manufacturer')) and bool(g.get('MPN')), f'{ref}: Manufacturer/MPN missing')
    check(bool(g.get('Datasheet')) and g.get('Datasheet') != '~' and bool(g.get('Description')),
          f'{ref}: Datasheet/Description missing')
    check(g.get('footprint') == fp, f"{ref}: footprint {g.get('footprint')} != {fp}")

if failures:
    print(f'FAIL: {len(failures)} of {passes + len(failures)} checks failed')
    for f in failures:
        print('  -', f)
    sys.exit(1)
print(f'PASS: {passes} checks. Both connection tables match pin for pin; INA_INP/INA_INN carry no GND tie; '
      f'PB6/PB7 gained exactly U13 + R56/R57; no pre-existing pin moved except U1 56/57; no net lost a pin; '
      f'{len(ca)} existing parts unchanged; {len(added)} new parts unique with Manufacturer, MPN, Datasheet, '
      f'Description and the specified footprints.')
