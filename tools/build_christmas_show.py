"""Twenty distinct Christmas scenes, hand drawn for the 12x8 sign."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw
from build_midnight import Show, blank, points, PALETTE, led_view, timeline
from build_halloween_show import html_preview

# Each source cell is one LED; black is deliberately part of the composition.
ART={
'tree':('.....Y....../....GG....../...GGGG...../....GG....../..GGGGGG..../...GGGG...../.GGGGGGGG.../.....OO.....'),
'santa':('....RRRR..../...RRRRRW.../..WWWWWWWW../..WO.OO.OW../..WOOOOOOW../...WWRRWW.../....WWWW..../.....WW.....'),
'snowman':('....PPPP..../...PPPPPP.../....WWWW..../....W.WW..../....WWOO..../...WRRRRW.../..WWWWWWWW../...WW.WW....'),
'reindeer':('..O.O..O.O../...OO..OO.../....OOOO..../...OOOOOO.../...O.OO.O.../...OOOROO.../....OOOO..../.....OO.....'),
'gift':('...YY..YY.../....YYYY..../..RRRYYRRR../..RRRYYRRR../..YYYYYYYY../..RRRYYRRR../..RRRYYRRR../..RRRYYRRR..'),
'bells':('.....RR...../....RRRR..../..YYY..YYY../..YYY..YYY../..YYY..YYY../.YYYYYYYYYY./...Y....Y.../............'),
'wreath':('....GGGG..../...GG..GG.../..GG....GG../..G......G../..G......G../..GG....GG../...GGRRGG.../....RRRR....'),
'cane':('....WWRR..../...WW..RR.../...WW..RR.../.......WW.../.......RR.../.......WW.../.......RR.../.......WW...'),
'stocking':('....WWWW..../....WWWW..../....RRRR..../....RRRR..../....RRRR..../..RRRRRR..../..RRRRRR..../...RRRR.....'),
'candle':('.....Y....../....YO....../.....O....../....RRRR..../....RYRR..../....RRRR..../....RRRR..../..GGGGGGGG..'),
'gingerbread':('....OOOO..../....O..O..../....OOOO..../..OOOOOOOO../....OWWO..../....OOOO..../....O..O..../...OO..OO...'),
'train':('..WW......../.WW....R..../..R...RRR.../..RRRRRRR.../.RRRRRWRR.../.RRRRRRRR.../..Y.Y.Y.Y.../OOOOOOOOOOOO'),
'house':('.....WW...../....WWWW..../...WWWWWW.../..WWWWWWWW../...ORROOR.../...ORROOR.../...OOOOOR.../...OO..OR...'),
'bauble':('.....YY...../.....WW...../...RRRRRR.../..RRRRRRRR../..RWWWWWWR../..RRRRRRRR../...RRRRRR.../....RRRR....'),
'star':('.....YY...../.....YY...../..YYYYYYYY../...YYYYYY.../....YYYY..../...YYYYYY.../..YYY..YYY../..YY....YY..'),
'sleigh':('............/.....WW...../.....RR...../..YRRRRRR.../..RRRRRRRR../..RRRRRRR.../...Y....Y.../..YYYYYYYYY.'),
'penguin':('....WWWW..../...WWWWWW.../...W.WW.W.../...WWYYWW.../..PWWWWWWP../..PWWWWWWP../...WWWWWW.../...YY..YY...'),
'fireplace':('.OOOOOOOOOO./.O........O./.O........O./.O...Y....O./.O..YY.O..O./.O.OYYOO..O./.O.OOOOOO.O./.OOOOOOOOOO.'),
'snowflake':('..W..W..W.../...W.W.W..../....WWW...../.WWWWWWWWW../....WWW...../...W.W.W..../..W..W..W.../.....W......'),
'globe':('....WWWW..../...W....W.../..W......W../..W..G...W../..W.GGG..W../...WGGGGW.../....OOOO..../...OOOOOO...')}


def art(name):
    rows=ART[name].split('/');assert len(rows)==8 and all(len(r)==12 for r in rows),(name,rows)
    im=blank()
    for y,row in enumerate(rows):
        for x,c in enumerate(row):im.putpixel((x,y),PALETTE[c])
    return im


def frames(name):
    result=[]
    for t in range(32):
        im=art(name)
        if name=='tree':
            for j,(x,y) in enumerate(((4,2),(6,4),(3,6),(7,6))):
                points(im,[(x,y)],'R' if (t//6+j)%2 else 'Y')
        elif name=='santa':
            if 12<=t<17:points(im,[(4,3)],'O')
            if t>=18:points(im,[(1,5),(0,3+(t//3)%2)],'W')
        elif name=='snowman':
            points(im,[(1,5),(0,3+(t//4)%2),(10,5),(11,4)],'O')
            points(im,[(6,6)],'.')
        elif name=='reindeer':
            points(im,[(6,5)],'R' if t%16<10 else 'O')
            if 18<=t<23:points(im,[(4,4)],'O')
        elif name=='gift':
            # Lid lifts, revealing a yellow star, then closes again.
            lift=(0,0,1,2,2,2,1,0)[t//4]
            if lift:
                lid=im.crop((2,0,10,3));points(im,[(x,y) for y in range(3) for x in range(2,10)],'.')
                im.paste(lid,(2,-lift))
                points(im,[(5,2),(4,3),(5,3),(6,3),(5,4)],'Y')
        elif name=='bells':
            shift=(0,1,0,-1)[(t//4)%4];moved=blank();moved.paste(im,(shift,0));im=moved
        elif name=='wreath':
            for j,(x,y) in enumerate(((4,0),(8,2),(7,6),(2,4))):
                points(im,[(x,y)],'R' if (t//8+j)%2 else 'Y')
        elif name=='cane':
            # Red and white stripes travel down the straight part.
            for y in range(3,8):points(im,[(7,y),(8,y)],'W' if (y+t//3)%4<2 else 'R')
        elif name=='stocking':
            if t>=8:
                rise=min(2,(t-8)//4)
                points(im,[(5,2-rise),(6,2-rise)],'Y')
            if t>=20:points(im,[(8,1),(9,0),(10,1),(9,2)],'Y')
        elif name=='candle':
            points(im,[(5,0)],'.');points(im,[(5+(t//4)%2,0)],'Y')
            points(im,[(5,3+(t//6)%4)],'Y')
        elif name=='gingerbread':
            points(im,[(2,3),(9,3)],'.')
            points(im,[(2,2 if t%12<6 else 4),(9,4 if t%12<6 else 2)],'O')
            points(im,[(5,4),(6,5)],'W')
        elif name=='train':
            points(im,[(x,y) for y in range(2) for x in range(4)],'.')
            points(im,[(2-(t//3)%3,1),(3-(t//4)%4,0)],'W')
            for x in (2,4,6,8):points(im,[(x,6)],'Y' if (t//3+x//2)%2 else 'W')
        elif name=='house':
            for j,x in enumerate((3,6,9)):
                points(im,[(x,(t//3+j*3)%8)],'W')
            points(im,[(4,4),(5,4),(4,5),(5,5)],'Y')
        elif name=='bauble':
            x=3+(t//3)%6;points(im,[(x,3),(x,5)],'W')
        elif name=='star':
            for j,(x,y) in enumerate(((0,1),(10,1),(0,6),(11,6))):
                if (t//5+j)%3==0:points(im,[(x,y)],'W')
        elif name=='sleigh':
            x=12-t if t<12 else (0 if t<22 else -(t-21))
            moved=blank();moved.paste(im,(x,0));im=moved
        elif name=='penguin':
            points(im,[(2,4),(2,5),(9,4),(9,5)],'.')
            points(im,[(2,3+(t//4)%2),(9,4-(t//4)%2)],'P')
            shift=(0,0,1,1,0,0,-1,-1)[t//4];moved=blank();moved.paste(im,(shift,0));im=moved
        elif name=='fireplace':
            points(im,[(5,3),(6,3),(4,4),(7,4)],'.')
            points(im,[(5,3+(t//3)%2),(6,4),(4,4+(t//4)%2)],'Y')
        elif name=='snowflake':
            if (t//8)%2:im=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            points(im,[(0,(t//3)%8),(11,(t//3+4)%8)],'W')
        elif name=='globe':
            for j,x in enumerate((4,6,7)):
                y=1+(t//3+j*2)%4
                if im.getpixel((x,y))==PALETTE['.']:points(im,[(x,y)],'W')
        result.append(im)
    return result


PROGRAM=[('tree','Tree lights','MERRY CHRISTMAS!','G'),
 ('santa','Santa waves','HO HO HO!','R'),
 ('snowman','Snowman waves','LET IT SNOW','W'),
 ('reindeer','Rudolph','RUDOLPH LIGHTS THE WAY','R'),
 ('gift','A present opens','DO NOT OPEN UNTIL CHRISTMAS','Y'),
 ('bells','Bells swing','JINGLE ALL THE WAY','Y'),
 ('wreath','Wreath lights','DECK THE HALLS','G'),
 ('cane','Candy cane stripes','CANDY CANE LANE','R'),
 ('stocking','Stocking surprise','HANG YOUR STOCKINGS','R'),
 ('candle','Candlelight','ALL IS CALM ALL IS BRIGHT','Y'),
 ('gingerbread','Gingerbread dance','FRESH FROM THE OVEN','O'),
 ('train','Christmas train','ALL ABOARD THE POLAR EXPRESS','R'),
 ('house','Snowy cottage','HOME FOR THE HOLIDAYS','G'),
 ('bauble','Shining ornament','MAKE THE SEASON BRIGHT','R'),
 ('star','Christmas star','STAR OF WONDER','Y'),
 ('sleigh','Santa takes flight','SANTA CLAUS IS COMING TO TOWN','R'),
 ('penguin','Penguin waddles','WALKING IN A WINTER WONDERLAND','W'),
 ('fireplace','Crackling fireplace','WARM WISHES ON COLD NIGHTS','O'),
 ('snowflake','Winter snowflake','DREAMING OF A WHITE CHRISTMAS','W'),
 ('globe','Snow globe','MERRY CHRISTMAS TO ALL','G')]


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--preview',type=Path,required=True);args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=True);args.preview.mkdir(parents=True,exist_ok=True)
    show=Show();chapters=[]
    for key,name,caption,color in PROGRAM:
        chapters.append({'name':name,'caption':caption,'start':show.width})
        show.text(caption,color);show.scene(name,frames(key))
    strip=show.render();assert strip.width<=12000
    target=args.output/'christmas_winter_magic.png';strip.save(target)
    target.with_suffix('.txt').write_text('\n'.join(show.commands)+'\n',encoding='ascii')
    html_preview(target,chapters,show.commands,.24,.29,args.preview/'christmas_winter_magic.html','Christmas Winter Magic')
    preview=args.preview/'christmas_winter_magic.html'
    preview.write_text(preview.read_text(encoding='utf-8').replace('#ff7300','#6fda8b').replace('#ffb04a','#f5d479'),encoding='utf-8')
    board=Image.new('RGB',(960,900),(12,14,20));d=ImageDraw.Draw(board)
    for i,(name,seq) in enumerate(show.scenes):
        x=i%4*240;y=i//4*180;board.paste(led_view(seq[16],18),(x+12,y))
        d.text((x+12,y+150),name,fill='white')
    board.save(args.preview/'christmas_storyboard.png')
    sample=Show()
    for i in (0,1,4,15):
        key,name,caption,color=PROGRAM[i];sample.text(caption,color);sample.scene(name,frames(key))
    seq,times=timeline(sample.render(),sample.commands,.24,.29)
    images=[led_view(f,16) for f in seq]
    images[0].save(args.preview/'christmas_messages.gif',save_all=True,append_images=images[1:],duration=times,loop=0,optimize=True)
    _,times=timeline(strip,show.commands,.24,.29)
    print(json.dumps({'width':strip.width,'chapters':len(PROGRAM),'seconds':sum(times)/1000}))

if __name__=='__main__':main()
