import cv2
import numpy as np
import pyautogui
import time
from playsound import playsound

def spustit(calibration_points):
    print("Program spustený. Stlač 'q' v okne videa pre ukončenie.")
    screen_w, screen_h = pyautogui.size()
    pyautogui.FAILSAFE = False

    # --- OPRAVA 1: Výpočet transformačnej matice priamo z načítaných bodov ---
    pts1 = np.float32(calibration_points)
    pts2 = np.float32([[0, 0], [screen_w, 0], [screen_w, screen_h], [0, screen_h]])
    transform_matrix = cv2.getPerspectiveTransform(pts1, pts2)

    # --- OPRAVA 2: Inicializácia stavových premenných pred cyklom ---
    is_drawing = False
    BRIGHTNESS_THRESHOLD = 40
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

    while True:
        stari_cas = time.time()
        success, frame = cap.read()
        if not success:
            break

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
            cv2.circle(frame, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
        
        else:
            # --- OPRAVA 4: Myš pustíme IBA vtedy, ak svetlo ZMIZNE ---
            if is_drawing:
                pyautogui.mouseUp(_pause=False)
                is_drawing = False

        # Vypočítanie a zobrazenie FPS
        ceky_cas = time.time() - stari_cas
        if ceky_cas > 0:
            fps = 1 / ceky_cas
            cv2.putText(frame, f"FPS: {round(fps, 2)}", (10, cam_h-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
        cv2.imshow("IR Interaktivna Tabula", frame)

        # Ukončenie cez kláves 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            if is_drawing:
                pyautogui.mouseUp(_pause=False)
            break
        
    cap.release()
    cv2.destroyAllWindows()
