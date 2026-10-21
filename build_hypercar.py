import bpy, math, os
from mathutils import Vector
from math import sin, cos, pi
OUT=os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
 if c.name!='Collection': bpy.data.collections.remove(c)
base=bpy.data.collections.get('Collection'); base.name='00 Studio'
def collection(n):
 c=bpy.data.collections.new(n); bpy.context.scene.collection.children.link(c); return c
body=collection('01 Removable body panels'); glasscol=collection('02 Cockpit glazing'); aero=collection('03 Carbon aerodynamics'); chassis=collection('04 Triangulated chassis'); suspension=collection('05 Suspension'); wheels=collection('06 Wheels and brakes'); interior=collection('07 Interior'); engine=collection('08 V8 hybrid powertrain'); lamps=collection('09 Lighting details')
C=body
def mat(n,col,metal=0,rough=.35):
 m=bpy.data.materials.new(n); m.diffuse_color=(*col,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*col,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
paint=mat('Liquid titanium • teal',(.025,.29,.32),.78,.23); dark=mat('Intake darkness',(.009,.013,.017),.2,.3); rubber=mat('Performance tire rubber',(.018,.02,.023),0,.7); metal=mat('Brushed aluminum',(.36,.42,.46),.85,.24); gold=mat('Anodized copper gold',(.9,.31,.055),.75,.25); carbon=mat('Woven carbon',(.025,.032,.04),.6,.3); red=mat('Harness crimson',(.5,.015,.025),0,.42); seatmat=mat('Alcantara',(.035,.045,.052),0,.85)
p=carbon.node_tree.nodes.get('Principled BSDF'); tex=carbon.node_tree.nodes.new('ShaderNodeTexChecker'); tex.inputs['Color1'].default_value=(.015,.02,.027,1); tex.inputs['Color2'].default_value=(.055,.063,.07,1); tex.inputs['Scale'].default_value=160; carbon.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
glass=mat('Smoked canopy',(.018,.045,.055),.35,.12); glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.25
white=mat('Ice white LED',(.6,.9,1),.2,.2); tail=mat('Red LED',(.6,.005,.008),.1,.2)
for m,color in [(white,(.5,.85,1,1)),(tail,(1,.005,.012,1))]:
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Emission Color'].default_value=color; p.inputs['Emission Strength'].default_value=5

def finish(o,n,m):
 o.name=n
 for c in list(o.users_collection): c.objects.unlink(o)
 C.objects.link(o)
 if m:o.data.materials.append(m)
 if o.type=='MESH':
  for f in o.data.polygons:f.use_smooth=True
 return o

def mesh(n,v,f,m,sub=0,solid=0):
 d=bpy.data.meshes.new(n); d.from_pydata(v,[],f); d.update(); o=bpy.data.objects.new(n,d); C.objects.link(o); d.materials.append(m)
 for p in d.polygons:p.use_smooth=True
 if sub: mod=o.modifiers.new('Smooth quad surface','SUBSURF'); mod.levels=sub
 if solid: mod=o.modifiers.new('Panel thickness','SOLIDIFY'); mod.thickness=solid
 return o

def box(n,loc,size,m,bev=.025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=finish(bpy.context.object,n,m); o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bev: mod=o.modifiers.new('Edge radius','BEVEL'); mod.width=bev; mod.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o

def rod(n,a,b,r,m):
 d=Vector(b)-Vector(a); bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2); o=finish(bpy.context.object,n,m); o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); return o

def line(n,pts,r,m):
 d=bpy.data.curves.new(n,'CURVE'); d.dimensions='3D'; d.bevel_depth=r; d.bevel_resolution=3; s=d.splines.new('POLY'); s.points.add(len(pts)-1)
 for p,co in zip(s.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(n,d); C.objects.link(o); d.materials.append(m); return o

def torus(n,loc,major,minor,m):
 bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=16,location=loc,major_radius=major,minor_radius=minor,rotation=(pi/2,0,0)); return finish(bpy.context.object,n,m)

