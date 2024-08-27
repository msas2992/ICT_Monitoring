import sys
import os
import time
import shutil
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
from tkinter import ttk
import configparser
import json
from tkinter import font

from tkinter import filedialog
from functools import partial
from tkinter import messagebox

class MonitorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ICT Monitoring ( Version : MSA-41763875 )")
        self.folder_info_list = {}
        self.row_start = 0
        self.create_widgets()
        self.folder_path = ''
        self.file_extension = '.dcl'
        self.url = "http://192.168.0.28/final_line_Q42023/"

    def create_widgets(self):
        
        # button to get choose path 
        self.path_choose_button = tk.Button(self.root, text="PATH / DIRECTORY", command=self.choose_folder)
        self.path_choose_button.grid(row=self.row_start, column=0, padx=4, pady=5)

        # text to view choose path
        self.path_textbox = tk.Text(self.root, height=1)
        self.path_textbox.configure(width=83)
        self.path_textbox.config(state=tk.DISABLED)
        self.path_textbox.grid(row=self.row_start, column=1, columnspan=4, padx=4, pady=5)
    
    def create_checkbuttons_widgets(self):
        self.clear_above_row(1)
        self.row_start +=1

        self.checkbuttons_label = tk.Label(self.root, text="Select Monitoring Folder : monitoring file format is .dcl")
        self.checkbuttons_label.grid(row=self.row_start, column=0, columnspan=2, padx=10, pady=5)

        self.show_hide_button = tk.Button(self.root, text="Show/Hide", command=self.toggle_items)
        self.show_hide_button.grid(row=self.row_start, column=4, padx=10, pady=5, sticky='e')

        self.hidden = False

        self.row_start = self.row_start + 1
        self.checkbuttons = []
        self.folder_checkboxes = {}
        self.project_comboboxes = {}
        self.stationName_comboboxes = {}
        self.parallelStation_comboboxes = {}
        self.serverApi_comboboxes = {}
        self.row_info = self.row_start
        
        for i, folder in enumerate(self.folder_list):
            var = tk.BooleanVar()
            self.folder_checkbox = tk.Checkbutton(self.root, text=folder, variable=var, onvalue=True, offvalue=False, command=partial(self.on_checkbox_select, folder, var))
            self.folder_checkbox.grid(row=self.row_start, column=0, padx=10, pady=5, sticky='w')
            self.folder_checkboxes[folder] = self.folder_checkbox

            self.project_combo = ttk.Combobox(self.root, state='readonly')
            self.project_combo.grid(row=self.row_start, column=1, padx=10, pady=7)
            self.project_combo.configure(width=18)
            self.project_combo.config(state=tk.DISABLED)
            self.project_combo.bind("<<ComboboxSelected>>", lambda event, folder_name=folder: self.on_change_project(folder_name))
            self.project_comboboxes[folder] = self.project_combo

            self.serverApi_combo = tk.Entry(self.root, state='readonly')
            self.serverApi_combo.grid(row=self.row_start, column=2, padx=10, pady=7)
            self.serverApi_combo.configure(width=55)
            self.serverApi_combo.config(state=tk.DISABLED)
            self.serverApi_comboboxes[folder] = self.serverApi_combo

            self.stationName_combo = ttk.Combobox(self.root, state='readonly')
            self.stationName_combo.grid(row=self.row_start, column=3, padx=10, pady=7)
            self.stationName_combo.configure(width=8)
            self.stationName_combo.config(state=tk.DISABLED)
            self.stationName_combo.bind("<<ComboboxSelected>>", lambda event, folder_name=folder: self.on_change_stationName(folder_name))
            self.stationName_comboboxes[folder] = self.stationName_combo

            self.parallelStation_combo = ttk.Combobox(self.root, state='readonly')
            self.parallelStation_combo.grid(row=self.row_start, column=4, padx=10, pady=7)
            self.parallelStation_combo.configure(width=7)
            self.parallelStation_combo.config(state=tk.DISABLED)
            self.parallelStation_combo.bind("<<ComboboxSelected>>", lambda event, folder_name=folder: self.on_change_parallelStation(folder_name))
            self.parallelStation_comboboxes[folder] = self.parallelStation_combo

            self.row_start +=1

        self.create_process_widgets()
    
    def create_process_widgets(self):
        
        self.row_startstop = self.row_start

        self.start_button = tk.Button(self.root, text="START", command=self.start_monitoring)
        self.start_button.grid(row=self.row_start, column=0, columnspan=5, padx=10, pady=5)
        self.start_button['bg'] = "green"
        self.start_button.configure(width=18)

        self.stop_button = tk.Button(self.root, text="STOP", command=self.stop_monitoring)
        self.stop_button.grid(row=self.row_start, column=0, columnspan=5, padx=10, pady=5)
        self.stop_button['bg'] = "red"
        self.stop_button.configure(width=18)
        self.stop_button.grid_forget()

        self.row_start +=1

        self.transaction_label = tk.Label(self.root, text="Transaction")
        self.transaction_label.grid(row=self.row_start, column=0, columnspan=5, padx=10, pady=5)

        self.row_start +=1

        self.transaction = tk.Listbox(self.root, width=120, height=20, xscrollcommand=True)
        self.transaction.grid(row=self.row_start, column=0, columnspan=5, padx=15, pady=10)

        self.hiddenStart = False

    def clear_above_row(self, row):
        widgets = self.root.grid_slaves()
        for widget in widgets:
            grid_info = widget.grid_info()
            if grid_info['row'] >= row:
                widget.grid_forget()
  
    def run(self):
        self.root.mainloop()

    def choose_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.path_textbox.config(state=tk.NORMAL)
            self.path_textbox.delete("1.0", tk.END)
            self.path_textbox.insert(tk.END, f" {self.folder_path} ")
            self.path_textbox.config(state=tk.DISABLED)
            self.folder_list = [f for f in os.listdir(self.folder_path) if os.path.isdir(os.path.join(self.folder_path, f))]
            for folder in self.folder_list:
                self.folder_info_list[folder] = {
                    "folder_name": folder, 
                    "project_name": "", 
                    "station_name": "", 
                    "parallel_station": "", 
                    "checked": False, 
                    "serverApi": False, 
                    "infoApi": False
                }
            self.create_checkbuttons_widgets()
            self.getProjectList()

    def on_checkbox_select(self, folder_name, var):
        self.folder_info_list[folder_name]['checked'] =  var.get()
        if var.get():
            self.project_comboboxes[folder_name].config(state='readonly')
            self.serverApi_comboboxes[folder_name].config(state='readonly')
            self.stationName_comboboxes[folder_name].config(state='readonly')
            self.parallelStation_comboboxes[folder_name].config(state='readonly')
        else:
            self.project_comboboxes[folder_name].config(state=tk.DISABLED)
            self.serverApi_comboboxes[folder_name].config(state=tk.DISABLED)
            self.stationName_comboboxes[folder_name].config(state=tk.DISABLED)
            self.parallelStation_comboboxes[folder_name].config(state=tk.DISABLED)

    def on_change_project(self, folder_name):
        selected_project = self.project_comboboxes[folder_name].get()
        self.folder_info_list[folder_name]['project_name'] =  selected_project
        self.getApiByProject(folder_name, selected_project)
            
    def on_change_stationName(self, folder_name):
        selected_station = self.stationName_comboboxes[folder_name].get()
        self.getStationInformationByStationName(folder_name, self.folder_info_list[folder_name]['infoApi'], selected_station)
        self.folder_info_list[folder_name]['station_name'] = selected_station
            
    def on_change_parallelStation(self, folder_name):
        selected_parallelStation = self.parallelStation_comboboxes[folder_name].get()
        self.folder_info_list[folder_name]['parallel_station'] = selected_parallelStation
    
    def getProjectList(self):
        url = self.url + "dgs/general_ReadProjectList.php"
        print("API use: ", url)
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            project_list = data['projectName']
            for folder in self.folder_list:
                self.project_comboboxes[folder]['values']= project_list
        else:
            print("Error:", response.status_code)

    def getApiByProject(self, folder_name, project):
        url = self.url + "dgs/general_ReadProjectList.php?projectName="+project
        print("API use: ", url)
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            serverApi = data['apiS'][0]
            infoApi = data['apiS'][1]
            self.folder_info_list[folder_name]['serverApi'] =  serverApi
            self.folder_info_list[folder_name]['infoApi'] =  infoApi
            self.getStationNameList(folder_name, self.folder_info_list[folder_name]['infoApi'], serverApi)
            
        else:
            print("Error:", response.status_code)

    def getStationNameList(self,folder_name, infoApi, serverApi):
        
        response = requests.get(infoApi+'?stationLike=ICT')
        print("API use: ", infoApi+'?stationLike=ICT')
        if response.status_code == 200:
            data = response.json()
            stationNameArray = data['result']
            if(stationNameArray != []):
                self.stationName_comboboxes[folder_name]['values']= stationNameArray
                self.stationName_comboboxes[folder_name].current(0)
                self.getStationInformationByStationName(folder_name, self.folder_info_list[folder_name]['infoApi'], stationNameArray[0])
                self.folder_info_list[folder_name]['station_name'] =  stationNameArray[0]
                self.serverApi_comboboxes[folder_name].config(state=tk.NORMAL)
                self.serverApi_comboboxes[folder_name].delete(0, tk.END)
                self.serverApi_comboboxes[folder_name].insert(0, serverApi)
                self.serverApi_comboboxes[folder_name].config(state=tk.DISABLED)
            else:
                self.stationName_comboboxes[folder_name]['values']= ['']
                self.stationName_comboboxes[folder_name].current(0)
                self.parallelStation_comboboxes[folder_name]['values']=['']
                self.parallelStation_comboboxes[folder_name].current(0)
                self.serverApi_comboboxes[folder_name].config(state=tk.NORMAL)
                self.serverApi_comboboxes[folder_name].delete(0, tk.END)
                self.serverApi_comboboxes[folder_name].config(state=tk.DISABLED)
                messagebox.showerror("Error", "ICT station not register for this project in the system")
            
        else:
            print("Error:", response.status_code)


    def getStationInformationByStationName(self, folder_name, infoApi, stationName):
        
        response = requests.get(infoApi+'?stationName='+stationName)
        print("API use: ", infoApi+'?stationName='+stationName)
        if response.status_code == 200:
            data = response.json()
            
            parallelStationArray = []
            for i in range(1, int(data['result']) + 1):
                parallelStationArray.append(i)
            self.parallelStation_comboboxes[folder_name]['values']= parallelStationArray
            self.parallelStation_comboboxes[folder_name].current(0)
            self.folder_info_list[folder_name]['parallel_station'] = parallelStationArray[0]
            
        else:
            print("Error:", response.status_code)

    def toggle_items(self):
        if self.hidden:
            row_info = self.row_info
            for i, folder in enumerate(self.folder_list):
                self.folder_checkboxes[folder].grid(row=self.row_info, column=0, padx=10, pady=5, sticky='w')
                self.project_comboboxes[folder].grid(row=self.row_info, column=1, padx=10, pady=7)
                self.serverApi_comboboxes[folder].grid(row=self.row_info, column=2, padx=10, pady=7)
                self.stationName_comboboxes[folder].grid(row=self.row_info, column=3, padx=10, pady=7)
                self.parallelStation_comboboxes[folder].grid(row=self.row_info, column=4, padx=10, pady=7)
                self.row_info +=1
            self.row_info = row_info
        else:
            for i, folder in enumerate(self.folder_list):
                self.folder_checkboxes[folder].grid_forget()
                self.project_comboboxes[folder].grid_forget()
                self.serverApi_comboboxes[folder].grid_forget()
                self.stationName_comboboxes[folder].grid_forget()
                self.parallelStation_comboboxes[folder].grid_forget()

        self.hidden = not self.hidden  # Toggle the flag

    def start_monitoring(self):
        path = self.folder_path
        haveChecked = False
        for i, folder in enumerate(self.folder_list):
            if self.folder_info_list[folder]['checked'] == True:
                if self.folder_info_list[folder]['project_name'] != '' and self.folder_info_list[folder]['station_name'] != '' and self.folder_info_list[folder]['parallel_station'] != '' and self.folder_info_list[folder]['serverApi'] != '':
                    haveChecked = True
                else:
                    messagebox.showinfo("Alert", "Empty input for folder checked of " + folder)
                    return
            
        if haveChecked:
            event_handler = {}
            self.observer = Observer()
            for i, folder in enumerate(self.folder_list):
                if self.folder_info_list[folder]['checked'] == True:
                    folder_path = os.path.join(path, folder)
                    if os.path.isdir(folder_path):
                        setting_folder = {
                            'folder': folder,
                            'model_name': self.folder_info_list[folder]['project_name'],
                            'server_url': self.folder_info_list[folder]['serverApi'],
                            'folder_path': folder_path,
                            'folder_pass': folder_path + '/pass',
                            'folder_fail': folder_path + '/fail',
                            'file_extension': self.file_extension
                        }
                        event_handler[i] = FileAddedHandler(self, setting_folder)
                        event_handler[i].process_existing_files()
                        self.observer.schedule(event_handler[i], folder_path, recursive=False)
            self.observer.start()
        else:
            messagebox.showinfo("Alert", "No folder selected")
            return
    
        if not self.hiddenStart:
            self.start_button.grid_forget()
            self.stop_button.grid(row=self.row_startstop, column=0, columnspan=5, padx=10, pady=5)
        self.hiddenStart = not self.hiddenStart
        
        for i, folder in enumerate(self.folder_list):
            self.folder_checkboxes[folder].config(state=tk.DISABLED)
            self.project_comboboxes[folder].config(state=tk.DISABLED)
            self.serverApi_comboboxes[folder].config(state=tk.DISABLED)
            self.stationName_comboboxes[folder].config(state=tk.DISABLED)
            self.parallelStation_comboboxes[folder].config(state=tk.DISABLED)

    def stop_monitoring(self):
        self.observer.stop()
        self.observer.join()
        if self.hiddenStart:
            self.stop_button.grid_forget()
            self.start_button.grid(row=self.row_startstop, column=0, columnspan=5, padx=10, pady=5)
        self.hiddenStart = not self.hiddenStart
        
        for i, folder in enumerate(self.folder_list):
            self.folder_checkboxes[folder].config(state='normal')
            self.project_comboboxes[folder].config(state='readonly')
            self.serverApi_comboboxes[folder].config(state='readonly')
            self.stationName_comboboxes[folder].config(state='readonly')
            self.parallelStation_comboboxes[folder].config(state='readonly')

    def send_file_to_server(self, folder_name, server_url, file_basename, file_name_without_ext, timestamp):
        try:
            # checked with api regarding variable input
            data={
                "serialNumber": file_name_without_ext,
                "mainStation": self.folder_info_list[folder_name]['station_name'],
                "parallelStation": self.folder_info_list[folder_name]['parallel_station'],
                "logFileName": file_basename,
                "status": 'PASS'
            }
            headers = {'Content-type': 'application/json'}
            response = requests.post(server_url, json.dumps(data), headers=headers)
            _response = json.loads(response.content.decode())
            result = _response[0]['success']
            description = _response[0]['description']
            return [result, description]
        except requests.exceptions.RequestException as e:
            print(f"Error POST file to server: {e}")
            return False

    def add_file_to_listbox(self, file_name):
        if self.transaction.size() == 50:
            self.transaction.delete(49)
        self.transaction.insert(0, file_name)
        self.transaction.itemconfig(0, fg="white")
        self.transaction.itemconfig(0, bg="darkgreen")
        bolded = font.Font(size=10, weight='bold')
        self.transaction.config(font=bolded)
        self.transaction.yview(0)

    def add_error_to_listbox(self, error_message, color):
        if self.transaction.size() == 50:
            self.transaction.delete(49)
        self.transaction.insert(0, error_message)
        self.transaction.itemconfig(0, fg="white")
        self.transaction.itemconfig(0, bg=color)
        bolded = font.Font(size=10, weight='bold')
        self.transaction.config(font=bolded)
        self.transaction.yview(0)

