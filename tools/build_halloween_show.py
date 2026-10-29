"""Extended Halloween show and a chapter-selectable, exact-grid preview."""
import argparse
import base64
import json
from pathlib import Path
from PIL import Image, ImageDraw
from build_midnight import (Show, blank, sprite, points, pumpkin, ghost, skull,
                            bats, potion, cat, spider, candle, eyes, led_view, timeline)


def stamp(im, rows, x, y, color):
    points(im,[(x+dx,y+dy) for dy,row in enumerate(rows.split('/'))
               for dx,c in enumerate(row) if c=='#'],color)


def pumpkin_peekaboo():
    frames=[]
    for t in range(32):
        im=blank()
        # A tiny ghost peeks from a pumpkin, waves, then hides again.
        rise=[0,0,1,2,3,4,4,4,4,4,4,3,2,1,0,0][t//2]
        y=5-rise
        stamp(im,'.####./######/######/######',3,y,'W')
        points(im,[(4,y+1),(7,y+1)],'.')
        if 12<=t<22:
            points(im,[(2,y+2),(1,y+1+(t//3)%2)],'W')
        stamp(im,'.######./########/.######.',2,5,'O')
        points(im,[(4,6),(7,6)],'.')
        frames.append(im)
    return frames


def witch():
    frames=[]
    for t in range(36):
        im=blank()
        stamp(im,'.##./####/###./.##.',8,0,'Y')
        x=12-t if t<12 else (0 if t<24 else -(t-23))
        stamp(im,'..#./.###/#####',x+2,0,'P')
        stamp(im,'###./.###',x+3,3,'G')
        stamp(im,'.##/###',x+2,5,'P')
        stamp(im,'########/##......',x,6,'O')
        frames.append(im)
    return frames


def owl():
    frames=[]
    for t in range(32):
        im=blank()
        stamp(im,'#....#/##..##/######/######/######/.####./..##..',3,0,'O')
        stamp(im,'##..##/##..##',3,2,'Y')
        points(im,[(4,3),(7,3)],'.'); points(im,[(5,4),(6,4)],'Y')
        points(im,[(x,7) for x in range(1,11)],'P')
        if 12<=t<18: points(im,[(3,3),(4,3),(7,3),(8,3)],'O')
        if t>=20:
            y=3+(t//2)%3
            stamp(im,'##/##',1,y,'O'); stamp(im,'##/##',9,y,'O')
        frames.append(im)
    return frames


def haunted_door():
    frames=[]
    for t in range(36):
        im=blank()
        stamp(im,'...##.../..####../.######./########',2,0,'P')
        stamp(im,'########/########/########/########',2,4,'O')
        points(im,[(3,4),(8,4)],'Y')
        opening=min(3,max(0,(t-6)//3)) if t<25 else max(0,(35-t)//3)
        for x in range(5,5+opening):
            points(im,[(x,y) for y in range(4,8)],'.')
        if 17<=t<25:
            stamp(im,'.#./###/###',5,4,'W')
            points(im,[(5,5),(7,5)],'.')
        frames.append(im)
    return frames


def vampire():
    frames=[]
    for t in range(32):
        im=blank()
        stamp(im,'.####./######/######/######/.####.',3,0,'W')
        stamp(im,'######/.####./..##..',3,0,'P')
        points(im,[(4,3),(7,3)],'.')
        stamp(im,'..##../.####./######',3,5,'P')
        points(im,[(4,4),(5,4),(6,4),(7,4)],'.')
        points(im,[(4,5),(7,5)],'W')
        spread=(0,1,2,3,3,3,2,1)[(t//2)%8]
        for n in range(spread):
            stamp(im,'#/##/###',2-n,4+n%2,'P')
            stamp(im,'../.#/##',8+n,4+n%2,'P')
        if t<8: points(im,[(5,4),(6,4)],'W')
        frames.append(im)
    return frames


def monster():
    frames=[]
    for t in range(32):
        im=sprite('...PPPPPP.../..PGGGGGGP../..GGGGGGGG../..G.GGGG.G../.WGGGGGGGGW./..GG....GG../...GGGGGG.../...PPPPPP...')
        if t<8: points(im,[(3,3),(8,3)],'G')
        if 16<=t<24: points(im,[(4,5),(7,5)],'G')
        # A rounded smile and a clearly raised hand replace the sideways jitter.
        points(im,[(4,5),(7,5)],'G')
        points(im,[(4,5),(5,6),(6,6),(7,5)],'.')
        if t>=16:
            points(im,[(10,5),(10,4),(11,2+(t//3)%2)],'G')
        frames.append(im)
    return frames


def candy():
    frames=[]
    for t in range(32):
        im=blank()
        x=(0,1,0,-1)[(t//4)%4]
        stamp(im,'.####./######/######/.####.',3+x,2,'O')
        stamp(im,'#.#./.#.#/#.#./.#.#',4+x,2,'Y')
        spread=0 if t<16 else min(3,(t-16)//3)
        stamp(im,'#./##/##/#.',1-spread+x,2,'P')
        stamp(im,'.#/##/##/.#',9+spread+x,2,'P')
        frames.append(im)
    return frames


def skeleton():
    frames=[]
    for t in range(32):
        im=blank()
        stamp(im,'####/#..#/####/.##.',4,0,'W')
        stamp(im,'.##./####/.##.',4,4,'W')
        left_up=(t//4)%2==0
        points(im,[(3,4),(2,3 if left_up else 5),(8,4),(9,5 if left_up else 3)],'W')
        points(im,[(4 if left_up else 3,7),(8 if left_up else 7,7)],'W')
        frames.append(im)
    return frames


def moon_bat():
    frames=[]
    for t in range(32):
        im=blank()
        stamp(im,'..####../.######./########/########/########/########/.######./..####..',2,0,'Y')
        x=12-t
        # Dark silhouette crosses the moon, with purple tips outside its edge.
        stamp(im,'#...#/.###./..#..' if t%4<2 else '..#../#####/.#.#.',x,2,'P')
        frames.append(im)
    return frames


def pumpkin_reveal():
    frames=[]
    source=pumpkin()[0]
    for t in range(32):
        im=blank()
        if t<12:
            height=min(8,t)
            im.paste(source.crop((0,0,12,height)),(0,8-height))
        else:
            im=source.copy()
            if t>=20: points(im,[(3,3),(4,3),(7,3),(8,3),(4,6),(5,6),(6,6),(7,6)],'Y')
        frames.append(im)
    return frames


def ghost_flyby():
    source=ghost()[0]; frames=[]
    for t in range(36):
        im=blank(); x=12-t if t<12 else (0 if t<23 else -(t-22))
        im.paste(source,(x,0)); frames.append(im)
    return frames


def ghost_wave():
    frames=[]
    for t in range(32):
        im=ghost()[0].copy()
        # Wave outside the body so the motion stays visible on sparse LEDs.
        hand_y=(2,1,2,3)[(t//3)%4]
        points(im,[(1,3),(0,hand_y),(10,3)],'W')
        points(im,[(5,4),(6,4)],'W')
        points(im,[(4,4),(5,5),(6,5),(7,4)],'.')
        frames.append(im)
    return frames


def silly_skull():
    frames=[]
    for t in range(32):
        im=skull()[0].copy()
        # Friendly wink, with no glowing red eyes.
        if 12<=t<18: points(im,[(3,3),(4,3)],'W')
        points(im,[(4,6),(5,6),(6,6),(7,6)],'W')
        points(im,[(4,7),(7,7)],'.')
        frames.append(im)
    return frames


PROGRAM=[
 ('The pumpkin awakens',pumpkin_reveal,'HAPPY HALLOWEEN!','O'),
 ('A ghost opens the door',haunted_door,'WELCOME LITTLE MONSTERS','P'),
 ('Peekaboo eyes',eyes,'PEEK A BOO! WE SEE YOU','G'),
 ('Pumpkin peekaboo',pumpkin_peekaboo,'A LITTLE BOO JUST FOR YOU','W'),
 ('A skeleton dances',skeleton,'SHAKE YOUR BONES!','W'),
 ('A silly skull winks',silly_skull,'SILLY TO THE BONE','W'),
 ('Flight across the moon',moon_bat,'WHEN THE MOON IS FULL','Y'),
 ('Bats take flight',bats,'THE BATS COME OUT','P'),
 ('Witch on a broom',witch,'WITCH WAY TO THE CANDY','G'),
 ('The cauldron bubbles',potion,'BUBBLE BUBBLE CANDY TROUBLE','G'),
 ('A candle burns',candle,'LET YOUR LITTLE LIGHT SHINE','O'),
 ('Ghost passes through',ghost_flyby,'BOO! HELLO TO YOU','W'),
 ('A friendly ghost waves',ghost_wave,'WAVE TO OUR GHOST FRIEND','W'),
 ('Owl spreads its wings',owl,'HOOT HOOT! YOU LOOK CUTE','Y'),
 ('Cat watches the crowd',cat,'PURR FECT HALLOWEEN','P'),
 ('Spider drops in',spider,'COME HANG WITH US','P'),
 ('A monster smiles and waves',monster,'MONSTER HUGS FOR EVERYONE','G'),
 ('A vampire opens his cape',vampire,'FANGS FOR STOPPING BY','P'),
 ('Candy unwraps',candy,'TRICK OR TREAT!','O'),
 ('The pumpkin lights up',pumpkin_reveal,'GIVE US SOMETHING GOOD TO EAT','Y'),
 ('The last dance',skeleton,'DO THE MONSTER WIGGLE','W'),
 ('A ghost says goodbye',ghost_flyby,'BE KIND AND STAY SPOOKY','W'),
 ('Until next Halloween',pumpkin,'HAPPY HAUNTING!','O')]


def html_preview(strip_path, chapters, commands, scroll, animation, output):
    data={'image':base64.b64encode(strip_path.read_bytes()).decode(), 'chapters':chapters,
          'spans':[list(map(int,line.split()[0].split('-'))) for line in commands[1:]],
          'scroll':scroll,'animation':animation}
    html='''<!doctype html><meta charset="utf-8"><title>Halloween After Dark</title>
<style>body{background:#101017;color:#f3ede4;font:17px system-ui;max-width:850px;margin:40px auto;padding:20px}h1{color:#ff7300}canvas{width:100%;max-width:576px;image-rendering:pixelated;display:block;margin:25px auto}button,select{font:inherit;padding:10px;margin:5px;background:#252331;color:white;border:1px solid #63536e;border-radius:8px}#caption{font-size:25px;color:#ffb04a;min-height:35px}.muted{color:#bbb3c5}#progress{width:100%}</style>
<h1>Halloween After Dark</h1><p>Family edition · 23 playful scenes · Native 12 × 8 artwork</p>
<canvas id="screen" width="576" height="384"></canvas><div id="caption"></div>
<p id="scene" class="muted"></p><button id="play">Pause</button><button id="restart">Restart chapter</button>
<select id="chapters"></select><p><label>Preview speed <select id="rate"><option value="1">Actual timing</option><option value="2">2×</option><option value="3">3×</option></select></label></p>
<input id="progress" type="range" min="0" value="0"><p class="muted">The caption below the grid is a reading aid. Only the 96 dots appear on your sign. Preview colors cannot reproduce physical LED brightness exactly.</p>
<script>const data=DATA; const image=new Image();const c=document.querySelector('#screen'),ctx=c.getContext('2d');const off=document.createElement('canvas');off.width=12;off.height=8;const oc=off.getContext('2d',{willReadFrequently:true});let x=0,playing=true,timer;
const select=document.querySelector('#chapters'),slider=document.querySelector('#progress');
data.chapters.forEach((ch,i)=>{let o=new Option((i+1)+'. '+ch.name,i);select.add(o)});
function chapter(){let i=0;data.chapters.forEach((ch,j)=>{if(x>=ch.start)i=j});return i}
function draw(){oc.fillStyle='black';oc.fillRect(0,0,12,8);oc.drawImage(image,-x,0);if(x+12>image.width)oc.drawImage(image,image.width-x,0);let p=oc.getImageData(0,0,12,8).data;ctx.fillStyle='#050609';ctx.fillRect(0,0,c.width,c.height);for(let y=0;y<8;y++)for(let j=0;j<12;j++){let k=(y*12+j)*4,r=p[k],g=p[k+1],b=p[k+2];ctx.fillStyle=r+g+b?`rgb(${r},${g},${b})`:'#16151d';ctx.beginPath();ctx.arc(j*48+24,y*48+24,17,0,Math.PI*2);ctx.fill()}let i=chapter();select.value=i;document.querySelector('#caption').textContent=data.chapters[i].caption;document.querySelector('#scene').textContent=(i+1)+' / '+data.chapters.length+' — '+data.chapters[i].name;slider.value=x}
function tick(){clearTimeout(timer);draw();if(!playing)return;let flip=data.spans.some(([a,b])=>x>=a&&x<=b);timer=setTimeout(()=>{x=(x+(flip?12:1))%image.width;tick()},1000*(flip?data.animation:data.scroll)/Number(document.querySelector('#rate').value))}
document.querySelector('#play').onclick=()=>{playing=!playing;document.querySelector('#play').textContent=playing?'Pause':'Play';tick()};select.onchange=()=>{x=data.chapters[Number(select.value)].start;tick()};document.querySelector('#restart').onclick=()=>{x=data.chapters[chapter()].start;tick()};slider.oninput=()=>{x=Number(slider.value);let span=data.spans.find(([a,b])=>x>=a&&x<=b);if(span)x=span[0]+12*Math.floor((x-span[0])/12);tick()};image.onload=()=>{slider.max=image.width-1;tick()};image.src='data:image/png;base64,'+data.image;</script>'''
    output.write_text(html.replace('DATA',json.dumps(data)),encoding='utf-8')


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--preview',type=Path,required=True);p.add_argument('--scroll',type=float,default=.24)
    p.add_argument('--animation',type=float,default=.29);args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=True);args.preview.mkdir(parents=True,exist_ok=True)
    show=Show();chapters=[]
    for name,fn,caption,color in PROGRAM:
        chapters.append({'name':name,'caption':caption,'start':show.width})
        show.text(caption,color);show.scene(name,fn()[:34])
    strip=show.render();assert strip.width<=12000,strip.width
    target=args.output/'halloween_after_dark.png';strip.save(target)
    target.with_suffix('.txt').write_text('\n'.join(show.commands)+'\n',encoding='ascii')
    _,durations=timeline(strip,show.commands,args.scroll,args.animation)
    html_preview(target,chapters,show.commands,args.scroll,args.animation,args.preview/'halloween_after_dark.html')
    board=Image.new('RGB',(960,((len(PROGRAM)+3)//4)*180),(12,14,20));d=ImageDraw.Draw(board)
    for i,(name,frames) in enumerate(show.scenes):
        sample_index=12 if i in (2,6) else 20
        x=(i%4)*240;y=(i//4)*180;board.paste(led_view(frames[min(sample_index,len(frames)-1)],18),(x+12,y))
        d.text((x+12,y+150),name,fill='white')
    board.save(args.preview/'after_dark_storyboard.png')
    # Complete messages with short animation excerpts; no skipped text steps.
    sample=Show()
    for index in (0,3,8,16,18):
        name,fn,caption,color=PROGRAM[index];sample.text(caption,color);sample.scene(name,fn())
    frames,times=timeline(sample.render(),sample.commands,args.scroll,args.animation)
    images=[led_view(f,16) for f in frames]
    images[0].save(args.preview/'after_dark_messages.gif',save_all=True,append_images=images[1:],duration=times,loop=0,optimize=True)
    manifest={'width':strip.width,'scenes':len(PROGRAM),'seconds':sum(durations)/1000,'chapters':chapters}
    (args.preview/'after_dark_chapters.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps({k:v for k,v in manifest.items() if k!='chapters'}))

if __name__=='__main__':main()
