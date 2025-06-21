@tool
extends EditorPlugin

func _enter_tree():
    print("Generated Game Content plugin loaded")
    # Add custom dock or tools here if needed

func _exit_tree():
    print("Generated Game Content plugin unloaded")
    # Clean up custom additions here

func get_plugin_name():
    return "Generated Game Content"
