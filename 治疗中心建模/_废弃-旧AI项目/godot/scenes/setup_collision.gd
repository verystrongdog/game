@tool
extends Node3D
## 一键生成全场景碰撞体
## 使用方法: 将此脚本挂到 HospitalScene 根节点, 在 Inspector 中点击 "Setup Collisions"

@export var collision_glb_path := "res://models/hospital_phase2_collision.glb"

var _collision_scene: Node3D = null

func setup_collisions():
	print("=== Setting up collision bodies ===")
	if _collision_scene:
		_collision_scene.queue_free()

	# 加载碰撞体 GLB
	var loader := ResourceLoader.load(collision_glb_path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE)
	if not loader:
		printerr("Failed to load: ", collision_glb_path)
		return
	_collision_scene = loader.instantiate()
	_collision_scene.name = "CollisionRoot"
	add_child(_collision_scene)

	var count := 0
	_process_node(_collision_scene, count)

	print("=== Done! Collision bodies created ===")

func _process_node(node: Node3D, count: int) -> int:
	for child in node.get_children():
		if child is MeshInstance3D:
			var mesh_inst := child as MeshInstance3D
			var mesh := mesh_inst.mesh
			if mesh:
				var body := StaticBody3D.new()
				body.name = "SB_" + child.name.trim_prefix("Col_")
				body.transform = mesh_inst.global_transform
				# 碰撞体设成不可见 (调试时可开启)
				body.visible = false

				var col_shape := CollisionShape3D.new()
				col_shape.name = "Shape"
				col_shape.shape = mesh.create_convex_shape(true, true)
				body.add_child(col_shape)

				# 放在碰撞体 mesh 原位置的兄弟节点
				child.get_parent().add_child(body)
				count += 1

		count = _process_node(child, count)

	return count
