extends CharacterBody3D

@export var speed := 8.0
@export var rotation_speed := 3.0
@export var mouse_sensitivity := 0.002

var _yaw := 0.0
var _pitch := 0.0

func _ready():
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

func _input(event):
	if event is InputEventMouseMotion and Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED:
		_yaw -= event.relative.x * mouse_sensitivity
		_pitch -= event.relative.y * mouse_sensitivity
		_pitch = clamp(_pitch, -1.4, 0.5)  # 限制俯仰

	if Input.is_action_just_pressed("ui_cancel"):
		if Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED:
			Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
		else:
			Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

func _physics_process(_delta):
	# 鼠标旋转
	rotation.y = _yaw
	$CameraPivot.rotation.x = _pitch

	# 键盘移动
	var input_dir := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	var direction := Vector3(input_dir.x, 0, input_dir.y).rotated(Vector3.UP, _yaw)

	# Q下降 / E上升
	if Input.is_key_pressed(KEY_Q):
		direction.y -= 1.0
	if Input.is_key_pressed(KEY_E):
		direction.y += 1.0

	velocity = direction.normalized() * speed
	move_and_slide()
