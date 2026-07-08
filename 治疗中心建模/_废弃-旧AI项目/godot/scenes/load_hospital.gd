extends Node3D

func _ready():
	# 加载视觉模型
	var vis = load("res://models/hospital_phase2.glb")
	if vis:
		var v = vis.instantiate()
		v.name = "HospitalVisual"
		add_child(v)
		print("Visual loaded")

	# 加载碰撞体 GLB
	var col = load("res://models/hospital_phase2_collision.glb")
	if col:
		var c = col.instantiate()
		c.name = "CollisionRoot"
		c.visible = false
		add_child(c)
		# 等一帧让子节点加载完
		await get_tree().process_frame
		_build_collisions(c)
		print("Collision built")

func _build_collisions(root: Node):
	var count := 0
	for child in _all_children(root):
		if child is MeshInstance3D and child.mesh:
			var body := StaticBody3D.new()
			body.name = "SB_" + child.name.trim_prefix("Col_")
			body.global_transform = child.global_transform
			var shape := CollisionShape3D.new()
			shape.shape = child.mesh.create_trimesh_shape()
			body.add_child(shape)
			add_child(body)
			count += 1
	print(count, " collision bodies")

func _all_children(node: Node) -> Array:
	var r := []
	for c in node.get_children():
		r.append(c)
		r.append_array(_all_children(c))
	return r
