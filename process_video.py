"""

Proof of principle video processor om op basis van een videoclip met gesproken tekst
een stappenplan te genereren. Hierbij kan gebruik worden gemaakt van keywords die het
begin (en eventueel einde) van een stap aangeven, die aangeven wanneer er een foto moet
worden opgeslagen en ingevoegd in de stappen en andere zaken.

Video's kunnen bijvoorbeeld worden opgenomen met behulp van een head-mounted camera
(bijvoorbeeld Vuzix of GoPro), waarbij de operator mondeling toelicht welke stappen
hij / zij op dat moment aan het uitvoeren is.

Gemaakt in het kader van het RAAK MKB project AR in de maakindustrie
"""
__author__ = "Etto Salomons, Lectoraat Ambient Intelligence, Saxion Enschede"

import json
from pathlib import Path

import cv2
import whisper_timestamped as wt
import markdown

_image_foldername = 'snapshots'

_HTML_HEAD = """<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="referrer" content="no-referrer" />
    <meta name="referrer" content="unsafe-url" />
    <meta name="referrer" content="origin" />
    <meta name="referrer" content="no-referrer-when-downgrade" />
    <meta name="referrer" content="origin-when-cross-origin" />
    <title>{{Page Title}}</title>
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            font-family: Helvetica,Arial,sans-serif;
            font-size: 18px;
        }
        code, pre {
            font-family: monospace;
        }
    </style>
</head>
<body>
<div class="container">
"""
_HTML_FOOT = """
</div>
</body>
</html>
"""


