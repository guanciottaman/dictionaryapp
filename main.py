from pathlib import Path
from customtkinter import *
import playsound
import requests
from tkinter.messagebox import showerror


class App(CTk):
    def __init__(self):
        super().__init__()
        self.title('Dictionary App')
        self.geometry('650x680')
        set_appearance_mode('dark')
        set_default_color_theme('green')
        
        self.entry = CTkEntry(self, width=150, height=30, placeholder_text='Enter a word...', font=('Segoe UI', 18, 'bold'))
        self.entry.grid(row=0, column=0, padx=50, pady=50)
        self.enter = CTkButton(self, width=130, height=30, text='Search', font=('Segoe UI', 18, 'bold'), command=self.search_word)
        self.enter.grid(row=0, column=1, padx=30, pady=50)

    def search_word(self):
        try:
            response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{self.entry.get()}')
            json = response.json()
            
            meanings = json[0]['meanings']
            synonyms_textbox = CTkTextbox(self, height=400, font=('Segoe UI', 16), scrollbar_button_color='darkgreen', scrollbar_button_hover_color='black')
            synonyms_textbox.insert('end', 'Synonyms: \n\n')
            for meaning in meanings:
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

            definitions = CTkTextbox(self, height=400, font=('Segoe UI', 16), scrollbar_button_color='darkgreen', scrollbar_button_hover_color='black')
            definitions.insert('end', 'Definitions: \n\n')
            for defin in meanings:
                definitions.insert('end', f'As {defin["partOfSpeech"]}:\n')
                for definit in defin['definitions']:
                    definitions.insert('end', f'{definit["definition"]}')
                definitions.insert('end', '\n -------------- \n')
            definitions.grid(row=1, column=1, padx=50, pady=20)
            definitions.configure(state='disabled')
            def hear():
                try:
                    phcs = json[0]['phonetics']
                    for phonetic, i in enumerate(phcs):
                        audio_link = phcs[phonetic]['audio']
                        if audio_link == '': continue
                        else: break
                    r = requests.get(audio_link)
                    with open(f'{json[0]["word"]}.mp3', 'wb') as f:
                        f.write(r.content)
                    playsound.playsound(f'{Path().cwd() / f"""{json[0]["word"]}.mp3"""}')
                    os.remove(f'{json[0]["word"]}.mp3')
                except requests.exceptions.MissingSchema:
                    showerror('Word has no audio', 'The API did not provide audio for this word.')
            hear_btn = CTkButton(self, width=50, height=30, text='Listen', command=hear, font=('Segoe UI', 16, 'bold'))
            hear_btn.grid(row=0, column=2, pady=20)
        except KeyError:
            showerror('Word not found', 'The word was not found correctly. \nPlease try again.')


if __name__ == '__main__':
    app = App()
    app.mainloop()
