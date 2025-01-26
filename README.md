How to move it on desktop(Linux)

1. cd ~/.local/share/applications/

2.nano my_app.desktop

3. [Desktop Entry]
Version=1.0
Name=MyApp
Comment=My Python Tkinter App
Exec=python3 /path/to/your_script.py
Icon=/path/to/icon.png
Terminal=false
Type=Application
Categories=Utility;


4. chmod +x my_app.desktop

5. mv my_app.desktop ~/Desktop/
