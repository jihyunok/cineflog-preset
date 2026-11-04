import sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
FB="C:/Users/uere/AppData/Local/Microsoft/Windows/Fonts/Cafe24Dangdanghae.ttf"
def mk(src,out,cx,cy,zoom,red,acc,bottom="결말까지 한 번에 몰아보기"):
    im=Image.open(src).convert("RGB"); W,H=im.size
    ch=476; cw=ch*16/9
    x0=max(110,min(W-cw,cx*W-cw/2)); y0=44
    im=im.crop((int(x0),int(y0),int(x0+cw),int(y0+ch))).resize((1280,720),Image.LANCZOS)
    im=ImageEnhance.Brightness(im).enhance(1.12); im=ImageEnhance.Contrast(im).enhance(1.12); im=ImageEnhance.Color(im).enhance(1.2); im=ImageEnhance.Sharpness(im).enhance(1.6)
    d=ImageDraw.Draw(im)
    f=ImageFont.truetype(FB,92); tw=d.textlength(bottom,font=f)
    d.text(((1280-tw)/2,570),bottom,font=f,fill=(255,230,30),stroke_width=9,stroke_fill=(0,0,0))
    f2=ImageFont.truetype(FB,64)
    y=300
    for t,c in ((red,(240,20,20)),(acc,(80,240,60))):
        if not t: continue
        w=d.textlength(t,font=f2); d.text((1235-w,y),t,font=f2,fill=c,stroke_width=7,stroke_fill=(0,0,0)); y+=95
    im.save(out,quality=93)
mk("f9220.png","n1.jpg",.55,.40,1.05,"마피아 변호사의","복수")
mk("f6700.png","n2.jpg",.55,.36,1.0,"변호사가","마피아였다")
mk("f5440.png","n3.jpg",.40,.40,1.0,"악은 악으로","처단한다")
mk("f12580.png","n4.jpg",.60,.40,1.0,"이탈리아 마피아","한국 상륙")
