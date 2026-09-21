import cv2
import numpy as np
import pyautogui
import time
from playsound import playsound

# Rozlíšenie obrazovky
screen_w, screen_h = pyautogui.size()
pyautogui.FAILSAFE = False

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

# Zvýšený prah, keďže bez odporu je dióda extrémne jasná
BRIGHTNESS_THRESHOLD = 40

# Premenné pre kalibráciu
calibration_points = []
corner_names = ["Lavy Horny", "Pravy Horny", "Pravy Dolny", "Lavy Dolny"]
is_calibrated = False
transform_matrix = None

is_drawing = False
prev_ir_detected = False

print("Spustený kalibračný režim. Klikni IR perom na 4 rohy obrazu.")

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    cam_h, cam_w = frame.shape[:2]

    # Prevod na čiernobielo a hľadanie najjasnejšieho bodu
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(blurred)

    cx, cy = maxLoc
    ir_detected = maxVal > BRIGHTNESS_THRESHOLD

    # --- FÁZA 1: KALIBRÁCIA ---
    if not is_calibrated:
        idx = len(calibration_points)
        cv2.putText(frame, f"KALIBRACIA: Klikni na {corner_names[idx]} roh", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Ak sme práve stlačili tlačidlo (IR svetlo sa objavilo tento frame)
        if ir_detected and not prev_ir_detected:
            calibration_points.append((cx, cy))
            print(f"Zaznamenaný roh {corner_names[idx]}: ({cx}, {cy})")
            
           
            
            # Ak máme všetky 4 rohy, vypočítame transformačnú maticu
            if len(calibration_points) == 4:
                # Namapujeme rohy kamery na plné rozlíšenie monitora
                pts2 = np.float32([[0, 0], [screen_w, 0], [screen_w, screen_h], [0, screen_h]])
                transform_matrix = cv2.getPerspectiveTransform(pts1, pts2)
                is_calibrated = True
                print("Kalibrácia úspešná! Môžeš kresliť.")
                playsound('zvuk/efekt2.wav', block=False)
            else:
                playsound('zvuk/efekt1.wav', block=False)
            time.sleep(1)
        # Vykreslenie doteraz naklikaných bodov
        for pt in calibration_points:
            cv2.circle(frame, pt, 5, (255, 0, 0), -1)

    # --- FÁZA 2: KRESLENIE ---
    else:
        # Vykreslenie zeleného štvorca kalibrovanej oblasti pre vizuálnu kontrolu
        pts = np.int32(calibration_points).reshape((-1, 1, 2))
        cv2.polylines(frame, [pts], True, (255, 0, 0), 2)

        if ir_detected:
            # Transformácia súradníc z kamery na obrazovku pomocou kalibračnej matice
            pt_cam = np.array([[[cx, cy]]], dtype=np.float32)
            pt_screen = cv2.perspectiveTransform(pt_cam, transform_matrix)
            
            screen_x, screen_y = pt_screen[0][0]

            # Zaistenie, aby kurzor neušiel mimo obrazovku a nespôsobil pád
            screen_x = max(0, min(screen_w, int(screen_x)))
            screen_y = max(0, min(screen_h, int(screen_y)))

            pyautogui.moveTo(screen_x, screen_y, _pause=False)

            if not is_drawing:
                pyautogui.mouseDown(_pause=False)
                is_drawing = True

            cv2.circle(frame, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
        else:
            if is_drawing:
                pyautogui.mouseUp(_pause=False)
                is_drawing = False

    # Uloženie stavu z tohto framu do premennej pre ďalší frame
    prev_ir_detected = ir_detected

    cv2.imshow("IR Interaktivna Tabula", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        if is_drawing:
            pyautogui.mouseUp(_pause=False)
        break

cap.release()
cv2.destroyAllWindows()