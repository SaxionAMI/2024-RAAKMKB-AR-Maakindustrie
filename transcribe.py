import whisper_timestamped as wt
import json
import os
import cv2
from pathlib import Path

def _create_paths_from_names(video_file, output_destination):
	video_file = Path(video_file)
	video_name = video_file.name

	if not output_destination:
		output_destination = Path(video_file.parent)
	else:
		output_destination = Path(output_destination)
	return video_file, video_name, output_destination

def transcribe(video_file, output_destination=None):
	video_file, video_name, output_destination = _create_paths_from_names(video_file, output_destination)
	
	output_file = output_destination / f'{video_name}_transcribed.txt'

	if output_file.is_file():
		print(f'existing file: {output_file}')
		with open(output_file, 'r') as inp:
			return json.loads(inp.read())
	
	audio = wt.load_audio(video_file)
	model = wt.load_model("medium", device="cpu")
	result = wt.transcribe(model, audio)
	
	with open(output_file,'w') as out:
		out.write(json.dumps(result, indent = 2, ensure_ascii = False))
	return result

def create_screenshots(video_file, output_destination=None):
	video_file, video_name, output_destination = _create_paths_from_names(video_file, output_destination)
	transcription = transcribe(video_file, output_destination)

	screenshot_times = []
	for seg in transcription['segments']:
		if 'screenshot' in seg['text'].lower():
			for wrd in seg['words']:
				if 'screenshot' in wrd['text'].lower():
					screenshot_times.append(wrd['end'])
	

	video = cv2.VideoCapture(str(video_file))
	fps = video.get(cv2.CAP_PROP_FPS)
	for screenshot_time in screenshot_times:
		framenr = int(screenshot_time * fps)
		video.set(cv2.CAP_PROP_POS_FRAMES, framenr)
		success, frame = video.read()
		out_file = output_destination / f'{video_name}_screenshot_{screenshot_time}.jpg'
		print(f'creating {out_file}')
		cv2.imwrite(str(out_file), frame)