# Coordinates: nose -X, rear +X, dimensions in meters.
# Longitudinal quad strips for continuous sculpted shoulder surfaces.
xs=[-2.30+i*4.58/80 for i in range(81)]
def width(x):return .88+.12*math.exp(-((x+1.4)/.6)**2)+.145*math.exp(-((x-1.35)/.67)**2)-.055*math.exp(-(x/.6)**2)
def shoulder(x):return .53+.35*math.exp(-((x+1.4)/.57)**2)+ .39*math.exp(-((x-1.4)/.64)**2)
for s in [-1,1]:
 v=[]
 for x in xs:
  w=width(x); top=shoulder(x); bottom=.23
  for wx,r in [(-1.4,.396),(1.4,.416)]:
   if abs(x-wx)<r:bottom=max(bottom,(.465 if wx<0 else .485)+math.sqrt(r*r-(x-wx)**2))
  bottom=min(bottom,top-.012)
  for t in [0,.22,.5,.8,1]:v.append((x,s*(w-.26+.26*t-.035*sin(pi*t)),top*(1-t)+bottom*t))
 f=[(i*5+j,i*5+j+1,(i+1)*5+j+1,(i+1)*5+j) for i in range(80) for j in range(4)]
 mesh(('Left' if s>0 else 'Right')+' continuous fender shoulder',v,f,paint,1,.014)
 # arch lips and inner wells
 for wx,r in [(-1.4,.396),(1.4,.416)]:
  pts=[(wx+r*cos(t),s*(width(wx)+.008),(.465 if wx<0 else .485)+r*sin(t)) for t in [i*pi/48 for i in range(49)]]; line('Carbon wheel arch lip',pts,.012,carbon)
  vv=[]
  for i in range(49):
   t=i*pi/48
   for y in [.67,width(wx)]:vv.append((wx+(r+.005)*cos(t),s*y,(.465 if wx<0 else .485)+(r+.005)*sin(t)))
  mesh('Wheel well liner',vv,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(48)],carbon,0,.008)
# bonnet and engine shell loft helper

def loft(n,rows,m,col,sub=2):
 global C; C=col; v=[]
 for x,w,z in rows:
  for j in range(13):
   t=-1+2*j/12; v.append((x,w*t,z-.075*t*t))
 return mesh(n,v,[(i*13+j,i*13+j+1,(i+1)*13+j+1,(i+1)*13+j) for i in range(len(rows)-1) for j in range(12)],m,sub,.012)
loft('Removable sculpted front hood',[(-2.30,.64,.49),(-2.25,.67,.51),(-1.95,.72,.57),(-1.5,.73,.64),(-1.05,.72,.63),(-.72,.67,.62),(-.68,.66,.62)],paint,body)
loft('Vented rear engine cover',[(.65,.60,.74),(.7,.65,.75),(1.25,.70,.77),(1.8,.74,.7),(2.22,.75,.60),(2.26,.74,.59)],paint,body)
C=aero
for s in [-1,1]:
 line('Hood airflow channel',[(-2.1,s*.48,.545),(-1.65,s*.5,.63),(-1.05,s*.48,.625),(-.79,s*.43,.615)],.016,carbon)
 # concave doors, inset intake cavity and rising intake blade
 C=body
 mesh('Sculpted door',[(x,s*y,z) for x,y,z in [(-.95,.78,.61),(-.4,.8,.71),(.43,.79,.72),(.66,.87,.64),(.2,.76,.37),(-.65,.77,.29),(-.9,.88,.36)]],[(0,1,2,3,4,5,6)],paint,0,.016)
 C=aero
 mesh('Deep side intake cavity',[(x,s*y,z) for x,y,z in [(.32,.84,.42),(.62,.9,.73),(1.01,.93,.76),(.96,.88,.32)]],[(0,1,2,3)],dark,0,.025)
 line('Intake flying buttress',[(.15,s*.86,.30),(.6,s*.96,.48),(.92,s*.99,.77)],.045,paint)
 box('Carbon side blade',(-.02,s*.93,.19),(1.94,.2,.06),carbon)
 for i in range(5):box('Side radiator slat',(.72+i*.045,s*.913,.54),(.015,.025,.25),metal,.003)
 for i in range(4):box('Front fender extraction louver',(-1.43+i*.085,s*.85,.797),(.044,.16,.014),carbon,.004)
