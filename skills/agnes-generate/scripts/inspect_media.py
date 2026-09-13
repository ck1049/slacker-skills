"""Local media inspection; every task-specific path is a command-line argument."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True)
    p.add_argument('--output-dir',required=True)
    p.add_argument('--kind',choices=['image','video'],required=True)
    p.add_argument('--sample-interval',type=float,default=0.5)
    args=p.parse_args()
    if args.sample_interval <= 0: p.error('--sample-interval must be positive')
    src=Path(args.input).resolve(); out=Path(args.output_dir).resolve()
    out.mkdir(parents=True,exist_ok=True)
    info={'input':str(src),'bytes':src.stat().st_size,'sha256':hashlib.sha256(src.read_bytes()).hexdigest()}
    from PIL import Image,ImageDraw
    if args.kind=='image':
        with Image.open(src) as im:
            im.load()
            info.update(width=im.width,height=im.height,format=im.format,mode=im.mode)
    else:
        import cv2
        cap=cv2.VideoCapture(str(src))
        if not cap.isOpened(): raise SystemExit('Video cannot be decoded')
        fps=cap.get(cv2.CAP_PROP_FPS)
        if fps<=0: raise SystemExit('Video FPS unavailable')
        declared=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        info.update(fps=fps,width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),declared_frames=declared)
        count=0; samples=[]
        while True:
            ok,frame=cap.read()
            if not ok: break
            if count%max(1,round(fps*args.sample_interval))==0:
                im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
                im.thumbnail((400,225))
                samples.append((count/fps,im))
            count+=1
        cap.release()
        info.update(decoded_frames=count,duration_seconds=count/fps,full_decode_pass=count==declared,visual_acceptance='not assessed')
        for start in range(0,len(samples),12):
            sheet=Image.new('RGB',(1600,750),'#171717')
            for i,(t,im) in enumerate(samples[start:start+12]):
                x=i%4*400;y=i//4*250
                sheet.paste(im,(x,y+25))
                ImageDraw.Draw(sheet).text((x+8,y+5),f'{t:.2f}s',fill='white')
            sheet.save(out/f'contact-sheet-{start//12+1:02}.jpg')
    (out/'media-check.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(info,ensure_ascii=False))


if __name__=='__main__': main()
