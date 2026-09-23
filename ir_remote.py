import cv2
import numpy as np
import pyautogui
import time
from playsound import playsound
import config

   # Premenné pre kalibráciu


calibration_points = []
corner_names = ["Lavy Horny", "Pravy Horny", "Pravy Dolny", "Lavy Dolny"]
prev_ir_detected = False  # <--- 1. PRIDANÁ GLOBÁLNA PREMENNÁ PRE STAV
cas_od_posledneho_stlacenia = 0  # <--- 2. PRIDANÁ GLOBÁLNA PREMENNÁ PRE ČAS POSLEDNÉHO STLAČENIA
is_drawing = False  # <--- 3. PRIDANÁ GLOBÁLNA PREMENNÁ PRE STAV KRESLENIA


def kalibracia(frame, BRIGHTNESS_THRESHOLD, screen_w, screen_h):
    global prev_ir_detected, cas_od_posledneho_stlacenia, calibration_points

    


    frame = cv2.flip(frame, 1)
    cam_h, cam_w = frame.shape[:2]

    # Prevod na čiernobielo a hľadanie najjasnejšieho bodu
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(blurred)

    cx, cy = maxLoc
    ir_detected = maxVal > BRIGHTNESS_THRESHOLD
    idx = len(calibration_points)
    cv2.putText(frame, f"KALIBRACIA: Klikni na {corner_names[idx]} roh", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    # Ak sme práve stlačili tlačidlo (IR svetlo sa objavilo tento frame)
    if ir_detected and not prev_ir_detected and not (time.time() - cas_od_posledneho_stlacenia < 1):
        cas_od_posledneho_stlacenia = time.time()
        calibration_points.append((cx, cy))
        print(f"Zaznamenaný roh {corner_names[idx]}: ({cx}, {cy})")
        
        
        
        # Ak máme všetky 4 rohy, vypočítame transformačnú maticu
        if len(calibration_points) == 4:
            # Namapujeme rohy kamery na plné rozlíšenie monitora
            pts2 = np.float32([[0, 0], [screen_w, 0], [screen_w, screen_h], [0, screen_h]])


            is_calibrated = True
            print("Kalibrácia úspešná! Môžeš kresliť.")
            playsound('zvuk/efekt2.wav', block=False)
            config.ulozit_do_config("calibration_points", calibration_points)
            prev_ir_detected = ir_detected
            return frame, is_calibrated

        else:
            playsound('zvuk/efekt1.wav', block=False)
    prev_ir_detected = ir_detected
            
        
    # Vykreslenie doteraz naklikaných bodov
    for pt in calibration_points:
        cv2.circle(frame, pt, 5, (255, 0, 0), -1)



 

    is_calibrated = False
    return frame, is_calibrated

def spustit(frame, BRIGHTNESS_THRESHOLD, screen_w, screen_h,transform_matrix, calibration_points):
    global is_drawing
 

    frame = cv2.flip(frame, 1)
    cam_h, cam_w = frame.shape[:2]

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(blurred)

    # Vykreslenie modrého štvorca kalibrovanej oblasti
    pts = np.int32(calibration_points).reshape((-1, 1, 2))
    cv2.polylines(frame, [pts], True, (255, 0, 0), 2)
    
    cx, cy = maxLoc
    ir_detected = maxVal > BRIGHTNESS_THRESHOLD

    if ir_detected:
        # Transformácia súradníc z kamery na obrazovku
        pt_cam = np.array([[[cx, cy]]], dtype=np.float32)
        pt_screen = cv2.perspectiveTransform(pt_cam, transform_matrix)
            
        screen_x, screen_y = pt_screen[0][0]

        screen_x = max(0, min(screen_w, int(screen_x)))
        screen_y = max(0, min(screen_h, int(screen_y)))

        # Plynulý pohyb myši na vypočítané súradnice
        pyautogui.moveTo(screen_x, screen_y, _pause=False)

        # --- OPRAVA 3: Správna logika pre držanie a kreslenie ---
        if not is_drawing:
            pyautogui.mouseDown(_pause=False)
            is_drawing = True

        # Vizuálna kontrola: ak detegujeme IR, nakreslíme zelený kruh na obrazovku kamery
        cv2.circle(frame, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
    
    else:
        # --- OPRAVA 4: Myš pustíme IBA vtedy, ak svetlo ZMIZNE ---
        if is_drawing:
            pyautogui.mouseUp(_pause=False)
            is_drawing = False
    return frame
        



