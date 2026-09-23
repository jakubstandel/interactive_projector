
import customtkinter as ctk
from screeninfo import get_monitors
import json
import os

os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"  # Vypne MSMF backend
import ir_remote
import cv2
import numpy as np
import pyautogui
import time
from playsound import playsound
from PIL import Image
import config


ctk.set_appearance_mode("System")

app = ctk.CTk()
app.title("Interactive Projector")
app.geometry("400x300")



screen_w, screen_h = pyautogui.size()
pyautogui.FAILSAFE = False


cap = cv2.VideoCapture(0)


sledovanie = ""
obrazovka = ""
rezim = "caka"

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
    global rezim
    if sledovanie == "Ir ovladacom a kamerov" and rezim == "caka":
        ir_remote.calibration_points = []
        ir_remote.prev_ir_detected = False
        rezim = "ir_kalibracia"

def spustit():
    if sledovanie == "Ir ovladacom a kamerov":
        ir_remote.spustit(config.nacitat_z_config("calibration_points"))




def obnov_video():
    stari_cas = time.time()
    global rezim
    success, frame = cap.read()
    if success:
        frame = cv2.flip(frame, 1)
        cam_h, cam_w = frame.shape[:2]

        if rezim == "ir_kalibracia":
            new_frame, is_calibrated = ir_remote.kalibracia(frame, 40, screen_w, screen_h)
            if is_calibrated:
                rezim = "caka"
                print("Kalibrácia dokončená.")
        else:
            new_frame = frame

        cv2.putText(new_frame, f"FPS: {round(1/(time.time()-stari_cas), 2)}", (10, cam_h-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)


        # Prevod obrazu z OpenCV (BGR) do formátu pre CustomTkinter (RGB)
        frame_rgb = cv2.cvtColor(new_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(480, 360))
        video_label.configure(image=ctk_img)

    # Zavolá sama seba o 15 miliseúnd (plynulých ~60 FPS)
    app.after(15, obnov_video)







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

video_label = ctk.CTkLabel(app, text="")
video_label.pack()



obnov_video()
app.mainloop()
cap.release()