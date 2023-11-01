import PySimpleGUI as sg
import os,sys,shutil
from search_list_box import ListboxWithSearch
values = ['hello', 'hello world', 'my world', 'your wold', 'god']
ID_list_box = ListboxWithSearch( values,key = '_ID LIST_')
file_list_column = [
    [sg.Text("Chose ID:"),sg.InputText(key="_ID_FILL_")],
    # [
    #     sg.Listbox(
    #         values=[], enable_events=True, size=(40, 10), key="_ID LIST_"
    #     )
    # ],
    
    [sg.Text("Chose image:")],
    [sg.Text("Current: None",key = "_ID INDEX_"),sg.Button('Reset', key='_BUTTON_RESET_')],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 10), key="_IMG LIST_"
        )
    ],
]

# For now will only show the name of the file that was chosen
image_viewer_column = [
    [sg.InputText(key="_NAME_"),sg.Button('Add', key='_BUTTON_ADD_')],
    [sg.Image(key="_IMAGE_")],
]

# ----- Full layout -----
layout = [
    [
        ID_list_box.layout,
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(image_viewer_column),
    ]
]
   
window = sg.Window("Image Viewer", layout)
current_ID = None
while True:
    event, values = window.read(timeout=1)
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    try:
        try:
            # Get list of files in folder
            new_ID_list = os.listdir("unknown_temp")
        except:
            new_ID_list = []
        window["_ID LIST_"].update(new_ID_list)

        try:
                # Get list of files in folder
                file_list = os.listdir(f"unknown_temp/{current_ID}")
        except:
                file_list = []

        fnames = [
                f
                for f in file_list
                if os.path.isfile(os.path.join(f"unknown_temp/{current_ID}", f))
                and f.lower().endswith((".png", ".jpg"))
        ]
        window["_IMG LIST_"].update(fnames)
        

        if event == "_ID LIST_":
            folder = values["_ID LIST_"][0]
            new_line = f"Current: {folder}"
            current_ID = folder
            window["_ID INDEX_"].update(new_line)
        if event == "_IMG LIST_":  # A file was chosen from the listbox
            if current_ID != None:
                try:
                    filename = os.path.join(os.getcwd(),f"unknown_temp\{current_ID}", values["_IMG LIST_"][0])
                    window["_IMAGE_"].update(filename=filename)
                except:
                    pass
        if event == "_BUTTON_RESET_":
            try:
                
                folder = os.path.join(os.getcwd(),f"unknown_temp\{current_ID}")
                print(folder)
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print('Failed to delete %s. Reason: %s' % (file_path, e))
            except:
                pass
        # if event == "-FOLDER-":
    except Exception as e:
        print(f"error: {e}")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"type:{exc_type}, name: {fname}, line: {exc_tb.tb_lineno}")
        # time.sleep(0.5)

window.close()