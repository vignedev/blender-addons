bl_info = {
    "name": "Bind to Armature",
    "author": "vignedev",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Object Mode",
    "description": "Bind a mesh to an already rigged mesh using Data Transfer method.",
    "warning": "",
    "doc_url": "",
    "category": "Rigging",
}

import bpy

def main(context, mapping, rest_pose):
    active_object = context.active_object
    objects = context.selected_objects

    armature = active_object.find_armature()
    if armature == None:
        raise Exception('No armature found on active_object')

    org_pose_position = armature.data.pose_position
    if rest_pose:
        armature.data.pose_position = 'REST'

    context.view_layer.objects.active = armature

    for cur_object in objects:
        if cur_object == active_object:
            continue
        if cur_object.type != 'MESH':
            continue

        context.view_layer.objects.active = armature
        bpy.ops.object.parent_set(type='ARMATURE_NAME')

        mod_transfer = cur_object.modifiers.new(name='tmp_bind-to-armature', type='DATA_TRANSFER')
        mod_transfer.data_types_verts = { 'VGROUP_WEIGHTS' }
        mod_transfer.vert_mapping = mapping
        mod_transfer.object = active_object

        bpy.context.view_layer.objects.active = cur_object
        while cur_object.modifiers[0].name != 'tmp_bind-to-armature':
            bpy.ops.object.modifier_move_up(modifier='tmp_bind-to-armature')
        bpy.ops.object.modifier_apply(modifier='tmp_bind-to-armature')
        bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0, keep_single=False)

    if rest_pose:        
        armature.data.pose_position = org_pose_position
    context.view_layer.objects.active = active_object



class BindToArmatureOperator(bpy.types.Operator):
    """Bind a mesh to an already rigged mesh using Data Transfer method."""
    bl_idname = "object.bind_to_armature"
    bl_label = "Bind to Armature"
    bl_options = {'REGISTER', 'UNDO'}

    vertex_mapping: bpy.props.EnumProperty(name='Vertex Mapping', items=[
        ('TOPOLOGY', 'Topology', '', 1),
        ('NEAREST', 'Nearest Vertex', '', 2),
        ('EDGE_NEAREST', 'Nearest Edge Vertex', '', 3),
        ('EDGEINTERP_NEAREST', 'Nearest Edge Interpolated', '', 4),
        ('POLY_NEAREST', 'Nearest Face Vertex', '', 5),
        ('POLYINTERP_NEAREST', 'Nearest Face Interpolated', '', 6),
        ('POLYINTERP_VNORPROJ', 'Projected Face Interpolated', '', 7)
    ], default='NEAREST')

    rest_pose: bpy.props.BoolProperty(name='Use Rest Position', default=True)

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        main(context, str(self.vertex_mapping), bool(self.rest_pose))
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


def register():
    bpy.utils.register_class(BindToArmatureOperator)


def unregister():
    bpy.utils.unregister_class(BindToArmatureOperator)


if __name__ == "__main__":
    register()
