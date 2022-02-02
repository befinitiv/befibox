import cairo
import numpy
import qrcode
from PIL import Image
import math
from urllib.parse import urlparse, parse_qs
import requests
from io import BytesIO
import argparse

MM_TO_POINTS = 72 / 2.54 / 10



def get_yt_thumbnail(url):
	vid = video_id(url)

	img_url = 'https://img.youtube.com/vi/%s/0.jpg' % vid
	print(img_url)
	response = requests.get(img_url)
	img = Image.open(BytesIO(response.content))

	return img


def video_id(value):
	"""
	Examples:
	- http://youtu.be/SA2iWivDJiE
	- http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
	- http://www.youtube.com/embed/SA2iWivDJiE
	- http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
	"""
	query = urlparse(value)
	if query.hostname == 'youtu.be':
		return query.path[1:]
	if query.hostname in ('www.youtube.com', 'youtube.com'):
		if query.path == '/watch':
			p = parse_qs(query.query)
			return p['v'][0]
		if query.path[:7] == '/embed/':
			return query.path.split('/')[2]
		if query.path[:3] == '/v/':
			return query.path.split('/')[2]
	# fail?
	return None


def surface_from_pil(im, alpha=1.0, format=cairo.FORMAT_ARGB32):
	"""
	:param im: Pillow Image
	:param alpha: 0..1 alpha to add to non-alpha images
	:param format: Pixel format for output surface
	"""
	assert format in (cairo.FORMAT_RGB24, cairo.FORMAT_ARGB32), "Unsupported pixel format: %s" % format
	if 'A' not in im.getbands():
			im.putalpha(int(alpha * 256.))
	arr = bytearray(im.tobytes('raw', 'BGRa'))
	surface = cairo.ImageSurface.create_for_data(arr, format, im.width, im.height)
	return surface


def add_tag(cr, yt_url, off_x, off_y):
	cr.rectangle(*[MM_TO_POINTS*v for v in (0+off_x,0+off_y, 20, 10)])
	cr.rectangle(*[MM_TO_POINTS*v for v in (0+off_x,0+off_y+10, 20, 30)])
	cr.rectangle(*[MM_TO_POINTS*v for v in (0+off_x,0+off_y+10+30, 20, 30)])
	cr.rectangle(*[MM_TO_POINTS*v for v in (0+off_x,0+off_y+10+30+30, 20, 10)])
	cr.rectangle(*[MM_TO_POINTS*v for v in (0+off_x,0+off_y+10+30+30+10, 20, 20)])
	cr.stroke()
	
	surface = surface_from_pil(qrcode.make(yt_url).convert('RGB'))
	print(surface.get_width(), surface.get_height())

	cr.save()
	sfx, sfy = (20*MM_TO_POINTS/surface.get_width(), 20*MM_TO_POINTS/surface.get_height())
	cr.scale(sfx, sfy)
	cr.set_source_surface(surface, off_x*MM_TO_POINTS/sfx, (off_y+10+30+30+10)*MM_TO_POINTS/sfy)
	cr.paint()
	cr.restore()

	thumbnail_img = get_yt_thumbnail(yt_url)
	cr.save()
	surface = surface_from_pil(thumbnail_img.transpose(Image.ROTATE_180))
	sfx, sfy = (20*MM_TO_POINTS/surface.get_width(), 30*MM_TO_POINTS/surface.get_height())
	cr.scale(sfx, sfy)
	cr.set_source_surface(surface, off_x*MM_TO_POINTS/sfx, (off_y+10)*MM_TO_POINTS/sfy)
	cr.paint()
	cr.restore()

	cr.save()
	surface = surface_from_pil(thumbnail_img)
	sfx, sfy = (20*MM_TO_POINTS/surface.get_width(), 30*MM_TO_POINTS/surface.get_height())
	cr.scale(sfx, sfy)
	cr.set_source_surface(surface, off_x*MM_TO_POINTS/sfx, (off_y+10+30)*MM_TO_POINTS/sfy)
	cr.paint()
	cr.restore()


def draw():
	parser = argparse.ArgumentParser(description='Convert Youtube URLs to QR code tags')
	parser.add_argument('urls', metavar='URL', type=str, nargs='+', help='Youtube URLs')
	args = parser.parse_args()

	ps = cairo.PDFSurface("pdffile.pdf", 504, 648)
	cr = cairo.Context(ps)
	cr.set_source_rgb(0, 0, 0)
	cr.set_line_width(0.2 * MM_TO_POINTS)

	idx_x = 0
	idx_y = 0
	for url in args.urls:
		add_tag(cr, url, 10+idx_x*20, 10+idx_y*100)
		idx_x += 1
		if idx_x >= 8:
			idx_y += 1
			idx_x = 0 
	
	cr.show_page()

draw()
