# rigging_tools.py (Version 2.0)

bl_info = {
    "name": "My Custom Rigging Tools",
    "author": "Talfi",
    "version": (1, 6, 0),
    "blender": (4, 4, 0),
    "location": "View3D > UI > Rig UI, and available for import",
    "description": "A personal library of reusable rigging utility functions and operators.",
    "category": "Development",
}

import bpy
from mathutils import Matrix, Vector
from mathutils.geometry import intersect_point_line

#============================================================
#  UTILITY FUNCTIONS (The "Engine")
#============================================================

def copy_bone_transform(source_bone, target_bone):
    source_rest_matrix = source_bone.bone.matrix_local
    target_rest_matrix = target_bone.bone.matrix_local
    offset_matrix = source_rest_matrix.inverted() @ target_rest_matrix
    target_bone.matrix = source_bone.matrix @ offset_matrix

def copy_bone_chain(source_names, target_names, armature_obj):
    pose_bones = armature_obj.pose.bones
    for s_name, t_name in zip(source_names, target_names):
        if s_name in pose_bones and t_name in pose_bones:
            copy_bone_transform(pose_bones[s_name], pose_bones[t_name])
            bpy.context.view_layer.update()

def snap_pole_vector(pole_bone_name, root_bone_name, pivot_bone_name, end_bone_name, armature_obj):
    pose_bones = armature_obj.pose.bones
    if not all(name in pose_bones for name in [pole_bone_name, root_bone_name, pivot_bone_name, end_bone_name]):
        return
    root_loc, pivot_loc, end_loc = pose_bones[root_bone_name].head, pose_bones[pivot_bone_name].head, pose_bones[end_bone_name].head
    line_point, _ = intersect_point_line(pivot_loc, root_loc, end_loc)
    pole_vector = pivot_loc - line_point
    pole_distance = (pivot_loc - root_loc).length
    pole_bone_obj = pose_bones[pole_bone_name]
    pole_bone_obj.matrix.translation = pivot_loc + (pole_vector.normalized() * pole_distance)
    bpy.context.view_layer.update()

def are_matrices_fuzzy_equal(mat1, mat2, tolerance=0.0001):
    for i in range(4):
        for j in range(4):
            if abs(mat1[i][j] - mat2[i][j]) > tolerance:
                return False
    return True

#============================================================
#  GENERIC OPERATOR CLASSES (The "Tools")
#============================================================

class RIG_OT_snap_bone_chain(bpy.types.Operator):
    bl_idname = "rig.snap_bone_chain"
    bl_label = "Snap Bone Chain"
    bl_options = {'REGISTER', 'UNDO'}

    source_bones: bpy.props.StringProperty()
    target_bones: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        armature = context.active_object
        source_names = [name.strip() for name in self.source_bones.split(',')]
        target_names = [name.strip() for name in self.target_bones.split(',')]
        copy_bone_chain(source_names, target_names, armature)
        return {'FINISHED'}
    
class RIG_OT_snap_to_ik_with_pole(bpy.types.Operator):
    bl_idname = "rig.snap_to_ik_with_pole"
    bl_label = "Snap to IK (with Pole)"
    bl_options = {'REGISTER', 'UNDO'}

    ik_control_bone: bpy.props.StringProperty()
    pole_control_bone: bpy.props.StringProperty()
    source_end_bone: bpy.props.StringProperty()
    source_chain_root: bpy.props.StringProperty()
    source_chain_pivot: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        armature = context.active_object
        snap_pole_vector(self.pole_control_bone, self.source_chain_root, self.source_chain_pivot, self.source_end_bone, armature)
        copy_bone_transform(armature.pose.bones[self.source_end_bone], armature.pose.bones[self.ik_control_bone])
        return {'FINISHED'}    

class DEBUG_OT_dissect_bone_matrix(bpy.types.Operator):
    """Prints the full transform hierarchy for the active bone."""
    bl_idname = "debug.dissect_bone_matrix"
    bl_label = "Dissect Active Bone Matrix"

    @classmethod
    def poll(cls, context):
        """Ensure the operator can only be run when a bone is selected in Pose Mode."""
        return context.active_pose_bone is not None

    def execute(self, context):
        pbone = context.active_pose_bone
        armature_obj = context.active_object
        
        # --- Start printing to the System Console ---
        print("\n" + "=" * 60)
        print(f"Full Transform Breakdown for Bone: '{pbone.name}'")
        print(f"In Armature: '{armature_obj.name}'")
        print("=" * 60)

        # 1. The Bone's LOCAL Transform (what you see in the UI)
        # This is the transform relative to its parent's final pose.
        print("--- 1. BONE's Local Transform (from UI) ---")
        print(f"Location: {pbone.location}")
        print(f"Rotation: {pbone.rotation_quaternion}")
        print(f"Scale:    {pbone.scale}")
        
        # 2. The ARMATURE OBJECT's Transform (The "Tilted Desk")
        # This is the transform of the entire Armature object in the world.
        print("\n--- 2. ARMATURE OBJECT's World Transform ---")
        print(f"Location: {armature_obj.location}")
        print(f"Rotation: {armature_obj.rotation_quaternion}")
        print(f"Scale:    {armature_obj.scale}")

        # 3. The Bone's FINAL World-Space Matrix (The end result)
        # This is the bone's absolute transform in the world.
        print("\n--- 3. BONE's Final World Matrix ---")
        world_matrix = pbone.matrix
        matrix_location = world_matrix.to_translation()
        matrix_rotation = world_matrix.to_quaternion()
        matrix_scale = world_matrix.to_scale()
        print(f"Location: {matrix_location}")
        print(f"Rotation: {matrix_rotation}")
        print(f"Scale:    {matrix_scale}")
        
        print("=" * 60)

        # This provides a small confirmation message in the Blender status bar.
        self.report({'INFO'}, f"Dissected matrix for '{pbone.name}'. Check System Console.")
        
        return {'FINISHED'}


