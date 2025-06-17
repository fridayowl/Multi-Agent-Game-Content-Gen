extends StaticBody3D

class_name Building

@export var building_type: String = ""
@export var building_data: Dictionary = {}

func _ready():
    add_to_group("buildings")
    
    # Set up interaction
    var interaction_area = Area3D.new()
    var collision_shape = CollisionShape3D.new()
    var shape = BoxShape3D.new()
    
    shape.size = Vector3(5, 4, 5)  # Slightly larger than building
    collision_shape.shape = shape
    
    interaction_area.add_child(collision_shape)
    add_child(interaction_area)
    
    interaction_area.body_entered.connect(_on_player_entered)
    interaction_area.body_exited.connect(_on_player_exited)

func _on_player_entered(body):
    if body.name == "Player":
        print("Entered ", building_type, " area")

func _on_player_exited(body):
    if body.name == "Player":
        print("Left ", building_type, " area")

func interact(player):
    print("Interacting with ", building_type)
    
    # Different interactions based on building type
    match building_type:
        "shop":
            open_shop()
        "house":
            enter_house()
        "tavern":
            enter_tavern()
        "blacksmith":
            open_blacksmith()
        _:
            print("This is a ", building_type)

func open_shop():
    print("Welcome to the shop!")
    print("Items for sale: Sword (50g), Shield (30g), Potion (10g)")

func enter_house():
    print("You enter the cozy house...")
    print("There's a warm fireplace and comfortable furniture.")

func enter_tavern():
    print("Welcome to the tavern!")
    print("The barkeeper nods at you. There are several patrons chatting.")

func open_blacksmith():
    print("The blacksmith looks up from his anvil.")
    print("'Need something forged?' he asks.")
