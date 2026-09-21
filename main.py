
import customtkinter as ctk
from screeninfo import get_monitors
import json
import os
import ir_remote
import cv2
import numpy as np
import pyautogui
import time
from playsound import playsound


ctk.set_appearance_mode("System")

app = ctk.CTk()
app.title("Interactive Projector")
app.geometry("400x300")


sledovanie = ""
obrazovka = ""

moznosti_sledovania = ["Ir ovladacom a kamerov", "Sledovanim ruky"]
moznosti_obrazoviek = []

for i, m in enumerate(get_monitors()):
    moznosti_obrazoviek.append(f"Monitor {i+1}: {m.width}x{m.height},{m.name}")



def zmena_typu_sledovania(vybrana_moznost):
    global sledovanie
    sledovanie = vybrana_moznost


def zmena_typu_obrazovky(vybrana_moznost):
    global obrazovka
    obrazovka = vybrana_moznost

def kalibrovat():
    if sledovanie == "Ir ovladacom a kamerov":
        ulozit_do_config("calibration_points", ir_remote.kalibracia())
        print("Kalibracia dokončena. Môžeš kresliť.")
def spustit():
    if sledovanie == "Ir ovladacom a kamerov":
        ir_remote.spustit(nacitat_z_config("calibration_points"))

def ulozit_do_config(kluc, hodnota):
    config_path = "config.json"
    config_data = {}

    # Ak súbor existuje, načítame jeho obsah
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config_data = json.load(f)

    # Aktualizujeme alebo pridáme nový kľúč a hodnotu
    config_data[kluc] = hodnota

    # Uložíme späť do súboru
    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=4)

def nacitat_z_config(kluc):
    config_path = "config.json"

    # Ak súbor existuje, načítame jeho obsah
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config_data = json.load(f)
            return config_data.get(kluc, None)
    return None








label = ctk.CTkLabel(app, text="Vyber si sposob sledovania", font=("Arial", 16))
label.pack(pady=20)

option_menu = ctk.CTkOptionMenu(
    app, 
    values=moznosti_sledovania, 
    command=zmena_typu_sledovania
)
option_menu.pack(pady=5)
option_menu.set("Vyber sposob") # Nastaví predvolený text


option_menu = ctk.CTkOptionMenu(
    app, 
    values=moznosti_obrazoviek, 
    command=zmena_typu_obrazovky
)
option_menu.pack(pady=5)
option_menu.set("Vyber obrazovku") # Nastaví predvolený text

button_frame = ctk.CTkFrame(app)
button_frame.pack(pady=20, fill="x", padx=20)

button_zrusit = ctk.CTkButton(button_frame, text="Zrusit", command=app.destroy,width=50,fg_color="red",hover_color="darkred")
button_zrusit.pack(side="left", padx=10, pady=10,)


button_spusit_kalibraciu = ctk.CTkButton(button_frame, text="Kalibrovat", command=kalibrovat,width=100,fg_color="blue",hover_color="darkblue")
button_spusit_kalibraciu.pack(side="left", padx=10, pady=10)

button_spusit_bez_kalibracie = ctk.CTkButton(button_frame, text="Spustit", command=spustit,width=150,fg_color="green",hover_color="darkgreen")
button_spusit_bez_kalibracie.pack(side="left", padx=10, pady=10)





app.mainloop()