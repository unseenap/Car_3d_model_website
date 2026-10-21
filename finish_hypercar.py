import bpy, os
P=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(P,'hypercar-concept.blend'))
c=bpy.data.collections['02 Cockpit glazing'];m=bpy.data.materials['Smoked canopy']
for s in [-1,1]:
 v=[(x,s*y,z) for x,y,z in [(-.79,.60,.65),(-.39,.569,.966),(-.15,.549,1.055),(.22,.509,1.07),(.58,.429,.985),(.9,.32,.75),(.43,.78,.735),(-.38,.79,.725)]]
 d=bpy.data.meshes.new('Side glazing');d.from_pydata(v,[],[tuple(range(8))]);d.materials.append(m);o=bpy.data.objects.new('Tapered side window',d);c.objects.link(o)
scene=bpy.context.scene
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(P,'hypercar-concept.blend'))
scene.render.filepath=os.path.join(P,'hypercar-preview.png');bpy.ops.render.render(write_still=True)
scene.view_layers['Complete car'].use=False;scene.view_layers['Engineering • body removed'].use=True
scene.render.filepath=os.path.join(P,'hypercar-engineering.png');bpy.ops.render.render(write_still=True)
print('VERIFIED',len(bpy.data.objects),'objects',len(bpy.data.collections),'collections')
