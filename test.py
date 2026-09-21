from screeninfo import get_monitors

for i, m in enumerate(get_monitors()):
    print(f"Monitor {i}: {m.width}x{m.height} na pozícii X={m.x}, Y={m.y} {'(Primárny)' if m.is_primary else ''}")
