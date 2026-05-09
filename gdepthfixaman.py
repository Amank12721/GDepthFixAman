bl_info = {
    "name": "GDepthFixAman",
    "author": "Aman",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Tool",
    "description": "Fix object depth offset relative to camera with auto-scaling",
    "category": "3D View",
}

import bpy
from mathutils import Vector

def update_depth(self, context):
    obj = context.active_object
    cam = context.scene.camera

    if not obj or not cam:
        return

    # Store original values once
    if "orig_loc" not in obj:
        obj["orig_loc"] = obj.location.copy()
        obj["orig_scale"] = obj.scale.copy()

    orig_loc = Vector(obj["orig_loc"])
    orig_scale = Vector(obj["orig_scale"])

    # 🔥 CORRECT DIRECTION (object -> camera)
    direction = (cam.location - orig_loc).normalized()

    # Distance calculations
    old_dist = (orig_loc - cam.location).length
    new_loc = orig_loc + direction * self.depth_offset
    new_dist = (new_loc - cam.location).length

    # Apply location
    obj.location = new_loc

    # Auto scale correction
    if old_dist != 0:
        factor = new_dist / old_dist
        obj.scale = orig_scale * factor


class OBJECT_OT_reset_origin(bpy.types.Operator):
    bl_idname = "object.reset_depth_origin"
    bl_label = "Set Current as Origin"
    bl_description = "Set current position as new origin point"
    
    def execute(self, context):
        obj = context.active_object
        if obj:
            # Update original position to current position
            obj["orig_loc"] = obj.location.copy()
            obj["orig_scale"] = obj.scale.copy()
            # Reset offset to 0
            context.scene.gdepthfixaman.depth_offset = 0.0
            self.report({'INFO'}, "Origin updated to current position")
        return {'FINISHED'}


class GDepthFixAmanProps(bpy.types.PropertyGroup):
    depth_offset: bpy.props.FloatProperty(
        name="Depth Offset",
        default=0.0,
        min=-5.0,
        max=5.0,
        update=update_depth
    )


class VIEW3D_PT_gdepthfixaman(bpy.types.Panel):
    bl_label = "Depth Fix"
    bl_idname = "VIEW3D_PT_gdepthfixaman"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        if obj:
            layout.prop(context.scene.gdepthfixaman, "depth_offset")
            layout.separator()
            layout.operator("object.reset_depth_origin", icon='PIVOT_CURSOR')
        else:
            layout.label(text="Select an object")


classes = [GDepthFixAmanProps, OBJECT_OT_reset_origin, VIEW3D_PT_gdepthfixaman]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.gdepthfixaman = bpy.props.PointerProperty(type=GDepthFixAmanProps)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.gdepthfixaman


if __name__ == "__main__":
    register()