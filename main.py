"""Import required packages"""
import os
import sys
from pathlib import Path
import webbrowser
from tkinter.messagebox import showerror

import requests
from customtkinter import (CTk, set_appearance_mode, set_default_color_theme,
                           CTkEntry, CTkButton, CTkTextbox)
import playsound


class App(CTk):
    """Application class"""
    def __init__(self):
        super().__init__()
        self.title('Dictionary App')
        self.geometry('650x680')
        set_appearance_mode('dark')
        set_default_color_theme('green')
        self.entry = CTkEntry(self, width=150, height=30, placeholder_text='Enter a word...',
                              font=('Segoe UI', 18, 'bold'))
        self.entry.grid(row=0, column=0, padx=50, pady=50)
        self.enter = CTkButton(self, width=130, height=30, text='Search',
                               font=('Segoe UI', 18, 'bold'), command=self.search_word)
        self.enter.grid(row=0, column=1, padx=20, pady=50)

    def search_word(self):
        """Search for a word in FreeDictionaryAPI"""
        try:
            url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{self.entry.get()}'
            response = requests.get(url, timeout=10)
            json = response.json()
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
                if len(synonyms) >= 5:
                    synonyms_text = '\n'.join(synon for synon in synonyms)
                else:
                    synonyms_text = ', '.join(synonyms)
                synonyms_textbox.insert('end', f'{synonyms_text}\n -------------- \n')
            synonyms_textbox.grid(row=1, column=0, padx=20, pady=20)
            synonyms_textbox.configure(state='disabled')
            definitions = CTkTextbox(self, width=260, height=400,
                                     font=('Segoe UI', 16),
                                     scrollbar_button_color='darkgreen',
                                     scrollbar_button_hover_color='black')
            definitions.insert('end', 'Definitions: \n\n')
            for defin in json[0]['meanings']:
                definitions.insert('end', f'As {defin["partOfSpeech"]}:\n')
                for definit in defin['definitions']:
                    definitions.insert('end', f'{definit["definition"]}')
                definitions.insert('end', '\n -------------- \n')
            definitions.grid(row=1, column=1, padx=20, pady=20)
            definitions.configure(state='disabled')
            def hear():
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
                        file_.write(audio_response.content)
                    playsound.playsound(f'{Path().cwd() / f"""{json[0]["word"]}.mp3"""}',
                                        block=False)
                    os.remove(f'{json[0]["word"]}.mp3')
                except requests.exceptions.MissingSchema:
                    showerror('Word has no audio', 'The API did not provide audio for this word.')
                except playsound.PlaysoundException:
                    os.system(f'{"main.exe" if "main.exe" in os.listdir() else "python main.py"}')
                    sys.exit(0)
            hear_btn = CTkButton(self, width=50, height=30, text='Listen', command=hear,
                                 font=('Segoe UI', 16, 'bold'))
            hear_btn.grid(row=0, column=2, pady=20, sticky='e')
            show_api_response = CTkButton(self, width=100, height=30, text='Show API response',
                                          command=lambda: webbrowser.open(url),
                                          font=('Segoe UI', 16, 'bold'))
            show_api_response.grid(row=2, column=0, padx=20, pady=20)
        except KeyError:
            showerror('Word not found', 'The word was not found correctly. \nPlease try again.')


if __name__ == '__main__':
    app = App()
    app.mainloop()
