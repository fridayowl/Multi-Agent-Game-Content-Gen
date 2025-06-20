@tool
extends EditorPlugin

func _enter_tree():
    print("Generated Game Content plugin loaded")

func _exit_tree():
    print("Generated Game Content plugin unloaded")
