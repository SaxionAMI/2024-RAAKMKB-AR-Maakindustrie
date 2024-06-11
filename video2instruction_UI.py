from glob import glob
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
toolname = 'video2instruction'
app_title = 'Instruction From Video'
###################
# END SETTINGS TO BE CHANGED!!!
###################


cfg_file = os.path.expanduser('~') + f'/{toolname}_settings.cfg'

# Components
root = Tk()

ui_elements = dict()
default_config = {
	'str_video_file': '',
	'str_output_path':'',
	'str_title':'Report Title',
	'str_photo_keyword':'foto',
	'chk_enable_intermezzo': 0,
	'str_begin_word':'stap',
	'chk_use_stop':1,
	'str_end_word':'klaar',
	'chk_add_begin_photo':0,
	'chk_add_end_photo':0,
}

def do_main():
	config = read_file_config()

	root.resizable(False, False)  # zorgt ervoor dat nieuw window niet gegroepeerd wordt
	root.option_add("*Font", ui_font())
	topFrame = Frame(root)
	bottomFrame = Frame(root)

	root.title(app_title)


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
	ui_elements[config_name] = input

	colnum += 1
	browse_but = Button(topFrame, text='Browse', command=browse_video_clicked)
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
	ui_elements[config_name] = input

	colnum += 1
	browse_but = Button(topFrame, text='Browse', command=browse_path_clicked)
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
	ui_elements[config_name] = input

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
	ui_elements[config_name] = input


	# end keyword row
	#--------------------------
	rownum += 1
	colnum = 0
	config_name = 'chk_use_stop'
	check_var = IntVar(value=config[config_name])
	check_box = Checkbutton(topFrame, variable=check_var, text='Stap eindwoord',command=toggle_endword)
	check_box.grid(sticky=W, row=rownum, column=colnum)
	ui_elements[config_name] = check_var

	colnum += 1
	config_name = 'str_end_word'
	input = Entry(topFrame, width=20)
	input.grid(row=rownum, column=colnum, sticky=W)
	input.insert(0, config[config_name])
	ui_elements[config_name] = input



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
	ui_elements[config_name] = input

	# include intermezzo
	#--------------------------
	rownum += 1
	colnum = 1
	config_name = 'chk_enable_intermezzo'
	check_var = IntVar(value=config[config_name])
	check_box = Checkbutton(topFrame, variable=check_var, text='Neem intermezzo op')
	check_box.grid(sticky=W, row=rownum, column=colnum)
	ui_elements['intermezzo_chck'] = check_box
	ui_elements[config_name] = check_var

	# include begin photo
	#--------------------------
	rownum += 1
	colnum = 1
	config_name = 'chk_add_begin_photo'
	check_var = IntVar(value=config[config_name])
	check_box = Checkbutton(topFrame, variable=check_var, text='Neem beginfoto op')
	check_box.grid(sticky=W, row=rownum, column=colnum)
	ui_elements[config_name] = check_var

	# include end photo
	#--------------------------
	rownum += 1
	colnum = 1
	config_name = 'chk_add_end_photo'
	check_var = IntVar(value=config[config_name])
	check_box = Checkbutton(topFrame, variable=check_var, text='Neem eindfoto op')
	check_box.grid(sticky=W, row=rownum, column=colnum)
	ui_elements['endphoto_chck'] = check_box
	ui_elements[config_name] = check_var


	toggle_endword()

	# bottom Frame
	start_but = Button(bottomFrame)
	start_but.configure(text='Start', command=start_clicked)
	start_but.pack(side=LEFT)
	cancel_but = Button(bottomFrame, text='Cancel', command=close_app)
	cancel_but.pack(side=LEFT)

	topFrame.pack(side=TOP, fill=X, pady=3)
	bottomFrame.pack(side=BOTTOM, fill=X, pady=3)

	root.protocol("WM_DELETE_WINDOW", close_app)
	root.eval('tk::PlaceWindow . center')
	root.mainloop()

################
# BUTTON HANDLERS
################
def close_app():
	process_config_fields()
	root.destroy()

def browse_video_clicked():
	ui_element = ui_elements['str_video_file']
	intdir = os.path.dirname(ui_element.get())
	foldername = askopenfilename(title='Selecteer video', initialdir=intdir)
	if foldername:
		ui_element.delete(0, END)
		ui_element.insert(0, foldername)
		process_config_fields()

def browse_path_clicked():
	ui_element = ui_elements['str_output_path']
	intdir = os.path.dirname(ui_element.get())
	foldername = askdirectory(title='Selecteer folder', initialdir=intdir)
	if foldername:
		ui_element.delete(0, END)
		ui_element.insert(0, foldername)
		process_config_fields()

def toggle_endword():
	if ui_elements['chk_use_stop'].get():
		ui_elements['str_end_word'].config(state=NORMAL)
		ui_elements['intermezzo_chck'].config(state=NORMAL)
		ui_elements['endphoto_chck'].config(state=NORMAL)
	else:
		ui_elements['str_end_word'].config(state=DISABLED)
		ui_elements['intermezzo_chck'].config(state=DISABLED)
		ui_elements['endphoto_chck'].config(state=DISABLED)


def start_clicked():
	process_config_fields()
	try:
		video_file = ui_elements['str_video_file'].get()
		out_path = ui_elements['str_output_path'].get()
		title = ui_elements['str_title'].get()
		kw_photo = ui_elements['str_photo_keyword'].get()
		kw_begin = ui_elements['str_begin_word'].get()
		kw_end = ui_elements['str_end_word'].get()
		enable_end = ui_elements['chk_use_stop'].get()
		enable_intermezzo = ui_elements['chk_enable_intermezzo'].get()
		enable_begin_photo = ui_elements['chk_add_begin_photo'].get()
		enable_end_photo = ui_elements['chk_add_end_photo'].get()

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
			enable_end_photo=enable_end_photo
		)

		htmlfile = processor.create_description()
		webbrowser.open('file://' + htmlfile)

	except Exception as e:
		print(traceback.format_exc())
		messagebox.showerror('Fout tijdens uitvoering programma',
							 f'Fout tijdens uitvoering. Details:\n{traceback.format_exc()}')


def show_result_window(txt):
	resultWindow = tkinter.Toplevel(root)

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
						wrap="none", font=txt_font())

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

def ui_font():
	if runs_on_win():
		return ('Arial', 14)
	return ('Arial', 18)

def ui_font_bold():
	if runs_on_win():
		return ('Arial', 14, 'bold')
	return ('Arial', 18, 'bold')

def txt_font():
	if runs_on_win():
		return ('Courier', 14)
	return ('Courier', 18)

#################
# Config management
#################

def read_file_config():
	config = copy.deepcopy(default_config)
	
	if os.path.exists(cfg_file):
		with open(cfg_file, 'r') as infile:
			file_config = json.load(infile)
			for config_item in default_config:
				if config_item in file_config:
					config[config_item] = file_config[config_item]
	else:
		with open(cfg_file, 'w') as outfile:
			json.dump(config, outfile)
	return config


def process_config_fields():
	config = dict()
	for config_item in ui_elements:
		if config_item in default_config:
			config[config_item] = ui_elements[config_item].get()

	with open(cfg_file, 'w') as outfile:
		json.dump(config, outfile)

	return config


def runs_on_win():
	return 'windows' in platform.system().lower()



if __name__ == '__main__':
	do_main()