class FileAddedHandler(FileSystemEventHandler):
    def __init__(self, app, test):
        self.app = app
        self.folder = test['folder']
        self.folder_path = test['folder_path']
        self.model_name = test['model_name']
        self.folder_pass = test['folder_pass']
        self.folder_fail = test['folder_fail']
        self.server_url = test['server_url']
        self.file_extension = test['file_extension']

    def on_created(self, event):
        if event.is_directory:
            return
        else:
            self.process_information(event.src_path)

    def process_existing_files(self):
        for filename in os.listdir(self.folder_path):
            file_path = os.path.join(self.folder_path, filename)
            self.process_information(file_path)

    def process_information(self, file_name):
        file_extension = os.path.splitext(file_name)[1]
        if file_extension.lower() == self.file_extension.lower():
            file_basename = os.path.basename(file_name)
            file_name_without_ext = os.path.splitext(file_basename)[0]
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            [result, description] = self.app.send_file_to_server(self.folder, self.server_url, file_basename, file_name_without_ext, timestamp)
            if result == True:            
                # Move to pass folder
                move_folder = self.folder_pass
                os.makedirs(move_folder, exist_ok=True)
                shutil.move(file_name, os.path.join(move_folder, file_basename))
                self.app.add_file_to_listbox(f"  {timestamp}  |  PASS  |  {self.model_name}  |  {file_name_without_ext}  |  {description}")

                filename = move_folder + '/log.txt'
                description = f"{timestamp}  |  PASS  |  {file_name_without_ext}  |  {description}\n"

                self.update_log(filename, self.model_name, "pass", description)

            elif result == False:
                # Move to fail folder
                move_folder = self.folder_fail
                os.makedirs(move_folder, exist_ok=True)
                shutil.move(file_name, os.path.join(move_folder, file_basename))
                self.app.add_error_to_listbox(f"  {timestamp}  |  FAIL   |  {self.model_name}  |  {file_name_without_ext}  |  {description}", "orange")

                filename = move_folder + '/log.txt'
                description = f"{timestamp}  |  FAIL  |  {file_name_without_ext}  |  {description}\n"

                self.update_log(filename, self.model_name, "fail", description)

            else:
                self.app.add_error_to_listbox(f"  {timestamp}  |  FAIL   |  {file_name_without_ext}  |  Error POST {file_name_without_ext} to server, file not move", "red")

    def update_log(self, filename, model, status, description):
        if not os.path.isfile(filename):
            with open(filename, 'w') as file:
                file.write(f"This are {status} log transaction for model {model}.\n\n")

        with open(filename, 'a+') as file:
            file.write(description)


if __name__ == "__main__":
    app = MonitorApp()
    app.run()
