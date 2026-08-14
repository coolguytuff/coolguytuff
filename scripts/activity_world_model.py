from __future__ import annotations

import dataclasses
import math
import re
import xml.etree.ElementTree as ET
from collections import defaultdict

MAX_INPUT_BYTES = 3_000_000
CANVAS_W = 1600.0
BASE_Y = 620.0
LEFT = 720.0
RIGHT = 720.0
TRACK_STEP = 58.0
LEVEL_HEIGHT = {0: 42, 1: 68, 2: 98, 3: 132, 4: 174}

@dataclasses.dataclass(frozen=True)
class Cell:
    x: float
    y: float
    level: int

@dataclasses.dataclass(frozen=True)
class Week:
    x: float
    levels: tuple[int, ...]
    @property
    def score(self) -> int: return sum(self.levels)
    @property
    def terrain_level(self) -> int:
        s=self.score
        return 0 if s<=0 else 1 if s<=2 else 2 if s<=5 else 3 if s<=9 else 4
    @property
    def height(self) -> int: return LEVEL_HEIGHT[self.terrain_level]

@dataclasses.dataclass(frozen=True)
class RouteStep:
    source:int; target:int; state:str

@dataclasses.dataclass(frozen=True)
class Frame:
    t:float; x:float; y:float; state:str; direction:int
    sx:float=1.0; sy:float=1.0; phase:float=0.0; contact:str='none'

def _local(tag:str)->str: return tag.rsplit('}',1)[-1]
def fmt(v:float)->str:
    return str(int(round(v))) if abs(v-round(v))<1e-7 else f'{v:.4f}'.rstrip('0').rstrip('.')

def parse_cells(svg_text:str)->list[Cell]:
    if len(svg_text.encode('utf-8'))>MAX_INPUT_BYTES: raise ValueError('contribution SVG is too large')
    lower=svg_text.lower()
    if '<!doctype' in lower or '<!entity' in lower: raise ValueError('DTD/entity declarations are not accepted')
    class_to_level={m.group(1):int(m.group(2)) for m in re.finditer(r'\.c\.([A-Za-z0-9_-]+)\s*\{[^{}]*?fill\s*:\s*var\(--c([0-4])\)',svg_text,re.S)}
    try: root=ET.fromstring(svg_text)
    except ET.ParseError as exc: raise ValueError(f'invalid contribution SVG: {exc}') from exc
    cells=[]
    for el in root.iter():
        if _local(el.tag)!='rect': continue
        classes=el.attrib.get('class','').split()
        if 'c' not in classes: continue
        level=next((class_to_level[t] for t in classes if t in class_to_level),0)
        inline=re.search(r'var\(--c([0-4])\)',el.attrib.get('style',''))
        if inline: level=int(inline.group(1))
        try: x=float(el.attrib.get('x','nan')); y=float(el.attrib.get('y','nan'))
        except ValueError: continue
        if not(math.isfinite(x) and math.isfinite(y)) or abs(x)>100000 or abs(y)>100000: continue
        cells.append(Cell(x,y,max(0,min(4,level))))
    if not cells: raise ValueError('no contribution cells found in SVG')
    return cells

def group_weeks(cells:list[Cell])->list[Week]:
    grouped=defaultdict(dict)
    for c in cells:
        x=round(c.x,3); y=round(c.y,3); grouped[x][y]=max(grouped[x].get(y,0),c.level)
    ys=sorted({y for per in grouped.values() for y in per})[:7]
    return [Week(x,tuple(grouped[x].get(y,0) for y in ys)) for x in sorted(grouped)]

def _flat_transition_indices(heights:list[int])->set[int]:
    result=set(); start=0
    while start<len(heights):
        end=start+1
        while end<len(heights) and heights[end]==heights[start]: end+=1
        if end-start>=3: result.update(range(start,end-1))
        start=end
    return result

def classify_steps(heights:list[int])->list[str]:
    flat=_flat_transition_indices(heights); out=[]
    for i,(a,b) in enumerate(zip(heights,heights[1:])):
        out.append('sprint' if i in flat else 'climb' if b>a and b-a<=32 else 'jump')
    return out

def build_route(weeks:list[Week])->list[RouteStep]:
    h=[w.height for w in weeks]; route=[]
    for i,state in enumerate(classify_steps(h)): route.append(RouteStep(i,i+1,state))
    for ri,state in enumerate(classify_steps(list(reversed(h)))):
        source=len(weeks)-1-ri; route.append(RouteStep(source,source-1,state))
    return route

def position(index:int,week:Week,count:int)->tuple[float,float]:
    x=LEFT+index*TRACK_STEP; raise_y=8.0*math.sin((index/max(1,count-1))*math.pi)
    return x,BASE_Y-week.height-raise_y

def world_width(count:int)->float: return LEFT+max(0,count-1)*TRACK_STEP+RIGHT

def _ease(p:float)->float:
    p=max(0,min(1,p)); return p*p*(3-2*p)

