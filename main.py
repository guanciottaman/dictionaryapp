"""Import required packages"""
import os
import sys
from pathlib import Path
import webbrowser
from tkinter.messagebox import showerror
import threading

import requests
from customtkinter import (CTk, set_appearance_mode, set_default_color_theme,
                           CTkEntry, CTkButton, CTkTextbox)
import playsound


class App(CTk):
    """Application class"""
    def __init__(self):
        super().__init__()
        self.title('Dictionary App')
        set_appearance_mode('dark')
        set_default_color_theme('green')
        self.geometry('650x680+550+100')
        self.resizable(False, False)
        self.iconbitmap('dict.ico')
        self.entry = CTkEntry(self, width=150, height=30, placeholder_text='Enter a word...',
                              font=('Segoe UI', 18, 'bold'))
        self.entry.grid(row=0, column=0, padx=50, pady=50)
        self.enter = CTkButton(self, width=130, height=30, text='Search',
                               font=('Segoe UI', 18, 'bold'), command=self.start_thread)
        self.enter.grid(row=0, column=1, padx=20, pady=50)

    def start_thread(self):
        threading.Thread(target=self.search_word).start()

    def search_word(self):
        if self.entry.get() == '':
            return
        """Search for a word in FreeDictionaryAPI"""
        try:
            # URL for API request
            url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{self.entry.get()}'
            response = requests.get(url, timeout=10)
            json = response.json()
            self.create_synonyms(json)
            self.create_definitions(json)
            hear_btn = CTkButton(self, width=50, height=30, text='Listen',
                                 command=lambda: self.hear(json),
                                 font=('Segoe UI', 16, 'bold'))
            hear_btn.grid(row=0, column=2, pady=20, sticky='e')
            show_api_response = CTkButton(self, width=100, height=30, text='Show API response',
                                          command=lambda: webbrowser.open(url),
                                          font=('Segoe UI', 16, 'bold'))
            show_api_response.grid(row=2, column=0, padx=20, pady=20)
        except KeyError:
            showerror('Word not found', 'The word was not found correctly. \nPlease try again.')

    def create_synonyms(self, json):
        synonyms_textbox = CTkTextbox(self, height=400,
                                          font=('Segoe UI', 16),
                                          scrollbar_button_color='darkgreen',
                                          scrollbar_button_hover_color='black')
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
        definitions = CTkTextbox(self, width=260, height=400,
                                     font=('Segoe UI', 16),
                                     scrollbar_button_color='darkgreen',
                                     scrollbar_button_hover_color='black')
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


if __name__ == '__main__':
    app = App()
    app.mainloop()
