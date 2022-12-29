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
    """Basically a bpy.ops.render.render proxy in a way"""
    bl_idname = 'render.render_autoname'
    bl_label = 'Render with given settings.'
    bl_options = { 'INTERNAL' }
    
    animation: bpy.props.BoolProperty(name='Render as animation', default=False)
    
    def execute(self, context):
        settings: RenderButtonSettings = context.scene.render_button_settings

        context.scene.render.filepath = settings.generate_name()
        context.scene.render.use_file_extension = True

        if not settings.use_scene_frame_range:
            context.scene.frame_start = settings.frame_start
            context.scene.frame_end = settings.frame_end

        if settings.pre_script:
            exec(settings.pre_script.as_string(), {})

        return bpy.ops.render.render('INVOKE_DEFAULT', animation=self.animation, use_viewport=True, write_still=True)


class RenderButtonSettings(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(name="Directory",
                                   description="Directory where files shall be stored.",
                                   default="//",
                                   subtype="DIR_PATH")
    format: bpy.props.StringProperty(name="Format",
                                     default="%y%m%d_%H%M%S/######")
    pre_script: bpy.props.PointerProperty(type=bpy.types.Text,
                                          name='Pre-render script',
                                          description='Script that\'d be called in a thread-safe manner before the render. (Note that this doesn\'t handle depsgraph or driver updates)')
    use_scene_frame_range: bpy.props.BoolProperty(name='Use scene\'s frame range', default=True)
    frame_start: bpy.props.IntProperty(name='Start frame', default=1)
    frame_end: bpy.props.IntProperty(name='End frame', default=1)
  
    def generate_name(self) -> str:
        return self.path + '/' + datetime.datetime.now().strftime(self.format)

class RenderButtonPanel(bpy.types.Panel):
    bl_label = 'Automatic Render Destination'
    bl_idname = 'SCENE_PT_renderbutton_layout'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'output'

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        new_path = scene.render_button_settings.generate_name()
        pre_script = scene.render_button_settings.pre_script
        pre_script_text = pre_script.as_string() if pre_script else ''
        use_scene_frame_range = scene.render_button_settings.use_scene_frame_range
        frame_start = scene.render_button_settings.frame_start
        frame_end = scene.render_button_settings.frame_end

        layout.prop(scene.render_button_settings, 'path')
        layout.prop(scene.render_button_settings, 'format')
        layout.prop(scene.render_button_settings, 'pre_script')
        layout.prop(scene.render_button_settings, 'use_scene_frame_range')

        if(not scene.render_button_settings.use_scene_frame_range):
            box = layout.box()
            split = box.split()
            split.prop(scene.render_button_settings, 'frame_start')
            split.prop(scene.render_button_settings, 'frame_end')
        
        split = layout.split()
        split.scale_y = 2.0

        col = split.column()
        render_still_btn = col.operator('render.render_autoname', text='Render Still', icon='RENDER_STILL')
        render_still_btn.animation = False

        col = split.column()
        render_anim_btn = col.operator('render.render_autoname', text='Render Animation', icon='RENDER_ANIMATION')
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
