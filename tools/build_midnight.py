"""Hand-drawn 12x8 Halloween show. Requires Pillow; no hardware dependencies.

Run: python tools/build_midnight.py --output assets --preview PREVIEW_DIRECTORY
Every animation is authored on the physical LED grid, without resampling.
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw

PALETTE = {'.': (0,0,0), 'O': (255,115,0), 'Y': (255,255,0),
           'G': (0,255,0), 'R': (255,5,5), 'W': (192,192,192),
           'P': (255,0,255)}
# Native 4x6 lettering: one empty row above and below, one column spacing.
FONT = {
'A':'0110/1001/1001/1111/1001/1001', 'B':'1110/1001/1110/1001/1001/1110',
'C':'0111/1000/1000/1000/1000/0111', 'D':'1110/1001/1001/1001/1001/1110',
'E':'1111/1000/1110/1000/1000/1111', 'F':'1111/1000/1110/1000/1000/1000',
'G':'0111/1000/1000/1011/1001/0111', 'H':'1001/1001/1111/1001/1001/1001',
'I':'111/010/010/010/010/111', 'J':'0011/0001/0001/0001/1001/0110',
'K':'1001/1010/1100/1010/1001/1001', 'L':'1000/1000/1000/1000/1000/1111',
'M':'10001/11011/10101/10001/10001/10001', 'N':'1001/1101/1101/1011/1011/1001',
'O':'0110/1001/1001/1001/1001/0110', 'P':'1110/1001/1001/1110/1000/1000',
'Q':'0110/1001/1001/1001/1010/0101', 'R':'1110/1001/1001/1110/1010/1001',
'S':'0111/1000/0110/0001/0001/1110', 'T':'1111/0110/0110/0110/0110/0110',
'U':'1001/1001/1001/1001/1001/0110', 'V':'1001/1001/1001/1001/0110/0110',
'W':'10001/10001/10001/10101/11011/10001', 'X':'1001/1001/0110/0110/1001/1001',
'Y':'1001/1001/0110/0010/0010/0010', 'Z':'1111/0001/0010/0100/1000/1111',
'!':'1/1/1/1/0/1', ' ':'000/000/000/000/000/000'}

def blank():
    return Image.new('RGB', (12,8))

def sprite(pattern):
    rows = pattern.split('/')
    assert len(rows) == 8 and all(len(row) == 12 for row in rows), rows
    im = blank()
    for y,row in enumerate(rows):
        for x,c in enumerate(row):
            im.putpixel((x,y), PALETTE[c])
    return im

def points(im, coords, color):
    for x,y in coords:
        if 0 <= x < 12 and 0 <= y < 8:
            im.putpixel((x,y), PALETTE[color])
    return im

PUMPKIN = '.....GG...../..OOOOOOOO../.OOOOOOOOOO./.OO..OO..OO./.OOOOOOOOOO./.O.O.OO.O.O./..OO....OO../...OOOOOO...'
GHOST = '....WWWW..../...WWWWWW.../...W.WW.W.../..WWWWWWWW../..WWW..WWW../..WWWWWWWW../...WWWWWW.../...W.WW.W...'
SKULL = '...WWWWWW.../..WWWWWWWW../..W..WW..W../..W..WW..W../..WWWWWWWW../...WW..WW.../....WWWW..../....W.WW....'
CAT = '..P......P../..PP....PP../..PPPPPPPP../..PYYPPYYP../..P.YPPY.P../...PPPPPP.../....P..P..../.....PP.....'
BAT_UP = '.P........P./.PP......PP./..PP.PP.PP../..PPPPPPPP../...PPYYPP.../....PPPP..../.....PP...../............'
BAT_MID = '............/.....PP...../PP...PP...PP/PPPPPPPPPPPP/.PPPPYYPPPP./..P.PPPP.P../.....PP...../............'
BAT_DOWN = '............/.....PP...../....PPPP..../...PPYYPP.../..PPPPPPPP../.PPPP..PPPP./.PP......PP./.P........P.'
POTION = '............/............/............/..GGGGGGGG../.P.GGGGGG.P./..PGGGGGGP../...PPPPPP.../....P..P....'
SPIDER = '.....W....../.....W....../.....W....../..P..PP..P../...PPPPPP.../..PPPRRPPP../.P..PPPP..P./.P.P....P.P.'
CANDLE = '.....Y....../....YO....../.....O....../....WWWW..../....WOWW..../....WWWW..../....WWWW..../...OOOOOO...'

def pumpkin():
    frames=[]
    for t in range(48):
        im=sprite(PUMPKIN)
        if t%24 in (17,18):
            points(im,[(3,3),(4,3)],'O')
        if t%16 in (6,7,8):
            points(im,[(4,6),(5,6),(6,6),(7,6)],'Y')
        frames.append(im)
    return frames

def ghost():
    frames=[]
    for t in range(48):
        source=sprite(GHOST)
        if t%24 in (18,19):
            points(source,[(4,2),(7,2)],'W')
        im=blank()
        # Full silhouette stays inside the grid; no clipped feet.
        im.paste(source, ((0,1,0,-1)[(t//6)%4],0))
        frames.append(im)
    return frames

def skull():
    frames=[]
    for t in range(48):
        im=sprite(SKULL)
        if 12 <= t%32 < 26:
            points(im,[(3,3),(8,3)],'R')
        if t%16 >= 8:
            points(im,[(4,6),(5,6),(6,6),(7,6)],'.')
        frames.append(im)
    return frames

def cat():
    frames=[]
    for t in range(48):
        im=sprite(CAT)
        pupil=(0,1,0,-1)[(t//8)%4]
        points(im,[(3,3),(4,3),(7,3),(8,3),(3,4),(4,4),(7,4),(8,4)],'Y')
        points(im,[(3+(pupil>0),3),(7+(pupil>0),3),(3+(pupil>0),4),(7+(pupil>0),4)],'.')
        if t in (27,28,29):
            points(im,[(3,4),(4,4),(7,4),(8,4)],'P')
        frames.append(im)
    return frames

def bats():
    poses=[sprite(p) for p in (BAT_UP,BAT_MID,BAT_DOWN,BAT_MID)]
    return [poses[(t//2)%4].copy() for t in range(48)]

def potion():
    frames=[]
    for t in range(48):
        im=sprite(POTION)
        for x,phase in ((3,0),(6,3),(8,5)):
            y=2-((t//2+phase)%6)
            points(im,[(x,y)],'G')
        points(im,[(3+(t//3)%6,3)],'Y')
        frames.append(im)
    return frames

def spider():
    frames=[]
    for t in range(48):
        source=sprite(SPIDER)
        shift=(0,0,-1,-2,-1,0)[(t//4)%6]
        im=blank(); im.paste(source,(0,shift))
        points(im,[(5,y) for y in range(max(0,3+shift))],'W')
        if t%8>=4:
            points(im,[(1,7),(10,7)],'.')
            points(im,[(2,7),(9,7)],'P')
        frames.append(im)
    return frames

def candle():
    frames=[]
    for t in range(40):
        im=sprite(CANDLE)
        points(im,[(5,0)],'.')
        points(im,[(5+(t//3)%2,0)],'Y')
        points(im,[(5,3+(t//6)%4)],'O')
        frames.append(im)
    return frames

def eyes():
    frames=[]
    for t in range(40):
        im=blank()
        if t not in (18,19,20):
            points(im,[(x,y) for x in (2,3,4,7,8,9) for y in (3,4)],'G')
            px=(0,1,0,-1)[(t//7)%4]
            points(im,[(3+px,3),(3+px,4),(8+px,3),(8+px,4)],'.')
        frames.append(im)
    return frames

class Show:
    def __init__(self):
        self.parts=[blank()]; self.width=12; self.commands=['0000 speed 0.100']
        self.scenes=[]
    def append(self, im):
        self.parts.append(im); self.width+=im.width
    def scene(self, name, frames):
        # Include every frame in the flip range. Range ends at last frame start.
        self.commands.append(f'{self.width:04d}-{self.width+12*(len(frames)-1):04d} flip 0.150')
        for frame in frames: self.append(frame)
        self.scenes.append((name,frames))
        self.append(blank())
    def text(self, text, color):
        rows=[FONT[c].split('/') for c in text]
        im=Image.new('RGB',(sum(len(r[0])+1 for r in rows)+12,8))
        x=0
        for glyph in rows:
            for y,row in enumerate(glyph,1):
                for dx,c in enumerate(row):
                    if c=='1': im.putpixel((x+dx,y),PALETTE[color])
            x+=len(glyph[0])+1
        self.append(im)
    def render(self):
        out=Image.new('RGB',(self.width,8)); x=0
        for im in self.parts: out.paste(im,(x,0)); x+=im.width
        return out

def timeline(strip, commands, scroll=.1, flip=.15):
    """Exact viewport order of the existing player, including loop seam."""
    canvas=Image.new('RGB',(strip.width+12,8)); canvas.paste(strip)
    canvas.paste(strip.crop((0,0,12,8)),(strip.width,0))
    spans=[]
    for line in commands[1:]:
        span=line.split()[0]; a,b=map(int,span.split('-')); spans.append((a,b))
    x=0; frames=[]; durations=[]
    while x < strip.width:
        active=any(a<=x<=b for a,b in spans)
        frames.append(canvas.crop((x,0,x+12,8)))
        durations.append(round(1000*(flip if active else scroll)))
        x+=12 if active else 1
    return frames,durations

def led_view(im, scale=24):
    out=Image.new('RGB',(12*scale,8*scale),(5,6,9)); d=ImageDraw.Draw(out)
    for y in range(8):
        for x in range(12):
            rgb=im.getpixel((x,y)); color=rgb if any(rgb) else (16,17,21)
            d.rounded_rectangle((x*scale+3,y*scale+3,(x+1)*scale-4,(y+1)*scale-4),radius=5,fill=color)
    return out

def main():
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,default=Path('assets'))
    p.add_argument('--preview',type=Path)
    p.add_argument('--scroll',type=float,default=.1)
    p.add_argument('--animation',type=float,default=.15)
    args=p.parse_args()
    show=Show()
    program=[('Jack-o-lantern',pumpkin,'HAPPY HALLOWEEN','O'),
             ('Eyes in the dark',eyes,'BEWARE!','G'),
             ('Restless skull',skull,'BONE ZONE','W'),
             ('Bat swarm',bats,'BATS OUT!','P'),
             ('Ghost drifts past',ghost,'BOO!','W'),
             ('Witches brew',potion,'HOCUS POCUS','G'),
             ('Watching cat',cat,'MEOW!','Y'),
             ('Spider descends',spider,'CREEP IT REAL','P'),
             ('Melting candle',candle,'CANDY OR CHAOS','O'),
             ('Pumpkin returns',pumpkin,'TRICK OR TREAT','O'),
             ('Ghost farewell',ghost,'STAY SPOOKY!','W')]
    for name,fn,caption,color in program:
        show.text(caption,color); show.scene(name,fn())
    strip=show.render(); assert strip.width<=12000
    args.output.mkdir(parents=True,exist_ok=True)
    strip.save(args.output/'halloween_midnight.png')
    (args.output/'halloween_midnight.txt').write_text('\n'.join(show.commands)+'\n',encoding='ascii')
    frames,durations=timeline(strip,show.commands,args.scroll,args.animation)
    if args.preview:
        args.preview.mkdir(parents=True,exist_ok=True)
        # Full movie uses every one-pixel scroll step, with real playback timing.
        scaled=[led_view(f) for f in frames]
        scaled[0].save(args.preview/'midnight_full_preview.gif',save_all=True,append_images=scaled[1:],duration=durations,loop=0,optimize=True)
        # A shorter, representative preview includes whole messages, never just sprites.
        excerpt=Show()
        for index in (0,4,9):
            name,fn,caption,color=program[index]
            excerpt.text(caption,color); excerpt.scene(name,fn()[:16])
        excerpt_frames,excerpt_times=timeline(excerpt.render(),excerpt.commands,args.scroll,args.animation)
        excerpt_leds=[led_view(frame) for frame in excerpt_frames]
        excerpt_leds[0].save(args.preview/'midnight_messages_preview.gif',save_all=True,
                            append_images=excerpt_leds[1:],duration=excerpt_times,loop=0,optimize=True)
        highlights=[]
        board=Image.new('RGB',(720,((len(show.scenes)+2)//3)*184),(12,14,20)); d=ImageDraw.Draw(board)
        for i,(name,seq) in enumerate(show.scenes):
            highlights.extend(led_view(f) for f in seq[:32])
            x=(i%3)*240; y=(i//3)*184
            board.paste(led_view(seq[12],18),(x+12,y+10)); d.text((x+12,y+158),name,fill='white')
        board.save(args.preview/'midnight_storyboard.png')
        highlights[0].save(args.preview/'midnight_highlights.gif',save_all=True,append_images=highlights[1:],duration=round(args.animation*1000),loop=0,optimize=True)
    print(f'{strip.width}x8; {len(show.scenes)} scenes; {sum(durations)/1000:.1f} seconds at {args.scroll} scroll / {args.animation} animation')

if __name__=='__main__': main()
