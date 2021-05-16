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

def main(context):
    active_object = context.active_object
    objects = context.selected_objects

    armature = active_object.find_armature()
    if armature == None:
        raise Exception('No armature found on active_object')

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
        mod_transfer.vert_mapping = 'NEAREST'
        mod_transfer.object = active_object

        bpy.context.view_layer.objects.active = cur_object
        while cur_object.modifiers[0].name != 'tmp_bind-to-armature':
            bpy.ops.object.modifier_move_up(modifier='tmp_bind-to-armature')
        bpy.ops.object.modifier_apply(modifier='tmp_bind-to-armature')
        bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0, keep_single=False)



class BindToArmatureOperator(bpy.types.Operator):
    """Bind a mesh to an already rigged mesh using Data Transfer method."""
    bl_idname = "object.bind_to_armature"
    bl_label = "Bind to Armature"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(context)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(BindToArmatureOperator)


def unregister():
    bpy.utils.unregister_class(BindToArmatureOperator)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.object.simple_operator()
