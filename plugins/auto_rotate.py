"""
KiCad Auto Rotation Plugin

Version 1.1

15 Mar 2026

Enables auto-rotation of your PCB in the 3D viewer.

https://github.com/HMOFA-CHAD/kicad-auto-rotation-plugin

License: GNU Affero General Public License v3.0

Author: Ian Pritchard

Contact: ian.pritchard@anthrobotics.ca

This plugin automates the rotating and flipping of your PCB in the 3D viewer, creating an automated 360 degree "rotation". Useful for showing off your shiny new PCB to the world, in all its 3D glory!

How to use:

If you haven't already, assign a hotkey for the Y-axis rotation in the 3D viewer preferences. The auto rotation tool will prompt you for this hotkey.

In pcbnew, open up the 3D viewer first. Next, go back to pcbnew and click on the Auto Rotation Plugin icon in the pcbnew toolbar. The 3D viewer window will automatically re-focus, and a dialog will open providing you with config options.

You can change the number of rotations, flips, and delays between movements by changing the values in the dialog window. Select to either flip or rotate the board, and select OK to begin.

If you have any questions, problems, or suggestions, please submit them to the issues page on GitHub! Contributions are welcome!

"""

import pcbnew
import wx
import time
from pathlib import Path
import subprocess
import threading

# Default values (still here for reference, but can be overridden via dialog)
rotate_hotkey_default = 'period' #hotkey assigned to Y-axis rotation in the 3D viewer
flip_hotkey_default = 'f' #hotkey assigned to flipping the board (default is F)
rotations_default = 36 #number of times the rotate hotkey will be pressed. Default of 10 degree increments.
rotate_delay_default = 0.2 #delay (in seconds) between virtual key presses for rotating. A lower value will increase the rotation speed.
flips_default = 11 #number of times the PCB will be rotated 180 degrees.
flip_delay_default = 2.5 #delay (in seconds) between virtual key presses for flipping. A value of 2.5 is tested to work well with a redraw speed of 1. Play around with the settings if you want, but YMMV.

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

        # Custom dialog for settings and choice
        class SettingsDialog(wx.Dialog):
            def __init__(self, parent):
                super(SettingsDialog, self).__init__(parent, -1, "Auto Rotation Settings")

                panel = wx.Panel(self)
                sizer = wx.BoxSizer(wx.VERTICAL)

                grid = wx.GridBagSizer(5, 5)

                # Labels and inputs
                row = 0

                grid.Add(wx.StaticText(panel, label="Rotate Hotkey:"), pos=(row, 0), flag=wx.ALIGN_CENTER_VERTICAL)
                self.rotate_hotkey_ctrl = wx.TextCtrl(panel, value=rotate_hotkey_default)
                grid.Add(self.rotate_hotkey_ctrl, pos=(row, 1))

                row += 1
                grid.Add(wx.StaticText(panel, label="Flip Hotkey:"), pos=(row, 0), flag=wx.ALIGN_CENTER_VERTICAL)
                self.flip_hotkey_ctrl = wx.TextCtrl(panel, value=flip_hotkey_default)
                grid.Add(self.flip_hotkey_ctrl, pos=(row, 1))

                row += 1
                grid.Add(wx.StaticText(panel, label="Rotations:"), pos=(row, 0), flag=wx.ALIGN_CENTER_VERTICAL)
                self.rotations_ctrl = wx.SpinCtrl(panel, value=str(rotations_default), min=1, max=1000)
                grid.Add(self.rotations_ctrl, pos=(row, 1))

                row += 1
                grid.Add(wx.StaticText(panel, label="Rotate Delay (s):"), pos=(row, 0), flag=wx.ALIGN_CENTER_VERTICAL)
                self.rotate_delay_ctrl = wx.TextCtrl(panel, value=str(rotate_delay_default))
                grid.Add(self.rotate_delay_ctrl, pos=(row, 1))

                row += 1
                grid.Add(wx.StaticText(panel, label="Flips:"), pos=(row, 0), flag=wx.ALIGN_CENTER_VERTICAL)
                self.flips_ctrl = wx.SpinCtrl(panel, value=str(flips_default), min=1, max=1000)
                grid.Add(self.flips_ctrl, pos=(row, 1))

                row += 1
                grid.Add(wx.StaticText(panel, label="Flip Delay (s):"), pos=(row, 0), flag=wx.ALIGN_CENTER_VERTICAL)
                self.flip_delay_ctrl = wx.TextCtrl(panel, value=str(flip_delay_default))
                grid.Add(self.flip_delay_ctrl, pos=(row, 1))

                row += 1
                grid.Add(wx.StaticText(panel, label="Action:"), pos=(row, 0), flag=wx.ALIGN_CENTER_VERTICAL)
                choices = ["Rotate the board", "Flip the board"]
                self.action_choice = wx.Choice(panel, choices=choices)
                self.action_choice.SetSelection(0)
                grid.Add(self.action_choice, pos=(row, 1))

                sizer.Add(grid, 0, wx.ALL | wx.EXPAND, 10)

                # Buttons
                btn_sizer = wx.StdDialogButtonSizer()
                ok_btn = wx.Button(panel, wx.ID_OK)
                btn_sizer.AddButton(ok_btn)
                cancel_btn = wx.Button(panel, wx.ID_CANCEL)
                btn_sizer.AddButton(cancel_btn)
                btn_sizer.Realize()
                sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

                panel.SetSizer(sizer)
                sizer.Fit(self)

        dialog = SettingsDialog(frame)
        if dialog.ShowModal() == wx.ID_OK:
            # Get values
            rotate_hotkey = dialog.rotate_hotkey_ctrl.GetValue()
            flip_hotkey = dialog.flip_hotkey_ctrl.GetValue()
            try:
                rotations = int(dialog.rotations_ctrl.GetValue())
            except ValueError:
                rotations = rotations_default
            try:
                rotate_delay = float(dialog.rotate_delay_ctrl.GetValue())
            except ValueError:
                rotate_delay = rotate_delay_default
            try:
                flips = int(dialog.flips_ctrl.GetValue())
            except ValueError:
                flips = flips_default
            try:
                flip_delay = float(dialog.flip_delay_ctrl.GetValue())
            except ValueError:
                flip_delay = flip_delay_default
            choice = dialog.action_choice.GetStringSelection()

            # Re-focus the viewer after dialog closes
            viewer.Raise()
            time.sleep(0.5)
            # Re-move mouse to center to ensure focus for key events
            subprocess.run(['flatpak-spawn', '--host', 'xdotool', 'mousemove', str(center_x), str(center_y)])
            time.sleep(0.5)

            # Define the thread functions with captured values
            def flip_thread():
                for _ in range(flips):
                    subprocess.run(['flatpak-spawn', '--host', 'xdotool', 'key', flip_hotkey])
                    time.sleep(flip_delay)

            def rotate_thread():
                for _ in range(rotations):
                    subprocess.run(['flatpak-spawn', '--host', 'xdotool', 'key', rotate_hotkey])
                    time.sleep(rotate_delay)

            if choice == "Rotate the board":
                threading.Thread(target=rotate_thread, daemon=True).start()
            elif choice == "Flip the board":
                threading.Thread(target=flip_thread, daemon=True).start()
        dialog.Destroy()
