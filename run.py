

## This code runs as to set up the script to run the VR in ratcave

import pyglet
import ratcave as rc
import math, time
from ratcave.resources import cube_shader, default_shader
from natnetclient import NatClient

# These Three lines send the data to the monitor next to the main monitor ( harder to recognize)
platform = pyglet.window.get_platform()
display = platform.get_default_display()
screens = display.get_screens()

#OPening the basic pyglet window
window = pyglet.window.Window(resizable=True, fullscreen=True, screen=screens[1])

# Assemble the Virtual Scene
# arena_filename = 'calibration_assets/arena.obj'
arena_filename = 'calibration_assets/arena2.obj'# we are taking an arena which has been opened in blender and rendered to 3D after scanning it does not have flipped normals
# arena_filename = 'calibration_assets/arena_flippednormals.obj'
arena_reader = rc.WavefrontReader(arena_filename)  # loading the mesh of the arena thought a wavefrontreader
arena = arena_reader.get_mesh("Arena")  # making the wafrotn into mesh so we can extrude texture ont top of it.
# arena.scale.xyz = .1
arena.uniforms['diffuse'] = 1., 1., 1.  # addign texture to the arena
arena.rotation = arena.rotation.to_quaternion() # we also need to get arena's rotation not just xyz so it can be tracked and moved if it gets bumped

projector = rc.Camera.from_pickle('calibration_assets/projector.pkl')  # settign the pickle filled of the projector, which gives us the coordinates of where the projector is
light = rc.Light()  # need to set a light ( sun ) somewhere
light.position = projector.position # in this case the sun is exactly at the point where the projector is
#
# cube = obj_reader.get_mesh("Cube", position=(0, 0, 0), scale=0.2)
# cube.uniforms['diffuse'] = 1, 1, 0
#
# # virtual_scene = rc.Scene(meshes=[sphere, cube], bgColor=(0., 0., 1.))
# virtual_scene = rc.Scene(meshes=[cube, sphere], bgColor=(0., 0., 1.))
# virtual_scene.light.position.xyz = 0, 3, -1
#
#
# cube_camera = rc.Camera(projection=rc.PerspectiveProjection(fov_y=90, aspect=1.))
# virtual_scene.camera = cube_camera
#
# # Assemble the Projected Scene
obj_reader = rc.WavefrontReader(rc.resources.obj_primitives)   # adding a monkey to the FBO scene
monkey = obj_reader.get_mesh("Monkey", position=(0, 0, 0), scale=.8)

cube_texture = rc.TextureCube()  # usign cube mapping to import eh image on the texture of the arena
framebuffer = rc.FBO(texture=cube_texture) ## creating a framebuffer as the texture - in tut 4 it was the blue screen
# arena.textures.append(cube_texture)

#
#gettign positions of rigib bodies in real time
client = NatClient()
arena_rb = client.rigid_bodies['Arena']
rat_rb = client.rigid_bodies['Rat']

# settign the camera to be on top of the rats head
rat_camera = rc.Camera()
rat_camera.projection.aspect = 1
rat_camera.projection.fov_y = 90

# seetign aset virtual scene to be projected as the mesh of the arena
virtual_scene = rc.Scene(meshes=[monkey], light=light, camera=rat_camera, bgColor=(0, 0, 255))

# updating the posiotn of the arena in xyz and also in rotational perspective
arena.position = arena_rb.position
arena.rotation.xyzw = arena_rb.quaternion

# main window for updating
def update(dt):

    # monkey.rotation.y += 35 * dt  #use to set to see where the monkey was in space
    rat_camera.position = rat_rb.position  # setting the actual osiont of the rat camera to vbe of the rat position
#     virtual_scene.camera.position.xyz = monkey.position.xyz
    arena.uniforms['playerPos'] = rat_rb.position
pyglet.clock.schedule(update)  # making it so that the app updates in real time
#
#


@window.event
def on_draw():
    ##################  usign the texture to project on them
    # with framebuffer:
    #     with cube_shader:
    #         virtual_scene.draw360_to_texture(cube_texture)

    # ########################
    window.clear()
    with cube_shader:  # usign cube shader to create the actuall 6 sided virtual cube which gets upated with position and angle of the camera/viewer
        rc.clear_color(255, 0, 0)
        projector.projection.match_aspect_to_viewport()
        projector.projection.fov_y = 39  # why is it here 39? e
        with projector, light:

            arena.draw()
            # with cube_fbo as fbo:
            #     virtual_scene.draw360_to_texture(fbo.texture)
            #     projected_scene.draw()

# actually run everything.
pyglet.app.run()