def camera_values(frames:list[Frame],count:int)->str:
    min_x=min(0.0,CANVAS_W-world_width(count)); vals=[]
    for f in frames:
        cx=max(min_x,min(0.0,CANVAS_W*.46-f.x)); airborne=max(0.0,BASE_Y-f.y-175.0); cy=min(24.0,airborne*.10)
        vals.append(f'{fmt(cx)} {fmt(cy)}')
    return ';'.join(vals)

def _append(frames,dt,x,y,state,direction,sx=1.0,sy=1.0,phase=0.0,contact='none'):
    t=(frames[-1].t if frames else 0.0)+dt; frames.append(Frame(t,x,y,state,direction,sx,sy,phase,contact))

def _sample_transition(frames,source,target,state,direction,cycle_index):
    x0,y0=source; x1,y1=target
    if state=='sprint':
        duration=.34; samples=8
        for i in range(1,samples+1):
            p=i/samples; e=_ease(p); phase=(cycle_index+p)%1.0; x=x0+(x1-x0)*e; y=y0+(y1-y0)*e+4.5*abs(math.sin(phase*math.tau)); contact='left' if phase<.18 or phase>.92 else 'right' if .42<phase<.68 else 'none'; stretch=math.sin(phase*math.tau)
            _append(frames,duration/samples,x,y,state,direction,1+.035*stretch,1-.028*stretch,phase,contact)
        return 2.25,'foot'
    if state=='climb':
        duration=.92; samples=14; ledge_x=x1-direction*12; hang_y=y1+34
        for i in range(1,samples+1):
            p=i/samples
            if p<.20:
                q=_ease(p/.20); x=x0+(ledge_x-x0)*q; y=y0+(hang_y-y0)*q; contact='none'
            elif p<.48:
                q=(p-.20)/.28; x=ledge_x; y=hang_y+2.5*math.sin(q*math.pi); contact='hands'
            elif p<.80:
                q=_ease((p-.48)/.32); x=ledge_x+(x1-ledge_x)*q; y=hang_y+(y1+8-hang_y)*q; contact='hands'
            else:
                q=_ease((p-.80)/.20); x=x1; y=y1+8*(1-q); contact='left'
            compression=math.sin(min(1,p/.2)*math.pi); _append(frames,duration/samples,x,y,state,direction,1+.025*compression,1-.035*compression,p,contact)
        return 4.8,'hands'
    duration=.78; samples=14; apex_lift=62+min(34,abs(y1-y0)*.34)
    for i in range(1,samples+1):
        p=i/samples; e=_ease(p); x=x0+(x1-x0)*e; baseline=y0+(y1-y0)*e; y=baseline-math.sin(p*math.pi)*apex_lift
        if p<.15: sx,sy,contact=1.14,.82,'both'
        elif p<.78: sx,sy,contact=.96,1.08,'none'
        elif p<.92: sx,sy,contact=1.16,.82,'both'
        else: sx,sy,contact=1.05,.95,'both'
        _append(frames,duration/samples,x,y,state,direction,sx,sy,p,contact)
    _append(frames,.06,x1,y1,'idle',direction,phase=0,contact='both'); return 7.1,'feet'

def build_frames(weeks:list[Week]):
    if len(weeks)<2: raise ValueError('need at least two contribution weeks')
    pos=[position(i,w,len(weeks)) for i,w in enumerate(weeks)]; frames=[Frame(0,*pos[0],'idle',1,phase=0,contact='both')]; arrivals=defaultdict(list); _append(frames,.50,*pos[0],'idle',1,phase=0,contact='both'); cycle=0
    def transition(source,target,state,direction):
        nonlocal cycle
        amp,kind=_sample_transition(frames,pos[source],pos[target],state,direction,cycle); cycle+=1; arrivals[target].append((frames[-1].t,amp,kind))
    for i,state in enumerate(classify_steps([w.height for w in weeks])): transition(i,i+1,state,1)
    ex,ey=pos[-1]
    for i in range(1,9):
        q=i/8; _append(frames,.06,ex+12*math.sin(q*math.pi),ey+5*math.sin(q*math.pi),'turn',1 if q<.5 else -1,1+.12*math.sin(q*math.pi),1-.10*math.sin(q*math.pi),q,'both')
    _append(frames,.16,ex,ey,'idle',-1,phase=0,contact='both')
    for ri,state in enumerate(classify_steps([w.height for w in reversed(weeks)])):
        source=len(weeks)-1-ri; transition(source,source-1,state,-1)
    sx0,sy0=pos[0]
    for i in range(1,9):
        q=i/8; _append(frames,.06,sx0-12*math.sin(q*math.pi),sy0+5*math.sin(q*math.pi),'turn',-1 if q<.5 else 1,1+.12*math.sin(q*math.pi),1-.10*math.sin(q*math.pi),q,'both')
    _append(frames,.28,sx0,sy0,'idle',1,phase=0,contact='both')
    return frames,arrivals