class VideoProcessor:

    def __init__(self, video_file, output_destination=None, snapshot_keyword='foto', begin_keyword='begin',
                 end_keyword='eind', force_new_transcription=False, title='', enable_intermezzo=False,
                 enable_begin_photo=True, enable_end_photo=True, add_photo_line_as_caption=False):
        """

        :param video_file: video file to be analyzed
        :param output_destination: default video file locatoin
        :param snapshot_keyword: default 'foto'
        :param begin_keyword: default 'begin'
        :param end_keyword: default 'end'; if same as begin_keyword or empty (e.g. 'step') end pictures are not included
        :param title: title of the description file that can be created for this video. Defaults to the video name
        """
        self._video_file = Path(video_file)
        self._video_name = self._video_file.name
        self._snapshot_keyword = snapshot_keyword.lower()
        self._begin_keyword = begin_keyword.lower()
        if end_keyword == '':
            self._end_keyword = begin_keyword
        else:
            self._end_keyword = end_keyword.lower()
        self._lines = None

        if not output_destination:
            self._output_destination = Path(self._video_file.parent)
        else:
            self._output_destination = Path(output_destination)
        self._transcription = self._transcribe(force_new=force_new_transcription)
        self._title = title
        self._enable_intermezzo = enable_intermezzo
        self._enable_begin_photo = enable_begin_photo
        self._enable_end_photo = enable_end_photo
        self._add_photo_line_as_caption = add_photo_line_as_caption

    def _transcribe(self, silent=False, force_new=False, ):
        output_file = self._output_destination / f'{self._video_name}_transcribed.txt'

        if output_file.is_file() and not force_new:
            if not silent:
                print(f'file: {output_file}')
            with open(output_file, 'r') as inp:
                return json.loads(inp.read())

        audio = wt.load_audio(self._video_file)
        model = wt.load_model("medium", device="cpu")
        result = wt.transcribe(model, audio, temperature=0.3)

        with open(output_file, 'w') as out:
            out.write(json.dumps(result, indent=2, ensure_ascii=False))
        return result

    def get_transcription(self):
        """

        :return: the entire transcription of the video
        """
        return self._transcription

    def create_snapshots(self):
        """
        Create photos each time the keyword is expressed in the transcription.
        """
        lines = self.get_lines()
        keyword = self._snapshot_keyword

        nr_snapshots = 0
        for line in lines:
            if keyword in line['text'].lower():
                self._create_snapshot_from_line(line, keyword)
                nr_snapshots += 1

        if nr_snapshots == 0:
            print(f'Snapshot keyword "{self._snapshot_keyword}" not in transcription')
        else:
            print(f'Created {nr_snapshots} snapshots')

    def _create_snapshot_from_line(self, line, keyword):
        for wrd in line['words']:
            if keyword == wrd['text'].lower().replace('.', ''):
                return self._create_snapshot(keyword, wrd['end'])

    def _create_snapshot(self, file_keyword, snapshot_time, verbose=False):
        image_destination = self._output_destination / _image_foldername
        image_destination.mkdir(exist_ok=True)

        video = cv2.VideoCapture(str(self._video_file))
        fps = video.get(cv2.CAP_PROP_FPS)

        framenr = int(snapshot_time * fps)
        video.set(cv2.CAP_PROP_POS_FRAMES, framenr)
        success, frame = video.read()
        out_file = image_destination / f'{self._video_name}_{file_keyword}_{snapshot_time}.jpg'
        if verbose:
            print(f'creating {out_file}')
        cv2.imwrite(str(out_file), frame)
        return out_file

    def get_text(self):
        """
        :return: The entire text of the transcription
        """
        return self._transcription['text']

    def get_lines(self):
        """
        Creates lines from the transcription. Lines are identified by the closing period (.)
        :return: list of lines (dict with keys 'text' and 'words')
        """
        if self._lines is None:
            transcript = self._transcription
            # collect all words
            all_words = [wrd for seg in transcript['segments'] for wrd in seg['words']]

            # find indices of '.'; use these to create lines
            idx_hi = [nr + 1 for nr in range(len(all_words)) if '.' in all_words[nr]['text']]
            idx_lo = [0] + [idx for idx in idx_hi[:-1]]

            line_words = [all_words[lo:hi] for (lo, hi) in zip(idx_lo, idx_hi)]
            line_texts = [' '.join([ln['text'] for ln in lw]) for lw in line_words]
            line_starts = [lw[0]['start'] for lw in line_words]
            line_ends = [lw[-1]['end'] for lw in line_words]
            self._lines = [{'text': text, 'words': words, 'start': strt, 'end': endt}
                           for text, words, strt, endt in zip(line_texts, line_words, line_starts, line_ends)]

        return self._lines

    def _get_step_indices(self):
        kw_start = self._begin_keyword
        kw_end = self._end_keyword

        lines = self.get_lines()
        nr_lines = len(lines)
        indices = []

        current_line = 0
        while current_line < nr_lines:
            next_begin = self._find_keyword_from(current_line, nr_lines, kw_start)
            if next_begin >= 0:
                next_end = self._find_keyword_from(next_begin + 1, nr_lines, kw_end)
                if next_end < 0:
                    next_end = nr_lines - 1
                if next_end > next_begin:
                    if kw_start != kw_end:
                        indices.append((next_begin, next_end))
                    else:  # only one keyword; no separate end keyword
                        if next_end != nr_lines - 1:  # if not final step
                            next_end -= 1  # one before next begin
                        indices.append((next_begin, next_end))
                current_line = next_end + 1
            else:
                current_line = nr_lines
        return indices

    def get_steps(self):
        """
        :return: a json representation of the steps in the transcription
        """
        # step:
        # start_text + start_image
        # step_lines:
        #	either text or image with text
        # end_text + end_image (if explicit start and end keyword)

        lines = self.get_lines()
        steps = []
        indices = self._get_step_indices()

        last_end = 0
        next_index = 0
        while next_index < len(indices):
            idx_start, idx_stop = indices[next_index]
            if last_end + 1 < idx_start:
                steps.append(('intermediate', self._create_intermediate(last_end + 1, idx_start, lines)))
            step = self._create_step(idx_start, idx_stop, lines)
            steps.append(('step', step))
            last_end = idx_stop
            next_index += 1

        if last_end + 1 < len(lines):
            steps.append(('intermediate', self._create_intermediate(last_end + 1, len(lines), lines)))

        return steps

    def _create_step(self, idx_start, idx_stop, lines):
        step = dict()
        # start
        start_time = lines[idx_start]['start']
        filename = _image_foldername + '/' + self._create_snapshot('begin', start_time).name
        start_text = lines[idx_start]['text']
        step['start'] = {'image': filename, 'text': start_text}
        # end, only when using explicit start and end keywords
        if self._begin_keyword != self._end_keyword:
            end_time = lines[idx_stop]['start']
            filename = _image_foldername + '/' + self._create_snapshot('end', end_time).name
            end_text = lines[idx_stop]['text']
            step['end'] = {'image': filename, 'text': end_text}
            # other lines
            step['lines'] = [self._create_step_line(lines[idx]) for idx in range(idx_start + 1, idx_stop)]
            # edge case: no explicit end keyword in last line
            if not self._end_keyword in end_text.lower():
                step['lines'].append(('text', end_text))
        else:
            # also include last line
            step['lines'] = [self._create_step_line(lines[idx]) for idx in range(idx_start + 1, idx_stop + 1)]
        return step

    def _create_intermediate(self, idx_start, idx_stop, lines):
        lines = [self._create_step_line(lines[idx]) for idx in range(idx_start, idx_stop)]
        return lines

    def _find_keyword_from(self, line_nr, nr_lines, keyword):
        lines = self.get_lines()
        for linenr in range(line_nr, nr_lines):
            if keyword in lines[linenr]['text'].lower():
                return linenr
        return -1

    def _create_step_line(self, line):
        if self._snapshot_keyword in line['text'].lower():
            filename = _image_foldername + '/' + self._create_snapshot_from_line(line, self._snapshot_keyword).name
            return 'image', {'text': line['text'], 'image': filename}
        return 'text', line['text']

    def create_description(self, ):
        """
        Create a markdown and an html file based on the transcription. The file contains a stepwise description
        based on the lines in the transcription. Photos are included at the begin of each step and each time
        the instruction to create a photo is recorded. If a separate end keyword is used, a photo is included at the
        end as well
        :return: html filename
        """
        steps = self.get_steps()

        title = self._title
        if not title:
            title = self._video_name.split('.')[0]

        underscored_title = title.replace(' ', '_')
        outfilename = f'{self._output_destination}/{underscored_title}.md'
        htmloutfilename = f'{self._output_destination}/{underscored_title}.html'

        with open(outfilename, 'w') as md_out, open(htmloutfilename, 'w') as html_out:
            html_out.write(_HTML_HEAD.replace('{{Page Title}}', title))
            def prt(value):
                md_out.write(f'{value}\n')
                html_out.write(markdown.markdown(f'{value}\n'))

            prt(self._descr_title(title))

            nr_steps = 0
            for step in steps:
                if step[0] == 'step':
                    nr_steps += 1
                    prt(self._descr_step_title(nr_steps))

                    step_info = step[1]

                    if self._enable_begin_photo:
                        prt(self._descr_image(step_info['start'], f'Begintoestand stap {nr_steps}'))

                    lines = step_info['lines']
                    for line in lines:
                        if 'text' == line[0]:
                            prt(f'* {line[1]}')
                        elif 'image' == line[0]:
                            if self._add_photo_line_as_caption:
                                caption = line[1]['text']
                            else:
                                caption = ''
                                # was f'{self._snapshot_keyword.capitalize()} tussenstap'
                            prt(self._descr_image(line[1], caption))

                    if 'end' in step_info and self._enable_end_photo:
                        prt(self._descr_image(step_info['end'], f'Eindtoestand stap {nr_steps}'))

                elif step[0] == 'intermediate' and self._enable_intermezzo:
                    prt(self._descr_intermediate_title())
                    lines = step[1]
                    for line in lines:
                        if 'text' == line[0]:
                            prt(f'* {line[1]}')
                        elif 'image' == line[0]:
                            prt(self._descr_image(line[1], f'{self._snapshot_keyword.capitalize()}'))
            prt(self._descr_full_text())

            html_out.write(_HTML_FOOT)

        print(f'created {outfilename} and {htmloutfilename}')
        return htmloutfilename

    def _descr_title(self, title):
        return '## Stappenplan ' + title

    def _descr_step_title(self, nr_steps):
        return f'### Stap {nr_steps}'

    def _descr_intermediate_title(self, ):
        return f'### _Intermezzo_'

    def _descr_full_text(self, ):
        txt = '\n\n## _Volledige transcriptie:_\n'
        txt +=  '<br/>'.join([p['text'] for p in self.get_lines()])
        return txt

    def _descr_image(self, img_dict, caption=''):
        fig = img_dict['image']
        alt = img_dict['text']
        return '''
<figure>
  <img src="{}" alt="{}" width="300" />
  <figcaption><em>{}</em></figcaption>
</figure>\n'''.format(fig, alt, caption)


def main():
    video_path = '/path/to/videos'
    video_file = 'video1.mp4'
    video_file2 = 'video2.mp4'

    out_path = '/path/to/output'

    p1withend = VideoProcessor(video_file=f'{video_path}/{video_file}', output_destination=out_path,
                               snapshot_keyword='screenshot', title='VID1 with end')
    p1withend.create_description()

    p2withend = VideoProcessor(f'{video_path}/{video_file2}', output_destination=out_path,
                               snapshot_keyword='screenshot', title='VID2 with end')
    p2withend.create_description()

    p1withoutend = VideoProcessor(video_file=f'{video_path}/{video_file}', output_destination=out_path,
                                  snapshot_keyword='screenshot', end_keyword='', title='VID1 without end')
    p1withoutend.create_description()

    p2withoutend = VideoProcessor(f'{video_path}/{video_file2}', output_destination=out_path,
                                  snapshot_keyword='screenshot', end_keyword='', title='VID2 without end')
    p2withoutend.create_description()


if __name__ == '__main__':
    main()
