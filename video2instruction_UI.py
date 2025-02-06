"""

Eenvoudige user interface (tkinter) voor process_video.Videoprocessor.
Het programma is een demonstrator om een instructieset (stappenplan) te genereren op basis van
gesproken tekst in een videoclip. Zie verder documentatie van process_video.Videoprocessor.
Gemaakt in het kader van het RAAK MKB project AR in de maakindustrie
"""
__author__ = "Etto Salomons, Lectoraat Ambient Intelligence, Saxion Enschede"
import os
import traceback
import json
import tkinter
import platform
import copy
import webbrowser

from tkinter import Tk, Entry, Button, Frame, TOP, Checkbutton, IntVar, messagebox, Label
from tkinter.constants import X, BOTTOM, LEFT, END, BOTH, RIGHT, HORIZONTAL, W, DISABLED, NORMAL
from tkinter.filedialog import askopenfilename, askdirectory

from process_video import VideoProcessor

###################
# SETTING / NAMES TO BE CHANGED!!!
###################
_toolname = 'video2instruction'
_app_title = 'Instruction From Video'
###################
# END SETTINGS TO BE CHANGED!!!
###################


_cfg_file = os.path.expanduser('~') + f'/{_toolname}_settings.cfg'

# Components
_root = Tk()

_ui_elements = dict()
_default_config = {
	'str_video_file': '',
	'str_output_path':'',
	'str_title':'Report Title',
	'str_photo_keyword':'foto',
	'chk_enable_intermezzo': 0,
	'str_begin_word':'stap',
	'chk_use_stop':1,
	'str_end_word':'klaar',
	'chk_photo_caption_txt':0,
	'chk_add_begin_photo':0,
	'chk_add_end_photo':0,
}