# canopy
loft('Teardrop glazed canopy',[(-.86,.60,.64),(-.80,.61,.67),(-.4,.57,1.04),(-.15,.55,1.13),(.22,.51,1.145),(.58,.43,1.06),(.91,.32,.79),(.96,.29,.76)],glass,glasscol)
C=body
for s in [-1,1]:line('Thin canopy perimeter',[(-.83,s*.60,.59),(-.4,s*.57,.965),(-.15,s*.55,1.055),(.22,s*.51,1.07),(.58,s*.43,.985),(.94,s*.3,.70)],.019,paint)
C=glasscol
for s in [-1,1]:
 mesh('Tapered side window',[(x,s*y,z) for x,y,z in [(-.79,.60,.65),(-.39,.569,.966),(-.15,.549,1.055),(.22,.509,1.07),(.58,.429,.985),(.9,.32,.75),(.43,.78,.735),(-.38,.79,.725)]],[(0,1,2,3,4,5,6,7)],glass,0,.008)
C=body
loft('Roof spine',[(-.2,.13,1.14),(-.15,.14,1.15),(.25,.14,1.16),(.56,.12,1.075),(.62,.11,1.04)],carbon,body)
C=aero; box('Roof scoop opening',(.38,0,1.135),(.22,.22,.07),dark); box('Roof scoop cowl',(.5,0,1.16),(.30,.28,.035),paint)
for s in [-1,1]:
 rod('Camera mirror arm',(-.60,s*.62,.72),(-.66,s*1.05,.79),.015,carbon); box('Camera mirror housing',(-.65,s*1.07,.80),(.20,.10,.06),paint)
# nose: black apertures with separated painted bridge elements
C=aero; box('Full width intake recess',(-2.22,0,.345),(.13,1.79,.23),dark)
mesh('Front splitter',[(-2.4,-.88,.13),(-2.4,.88,.13),(-2.13,1.02,.16),(-1.91,.98,.18),(-1.92,-.98,.18),(-2.13,-1.02,.16)],[(0,1,2,3,4,5)],carbon,0,.035)
C=body
for s in [-1,1]:
 o=box('Front intake divider',(-2.25,s*.44,.35),(.2,.055,.25),paint);o.rotation_euler.x=s*.25
 line('Angular bumper brow',[(-2.29,s*.1,.47),(-2.24,s*.53,.49),(-2.15,s*.89,.52)],.034,paint)
 C=lamps; line('Blade headlamp housing',[(-2.19,s*.56,.54),(-2.10,s*.89,.56),(-2.17,s*.82,.43)],.032,dark);line('Boomerang LED',[(-2.22,s*.56,.55),(-2.13,s*.88,.57),(-2.20,s*.81,.45)],.009,white);C=body
C=aero
for y in [-.8,-.5,0,.5,.8]:box('Front splitter strake',(-2.12,y,.185),(.30,.013,.11),carbon,.003)
box('Flat carbon floor',(0,0,.125),(3.92,1.55,.05),carbon)
for s in [-1,1]:
 mesh('Venturi tunnel ramp',[(.2,s*.5,.13),(.2,s*.84,.13),(2.32,s*.88,.37),(2.32,s*.45,.37)],[(0,1,2,3)],carbon,0,.015)
for y in [-.88,-.59,-.3,0,.3,.59,.88]:
 mesh('Deep diffuser vertical fin',[(1.45,y,.12),(2.34,y,.12),(2.34,y,.4),(1.45,y,.2)],[(0,1,2,3)],carbon,0,.014)
box('Rear grille recess',(2.23,0,.49),(.06,1.69,.24),dark)
for i in range(17):box('Rear ventilation grille',(2.27,-.77+i*.096,.5),(.022,.016,.19),metal,.003)
for s in [-1,1]:
 C=lamps;line('Rear thin LED',[(2.285,s*.14,.63),(2.285,s*.86,.63)],.012,tail);C=aero
 rod('Titanium exhaust',(2.15,s*.2,.45),(2.37,s*.2,.45),.068,metal);rod('Exhaust bore',(2.375,s*.2,.45),(2.382,s*.2,.45),.052,dark)
 box('Swan neck wing support',(1.87,s*.54,.83),(.075,.04,.46),carbon)
# curved quad wing
v=[]
for j in range(25):
 y=-1.025+j*2.05/24
 for i in range(7):
  t=i/6;v.append((1.8+.40*t,y,1.045+.05*sin(t*pi)+.025*(y*y)))
