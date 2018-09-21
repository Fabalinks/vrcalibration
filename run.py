"""
This code runs as to set up the script to run the VR in ratcave
"""

import pyglet
import ratcave as rc
from ratcave.resources import cube_shader, default_shader
from natnetclient import NatClient

def get_screen(idx):
    """These Three lines send the data to the monitor next to the main monitor ( harder to recognize)"""
    platform = pyglet.window.get_platform()
    display = platform.get_default_display()
    screens = display.get_screens()
    return screens[idx]


#gettign positions of rigib bodies in real time
client = NatClient()
arena_rb = client.rigid_bodies['Arena']
rat_rb = client.rigid_bodies['Gerbil']


window = pyglet.window.Window(resizable=True, fullscreen=True, screen=get_screen(1))  # Opening the basic pyglet window


# Load Arena
arena_filename = 'calibration_assets/arena2.obj'# we are taking an arena which has been opened in blender and rendered to 3D after scanning it does not have flipped normals
arena_reader = rc.WavefrontReader(arena_filename)  # loading the mesh of the arena thought a wavefrontreader
arena = arena_reader.get_mesh("Arena", position=arena_rb.position)  # making the wafrotn into mesh so we can extrude texture ont top of it.
arena.uniforms['diffuse'] = 1., 1., 1.  # addign a white diffuse material to the arena
arena.rotation = arena.rotation.to_quaternion() # we also need to get arena's rotation not just xyz so it can be tracked and moved if it gets bumped

# Load the projector as a Ratcave camera, set light to its position
projector = rc.Camera.from_pickle('calibration_assets/projector.pkl')  # settign the pickle filled of the projector, which gives us the coordinates of where the projector is
projector.projection = rc.PerspectiveProjection(fov_y =41.5, aspect=1.777777778)
light = rc.Light(position=projector.position)

## Make Virtual Scene ##
virtual_arena = arena_reader.get_mesh('Arena')
wall = arena_reader.get_mesh("Plane")
wall.parent = virtual_arena
rat_camera = rc.Camera(projection=rc.PerspectiveProjection(aspect=1, fov_y=90, z_near=.001), position=rat_rb.position)  # settign the camera to be on top of the rats head
virtual_scene = rc.Scene(meshes=[wall, virtual_arena], light=light, camera=rat_camera, bgColor=(0, 0, 255))  # seetign aset virtual scene to be projected as the mesh of the arena
virtual_scene.gl_states.states = virtual_scene.gl_states.states[:-1]

checkerboard_texture = rc.Texture.from_image(rc.resources.img_uvgrid)  # or 'assets/wood.jpg'
wall.textures.append(checkerboard_texture)
virtual_arena.textures.append(checkerboard_texture)
virtual_arena.uniforms['flat_shading'] = True
wall.uniforms['flat_shading'] = True



## Make Cubemapping work on arena
cube_texture = rc.TextureCube(width=4096, height=4096)  # usign cube mapping to import eh image on the texture of the arena
framebuffer = rc.FBO(texture=cube_texture) ## creating a fr`amebuffer as the texture - in tut 4 it was the blue screen
arena.textures.append(cube_texture)


# updating the posiotn of the arena in xyz and also in rotational perspective
def update(dt):
    """main update function: put any movement or tracking steps in here, because it will be run constantly!"""
    rat_camera.position = rat_rb.position  # setting the actual osiont of the rat camera to vbe of the rat position
    arena.uniforms['playerPos'] = rat_rb.position
    arena.position, arena.rotation.xyzw = arena_rb.position, arena_rb.quaternion
    virtual_arena.position, virtual_arena.rotation = arena.position, arena.rotation
pyglet.clock.schedule(update)  # making it so that the app updates in real time


@window.event
def on_draw():

    ## Render virtual scene onto cube texture
    with framebuffer:
        with cube_shader:
            virtual_scene.draw360_to_texture(cube_texture)

    ## Render real scene onto screen
    window.clear()
    with cube_shader:  # usign cube shader to create the actuall 6 sided virtual cube which gets upated with position and angle of the camera/viewer
        rc.clear_color(255, 0, 0)
          # why is it here 39? e
        with projector, light:
            arena.draw()

# actually run everything.
pyglet.app.run()