#============================================================
#  STATE MANAGEMENT CLASSES 
#============================================================

class RigUIStateItem(bpy.types.PropertyGroup):
    is_expanded: bpy.props.BoolProperty(name="Is Expanded", default=True)

class RigUIStateManager(bpy.types.PropertyGroup):
    box_states: bpy.props.CollectionProperty(type=RigUIStateItem)

    def get_box_state(self, box_id, default=True):
        if box_id not in self.box_states:
            item = self.box_states.add()
            item.name = box_id
            item.is_expanded = default
        return self.box_states[box_id].is_expanded

    def set_box_state(self, box_id, value):
        if box_id not in self.box_states:
            item = self.box_states.add()
            item.name = box_id
        self.box_states[box_id].is_expanded = value

class WM_OT_RigUIToggleBox(bpy.types.Operator):
    """A simple operator to toggle the expanded state of a box."""
    bl_idname = "wm.rig_ui_toggle_box"
    bl_label = "Toggle UI Box"
    bl_options = {'REGISTER', 'UNDO'}

    box_id: bpy.props.StringProperty()

    def execute(self, context):
        # This is where you can add your debug print statement!
        print(f"Toggling box with ID: {self.box_id}") 
        
        state_manager = context.window_manager.rig_ui_state
        current_state = state_manager.get_box_state(self.box_id)
        state_manager.set_box_state(self.box_id, not current_state)
        
        # This forces the UI to redraw immediately after the state changes.
        # It's important for responsiveness.
        for region in context.area.regions:
            if region.type == 'UI':
                region.tag_redraw()
                
        return {'FINISHED'}

#============================================================
#  REUSABLE UI DRAWING FUNCTION (The "UI Component")
#============================================================
def draw_collapsible_box(layout, context, box_id, text, icon='NONE', default_expanded=True):
    state_manager = context.window_manager.rig_ui_state
    is_expanded = state_manager.get_box_state(box_id, default=default_expanded)

    box = layout.box()
    row = box.row()
    row.alignment = 'LEFT'
    
    # --- THE FINAL FIX ---
    # We use an operator, which allows us to pass the unique box_id.
    # We make it look like a property toggle by using text="" and emboss=False.
    op = row.operator("wm.rig_ui_toggle_box", 
                      icon="TRIA_DOWN" if is_expanded else "TRIA_RIGHT",
                      text="", emboss=False) # emboss=False makes it flat like a prop
    op.box_id = box_id # Pass the unique ID to the operator instance
    
    row.label(text=text, icon=icon)

    if is_expanded:
        return box.column()
    return None

def draw_collection_button(layout, collection_name, text=None, show_solo_button=False):
    """
    Draws a visibility toggle for a bone collection, with an optional built-in solo button.

    :param layout: The layout object to draw on (e.g., a row or column).
    :param collection_name: The string name of the bone collection.
    :param text: Optional custom text for the button. If None, it's auto-generated.
    :param show_solo_button: If True, a solo toggle star will be drawn.
    """
    rig = bpy.context.active_object
    if not (rig and rig.type == 'ARMATURE'):
        return

    collections = rig.data.collections
    
    if collection_name not in collections:
        layout.label(text=f"'{collection_name}'?", icon='ERROR')
        return

    if text is None:
        text = collection_name.replace("_", " ").title()

    collection = collections[collection_name]

    # --- New, Simplified Drawing Logic ---
    if show_solo_button:
        # Create a row to hold both the visibility and solo toggles
        row = layout.row(align=True)
        # The main visibility toggle. 'toggle=True' makes it a checkbox.
        row.prop(collection, 'is_visible', text=text, toggle=True)
        # The built-in solo toggle. This is the star icon.
        # It has no text and is just the icon. 'toggle=True' is implied.
        row.prop(collection, 'is_solo', text="", icon='VIS_SEL_11')
    else:
        # If no solo button is needed, just draw the simple visibility toggle
        layout.prop(collection, 'is_visible', text=text, toggle=True)



#============================================================
#  REGISTRATION
#============================================================

# Add all the classes that need to be registered to this list
classes = (
    RIG_OT_snap_bone_chain,
    RIG_OT_snap_to_ik_with_pole,
    DEBUG_OT_dissect_bone_matrix,
    RigUIStateItem,
    RigUIStateManager,
    WM_OT_RigUIToggleBox,
)

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    # Add a POINTER to our State Manager class on Blender's Window Manager.
    # This creates a single, global instance of our state manager.
    bpy.types.WindowManager.rig_ui_state = bpy.props.PointerProperty(type=RigUIStateManager)        



    addon_name = bl_info.get("name", "Unknown Addon")
    version_tuple = bl_info.get("version", (0, 0, 0))
    version_string = ".".join(map(str, version_tuple))

    print(f"{addon_name} (v{version_string}) loaded successfully.")

def unregister():

    del bpy.types.WindowManager.rig_ui_state
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    addon_name = bl_info.get("name", "Unknown Addon")
    print(f"{addon_name} unloaded.")

if __name__ == "__main__":
    register()
