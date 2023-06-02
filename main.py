"""Import required packages"""
import os
import sys
from pathlib import Path
import webbrowser
from tkinter.messagebox import showerror
import threading

import requests
from customtkinter import (CTk, set_appearance_mode, set_default_color_theme, get_appearance_mode,
                           CTkEntry, CTkButton, CTkTextbox, CTkLabel, CTkImage)
from PIL import Image
import playsound


class App(CTk):
    """Application class"""
    def __init__(self):
        super().__init__()
        self.title('Dictionary App')
        set_appearance_mode('dark')
        set_default_color_theme('green')
        self.geometry('660x680+550+100')
        self.resizable(False, False)
        self.iconbitmap('assets\\dict.ico')
        self.entry = CTkEntry(self, width=150, height=30, placeholder_text='Enter a word...',
                              font=('Segoe UI', 18, 'bold'))
        self.entry.grid(row=0, column=0, padx=50, pady=50)
        self.enter = CTkButton(self, width=130, height=30, text='Search',
                               fg_color=('lightgreen', '#2CC985'),
                               font=('Segoe UI', 18, 'bold'), command=self.start_thread)
        self.enter.grid(row=0, column=1, padx=20, pady=50)
        self.icon = CTkImage(light_image=Image.open('assets\\darkicon.png'),
                             dark_image=Image.open('assets\\lighticon.png'))
        self.change_app_mode = CTkButton(self, width=60, height=30, text='',
                                         image=self.icon,
                                         command=self._change_app_mode,
                                         fg_color=('lightgreen', '#2CC985'))
        self.change_app_mode.grid(row=0, column=2, pady=30)

    def _change_app_mode(self):
        if get_appearance_mode() == 'Light':
            set_appearance_mode('dark')
        elif get_appearance_mode() == 'Dark':
            set_appearance_mode('light')

    def start_thread(self):
        """Start word search thread"""
        thread = threading.Thread(target=self.search_word)
        thread.start()
        img = CTkImage(Image.open('assets\\spin.gif'))
        loading = CTkLabel(self, width=40, height=40, text='', font=('Segoe UI', 16), image=img)
        loading.grid(row=1, column=0, padx=40, pady=30)
        while thread.is_alive():
            self.update()
        loading.destroy()

    def search_word(self):
        """Search for a word in FreeDictionaryAPI"""
        if self.entry.get() == '':
            return
        try:
            # URL for API request
            word = self.entry.get()
            url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'
            response = requests.get(url, timeout=10)
            json = response.json()
            self.create_synonyms(json)
            self.create_definitions(json)
            icon = CTkImage(Image.open('assets\\icon.png'), size=(25, 25))
            hear_btn = CTkButton(self, width=50, height=30, text='Listen', image=icon,
                                 command=lambda: self.start_audio_thread(json),
                                 font=('Segoe UI', 16, 'bold'),
                                 fg_color=('lightgreen', '#2CC985'))
            hear_btn.grid(row=0, column=2, pady=20, sticky='e')
            show_api_response = CTkButton(self, width=100, height=30, text='Show API response',
                                          command=lambda: webbrowser.open(url),
                                          font=('Segoe UI', 16, 'bold'),
                                          fg_color=('lightgreen', '#2CC985'))
            show_api_response.grid(row=2, column=0, padx=20, pady=20)
            self.change_app_mode.grid(row=1, column=2)
        except KeyError:
            showerror('Word not found', 'The word was not found correctly. \nPlease try again.')
        except requests.exceptions.ReadTimeout:
            showerror('Connection timed out')

    def create_synonyms(self, json):
        """Creates a list of synonyms"""
        synonyms_textbox = CTkTextbox(self, height=400,
                                          font=('Segoe UI', 16),
                                          scrollbar_button_color=('lightgreen', 'darkgreen'),
                                          scrollbar_button_hover_color=('darkgreen', 'black'))
        synonyms_textbox.tag_config('sel', background='lightgreen', foreground='black')
        synonyms_textbox.insert('end', 'Synonyms: \n\n')
        for meaning in json[0]['meanings']:
            synonyms_textbox.insert('end', f'As {meaning["partOfSpeech"]}:\n')
            synonyms = []
            for syn in meaning["synonyms"]:
                if not meaning["synonyms"]:
                    synonyms.append('None')
                else:
                    synonyms.append(syn)
            # if lenght is greater or equal than 5 make synonyms go in newlines
            if len(synonyms) >= 5:
                synonyms_text = '\n'.join(synon for synon in synonyms)
            else:
                synonyms_text = ', '.join(synonyms)
            synonyms_textbox.insert('end', f'{synonyms_text}\n -------------- \n')
        synonyms_textbox.grid(row=1, column=0, padx=20, pady=20)
        synonyms_textbox.configure(state='disabled')

    def create_definitions(self, json):
        """Create definitions"""
        definitions = CTkTextbox(self, width=260, height=400,
                                     font=('Segoe UI', 16),
                                     scrollbar_button_color=('lightgreen', 'darkgreen'),
                                     scrollbar_button_hover_color=('darkgreen', 'black'))
        definitions.tag_config('sel', background='lightgreen', foreground='black')
        definitions.insert('end', 'Definitions: \n\n')
        for defin in json[0]['meanings']:
            definitions.insert('end', f'As {defin["partOfSpeech"]}:\n')
            for definit in defin['definitions']:
                definitions.insert('end', f'{definit["definition"]}')
            definitions.insert('end', '\n -------------- \n') # spacing
        definitions.grid(row=1, column=1, padx=20, pady=20)
        definitions.configure(state='disabled')


    def hear(self, json):
        """Play word phonetics"""
        try:
            phcs = json[0]['phonetics']
            for i in range(len(phcs)):
                audio_link = phcs[i]['audio']
                if audio_link == '':
                    continue
                break
            audio_response = requests.get(audio_link, timeout=10)
            with open(f'{json[0]["word"]}.mp3', 'wb') as file_:
                file_.write(audio_response.content) # write the mp3 to disk in binary format
            playsound.playsound(f'{Path().cwd() / f"""{json[0]["word"]}.mp3"""}',
                                block=False)
            os.remove(f'{json[0]["word"]}.mp3')
        except requests.exceptions.MissingSchema: # No audio link in the phonetics
            showerror('Word has no audio', 'The API did not provide audio for this word.')
        except playsound.PlaysoundException: # Fixing error when playing multiple tracks
            os.system(f'{"main.exe" if "main.exe" in os.listdir() else "python main.py"}')
            sys.exit(0)

    def start_audio_thread(self, json):
        """Start audio thread"""
        threading.Thread(target=self.hear, args=(json, )).start()


if __name__ == '__main__':
    app = App()
    app.mainloop()
