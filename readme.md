# Blender Addons

Blender addons that I've written that are somewhat useful (for me).

---

## `blender-gl.py`

This addons adds a section into the Render settings which just displays the current OpenGL renderer information.

The sole reason why this addon exists is because of [a bug](https://developer.blender.org/T80458), that causes a full GPU hang on Linux on Intel UHD620. One of the workarounds I found is to switch the driver from `iris` to `i965` and to ensure that the correct driver is set, I check if the driver Blender uses is `DRI`.

---

## `bind-to-armature.py`

Automates the process of rigging clothes to a mesh as described [here](https://blender.stackexchange.com/questions/67625/how-to-rig-clothes). Alongside that, it also cleans the weights as wel.

**Usage**: Select the meshes you want to bind and *set the source mesh as the active selection*.