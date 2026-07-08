extends CharacterBody3D

@export var speed := 5.0
@export var jump_velocity := 5.0
@export var mouse_sensitivity := 0.003

var _yaw := 0.0
var _noclip := false
var gravity := 9.8 * 3

func _ready():
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

func _input(event):
	if event is InputEventMouseMotion and Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED:
		_yaw -= event.relative.x * mouse_sensitivity

	if Input.is_action_just_pressed("ui_cancel"):
		if Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED:
			Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
		else:
			Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

	# V 键切换穿墙模式
	if Input.is_action_just_pressed("noclip"):
		_noclip = not _noclip
		if _noclip:
			Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

func _physics_process(delta):
	if _noclip:
		# 飞行模式
		velocity.y = 0
		var input_dir := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
		var direction := Vector3(input_dir.x, 0, input_dir.y).rotated(Vector3.UP, _yaw)
		if Input.is_key_pressed(KEY_E):
			direction.y += 1.0
		if Input.is_key_pressed(KEY_Q):
			direction.y -= 1.0
		velocity = direction.normalized() * speed * 2.0
	else:
		# 正常模式
		if not is_on_floor():
			velocity.y -= gravity * delta
		if Input.is_action_just_pressed("ui_accept") and is_on_floor():
			velocity.y = jump_velocity

		var input_dir := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
		var direction := Vector3(input_dir.x, 0, input_dir.y).rotated(Vector3.UP, _yaw)
		if direction.length() > 0:
			direction = direction.normalized()
		velocity.x = direction.x * speed
		velocity.z = direction.z * speed

	rotation.y = _yaw
	$Camera3D.position = Vector3(0, 3.5, 4.0)
	$Camera3D.look_at(global_position + Vector3(0, 0.8, 0))

	move_and_slide()
