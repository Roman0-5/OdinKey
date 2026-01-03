# OdinKey - Lokaler Passwortmanager
Passwortmanager mit CLI und GUI

## How OdinKey Handles Login and Session (Simple Explanation)

OdinKey keeps your data safe by using a session. Here is how it works, step by step:

1. **What is a session?**
   - A session is like a visitor pass. When you log in, you get a pass. This pass lets you use the app and see your passwords.
   - The session stores who you are and a special key (called the master key) to unlock your passwords.

2. **How do you get a session?**
   - When you enter your username and password and click login, the app checks if your password is correct.
   - If it is correct, the app creates a session for you. Now you are logged in.

3. **What happens during a session?**
   - While you are logged in, you can see, add, edit, or delete your password profiles.
   - The app always checks if your session is still active before showing or changing any passwords.

4. **How does the app know if you are still logged in?**
   - The session has a timer. If you do not use the app for 10 minutes, your session ends. This is for your safety.
   - When the session ends, you must log in again to see your passwords.

5. **Where is the session stored?**
   - The session is saved in the main window of the app. Other parts of the app (like the dashboard) ask the main window for the session.
   - The session is never saved to disk. It only exists while the app is open and you are logged in.

6. **Why is this safe?**
   - Your master key and passwords are only in memory while you are logged in.
   - When you log out or the session ends, the app forgets your key and passwords.

7. **What if you log out?**
   - If you click logout, the session is deleted. You must log in again to use the app.

**Summary:**
- You must log in to use OdinKey.
- The app gives you a session (a pass) when you log in.
- The session lets you use all features.
- If you are inactive for 10 minutes, or you log out, the session ends and you must log in again.

This keeps your passwords safe, even if you forget to close the app.

---

*This section documents the core principles for session and state management in OdinKey. For details, see the implementation in `src/core/session.py` and GUI state classes.*