mesh('Adjustable rear wing blade',v,[(j*7+i,j*7+i+1,(j+1)*7+i+1,(j+1)*7+i) for j in range(24) for i in range(6)],carbon,1,.018)
for s in [-1,1]:box('Wing endplate',(2,s*1.025,1.07),(.45,.018,.14),paint,.018)
for i in range(8):box('Engine cover louver',(1.02+i*.13,0,.79-i*.017),(.055,.69,.022),carbon,.009)
# Triangular subframes and monocoque
C=chassis
box('Carbon passenger tub',(0,0,.29),(1.63,1.23,.25),carbon)
for s in [-1,1]:
 for start,end in [(-2.03,-.72),(.73,1.99)]:
  for z in [.25,.52]:rod('Subframe longitudinal rail',(start,s*.48,z),(end,s*.48,z),.022,metal)
  for i in range(3):
   x=start+(end-start)*i/3;nx=start+(end-start)*(i+1)/3
   rod('Triangular frame brace',(x,s*.48,.25),(nx,s*.48,.52),.018,metal)
   rod('Cross car frame',(x,-.48,.25),(x,.48,.25),.018,metal)
 rod('Monocoque sill',(-.77,s*.63,.25),(.77,s*.63,.25),.05,carbon)
# Wheels: independent tire profile, forged split spokes, discs and calipers
for x,track,r,tw in [(-1.4,1.75,.365,.295),(1.4,1.79,.385,.345)]:
 for s in [-1,1]:
  y=s*track/2;z=r+.10; C=wheels
  profile=[(-tw/2,.285),(-tw/2,r-.04),(-tw*.38,r), (tw*.38,r),(tw/2,r-.04),(tw/2,.285)]
  vv=[]
  for i in range(80):
   a=i*2*pi/80
   for dy,rr in profile:vv.append((x+rr*cos(a),y+dy,z+rr*sin(a)))
  mesh('Sculpted performance tire',vv,[(i*6+j,((i+1)%80)*6+j,((i+1)%80)*6+(j+1)%6,i*6+(j+1)%6) for i in range(80) for j in range(6)],rubber,1)
  outer=y+s*(tw/2+.002)
  torus('Forged rim lip',(x,outer,z),.275,.012,metal);torus('Inner rim lip',(x,y-s*.1,z),.27,.012,dark)
  rod('Carbon ceramic disc',(x,outer-s*.053,z),(x,outer-s*.072,z),.228,metal)
  for i in range(10):
   a=i*2*pi/10
   for delta in [-.085,.085]:rod('Split swept forged spoke',(x+.065*cos(a),outer,z+.065*sin(a)),(x+.265*cos(a+.15+delta),outer-s*.015,z+.265*sin(a+.15+delta)),.013,carbon)
  rod('Center lock hub',(x,outer-s*.015,z),(x,outer+s*.025,z),.058,metal);rod('Gold center lock',(x,outer+s*.025,z),(x,outer+s*.035,z),.026,gold)
  for i in range(24):
   a=i*2*pi/24
   for rr in [.177,.20]:rod('Rotor drilled recess',(x+rr*cos(a),outer-s*.051,z+rr*sin(a)),(x+rr*cos(a),outer-s*.049,z+rr*sin(a)),.006,dark)
  box('Six piston gold caliper',(x+.18,outer-s*.08,z),(.085,.085,.23),gold)
  # narrow longitudinal tread lines
  for off in [-.08,0,.08]:torus('Tire circumferential tread',(x,y+off,z),r-.001,.003,dark)
  C=suspension
  for zz in [z-.13,z+.10]:
   for dx in [-.25,.25]:rod('Double wishbone control arm',(x+dx,s*.45,zz),(x,s*.79,zz),.016,metal)
  rod('Pushrod',(x,s*.79,z-.13),(x+.16,s*.41,.63),.014,gold)
  a=Vector((x+.16,s*.41,.63));b=Vector((x-.18,s*.29,.42));rod('Inboard coilover damper',a,b,.026,metal)
  axis=(b-a).normalized();u=axis.cross(Vector((0,0,1))).normalized();vvv=axis.cross(u)
  line('Gold coil spring',[a+(b-a)*t+.047*(u*cos(t*16*pi)+vvv*sin(t*16*pi)) for t in [i/160 for i in range(161)]],.008,gold)
  rod('Anti roll bar',(x-.2,-.45,.4),(x-.2,.45,.4),.014,metal)
