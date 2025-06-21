extends StaticBody3D

class_name Building

@export var building_type: String = ""
@export var building_data: Dictionary = {}

func _ready():
    add_to_group("buildings")
    setup_interaction_area()

func setup_interaction_area():
    # Set up interaction area
    var interaction_area = Area3D.new()
    var collision_shape = CollisionShape3D.new()
    var shape = BoxShape3D.new()
    
    shape.size = Vector3(5, 4, 5)
    collision_shape.shape = shape
    
    interaction_area.add_child(collision_shape)
    add_child(interaction_area)
    
    interaction_area.body_entered.connect(_on_player_entered)
    interaction_area.body_exited.connect(_on_player_exited)

func _on_player_entered(body):
    if body.is_in_group("player"):
        print("Entered ", building_type, " area")

func _on_player_exited(body):
    if body.is_in_group("player"):
        print("Left ", building_type, " area")

func interact(player: Variant):
    print("Interacting with ", building_type)

func open_shop():
    print("Welcome to the shop!")

func enter_house():
    print("You enter the cozy house...")

func enter_tavern():
    print("Welcome to the tavern!")

func open_blacksmith():
    print("The blacksmith looks up from his anvil.")
