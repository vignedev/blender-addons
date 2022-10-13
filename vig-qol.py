bl_info = {
    "name": "vignedev's quality of life",
    "author": "vignedev",
    "version": (1, 0),
    "blender": (3, 4, 0),
    "location": "Random",
    "description": "Adds a few operators to ease life, since it is painful either way.",
    "warning": "",
    "doc_url": "",
    "category": "Generic",
}

import webbrowser
import bpy
from functools import reduce

# 
#  Quickly creates a bridge between two edge loops
#  and deletes its faces
# 
class QuickSew(bpy.types.Operator):
    """Create a bridge between two selected edge loops and delets faces"""
    bl_idname = "mesh.quicksew"
    bl_label = 'Quick Sew'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.mesh.bridge_edge_loops()
        bpy.ops.mesh.delete(type='ONLY_FACE')
        return {'FINISHED'}

#
#  Quickly switch between Pose and Rest position mode
#  - works when active object is mesh (and has armature) or a armature
#
class SwitchPosePositionOperator(bpy.types.Operator):
    """Switches between pose and rest mode."""
    bl_idname = "pose.toggle_pose_position"
    bl_label = "Switch Pose Position"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        curr_object = context.active_object
        if curr_object == None: return False
        if curr_object.type == 'ARMATURE': return True
        if curr_object.type == 'MESH': return curr_object.find_armature() != None
        return False

    def execute(self, context):
        active_object = context.active_object
        if active_object.type == 'MESH': armature = active_object.find_armature()
        elif active_object.type == 'ARMATURE': armature = active_object
        else: return {'CANCELLED'}

        armature.data.pose_position = 'REST' if armature.data.pose_position == 'POSE' else 'POSE'
        return {'FINISHED'}

#
#  Adds a panel to quickly toggle saved bone layers
#
class BoneLayerSwitcherUpdateOperator(bpy.types.Operator):
    bl_idname = 'bonelayerswitcher.update'
    bl_label = 'Bone Layout Update'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    
    action: bpy.props.EnumProperty(name='Action', items=[
        ('ADD', 'Add', '') ,
        ('REMOVE', 'Remove', ''),
        ('UNPACK', 'Unpack', '')
    ], options={'HIDDEN'} )
    key: bpy.props.StringProperty(name='Key', default='wah')

    def execute(self, context):
        armature = context.active_object.data

        if 'saved_bonelayers' not in armature:
            armature['saved_bonelayers'] = {}

        if self.action == 'ADD':
            armature['saved_bonelayers'][self.key] = armature.layers[:]
        elif self.action == 'REMOVE':
            armature['saved_bonelayers'].pop(self.key, None)
        elif self.action == 'UNPACK':
            armature.layers[31] = True # workaround, set the last one to true, but it will be overwritten anyways
            for i in range(0, 32):
                armature.layers[i] = armature['saved_bonelayers'][self.key][i]
        return {'FINISHED'}
    
    def invoke(self, context, event):
        if self.action == 'ADD':
            wm = context.window_manager
            return wm.invoke_props_dialog(self)
        else:
            return self.execute(context)

class BoneLayerSwitcherPanel(bpy.types.Panel):
    """Save and restore armature's bone layers"""
    bl_idname = 'POSE_PT_boneLayerSwitcher'
    bl_label = 'Bone Layer Switcher'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'

    @classmethod
    def poll(self, context):
        obj = context.active_object
        if obj == None: return False
        return obj.type == 'ARMATURE'

    def draw(self, context):
        armature = context.active_object.data

        layout = self.layout
        # layout.operator(operator='script.reload', text='Reload Script', icon='FILE_REFRESH')
        
        layout.prop(armature, 'pose_position', expand=True)
        row = layout.row()
        add_button = row.operator(operator='bonelayerswitcher.update', text='Save current layers', icon='ADD')
        add_button.action = 'ADD'

        box = layout.box()
        if 'saved_bonelayers' in armature:
            for key in armature['saved_bonelayers']:
                row = box.row()
                btn = row.operator(operator='bonelayerswitcher.update', text=key)
                btn.action = 'UNPACK'
                btn.key = key
                del_button = row.operator(operator='bonelayerswitcher.update', icon='REMOVE', text='')
                del_button.key = key
                del_button.action = 'REMOVE'

        # layout.label(text='wah')

