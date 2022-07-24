bl_info = {
    "name": "Change Image Projection Type",
    "author": "vignedev",
    "version": (1, 0),
    "blender": (3, 20, 0),
    "location": "Render Settings",
    "description": "Allows to quickly change Image Projection Type in the Shader Editor",
    "warning": "",
    "doc_url": "",
    "category": "Material",
}

import bpy

class ChangeImageProjectionOperator(bpy.types.Operator):
    """Change selected image textures' projection type."""
    bl_idname = "node.change_image_projection_operator"
    bl_label = "Change Image Texture Projection"
    bl_options = {'REGISTER', 'UNDO'}

    projection: bpy.props.EnumProperty(name='Projection', items=[
        ('FLAT', 'Flat', '', 1),
        ('BOX', 'Box', '', 2),
        ('SPHERE', 'Sphere', '', 3),
        ('TUBE', 'Tube', '', 3)
    ])
    blend: bpy.props.FloatProperty(name='Box Blending', min=0.0, max=1.0)

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'NODE_EDITOR' and context.space_data.shader_type == 'OBJECT'

    def execute(self, context):
        for node in bpy.context.space_data.edit_tree.nodes:
            if node.select != True or node.type != 'TEX_IMAGE':
                continue
            node.projection = str(self.projection)
            node.projection_blend = float(self.blend)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


def register():
    bpy.utils.register_class(ChangeImageProjectionOperator)

def unregister():
    bpy.utils.unregister_class(ChangeImageProjectionOperator)

if __name__ == "__main__":
    register()