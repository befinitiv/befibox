import numpy
import shlex
import subprocess
from pyzbar.pyzbar import decode, ZBarSymbol
import math
import fluidsynth
import threading
import time
import mpd
import alsaaudio


fs = fluidsynth.Synth()
fs.start(driver='alsa')
sfid = fs.sfload('/usr/share/sounds/sf2/FluidR3_GM.sf2')
fs.program_select(0, sfid, 0, 0)
fs.program_select(1, sfid, 0, 11)
seq = fluidsynth.Sequencer()
sid = seq.register_fluidsynth(fs)

client = mpd.MPDClient()
client.connect("localhost", 6600)
client.stop()

# Mopidy is too slow for volume change, so we use alsa
m = alsaaudio.Mixer('Headphone')
m.setvolume(80)



def ack_sound():
	global seq, sid
	current_time = seq.get_tick()
	seq.note_on(current_time, 1, 72, 127, dest=sid)
	seq.note_on(current_time+150, 1, 84, 127, dest=sid)

def start_sound():
	global seq, sid
	current_time = seq.get_tick()
	seq.note_on(current_time, 1, 60, 127, dest=sid)
	seq.note_on(current_time+200, 1, 64, 127, dest=sid)
	seq.note_on(current_time+400, 1, 67, 127, dest=sid)

class Code:
	def __init__(self, data, bbox, angle_event_size = 3):
		self.data = data
		self.bbox = bbox
		self.not_seen_cnt = 0
		self.angle_offset = 0

		self.initial_angle = self.angle() 
		self.last_angle = self.initial_angle
		self.last_angle_event_angle = self.initial_angle
		self.ANGLE_EVENT_SIZE = angle_event_size

	def angle(self):
		vec = [self.bbox[0][0]-self.bbox[1][0], self.bbox[0][1]-self.bbox[1][1]]
		ang = math.atan2(vec[0], vec[1])*180/math.pi-90+self.angle_offset
		return ang

	def angle_event(self):
		pass

	def update(self, bbox):
		self.bbox = bbox
		if abs(self.angle() - self.last_angle) >= 45:
			if self.angle() - self.last_angle > 0:
				self.angle_offset -= 90
			else:
				self.angle_offset += 90

		self.last_angle = self.angle()


		if abs(self.last_angle_event_angle - self.angle()) >= self.ANGLE_EVENT_SIZE:
			self.angle_event()
			self.last_angle_event_angle = self.angle()
		


class YoutubeCode(Code):
	def __init__(self, data, bbox):
		super().__init__(data, bbox)
		ack_sound()
		#MPD play
		client.clear()
		client.add('yt:'+data)
		client.play()

	def __del__(self):
		#MPD stop
		client.stop()

class VolumeCode(Code):
	def __init__(self, data, bbox):
		super().__init__(data, bbox)

	def angle_event(self):
		current_volume = m.getvolume()[0]
		if self.last_angle_event_angle - self.angle() > 0:
			print('Increasing volume')
			current_volume = min(current_volume+3, 100)
		else:
			print('Decreasing volume')
			current_volume = max(current_volume-3, 0)
		m.setvolume(current_volume)

class SeekCode(Code):
	def __init__(self, data, bbox):
		super().__init__(data, bbox)
		ack_sound()

	def angle_event(self):
		if self.last_angle_event_angle - self.angle() > 0:
			print('Seeking +10s')
			client.seekcur('+10')
		else:
			print('Seeking -10s')
			client.seekcur('-10')


class InstrumentCode(Code):
	def __init__(self, data, bbox):
		super().__init__(data, bbox)
		print(data)

		self.note = 60

	def angle_event(self):
		global fs
		if self.last_angle_event_angle - self.angle() > 0:
			self.note += 1
		else:
			self.note -= 1
		
		fs.noteon(0, self.note, 127)


MAX_NOT_SEEN=2
codes = dict()


frame = None
def decodethreadfn():
	global codes, MAX_NOT_SEEN, frame

    
	while True:
		if frame is None:
			time.sleep(1)
			continue

		d = decode(frame)
		#print(d)

		data = [x.data.decode('utf-8') for x in d]
		bbox = [ [[-p.x, p.y] for p in x.polygon] for x in d]

		# Create or update code
		for i,d in enumerate(data):
			if d == '':
				continue

			if d not in codes:
				if d.startswith('https://www.youtube.com'):
					codes[d] = YoutubeCode(d, bbox[i])
				elif d == 'volume':
					codes[d] = VolumeCode(d, bbox[i])
				elif d == 'seek':
					codes[d] = SeekCode(d, bbox[i])
				elif d.startswith('instrument'):
					codes[d] = InstrumentCode(d, bbox[i])
				else:
					print('Unknown type of QR code')
			else:
				codes[d].update(bbox[i])



		# Get rid of removed codes
		for d in list(codes):
			if d not in data:
				codes[d].not_seen_cnt += 1
				if codes[d].not_seen_cnt > MAX_NOT_SEEN:
					print('Lost %s' % d)
					del codes[d]


decode_thread = threading.Thread(target=decodethreadfn)
decode_thread.start()

# We execute libcamera-vid as a subprocess and read its images from stdin. This is rather silly but more traditional ways like gstreamer libcamerasrc do not offer the required parameters to fix shutter and gain etc. And I was not really in the mood to write a C++ libcamera client.
cmd = 'libcamera-vid -t 0 --codec yuv420 --width 1024 --height 1024 --inline --listen -o - --awbgains 2,1 --shutter 5000 --brightness 0.2 --contrast 2 --gain 5'
args = shlex.split(cmd)
p = subprocess.Popen(args, stdout=subprocess.PIPE)

start_sound()
while True:
    data = p.stdout.read(int(1024*1024*1.5))
    frame = numpy.frombuffer(data, numpy.uint8, count=1024*1024).reshape((1024, 1024))