# cabin details
C=interior
for s in [-1,1]:
 box('Carbon bucket seat base',(.13,s*.32,.39),(.55,.43,.09),carbon)
 o=box('Reclined bucket seat back',(.39,s*.32,.62),(.10,.43,.48),seatmat);o.rotation_euler.y=-.2
 box('Integrated headrest',(.43,s*.32,.87),(.13,.25,.17),carbon)
 for dy in [-.1,.1]:line('Four point harness',[(.39,s*.32+dy,.82),(.31,s*.32+dy,.56),(.07,s*.32+dy,.44)],.019,red)
box('Dashboard',(-.54,0,.68),(.17,1.02,.12),carbon)
box('Digital instrument cluster',(-.43,-.32,.76),(.03,.25,.11),white,.008)
rod('Steering column',(-.50,-.32,.57),(-.26,-.32,.66),.026,metal)
line('Digital racing steering wheel',[(-.27,-.49,.7),(-.27,-.47,.78),(-.27,-.19,.78),(-.27,-.15,.7),(-.27,-.2,.62),(-.27,-.43,.62),(-.27,-.49,.7)],.02,carbon)
box('Center console',(0,0,.49),(.7,.14,.18),carbon);box('Central touchscreen',(-.28,0,.64),(.15,.13,.012),dark)
# powertrain
C=engine
box('Low mounted V8 block',(1.13,0,.39),(.62,.62,.29),metal)
for s in [-1,1]:
 o=box('V8 cylinder bank',(1.13,s*.24,.57),(.65,.22,.17),carbon);o.rotation_euler.x=s*.3
 for i in range(4):rod('Intake runner',( .89+i*.15,s*.1,.66),(.89+i*.15,s*.3,.57),.028,metal)
 torus('Twin turbo compressor',(1.54,s*.36,.48),.09,.035,metal)
 box('Side intercooler',(.94,s*.53,.47),(.42,.12,.27),metal)
 line('Charge cooling pipe',[(1.55,s*.35,.53),(1.6,s*.46,.68),(1.14,s*.45,.72),(1.14,s*.1,.72)],.03,metal)
box('Intake plenum',(1.14,0,.7),(.52,.24,.10),gold)
box('Rear transmission',(1.77,0,.36),(.39,.30,.26),metal)
rod('Hybrid motor',(1.48,0,.38),(1.63,0,.38),.16,dark)
box('Battery module',(.61,0,.33),(.16,1.02,.19),dark)
# studio
C=base
floor=mat('Studio graphite',(.085,.1,.12),.15,.5);box('Studio floor',(0,0,-.065),(200,200,.1),floor)
scene=bpy.context.scene;scene.unit_settings.system='METRIC'
def camera(n,loc,target):
 bpy.ops.object.camera_add(location=loc);o=bpy.context.object;o.name=n;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=6.4;return o
cam=camera('Camera • front three quarter',(-6.3,-6.6,3.35),(0,0,.52));scene.camera=cam
camera('Camera • rear three quarter',(6,-6,2.9),(0,0,.55));camera('Camera • side',(0,-8,1.8),(0,0,.55))
for n,loc,power,size in [('Key',(-3,-4,6),1800,5),('Rim',(2,4,5),2200,4),('Front',(-4,2,3),1000,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=n;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
scene.world.color=(.22,.22,.22);scene.render.engine='CYCLES';scene.cycles.samples=32
scene.render.resolution_x=1500;scene.render.resolution_y=950;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
scene['Design brief']='car-specification.txt';scene['Model status']='Procedural concept model, not production CAD';scene['Wheelbase meters']=2.8
# engineering layer preserves shared assemblies while hiding shells
scene.view_layers[0].name='Complete car'
eng=scene.view_layers.new('Engineering • body removed')
for c in eng.layer_collection.children:
 if c.name in [body.name,glasscol.name]:c.exclude=True
eng.use=False
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':a.spaces.active.region_3d.view_distance=6;a.spaces.active.region_3d.view_location=(0,0,.5)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'hypercar-concept.blend'))
scene.render.filepath=os.path.join(OUT,'hypercar-preview.png');bpy.ops.render.render(write_still=True)


