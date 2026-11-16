"""Combine vivify/board/*.png into one PDF for Marine: vivify/Vivify-Sports-website-preview.pdf"""
import glob, os
from PIL import Image
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/vivify/'
ims = []
for f in sorted(glob.glob(R + 'board/*.png')):
    im = Image.open(f).convert('RGB')
    ims.append(im.resize((1200, int(im.size[1] * 1200 / im.size[0])), Image.LANCZOS))
ims[0].save(R + 'Vivify-Sports-website-preview.pdf', save_all=True, append_images=ims[1:], resolution=100, quality=80)
print(len(ims), 'pages', os.path.getsize(R + 'Vivify-Sports-website-preview.pdf') // 1024, 'KB')
