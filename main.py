
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
app.geometry("665x440")



screen_w, screen_h = pyautogui.size()
pyautogui.FAILSAFE = False


cap = cv2.VideoCapture(0)


sledovanie = config.nacitat_z_config("sledovanie")
obrazovka = config.nacitat_z_config("obrazovka")
rezim = "caka"
BRIGHTNESS_THRESHOLD = config.nacitat_z_config("BRIGHTNESS_THRESHOLD")


moznosti_sledovania = ["Ir ovladacom a kamerov", "Sledovanim ruky"]
moznosti_obrazoviek = []

for i, m in enumerate(get_monitors()):
    moznosti_obrazoviek.append(f"Monitor {i+1}: {m.width}x{m.height},{m.name}")



def zmena_typu_sledovania(vybrana_moznost):
    global sledovanie
    sledovanie = vybrana_moznost
    config.ulozit_do_config("sledovanie", sledovanie)  # Uložíme vybranú možnosť do config.json


def zmena_typu_obrazovky(vybrana_moznost):
    global obrazovka
    obrazovka = vybrana_moznost
    config.ulozit_do_config("obrazovka", obrazovka)  # Uložíme vybranú možnosť do config.json

def kalibrovat():
    global rezim
    button_zrusit.configure(text="Stop")
    if sledovanie == "Ir ovladacom a kamerov" and rezim == "caka":
        ir_remote.calibration_points = []
        ir_remote.prev_ir_detected = False
        rezim = "ir_kalibracia"

def spustit():
    global rezim, transform_matrix
    button_zrusit.configure(text="Stop")
    if sledovanie == "Ir ovladacom a kamerov" and rezim == "caka":
        global calibration_points
        calibration_points = config.nacitat_z_config("calibration_points")
        pts1 = np.float32(calibration_points)
        pts2 = np.float32([[0, 0], [screen_w, 0], [screen_w, screen_h], [0, screen_h]])
        transform_matrix = cv2.getPerspectiveTransform(pts1, pts2)
        rezim = "ir_sledovanie"
def stop():
    global rezim
    if rezim != "caka":
        rezim = "caka"
        button_zrusit.configure(text="Zrusit")
    else:
        app.destroy()

def pridat_citlivost():
    global BRIGHTNESS_THRESHOLD
    if BRIGHTNESS_THRESHOLD < 255:
        BRIGHTNESS_THRESHOLD += 5
        citlivost.configure(text=f"{BRIGHTNESS_THRESHOLD}")
        config.ulozit_do_config("BRIGHTNESS_THRESHOLD", BRIGHTNESS_THRESHOLD)
def ubrat_citlivost():
    global BRIGHTNESS_THRESHOLD
    if BRIGHTNESS_THRESHOLD > 0:
        BRIGHTNESS_THRESHOLD -= 5
        citlivost.configure(text=f"{BRIGHTNESS_THRESHOLD}")
        config.ulozit_do_config("BRIGHTNESS_THRESHOLD", BRIGHTNESS_THRESHOLD)




def obnov_video():
    stari_cas = time.time()
    global rezim
    success, frame = cap.read()
    if success:
        frame = cv2.flip(frame, 1)
        cam_h, cam_w = frame.shape[:2]

        if rezim == "ir_kalibracia":
            new_frame, is_calibrated = ir_remote.kalibracia(frame, BRIGHTNESS_THRESHOLD, screen_w, screen_h)
            if is_calibrated:
                rezim = "caka"
                print("Kalibrácia dokončená.")



        elif rezim == "ir_sledovanie":
            new_frame = ir_remote.spustit(frame, BRIGHTNESS_THRESHOLD, screen_w, screen_h, transform_matrix, calibration_points)


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







option_frame = ctk.CTkFrame(app)
option_frame.grid(row=0, column=1, pady=10 , padx=20, sticky="n")

nastavenia_label = ctk.CTkLabel(option_frame, text="Nastavenia")
nastavenia_label.grid(row=0, column=0, pady=5)

option_menu = ctk.CTkOptionMenu(
    option_frame, 
    values=moznosti_sledovania, 
    command=zmena_typu_sledovania
)
option_menu.grid(row=1, column=0, pady=5, padx=5)
option_menu.set(sledovanie) # Nastaví predvolený text


option_menu = ctk.CTkOptionMenu(
    option_frame, 
    values=moznosti_obrazoviek, 
    command=zmena_typu_obrazovky
)
option_menu.grid(row=2, column=0, pady=5, padx=5)
option_menu.set(obrazovka) # Nastaví predvolený text

citlivost_frame = ctk.CTkFrame(option_frame)
citlivost_frame.grid(row=3, column=0, pady=5)

nadpis_citlivost = ctk.CTkLabel(citlivost_frame, text="Citlivost")
nadpis_citlivost.grid(row=0, column=0,columnspan=2, pady=5)

citlivost = ctk.CTkLabel(citlivost_frame, text=f"{BRIGHTNESS_THRESHOLD}")
citlivost.grid(row=1, column=0,columnspan=2, padx=5)

pridat_citlivost = ctk.CTkButton(citlivost_frame, command=pridat_citlivost, text="Pridať",width=30)
pridat_citlivost.grid(row=2, column=1, padx=5, pady=5)

ubrat_citlivost = ctk.CTkButton(citlivost_frame, command=ubrat_citlivost, text="Ubrať",width=30)
ubrat_citlivost.grid(row=2, column=0, padx=5, pady=5)

video_label = ctk.CTkLabel(app, text="")
video_label.grid(row=0, column=0, pady=10)

button_frame = ctk.CTkFrame(app)
button_frame.grid(row=4, column=0, padx=20)

button_zrusit = ctk.CTkButton(button_frame, text="Zrusit", command=stop,width=50,fg_color="red",hover_color="darkred")
button_zrusit.grid(row=0, column=0, padx=10, pady=10)


button_spusit_kalibraciu = ctk.CTkButton(button_frame, text="Kalibrovat", command=kalibrovat,width=100,fg_color="blue",hover_color="darkblue")
button_spusit_kalibraciu.grid(row=0, column=1, padx=10, pady=10)

button_spusit_bez_kalibracie = ctk.CTkButton(button_frame, text="Spustit", command=spustit,width=150,fg_color="green",hover_color="darkgreen")
button_spusit_bez_kalibracie.grid(row=0, column=2, padx=10, pady=10)





obnov_video()
app.mainloop()
cap.release()