import whisper_timestamped as wt
import json
import os
import cv2
from pathlib import Path

class VideoProcessor:
	
	def __init__(self, video_file, output_destination=None, snapshot_keyword='foto', begin_keyword='begin', end_keyword='einde'):
		self.video_file = Path(video_file)
		self.video_name = self.video_file.name
		self.snapshot_keyword = snapshot_keyword
		self.begin_keyword = begin_keyword
		self.end_keyword = end_keyword
		self.lines = None

		if not output_destination:
			self.output_destination = Path(self.video_file.parent)
		else:
			self.output_destination = Path(output_destination)


	def transcribe(self, silent=False):
		output_file = self.output_destination / f'{self.video_name}_transcribed.txt'

		if output_file.is_file():
			if not silent:
				print(f'file: {output_file}')
			with open(output_file, 'r') as inp:
				return json.loads(inp.read())

		audio = wt.load_audio(self.video_file)
		model = wt.load_model("medium", device="cpu")
		result = wt.transcribe(model, audio)

		with open(output_file,'w') as out:
			out.write(json.dumps(result, indent = 2, ensure_ascii = False))
		return result

	def create_snapshots(self):
		transcription = self.transcribe()
		keyword = self.snapshot_keyword

		screenshot_times = []
		for seg in transcription['segments']:
			if keyword in seg['text'].lower():
				for wrd in seg['words']:
					if keyword == wrd['text'].lower().replace('.',''):
						screenshot_times.append(wrd['end'])


		video = cv2.VideoCapture(str(self.video_file))
		fps = video.get(cv2.CAP_PROP_FPS)
		for screenshot_time in screenshot_times:
			framenr = int(screenshot_time * fps)
			video.set(cv2.CAP_PROP_POS_FRAMES, framenr)
			success, frame = video.read()
			out_file = self.output_destination / f'{self.video_name}_{keyword}_{screenshot_time}.jpg'
			print(f'creating {out_file}')
			cv2.imwrite(str(out_file), frame)

		if len(screenshot_times) == 0:
			print(f'Snapshot keyword "{self.snapshot_keyword}" not in transcription')
		else:
			print(f'Created {len(screenshot_times)} snapshots')

	def text(self):
		transcription = self.transcribe(silent=True)
		return transcription['text']

	def get_lines(self):
		if self.lines is None:
			print('calc')
			transcript = self.transcribe(True)
			all_words = [wrd for seg in transcript['segments'] for wrd in seg['words']]
			idx_hi = [nr+1 for nr in range(len(all_words)) if '.' in all_words[nr]['text']]
			idx_lo = [0] + [idx for idx in idx_hi[:-1]]
			line_words = [all_words[lo:hi] for (lo,hi) in zip(idx_lo, idx_hi)]
			line_texts = [' '.join([ln['text'] for ln in lw]) for lw in line_words]
			self.lines = [{'text': text, 'words':words} for text,words in zip(line_texts, line_words)]
		return self.lines

	def create_segments(self):
		transcription = self.transcribe(silent=True)
		kw_start = self.begin_keyword
		kw_end = self.end_keyword

		# for seg in transcription['segments']:
			# if kw_start in seg['text'].lower():
			# 	for wrd in seg['words']:
			# 		if keyword == wrd['text'].lower().replace('.',''):
			# 			screenshot_times.append(wrd['end'])
