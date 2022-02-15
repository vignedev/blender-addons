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
import platform
import subprocess

class RenderButtonOperator(bpy.types.Operator):
    """Basically a bpy.ops.render.render proxy"""
    bl_idname = 'render.render_autoname'
    bl_label = 'Render with given settings.'
    
    terminal: bpy.props.BoolProperty(name='External', default=False)
    new_path: bpy.props.StringProperty(name='Render output to be set before render', default='')
    animation: bpy.props.BoolProperty(name='Render as animation', default=False)
    
    def execute(self, context):
        if self.terminal is False:
            bpy.context.scene.render.filepath = self.new_path
            bpy.context.scene.render.use_file_extension = True
            return bpy.ops.render.render(animation=self.animation, use_viewport=True, write_still=True)
        else:
            general_cmd = [
                *context.scene.render_button_settings.determine_terminal(),
                bpy.app.binary_path,
                '-b',
                bpy.data.filepath,
                '-o',
                self.new_path
            ]
            if self.animation:
                subprocess.Popen([*general_cmd, '-a'])
            else:
                subprocess.Popen([*general_cmd, '-f', str(bpy.context.scene.frame_current)])
            return {'FINISHED'}


class RenderButtonSettings(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(name="Directory",
                                   description="Directory where files shall be stored.",
                                   default="//",
                                   subtype="DIR_PATH")
    format: bpy.props.StringProperty(name="Format",
                                     default="%y%m%d_%H%M%S/######")
    terminal: bpy.props.BoolProperty(name='Render on separate instance',
                                     default=False,
                                     description='Run render job in Terminal')
    linux_terminal: bpy.props.StringProperty(name='Linux Terminal',
                                             default='urxvt',
                                             description='Path to a Linux terminal')

    def determine_terminal(self) -> list[str]:
        """Returns the path to the terminal emulator that is available"""
        platform_name = platform.system()
        if platform_name == 'Linux':
            return [str(self.linux_terminal), '-e']
        elif platform_name == 'Windows':
            return ['cmd.exe', '/c', 'start']
        else:
            raise Exception(f'Cannot find terminal for "{platform_name}" platform.')

  
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
        render_still_btn.terminal = scene.render_button_settings.terminal
        render_still_btn.new_path = new_path
        render_still_btn.animation = False
        col = split.column()
        render_anim_btn = col.operator('render.render_autoname', text='Render Animation', icon='RENDER_ANIMATION')
        render_anim_btn.terminal = scene.render_button_settings.terminal
        render_anim_btn.new_path = new_path
        render_anim_btn.animation = True
        
        platform_name = platform.system()
        if platform_name in ('Windows', 'Linux'):
            layout.prop(scene.render_button_settings, 'terminal')
            if scene.render_button_settings.terminal:
                box = layout.box()
                box.label(text='This will use the currently opened project and its last saved instance!', icon='ERROR')
                box.label(text='This is purely experimental.', icon='ERROR')
                if platform.system() == 'Linux':
                    box.prop(scene.render_button_settings, 'linux_terminal')

        layout.label(text='Preview: "' + new_path + '"', icon='QUESTION')
        layout.label(text='The UI will be locked and can be only cancelled using SIGINT.', icon='ERROR')


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
