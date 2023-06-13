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
import gpu
import os

class GLRendererInfo(bpy.types.Panel):
    """Display GL Renderer info"""
    bl_label = "GL Renderer"
    bl_idname = "OBJECT_PT_glRenderer"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    backend = gpu.platform.backend_type_get()
    renderer = gpu.platform.renderer_get()
    vendor = gpu.platform.vendor_get()
    version = gpu.platform.vendor_get()
    
    workaround_path = '/sys/class/drm/card0/engine/rcs0/preempt_timeout_ms'
    last_time_check = None

    def get_timeout_ms(self):
        try:
            with open(self.workaround_path) as file:
                self.last_time_check = int(file.read())
        except:
            pass

    def draw(self, context):
        layout = self.layout

        if self.backend == 'OPENGL' and 'Mesa Intel(R) UHD Graphics 620' in self.renderer:
            box = layout.box()
            if self.last_time_check is None:
                self.get_timeout_ms()
            if self.last_time_check <= 640:
                box.label(text=f'preempt_timeout_ms seems too low! ({self.last_time_check}ms)', icon='ERROR')
            if 'INTEL_DEBUG' not in os.environ or 'reemit' not in os.environ['INTEL_DEBUG']:
                box.label(text=f'INTEL_DEBUG=reemit is not enabled!', icon='ERROR')


        row = layout.row(align=True)
        row.label(text="Renderer: " + self.renderer)
        row = layout.row()
        row.label(text="Vendor: " + self.vendor)
        row = layout.row()
        row.label(text="Version: " + self.version)
        row = layout.row()
        row.label(text="Backend: " + self.backend)
        row = layout.row()

def register():
    bpy.utils.register_class(GLRendererInfo)


def unregister():
    bpy.utils.unregister_class(GLRendererInfo)


if __name__ == "__main__":
    register()