def do_main():
	config = _read_file_config()

	_root.resizable(False, False)  # zorgt ervoor dat nieuw window niet gegroepeerd wordt
	_root.option_add("*Font", _ui_font())
	topFrame = Frame(_root)
	bottomFrame = Frame(_root)

	_root.title(_app_title)


	# top Frame
	##########################

	# video row
	#--------------------------
	rownum = 0
	colnum = 0
	Label(topFrame, text='Video file').grid(row=rownum, column=colnum)

	colnum += 1
	config_name = 'str_video_file'
	input = Entry(topFrame, width=50)
	input.grid(row=rownum, column=colnum)
	input.insert(0, config[config_name])
	input.xview_moveto(1) # show right hand side of textfield
	_ui_elements[config_name] = input

	colnum += 1
	browse_but = Button(topFrame, text='Browse', command=_browse_video_clicked)
	browse_but.grid(row=rownum, column=colnum)

	# output path row
	#--------------------------
	rownum += 1
	colnum = 0
	Label(topFrame, text='Output path').grid(row=rownum, column=colnum)

	colnum += 1
	config_name = 'str_output_path'
	input = Entry(topFrame, width=50)
	input.grid(row=rownum, column=colnum)
	input.insert(0, config[config_name])
	input.xview_moveto(1)
	_ui_elements[config_name] = input

	colnum += 1
	browse_but = Button(topFrame, text='Browse', command=_browse_path_clicked)
	browse_but.grid(row=rownum, column=colnum)

	# title path row
	#--------------------------
	rownum += 1
	colnum = 0
	Label(topFrame, text='Report title').grid(row=rownum, column=colnum)

	colnum += 1
	config_name = 'str_title'
	input = Entry(topFrame, width=30)
	input.grid(row=rownum, column=colnum, sticky=W)
	input.insert(0, config[config_name])
	_ui_elements[config_name] = input

	# start keyword row
	#--------------------------
	rownum += 1
	colnum = 0
	Label(topFrame, text='Stap beginwoord').grid(row=rownum, column=colnum)

	colnum += 1
	config_name = 'str_begin_word'
	input = Entry(topFrame, width=20)
	input.grid(row=rownum, column=colnum, sticky=W)
	input.insert(0, config[config_name])
	_ui_elements[config_name] = input


	# end keyword row
	#--------------------------
	rownum += 1
	colnum = 0
	config_name = 'chk_use_stop'
	check_var = IntVar(value=config[config_name])
	check_box = Checkbutton(topFrame, variable=check_var, text='Stap eindwoord', command=_toggle_endword)
	check_box.grid(sticky=W, row=rownum, column=colnum)
	_ui_elements[config_name] = check_var

	colnum += 1
	config_name = 'str_end_word'
	input = Entry(topFrame, width=20)
	input.grid(row=rownum, column=colnum, sticky=W)
	input.insert(0, config[config_name])
	_ui_elements[config_name] = input



	# photo keyword row
	#--------------------------
	rownum += 1
	colnum = 0
	Label(topFrame, text='Fotowoord').grid(row=rownum, column=colnum)

	colnum += 1
	config_name = 'str_photo_keyword'
	input = Entry(topFrame, width=20)
	input.grid(row=rownum, column=colnum, sticky=W)
	input.insert(0, config[config_name])
	_ui_elements[config_name] = input

	# include photo text as caption
	#--------------------------
	rownum += 1
	colnum = 1
	config_name = 'chk_photo_caption_txt'
	check_var = IntVar(value=config[config_name])
	check_box = Checkbutton(topFrame, variable=check_var, text='Foto tekst als onderschrift')
	check_box.grid(sticky=W, row=rownum, column=colnum)
	_ui_elements[config_name] = check_var

	# include intermezzo
	#--------------------------
	rownum += 1
	colnum = 1
	config_name = 'chk_enable_intermezzo'
	check_var = IntVar(value=config[config_name])
	check_box = Checkbutton(topFrame, variable=check_var, text='Neem intermezzo op')
	check_box.grid(sticky=W, row=rownum, column=colnum)
	_ui_elements['intermezzo_chck'] = check_box
	_ui_elements[config_name] = check_var

	# include begin photo
	#--------------------------
	rownum += 1
	colnum = 1
	config_name = 'chk_add_begin_photo'
	check_var = IntVar(value=config[config_name])
	check_box = Checkbutton(topFrame, variable=check_var, text='Neem beginfoto op')
	check_box.grid(sticky=W, row=rownum, column=colnum)
	_ui_elements[config_name] = check_var

	# include end photo
	#--------------------------
	rownum += 1
	colnum = 1
	config_name = 'chk_add_end_photo'
	check_var = IntVar(value=config[config_name])
	check_box = Checkbutton(topFrame, variable=check_var, text='Neem eindfoto op')
	check_box.grid(sticky=W, row=rownum, column=colnum)
	_ui_elements['endphoto_chck'] = check_box
	_ui_elements[config_name] = check_var

	_toggle_endword()

	# bottom Frame
	start_but = Button(bottomFrame)
	start_but.configure(text='Start', command=_start_clicked)
	start_but.pack(side=LEFT)
	cancel_but = Button(bottomFrame, text='Cancel', command=_close_app)
	cancel_but.pack(side=LEFT)

	topFrame.pack(side=TOP, fill=X, pady=3)
	bottomFrame.pack(side=BOTTOM, fill=X, pady=3)

	_root.protocol("WM_DELETE_WINDOW", _close_app)
	_root.eval('tk::PlaceWindow . center')
	_root.mainloop()

################
# BUTTON HANDLERS
################
def _close_app():
	_process_config_fields()
	_root.destroy()

def _browse_video_clicked():
	ui_element = _ui_elements['str_video_file']
	intdir = os.path.dirname(ui_element.get())
	foldername = askopenfilename(title='Selecteer video', initialdir=intdir)
	if foldername:
		ui_element.delete(0, END)
		ui_element.insert(0, foldername)
		ui_element.xview_moveto(1)
		_process_config_fields()

def _browse_path_clicked():
	ui_element = _ui_elements['str_output_path']
	intdir = os.path.dirname(ui_element.get())
	foldername = askdirectory(title='Selecteer folder', initialdir=intdir)
	if foldername:
		ui_element.delete(0, END)
		ui_element.insert(0, foldername)
		ui_element.xview_moveto(1)
		_process_config_fields()

def _toggle_endword():
	if _ui_elements['chk_use_stop'].get():
		_ui_elements['str_end_word'].config(state=NORMAL)
		_ui_elements['intermezzo_chck'].config(state=NORMAL)
		_ui_elements['endphoto_chck'].config(state=NORMAL)
	else:
		_ui_elements['str_end_word'].config(state=DISABLED)
		_ui_elements['intermezzo_chck'].config(state=DISABLED)
		_ui_elements['endphoto_chck'].config(state=DISABLED)


