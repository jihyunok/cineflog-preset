# 사용: bash deliver_ja.sh 폴더이름(woo) 파일이름(우영우) — 일본어판
S=/d/cine_work/redub_$1_ja; N=$2
for T in "/g/내 드라이브/다시나레/일본어판"; do   # 11-03 사용자 「구글드라이브에만저장해」
  mkdir -p "$T"; rm -f "$T/${N}_일본어판.mp4"; cp "$S/final.mp4" "$T/${N}_일본어판.mp4"
  for k in 1 2; do cp "$S/th/j$k.jpg" "$T/${N}_일본어판_썸네일_$k.jpg"; done
  cp "$S/upload.txt" "$T/${N}_일본어판_업로드.txt"
done; ls -la "/g/내 드라이브/다시나레/일본어판/" | grep "$N"
