"""
Enables auto-rotation of your PCB in the 3D viewer

https://github.com/HMOFA-CHAD/kicad-auto-rotation-plugin

License: GNU Affero General Public License v3.0

Author: Ian Pritchard

Contact: ian.pritchard@anthrobotics.ca

This plugin automates the F-key flipping of your PCB in the 3D viewer, creating an automated 360 degree "rotation". Useful for showing off your shiny new PCB to the world, in all its 3D glory!

How to use:

In pcbnew, open up the 3D viewer first. Next, go back to pcbnew and click on the Auto Rotation Plugin icon in the pcbnew toolbar. The 3D viewer window will automatically re-focus, and your PCB will begin rotating.

You can change the number of rotations and pauses between F-key presses by changing the "flips" and "pause" variables in the auto_rotate.py script.

If you have any questions, problems, or suggestions, please submit them to the issues page on GitHub! Contributions are welcome!

"""

import pcbnew
import wx
import time
from pathlib import Path
import subprocess
import threading

flips = 10 #number of times the PCB will be rotated 180 degrees.
pause = 2.5 #delay (in seconds) between flips (when the "F" key is virtually pressed). A setting of 2.5 is tested to work well with a redraw speed of 1. Play around with the settings if you want, but YMMV.

class AutoRotatePlugin(pcbnew.ActionPlugin):
    def defaults(self):
        plugin_dir = Path(__file__).resolve().parent
        self.resources_dir = plugin_dir.parent.parent / "resources" / plugin_dir.name
        self.icon_file_name = str(self.resources_dir / "icon.png")
        self.show_toolbar_button = True
        self.name = "Auto Rotation Plugin"
        self.category = "3D Viewer"
        self.description = "Enables auto-rotating in the 3D viewer (open and focus viewer first)"

    def Run(self):
        # Print all top-level window titles to console for debug
        print("Available windows:")
        for w in wx.GetTopLevelWindows():
            print(w.GetTitle())

        # Find PCB editor frame
        frame = None
        for window in wx.GetTopLevelWindows():
            title = window.GetTitle().lower()
            if 'pcb editor' in title or 'pcbnew' in title:
                frame = window
                break

        if frame is None:
            wx.MessageBox("Cannot find the PCB editor window.", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Find 3D viewer
        viewer = None
        for window in wx.GetTopLevelWindows():
            title = window.GetTitle().lower()
            if '3d viewer' in title:
                viewer = window
                break

        if viewer is None:
            wx.MessageBox("Cannot find the 3D viewer. Open it manually (View > 3D Viewer), focus it, and retry.", "Error", wx.OK | wx.ICON_ERROR)
            return


        viewer.Raise()

        # Get position and size, print for debug
        pos = viewer.GetScreenPosition()
        size = viewer.GetSize()
        center_x = pos.x + size.x // 2
        center_y = pos.y + size.y // 2 + 30  # Offset for title bar
        print(f"Viewer pos: {pos}, size: {size}, center: ({center_x}, {center_y})")

        # Get screen dimensions (for edge detection; assuming single screen)
        try:
            geom_cmd = ['flatpak-spawn', '--host', 'xdotool', 'getdisplaygeometry']
            geom_output = subprocess.run(geom_cmd, capture_output=True, text=True).stdout.strip()
            screen_width, screen_height = map(int, geom_output.split())
        except:
            screen_width = 1280  # Default Steam Deck resolution
            screen_height = 800
            print("Using default screen size: 1280x800")

        # Move mouse to center
        subprocess.run(['flatpak-spawn', '--host', 'xdotool', 'mousemove', str(center_x), str(center_y)])
        time.sleep(0.5)  # Pause to ensure move completes

        # Single "flip" testing:
        # # Simulate pressing "F" key for flip (replace drag with this for slower animation)
        # subprocess.run(['flatpak-spawn', '--host', 'xdotool', 'key', 'f'])

        # Optional: For repeated flips (e.g., continuous rotation), uncomment and adjust loop/repeats
        def flip_thread():
           repeats = flips  # Number of flips (each 180 degrees)
           for _ in range(repeats):
               subprocess.run(['flatpak-spawn', '--host', 'xdotool', 'key', 'f'])
               time.sleep(pause)  # Pause between flips (adjust based on animation duration and redraw speed)
        threading.Thread(target=flip_thread, daemon=True).start()

