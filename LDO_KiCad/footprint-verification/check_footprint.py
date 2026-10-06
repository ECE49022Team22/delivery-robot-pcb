"""Independent checks of KiCad-loaded geometry vs TI drawing 4218875/A.
Run with KiCad's bundled Python (pcbnew required).
This checks a library footprint, not a routed PCB or assembly process.
"""
from pathlib import Path
import json, hashlib
import pcbnew

HERE=Path(__file__).resolve().parent
lib=HERE.parent/'LDO_Power.pretty'
name='TI_DRB0008A_VSON8_3x3mm'
fp=pcbnew.FootprintLoad(str(lib),name)
assert fp is not None
mm=pcbnew.ToMM
def vec(v):return (round(mm(v.x),6),round(mm(v.y),6))
def close(a,b):return all(abs(x-y)<2e-6 for x,y in zip(a,b))
pads=list(fp.Pads())
expected={str(i+1):(-1.4,y) for i,y in enumerate([-.975,-.325,.325,.975])}
expected.update({str(i+5):(1.4,y) for i,y in enumerate([.975,.325,-.325,-.975])})
checks=[]
for n,pos in expected.items():
    p=[p for p in pads if p.GetNumber()==n]
    assert len(p)==1
    assert close(vec(p[0].GetPosition()),pos)
    assert close(vec(p[0].GetSize()),(.6,.31))
    assert {pcbnew.F_Cu,pcbnew.F_Mask,pcbnew.F_Paste}.issubset(set(p[0].GetLayerSet().Seq()))
    assert abs(mm(p[0].GetRoundRectCornerRadius())-.05)<2e-6
checks.append('PASS: pads 1-8 positions, size, pitch, numbering, copper/mask/paste layers and R0.05 corners')
ep=[p for p in pads if p.GetNumber()=='9']
assert len(ep)==5
assert any(close(vec(p.GetPosition()),(0,0)) and close(vec(p.GetSize()),(1.5,1.75)) for p in ep)
for x in [-.325,.325]:
    for y in [-1.3125,1.3125]:
        assert any(close(vec(p.GetPosition()),(x,y)) and close(vec(p.GetSize()),(.23,.975)) for p in ep)
assert all(p.IsOnLayer(pcbnew.F_Cu) and p.IsOnLayer(pcbnew.F_Mask) and not p.IsOnLayer(pcbnew.F_Paste) for p in ep)
checks.append('PASS: central EP 1.5 x 1.75 and four 0.23-wide copper extensions; all assigned ground pad 9')
paste=[p for p in pads if not p.GetNumber()]
assert len(paste)==5
assert any(close(vec(p.GetPosition()),(0,0)) and close(vec(p.GetSize()),(1.34,1.55)) for p in paste)
for x in [-.325,.325]:
    for y in [-.9745,.9745]:
        assert any(close(vec(p.GetPosition()),(x,y)) and close(vec(p.GetSize()),(.23,.725)) for p in paste)
assert all(set(p.GetLayerSet().Seq())=={pcbnew.F_Paste} for p in paste)
checks.append('PASS: TI stencil central aperture and four tabs; overall tab extent 2.674 mm')
# Footprint-level override fixes mask/paste behavior independently of board defaults.
assert abs(mm(fp.GetLocalSolderMaskMargin())-.07)<2e-6
assert mm(fp.GetLocalSolderPasteMargin())==0
assert fp.GetLocalSolderPasteMarginRatio()==0
checks.append('PASS: explicit +0.07 mm mask expansion; no additional paste shrink')

# A small board for visual inspection/export only, NOT a production PCB.
board=pcbnew.BOARD()
board.Add(fp)
fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(20),pcbnew.FromMM(20)))
fp.SetReference('U1');fp.SetValue('TPS7A8101DRBR')
for n in [str(i) for i in range(1,10)]:
    net=pcbnew.NETINFO_ITEM(board,'GND' if n=='9' else 'PIN_'+n)
    board.Add(net)
    for p in fp.Pads():
        if p.GetNumber()==n:p.SetNet(net)
pcbnew.SaveBoard(str(HERE/'FOOTPRINT_CHECK_ONLY.kicad_pcb'),board)
file=lib/(name+'.kicad_mod')
report={'source':'TI TPS7A8101 datasheet, DRB0008A drawing 4218875/A, pages 25-27; pin table page 3',
 'footprint_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),
 'datasheet_sha256':hashlib.sha256((HERE/'TI-TPS7A8101-datasheet.pdf').read_bytes()).hexdigest(),
 'checks':checks,
 'scope':'Nominal footprint geometry and pin mapping. Not manufacturing, thermal or assembly approval.'}
(HERE/'geometry-check-results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('\n'.join(checks))
