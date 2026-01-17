import pyperclip
import threading


def clear_clipboard():
    """Leert die Zwischenablage."""
    try:
        pyperclip.copy("")
    except Exception:
        pass  # Fehler ignorieren, falls Clipboard blockiert ist


def copy_with_timeout(text, timeout=180): #NFMR10
    """
    Kopiert Text in die Zwischenablage und löscht ihn automatisch nach X Sekunden.
    Startet einen Hintergrund-Timer.
    """
    try:
        pyperclip.copy(text)

        # Timer starten, der das Clipboard leert
        timer = threading.Timer(timeout, clear_clipboard)
        timer.daemon = True  # Wichtig: Timer stirbt, wenn Hauptprogramm beendet wird
        timer.start()

        return True
    except Exception as e:
        print(f"Fehler beim Zugriff auf Zwischenablage: {e}")
        return False