bl_info = {
    "name": "Apply modifiers and perserve shapekeys",
    "author": "vignedev",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Object Mode",
    "description": "Applies all modifiers while perserving shape keys",
    "warning": "",
    "doc_url": "",
    "category": "Rigging",
}

import bpy

def main(context):
    if(context.active_object == None):
        raise Exception('No active_object')

    source = context.active_object
    shapekey_max = len(source.data.shape_keys.key_blocks)
    clones = []
    
    # create a target
    for x in range(1, shapekey_max):
        source.data.shape_keys.key_blocks[x].value = 0.0;
    bpy.ops.object.convert(target='MESH', keep_original=True)
    target = context.active_object
    target.name = source.name + "_target"
    target.select_set(False)

    # create a duplicate for each shapekey
    for i in range(1, shapekey_max):
        context.view_layer.objects.active = source
        source.select_set(True);
        
        for j in range(1, shapekey_max):
            if j == i:
                source.data.shape_keys.key_blocks[j].value = 1.0;
            else:
                source.data.shape_keys.key_blocks[j].value = 0.0;
        bpy.ops.object.convert(target='MESH', keep_original=True) 
        
        duplicate = context.active_object
        duplicate.select_set(False)
        duplicate.name = duplicate.name + "_" + source.data.shape_keys.key_blocks[i].name
        clones.append(duplicate)
    
    # select all clones and the source as last
    bpy.ops.object.select_all(action='DESELECT')
    for clone in clones:
        clone.select_set(True);
    context.view_layer.objects.active = target
    target.select_set(True);

    # merge them all
    bpy.ops.object.join_shapes()
    
    # remove residue
    bpy.ops.object.select_all(action='DESELECT')
    for clone in clones:
        clone.select_set(True);
    bpy.ops.object.delete()
    
    # hide original mesh
    source.hide_viewport = True
    source.hide_render = True
    
    # if source has armature, then add armature to the target as well
    armature = source.find_armature()
    if armature != None:
        modifier = target.modifiers.new(name='ArmaturePerserved', type='ARMATURE')
        modifier.object = armature
        modifier.use_vertex_groups = True
        modifier.use_bone_envelopes = False

class ApplyModifierShapeKeyPerservationOperator(bpy.types.Operator):
    """Applies all modifiers while perserving shape keys."""
    bl_idname = "object.apply_modifiers_perserve_shapekeys"
    bl_label = "Apply modifiers, perserve shapekeys"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(context)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(ApplyModifierShapeKeyPerservationOperator)


def unregister():
    bpy.utils.unregister_class(ApplyModifierShapeKeyPerservationOperator)


if __name__ == "__main__":
    register()