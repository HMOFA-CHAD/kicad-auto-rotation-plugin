# kicad-auto-rotation-plugin
Enables auto-rotation of your PCB in the 3D viewer.

### Version 1.1

## What's new!
- Added true rotation functionality, assignable with custom hotkeys
- Added a dialog box for configuring the plugin. You can now choose from rotating or flipping your PCB.

#### https://github.com/HMOFA-CHAD/kicad-auto-rotation-plugin

#### License: GNU Affero General Public License v3.0

#### Author: Ian Pritchard
#### Contact: ian.pritchard@anthrobotics.ca

This plugin automates the rotating and flipping of your PCB in the 3D viewer, creating an automated 360 degree "rotation". Useful for showing off your shiny new PCB to the world, in all its 3D glory!

### Installation

Simply install the *auto_rotate.zip* archive using the PCM. Open the PCM in KiCad, and select *Install from file*, then select the .zip archive.


### How to use: 


If you haven't already, assign a hotkey for the Y-axis rotation in the 3D viewer preferences. The auto rotation tool will prompt you for this hotkey.

In pcbnew, open up the 3D viewer first. Next, go back to pcbnew and click on the Auto Rotation Plugin icon in the pcbnew toolbar. The 3D viewer window will automatically re-focus, and a dialog will open providing you with config options.

You can change the number of rotations, flips, and delays between movements by changing the values in the dialog window. Select to either flip or rotate the board, and select OK to begin.

If you have any questions, problems, or suggestions, please submit them to the issues page on GitHub! Contributions are welcome (on the dev branch)!

### Acknowledgements:

I'd like to thank [Alex](https://x.com/averagearc) for help with the hotkeys, and [Brady](https://x.com/BradyRMayes) for the idea of building a plugin like this. I'd also like to thank Frank ([Zzoeffie](https://forum.kicad.info/t/how-to-make-a-personal-user-library-install-under-pcm/55589)) on the KiCad forum for the guide on installing custom PCM content, and [Adam](https://github.com/adamalfath) for the suggestion to add rotations as opposed to just flips. I hope others may find it useful!
