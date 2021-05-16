bl_info = {
    "name": "GL Renderer Info",
    "author": "vignedev",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Render Settings",
    "description": "Displays current OpenGL renderer information",
    "warning": "",
    "doc_url": "",
    "category": "Render",
}

import bpy
import bgl

class GLRendererInfo(bpy.types.Panel):
    """Display GL Renderer info"""
    bl_label = "GL Renderer"
    bl_idname = "OBJECT_PT_glRenderer"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    renderer = bgl.glGetString(bgl.GL_RENDERER)
    vendor = bgl.glGetString(bgl.GL_VENDOR)
    version = bgl.glGetString(bgl.GL_VERSION)
    
    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.label(text="Renderer: " + self.renderer)
        row = layout.row()
        row.label(text="Vendor: " + self.vendor)
        row = layout.row()
        row.label(text="Version: " + self.version)
        row = layout.row()

def register():
    bpy.utils.register_class(GLRendererInfo)


def unregister():
    bpy.utils.unregister_class(GLRendererInfo)


if __name__ == "__main__":
    register()
