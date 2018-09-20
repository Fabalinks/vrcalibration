import pyglet
import ratcave as rc
import math, time
from ratcave.resources import cube_shader, default_shader
from natnetclient import NatClient

platform = pyglet.window.get_platform()
display = platform.get_default_display()
screens = display.get_screens()
window = pyglet.window.Window(resizable=True, fullscreen=True, screen=screens[1])

# Assemble the Virtual Scene
# arena_filename = 'calibration_assets/arena.obj'
arena_filename = 'calibration_assets/arena2.obj'
# arena_filename = 'calibration_assets/arena_flippednormals.obj'
arena_reader = rc.WavefrontReader(arena_filename)
arena = arena_reader.get_mesh("Arena")
# arena.scale.xyz = .1
arena.uniforms['diffuse'] = 1., 1., 1.
arena.rotation = arena.rotation.to_quaternion()

projector = rc.Camera.from_pickle('calibration_assets/projector.pkl')
light = rc.Light()
light.position = projector.position
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
obj_reader = rc.WavefrontReader(rc.resources.obj_primitives)
monkey = obj_reader.get_mesh("Monkey", position=(0, 0, 0), scale=.8)

cube_texture = rc.TextureCube()
framebuffer = rc.FBO(texture=cube_texture)
# arena.textures.append(cube_texture)

#
#
client = NatClient()
arena_rb = client.rigid_bodies['Arena']
rat_rb = client.rigid_bodies['Rat']

rat_camera = rc.Camera()
rat_camera.projection.aspect = 1
rat_camera.projection.fov_y = 90

virtual_scene = rc.Scene(meshes=[monkey], light=light, camera=rat_camera, bgColor=(0, 0, 255))

arena.position = arena_rb.position
arena.rotation.xyzw = arena_rb.quaternion
def update(dt):

    # monkey.rotation.y += 35 * dt
    rat_camera.position = rat_rb.position
#     virtual_scene.camera.position.xyz = monkey.position.xyz
    arena.uniforms['playerPos'] = rat_rb.position
pyglet.clock.schedule(update)
#
#


@window.event
def on_draw():
    ##################
    # with framebuffer:
    #     with cube_shader:
    #         virtual_scene.draw360_to_texture(cube_texture)

    # ########################
    window.clear()
    with cube_shader:
        rc.clear_color(255, 0, 0)
        projector.projection.match_aspect_to_viewport()
        projector.projection.fov_y = 39
        with projector, light:

            arena.draw()
            # with cube_fbo as fbo:
            #     virtual_scene.draw360_to_texture(fbo.texture)
            #     projected_scene.draw()


pyglet.app.run()