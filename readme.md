# Blender Addons

Blender addons that I've written that are somewhat useful (for me).

---

## `vig-qol.py`

Basically, I got lazy with separating things into different files/addons, so this is my general QOL package, which includes:

<details>
    <summary><b>Quick Sew</b></summary>
    Shorthand version for "bridge two edge loops and delete only faces".    
</details>

<details>
    <summary><b>Toggle Pose Position operator</b></summary>
    Allows to quicky toggle between pose/rest position modes for armatures. Works on active armatures or meshes that belong to an armature.
</details>

<details>
    <summary><b>Bone Layer Switcher</b></summary>
    Allows to quicky switch between multiple group of bone layers.
    
https://user-images.githubusercontent.com/18449733/187050267-954c92c0-9302-4a93-a048-90b43fda7538.mp4
</details>

<details>
    <summary><b>View Settings Switcher</b></summary>
    Allows to quicky switch between view settings of the scene. This includes the entirety of the "Color Management" panel in the Render properties (with the exception of Sequencer setting).
    
https://user-images.githubusercontent.com/18449733/187050269-1d5c82dd-799d-4dec-92bc-86fbe1d3a6a2.mp4
</details>

<details>
    <summary><b>Open Project's directory</b></summary>
    Opens the directory where the project is located in the file explorer.
</details>

<details>
    <summary><b>Add Selected PoseBones To KeyingSet</b></summary>
    Adds the selected pose bones into the currently active keying set. Only adds the position, scale and rotation based on the rotation mode being chosen.
</details>

<details>
    <summary><b>Rename Bone Chain</b></summary>
    Renames selected bones as a numbered chain, beginning with the *active selection* as the starting bone.
    
https://user-images.githubusercontent.com/18449733/226142881-ca2747c6-11cc-4d3a-8c69-59062e900c98.mp4
</details>

<details>
    <summary><b>Quick Group into Empty</b></summary>
    Quickly creates an empty at current selection's median location and parents all selected to the newly created empty.
    
https://user-images.githubusercontent.com/18449733/226142915-5b2a0aba-7fb0-4e35-bf22-8fe76f37d75c.mp4
</details>

Please do note that UI wise they may feel cluttery, clunky and may be unoptimized, however these addons were added to just accelerate the trial-and-error process of figuring out different settings.

---

## `blender-gl.py`

This addons adds a section into the Render settings which just displays the current OpenGL renderer information.

The sole reason why this addon exists is because of [a bug](https://developer.blender.org/T80458), that causes a full GPU hang on Linux on Intel UHD620. One of the workarounds I found is to switch the driver from `iris` to `i965` and to ensure that the correct driver is set, I check if the driver Blender uses is `DRI`.

---

## `bind-to-armature.py`

Automates the process of rigging clothes to a mesh as described [here](https://blender.stackexchange.com/questions/67625/how-to-rig-clothes). Alongside that, it also cleans the weights as wel.

**Usage**: Select the meshes you want to bind and *set the source mesh as the active selection*.

***Note***: None of the objects to be binded should not have any modifiers that drastically change the shape (eg. shrinkwrap).

---

## `apply-modifiers-preserve-shapekeys.py`

Creates a clone of active object and applies all of its modifiers while perserving shape keys. If the source is linked to an armature, then the script attempts to do the same to the final mesh.

***Note***: This was only tested on modifiers that do not change vertex count or weight groups while using different shape key values.

---

## [`Rigify-To-Unity`](https://github.com/vignedev/Rigify-To-Unity)

Fork of [AlexLemminG's](https://github.com/AlexLemminG/Rigify-To-Unity) Blender script with support for already weight mapped rigs.

As it is a fork of an already existing script, it can be found [in its own repository](https://github.com/vignedev/Rigify-To-Unity).

In addition to removal of incompatible bones, it merges vertex groups of deleted deform bones of into their parent bone's vertex group.

***Note***: It performs destructive operations (deleting bones, reparenting them, modifies vertex groups), so it is advised to *use this script, export and then revert back*. 

---

## `render-button.py`

![](./assets/render_btn.png)

Adds a new panel into Output settings with two buttons for rendering stills and animations, which will render into a generated path based on the format and directory.

You can also set a script that'll be run before the render operator is called. This is useful for eg. to set certain properties from a UI-safe thread, which might result in a crash if pre-render handlers were to be used. This however does not update the depsgraph or driver, you can however trigger this behaviour manually by ending the script with:

```py
bpy.data.objects["ina_uber"]["high_quality"] = 1
bpy.data.objects["ina_uber"].update_tag()                    # https://developer.blender.org/T74000#879966
bpy.context.scene.frame_set(bpy.context.scene.frame_current) # This triggers the update of the drivers relevant to the property at this object
```

---

## `render-webhook.py`

Adds an option to execute a Discord webhook after a render job is completed.

You'll need to enable the addon, set the Webhook URL in the addon's preferences and then enable the Webhook feature in the Scene's Output panel.

---

## `change-imageprojection.py`

Quickly changes image projection type of selected nodes in the Shader Node editor.

[![Example](./assets/projection_change.gif)](./assets/projection_change.mp4)
