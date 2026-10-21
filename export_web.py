import bpy, os
P=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(P,'hypercar-concept.blend'))
bpy.context.window.view_layer=bpy.context.scene.view_layers['Complete car']
bpy.ops.object.select_all(action='DESELECT')
for o in list(bpy.data.objects):
 if o.type not in ['MESH','CURVE'] or any(c.name=='00 Studio' for c in o.users_collection):continue
 o.hide_set(False);o.select_set(True)
 o['assembly']=o.users_collection[0].name
 for mod in o.modifiers:
  if mod.type=='SUBSURF':mod.levels=1;mod.render_levels=1
  if mod.type=='BEVEL':mod.segments=2
 if o.type=='CURVE':o.data.bevel_resolution=2
# glTF uses physical material values; remove unsupported procedural checker.
for m in bpy.data.materials:
 if m.use_nodes:
  p=m.node_tree.nodes.get('Principled BSDF')
  if p:
   for link in list(p.inputs['Base Color'].links):m.node_tree.links.remove(link)
   p.inputs['Base Color'].default_value=m.diffuse_color
bpy.ops.object.convert(target='MESH')
bpy.ops.export_scene.gltf(filepath=os.path.join(P,'hypercar-site','public','hypercar.glb'),export_format='GLB',use_selection=True,export_extras=True,export_apply=True,export_cameras=False,export_lights=False)
