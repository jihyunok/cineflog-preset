from PIL import Image, ImageDraw, ImageFont, ImageEnhance
FB="C:/Users/uere/AppData/Local/Microsoft/Windows/Fonts/Cafe24Dangdanghae.ttf"
def mk(src,out,cx,cy,zoom,top,bottom="결말까지 한 번에 몰아보기"):
    im=Image.open(src).convert("RGB"); W,H=im.size; ch=H/zoom; cw=ch*16/9
    x0=max(0,min(W-cw,cx*W-cw/2)); y0=max(0,min(H-ch,cy*H-ch/2))
    im=im.crop((int(x0),int(y0),int(x0+cw),int(y0+ch))).resize((1280,720),Image.LANCZOS)
    im=ImageEnhance.Brightness(im).enhance(1.1); im=ImageEnhance.Contrast(im).enhance(1.12); im=ImageEnhance.Color(im).enhance(1.15); im=ImageEnhance.Sharpness(im).enhance(1.5)
    d=ImageDraw.Draw(im)
    f=ImageFont.truetype(FB,96); w=d.textlength(bottom,font=f); d.text(((1280-w)/2,575),bottom,font=f,fill=(255,230,30),stroke_width=9,stroke_fill=(0,0,0))
    f2=ImageFont.truetype(FB,74); w=d.textlength(top,font=f2); d.text(((1280-w)/2,28),top,font=f2,fill=(240,20,20),stroke_width=8,stroke_fill=(0,0,0))
    im.save(out,quality=93)
mk("f480.png","n1.jpg",.45,.5,1.1,"15년 만에 돌아온 재벌 외동딸")
mk("f5410.png","n2.jpg",.35,.5,1.15,"재벌가의 숨겨진 살인")
mk("f11790.png","n3.jpg",.6,.5,1.15,"새엄마를 의심하는 재벌 딸")
mk("f6860.png","n4.jpg",.75,.5,1.2,"엄마를 죽인 범인은 가족 안에")
