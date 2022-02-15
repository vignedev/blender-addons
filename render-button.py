bl_info = {
    'name': 'Automatic Render Button',
    'author': 'vignedev',
    'version': (0, 0, 1),
    'blender': (3, 1, 0),
    'description': 'A render button that automates saving them into a automatically generated path.',
    'category': 'Render',
    'location': 'in the output panel ya muppet',
    'warning': 'Look, I\'m going to honest with you. I am writing this at 8 AM while feeling depressed and drinking black coffee, you ought to see how the source code works and ensure it will work yourself.'
}

import bpy
import datetime

class RenderButtonOperator(bpy.types.Operator):
    """Basically a bpy.ops.render.render proxy"""
    bl_idname = 'render.render_autoname'
    bl_label = 'Render with given settings.'
    
    new_path: bpy.props.StringProperty(name='Render output to be set before render', default='')
    animation: bpy.props.BoolProperty(name='Render as animation', default=False)
    
    def execute(self, context):
        bpy.context.scene.render.filepath = self.new_path
        bpy.context.scene.render.use_file_extension = True
        return bpy.ops.render.render(animation=self.animation, use_viewport=True, write_still=True)

class RenderButtonSettings(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(name="Directory",
                                   description="Directory where files shall be stored.",
                                   default="//",
                                   subtype="DIR_PATH")
    format: bpy.props.StringProperty(name="Format",
                                     default="%y%m%d_%H%M%S/######")
                                     
    def generate_name(self) -> str:
        return self.path + '/' + datetime.datetime.now().strftime(self.format)

class RenderButtonPanel(bpy.types.Panel):
    bl_label = 'Automatic Render Destination'
    bl_idname = 'SCENE_PT_layout'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'output'

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        new_path = scene.render_button_settings.generate_name()

        layout.prop(scene.render_button_settings, 'path')
        layout.prop(scene.render_button_settings, 'format')
        
        split = layout.split()
        split.scale_y = 2.0
        col = split.column()
        render_still_btn = col.operator('render.render_autoname', text='Render Still', icon='RENDER_STILL')
        render_still_btn.new_path = new_path
        render_still_btn.animation = False
        col = split.column()
        render_anim_btn = col.operator('render.render_autoname', text='Render Animation', icon='RENDER_ANIMATION')
        render_anim_btn.new_path = new_path
        render_anim_btn.animation = True
        
        layout.label(text='Preview: "' + new_path + '"', icon='QUESTION')


def register():
    bpy.utils.register_class(RenderButtonOperator)
    bpy.utils.register_class(RenderButtonSettings)
    bpy.utils.register_class(RenderButtonPanel)
    bpy.types.Scene.render_button_settings = bpy.props.PointerProperty(type=RenderButtonSettings)


def unregister():
    bpy.utils.unregister_class(RenderButtonPanel)
    bpy.utils.unregister_class(RenderButtonSettings)
    bpy.utils.unregister_class(RenderButtonOperator)
    del bpy.types.Scene.render_button_settings


if __name__ == "__main__":
    register()