def _start_clicked():
	_process_config_fields()
	try:
		video_file = _ui_elements['str_video_file'].get()
		out_path = _ui_elements['str_output_path'].get()
		title = _ui_elements['str_title'].get()
		kw_photo = _ui_elements['str_photo_keyword'].get()
		kw_begin = _ui_elements['str_begin_word'].get()
		kw_end = _ui_elements['str_end_word'].get()
		enable_end = _ui_elements['chk_use_stop'].get()
		enable_intermezzo = _ui_elements['chk_enable_intermezzo'].get()
		enable_begin_photo = _ui_elements['chk_add_begin_photo'].get()
		enable_end_photo = _ui_elements['chk_add_end_photo'].get()
		add_photocaption = _ui_elements['chk_photo_caption_txt'].get()

		if not enable_end:
			kw_end = ''

		processor = VideoProcessor(
			video_file=video_file,
			output_destination=out_path,
			snapshot_keyword=kw_photo,
			begin_keyword=kw_begin,
			end_keyword=kw_end,
			title=title,
			enable_intermezzo=enable_intermezzo,
			enable_begin_photo=enable_begin_photo,
			enable_end_photo=enable_end_photo,
			add_photo_line_as_caption=add_photocaption
		)

		htmlfile = processor.create_description()
		webbrowser.open('file://' + htmlfile)

	except Exception as e:
		print(traceback.format_exc())
		messagebox.showerror('Fout tijdens uitvoering programma',
							 f'Fout tijdens uitvoering. Details:\n{traceback.format_exc()}')


def _show_result_window(txt):
	resultWindow = tkinter.Toplevel(_root)

	resultWindow.title('Resultaat')
	resultWindow.geometry('1000x800+200+200')

	txtFrame = Frame(resultWindow)
	btnFrame = Frame(resultWindow)

	SVBar = tkinter.Scrollbar(txtFrame)
	SVBar.pack(side=RIGHT,
			   fill="y")

	SHBar = tkinter.Scrollbar(txtFrame,
							  orient=HORIZONTAL)
	SHBar.pack(side=BOTTOM,
			   fill="x")

	TBox = tkinter.Text(txtFrame,
						height=50,
						width=1000,
						yscrollcommand=SVBar.set,
						xscrollcommand=SHBar.set,
						wrap="none", font=_txt_font())

	TBox.pack(expand=0, fill=BOTH)
	TBox.insert(END, txt)

	SHBar.config(command=TBox.xview)
	SVBar.config(command=TBox.yview)

	def exit_btn():
		resultWindow.destroy()
		resultWindow.update()

	btn = Button(btnFrame, text='Close', command=exit_btn)
	btn.pack(expand=True)

	btnFrame.pack(side=BOTTOM, fill=BOTH, pady=3)
	txtFrame.pack(side=TOP, fill=X, pady=3)

####################
# font defs
####################

def _ui_font():
	if _runs_on_win():
		return ('Arial', 14)
	return ('Arial', 18)

def _ui_font_bold():
	if _runs_on_win():
		return ('Arial', 14, 'bold')
	return ('Arial', 18, 'bold')

def _txt_font():
	if _runs_on_win():
		return ('Courier', 14)
	return ('Courier', 18)

#################
# Config management
#################

def _read_file_config():
	config = copy.deepcopy(_default_config)
	
	if os.path.exists(_cfg_file):
		with open(_cfg_file, 'r') as infile:
			file_config = json.load(infile)
			for config_item in _default_config:
				if config_item in file_config:
					config[config_item] = file_config[config_item]
	else:
		with open(_cfg_file, 'w') as outfile:
			json.dump(config, outfile)
	return config


def _process_config_fields():
	config = dict()
	for config_item in _ui_elements:
		if config_item in _default_config:
			config[config_item] = _ui_elements[config_item].get()

	with open(_cfg_file, 'w') as outfile:
		json.dump(config, outfile)

	return config


def _runs_on_win():
	return 'windows' in platform.system().lower()



if __name__ == '__main__':
	do_main()