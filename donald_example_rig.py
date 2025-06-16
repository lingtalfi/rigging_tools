# --- This is the complete and unified script for your rig UI and tools ---
import bpy
from mathutils import Matrix, Vector, Quaternion
from rigging_tools import draw_collection_button, draw_collapsible_box

#----------------------------
# Dependencies
#----------------------------
# This rig needs the rigging_tools addon to be installed to work correctly.



# --- Global Configuration ---
armature_name = "donald-armature"




######################################################################################
# Main UI Panel
######################################################################################
class DONALDRIG_PT_rigui(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'
    bl_label = "Rig UI"
    bl_idname = "DONALDRIG_PT_rigui"

    @classmethod
    def poll(self, context):
        return (context.active_object and context.active_object.type == 'ARMATURE' and 
                context.active_object.name == armature_name)

    def draw(self, context):
        layout = self.layout
        rig = context.active_object

        #-------------------------
        # Core layer 
        #-------------------------
        col = draw_collapsible_box(layout, context, "donald_core_expanded", "Core", icon='MOD_ARMATURE')
        if col:
            row = col.row(align=True)
            draw_collection_button(row, "root_props", text="Root & props")
            row = col.row(align=True)
            draw_collection_button(row, "def")
            draw_collection_button(row, "org")
            draw_collection_button(row, "mch")
            draw_collection_button(row, "tweaks")     
        
        
        #-------------------------
        # Body visibility
        #-------------------------        
        col = draw_collapsible_box(layout, context, "donald_body_visibility", "Body Visibility", icon='ARMATURE_DATA')
        if col:        
            row = col.row(align = True)  
            draw_collection_button(row, "shoulder_L", show_solo_button=True)
            draw_collection_button(row, "shoulder_R", show_solo_button=True)
            row = col.row(align = True)  
            draw_collection_button(row, "arm_fk_L", show_solo_button=True)
            draw_collection_button(row, "arm_fk_R", show_solo_button=True)
            row = col.row(align = True)  
            draw_collection_button(row, "arm_ik_L", show_solo_button=True)
            draw_collection_button(row, "arm_ik_R", show_solo_button=True)
            row = col.row(align = True)  
            draw_collection_button(row, "hand_L", show_solo_button=True)
            draw_collection_button(row, "hand_R", show_solo_button=True)
            row = col.row(align = True)  
            draw_collection_button(row, "finger_tips", show_solo_button=True)
            row = col.row(align = True)  
            draw_collection_button(row, "tail_fk", show_solo_button=True)
            draw_collection_button(row, "tail_ik", show_solo_button=True)
            row = col.row(align = True)          
            draw_collection_button(row, "leg_fk_L", show_solo_button=True)
            draw_collection_button(row, "leg_fk_R", show_solo_button=True)
            row = col.row(align = True)  
            draw_collection_button(row, "leg_ik_L", show_solo_button=True)
            draw_collection_button(row, "leg_ik_R", show_solo_button=True)
            row = col.row(align = True)  
            draw_collection_button(row, "foot_L", show_solo_button=True)
            draw_collection_button(row, "foot_R", show_solo_button=True)
            row = col.row(align = True)  
            draw_collection_button(row, "toe_tips", show_solo_button=True)

        #-------------------------
        # Snapping
        #-------------------------
        col = draw_collapsible_box(layout, context, "donald_snapping", "Snapping", icon='SNAP_ON')
        if col:                
            # --- Arm Snapping ---
            row = col.row(align=True)
            op_to_fk = row.operator("rig.snap_bone_chain", text="Arm L < FK")
            op_to_fk.source_bones = "mch_ik_arm.L, mch_ik_forearm.L, hand_ik.L"
            op_to_fk.target_bones = "arm_fk.L, forearm_fk.L, hand_fk.L"
            
            op_to_fk = row.operator("rig.snap_bone_chain", text="Arm R < FK")
            op_to_fk.source_bones = "mch_ik_arm.R, mch_ik_forearm.R, hand_ik.R" 
            op_to_fk.target_bones = "arm_fk.R, forearm_fk.R, hand_fk.R"        
            
            
            row = col.row(align=True)
            op_to_ik_arm_L = row.operator("rig.snap_to_ik_with_pole", text="Arm L < IK")
            op_to_ik_arm_L.ik_control_bone = "hand_ik.L"
            op_to_ik_arm_L.pole_control_bone = "pole_arm.L"
            op_to_ik_arm_L.source_end_bone = "hand_fk.L"
            op_to_ik_arm_L.source_chain_root = "arm_fk.L"
            op_to_ik_arm_L.source_chain_pivot = "forearm_fk.L"
            
            op_to_ik_arm_R = row.operator("rig.snap_to_ik_with_pole", text="Arm R < IK")
            op_to_ik_arm_R.ik_control_bone = "hand_ik.R"
            op_to_ik_arm_R.pole_control_bone = "pole_arm.R"
            op_to_ik_arm_R.source_end_bone = "hand_fk.R"
            op_to_ik_arm_R.source_chain_root = "arm_fk.R"
            op_to_ik_arm_R.source_chain_pivot = "forearm_fk.R"    
            
            # --- Tail Snapping ---
            row = col.row(align=True)
            op_to_fk = row.operator("rig.snap_bone_chain", text="Tail < FK")
            op_to_fk.source_bones = "tail_01_ik, tail_02_ik"
            op_to_fk.target_bones = "tail_01_fk, tail_02_fk"           
            
            op_to_ik = row.operator("rig.snap_bone_chain", text="Tail < IK")
            op_to_ik.source_bones = "tail_01_fk, tail_02_fk"
            op_to_ik.target_bones = "tail_01_ik, tail_02_ik"          

            # --- Leg Snapping ---
            row = col.row(align=True)
            op_to_fk = row.operator("rig.snap_bone_chain", text="Leg L < FK")
            op_to_fk.source_bones = "mch_thigh_ik.L, mch_shin_ik.L, foot_ik_master.L"
            op_to_fk.target_bones = "thigh_fk.L, shin_fk.L, foot_fk.L"
            
            op_to_fk = row.operator("rig.snap_bone_chain", text="Leg R < FK")
            op_to_fk.source_bones = "mch_thigh_ik.R, mch_shin_ik.R, foot_ik_master.R"
            op_to_fk.target_bones = "thigh_fk.R, shin_fk.R, foot_fk.R"        

            row = col.row(align=True)
            op_to_ik = row.operator("rig.snap_bone_chain", text="Leg L < IK")
            op_to_ik.source_bones = "foot_fk.L" 
            op_to_ik.target_bones = "foot_ik_master.L"
         
            op_to_ik = row.operator("rig.snap_bone_chain", text="Leg R < IK")
            op_to_ik.source_bones = "foot_fk.R" 
            op_to_ik.target_bones = "foot_ik_master.R"     
        
        
        
        #-------------------------
        # Properties
        #-------------------------     
        col = draw_collapsible_box(layout, context, "donald_properties", "Rig Properties", icon='PROPERTIES')
        if col:  
            # First, get a reference to the 'properties' bone, if it exists
            properties_bone = rig.pose.bones.get("properties")
            
            if properties_bone:
                col.prop(properties_bone, '["arm_fk_ik.L"]', text="Arm FK/IK L", slider=True)
                col.prop(properties_bone, '["arm_fk_ik.R"]', text="Arm FK/IK R", slider=True)
                col.prop(properties_bone, '["arm_follow.L"]', text="Arm Follow L", slider=True)        
                col.prop(properties_bone, '["arm_follow.R"]', text="Arm Follow R", slider=True)        
                col.prop(properties_bone, '["tail_fk_ik"]', text="Tail FK/IK", slider=True)
                col.prop(properties_bone, '["leg_fk_ik_L"]', text="Leg FK/IK L", slider=True)
                col.prop(properties_bone, '["leg_fk_ik_R"]', text="Leg FK/IK R", slider=True)

        #-------------------------
        # Debug
        #-------------------------
        col = draw_collapsible_box(layout, context, "donald_debug", "Debug Tools", icon='TOOL_SETTINGS', default_expanded=False)
        if col:
            col.operator("debug.dissect_bone_matrix", icon='CONSOLE')        
        
        
######################################################################################
# Registration
######################################################################################
classes = (
    DONALDRIG_PT_rigui,
)


# This function runs once when the script is registered
def register(): 
    for cls in classes:
        bpy.utils.register_class(cls)

# This function runs once when the script is unregistered
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        

# This is the standard entry point that allows the script to be run from the Text Editor.
if __name__ == "__main__":
    try:
        unregister()
    except (RuntimeError, AttributeError): pass
    register()
