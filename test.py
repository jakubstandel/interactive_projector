import cv2
import customtkinter as ctk
from PIL import Image

# 1. Vytvorenie okna (bez class)
app = ctk.CTk()
app.title("IR Interaktívna Tabuľa")
app.geometry("950x550")

# 2. Načítanie kamery
cap = cv2.VideoCapture(0)

# 3. Rozloženie prvkov v okne
video_label = ctk.CTkLabel(app, text="")
video_label.pack(side="left", padx=20, pady=20)

sidebar = ctk.CTkFrame(app, width=200)
sidebar.pack(side="right", fill="y", padx=20, pady=20)

# --- Obyčajné funkcie pre tlačidlá (bez self) ---
def spusti_kalibraciu():
    print("Kalibrácia spustená...")

def resetuj():
    print("Resetované!")

def zmena_jasu(hodnota):
    print(f"Prah jasu: {int(hodnota)}")

# --- Tlačidlá a posuvník ---
btn_calibrate = ctk.CTkButton(sidebar, text="Spustiť kalibráciu", command=spusti_kalibraciu)
btn_calibrate.pack(pady=15, padx=15)

btn_reset = ctk.CTkButton(sidebar, text="Resetovať", fg_color="red", command=resetuj)
btn_reset.pack(pady=15, padx=15)

slider_thresh = ctk.CTkSlider(sidebar, from_=10, to=255, command=zmena_jasu)
slider_thresh.set(180)
slider_thresh.pack(pady=15, padx=15)

# 4. Funkcia, ktorá stále dokola obnovuje obraz z kamery
def obnov_video():
    success, frame = cap.read()
    if success:
        frame = cv2.flip(frame, 1)

        # Tu spracuješ IR bod (OpenCV logika)
        # ...

        # Prevod obrazu z OpenCV (BGR) do formátu pre CustomTkinter (RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(640, 480))
        video_label.configure(image=ctk_img)

    # Zavolá sama seba o 15 miliseúnd (plynulých ~60 FPS)
    app.after(15, obnov_video)

# Spustenie obnovovania videa a hlavnej slučky okna
obnov_video()
app.mainloop()

# Po zatvorení okna uvoľníme kameru
cap.release()