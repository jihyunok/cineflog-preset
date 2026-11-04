# 사용: bash frames.sh 이름 — zoom_args 확대 구역 20장(th/c/NN.png) + 번호 붙은 한눈에(th/csheet.jpg)
W=/d/cine_work/redub_$1; read cr dl < $W/zoom_args.txt; mkdir -p $W/th/c
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $W/src720.mp4 | cut -d. -f1)
for k in $(seq 1 20); do ffmpeg -v error -y -ss $((D*k/21)) -i $W/src720.mp4 -frames:v 1 -vf "crop=$cr,scale=1280:720" $W/th/c/$(printf %02d $k).png; done
python - $W <<'P'
import sys; from PIL import Image, ImageDraw, ImageFont
W=sys.argv[1]; S=Image.new("RGB",(5*320,4*180)); f=ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf",40)
for k in range(20):
    im=Image.open(f"{W}/th/c/{k+1:02d}.png").resize((320,180)); d=ImageDraw.Draw(im); d.text((8,4),f"{k+1:02d}",font=f,fill=(255,255,0),stroke_width=3,stroke_fill=(0,0,0)); S.paste(im,((k%5)*320,(k//5)*180))
S.save(f"{W}/th/csheet.jpg",quality=88)
P
echo frames $1