#
#  View Settings state saver
#
class ViewSettingsSwitcherUpdateOperator(bpy.types.Operator):
    bl_idname = 'viewsettingsswitcher.update'
    bl_label = 'View Settings Update'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    action: bpy.props.EnumProperty(name='Action', items=[
        ('ADD', 'Add', '') ,
        ('REMOVE', 'Remove', ''),
        ('UNPACK', 'Unpack', '')
    ], options={'HIDDEN'} )
    key: bpy.props.StringProperty(name='Key', default='wah')

    def execute(self, context):
        scene = context.scene
        view_settings = scene.view_settings
        display_settings = scene.display_settings        

        if 'saved_viewsettings' not in scene:
            scene['saved_viewsettings'] = {}

        if self.action == 'ADD':
            scene['saved_viewsettings'][self.key] = {
                'display_device': display_settings.display_device,
                'view_transform': view_settings.view_transform, 
                'look': view_settings.look, 
                'exposure': view_settings.exposure, 
                'gamma': view_settings.gamma, 
                'use_curve_mapping': view_settings.use_curve_mapping,
                'curve_mapping': [
                    [
                        { 'x': point.location.x, 'y': point.location.y, 'handle_type': point.handle_type } for point in curve.points
                    ] for curve in view_settings.curve_mapping.curves
                ],
                'black_level': view_settings.curve_mapping.black_level,
                'white_level': view_settings.curve_mapping.white_level
            }
        elif self.action == 'REMOVE':
            scene['saved_viewsettings'].pop(self.key, None)
        elif self.action == 'UNPACK':
            requested = scene['saved_viewsettings'][self.key]

            display_settings.display_device = requested['display_device']
            view_settings.view_transform = requested['view_transform']
            view_settings.look = requested['look']
            view_settings.exposure = requested['exposure']
            view_settings.gamma = requested['gamma']
            view_settings.use_curve_mapping = requested['use_curve_mapping']

            view_settings.curve_mapping.black_level = requested['black_level']
            view_settings.curve_mapping.white_level = requested['white_level']

            for c in range(0, 4):
                channel = view_settings.curve_mapping.curves[c]
                requested_channel = requested['curve_mapping'][c]

                # remove all points in that given channel
                while len(channel.points) != 2:
                    channel.points.remove(channel.points[0])
                # at this point, only two points are in the channel (enforced)
                
                # move them back to space, if out of predefined range, create new ones
                for p in range(0, len(requested_channel)):
                    print(p)
                    if(p <= 1): channel.points[p].location = (requested_channel[p]['x'], requested_channel[p]['y'])
                    else: channel.points.new(requested_channel[p]['x'], requested_channel[p]['y'])
                    channel.points[p].handle_type = requested_channel[p]['handle_type']

                # request an update
                view_settings.curve_mapping.update()

        return {'FINISHED'}
    
    def invoke(self, context, event):
        if self.action == 'ADD':
            wm = context.window_manager
            return wm.invoke_props_dialog(self)
        else:
            return self.execute(context)

class ViewSettingsSwitcherPanel(bpy.types.Panel):
    bl_idname = 'RENDER_PT_viewsettingspanel'
    bl_label = 'View Settings Switcher'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

    @classmethod
    def poll(self, context):
        return True

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        # layout.operator(operator='script.reload', text='Reload Script', icon='FILE_REFRESH')

        row = layout.row()
        add_button = row.operator(operator='viewsettingsswitcher.update', text='Save current settings', icon='ADD')
        add_button.action = 'ADD'

        box = layout.box()
        if 'saved_viewsettings' in scene:
            for key in scene['saved_viewsettings']:
                row = box.row()
                btn = row.operator(operator='viewsettingsswitcher.update', text=key)
                btn.action = 'UNPACK'
                btn.key = key
                del_button = row.operator(operator='viewsettingsswitcher.update', icon='REMOVE', text='')
                del_button.key = key
                del_button.action = 'REMOVE'

        # layout.label(text='wah')


#
#
#  Open the local project's folder
#
class OpenProjectFolder(bpy.types.Operator):
    bl_idname = 'os.openprojectfolder'
    bl_label = 'Open project\'s folder'

    @classmethod
    def poll(self, context):
        return bpy.path.abspath('//') != ''

    def execute(self, context):
        webbrowser.open(bpy.path.abspath('//'))
        return { 'FINISHED' }

# Registration
classes = (
    SwitchPosePositionOperator,
    BoneLayerSwitcherUpdateOperator,
    BoneLayerSwitcherPanel,
    QuickSew,
    ViewSettingsSwitcherUpdateOperator,
    ViewSettingsSwitcherPanel,
    OpenProjectFolder,
)
def register():
    for c in classes: bpy.utils.register_class(c)
def unregister():
    for c in classes: bpy.utils.unregister_class(c)
if __name__ == "__main__":
    register()