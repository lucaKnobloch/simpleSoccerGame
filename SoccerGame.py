import sys
import time

import gl as gl
import glm as glm
import numpy as np
from OpenGL import GLUT as glut
from OpenGL.GL import shaders
from OpenGL.raw.GLUT import GLUT_KEY_LEFT, GLUT_KEY_RIGHT, GLUT_KEY_UP, GLUT_KEY_DOWN


class GameObject:
    def __init__(self, position=None, scale=None, gravity=None, color=None):
        self.position = position or glm.vec3(0.0)
        self.scale = scale or glm.vec3(1.0)
        self.velocity = glm.vec3(0.0)
        self.gravity = gravity or glm.vec3(0.0, 0.0, 0.0)
        self.color = color or glm.vec3(0, 1, 0)

    def get_transformation(self):
        transformation = glm.mat4x4()
        transformation = glm.translate(transformation, self.position)
        transformation = glm.scale(transformation, self.scale)
        return transformation

    def translate(self, x):
        self.position = glm.vec3(x)
        # Set the transform uniform to self.transform
        gl.glUniformMatrix4fv(transformation_location, 1, False, glm.value_ptr(self.get_transformation()))
        # Draw the cube with an element array.
        # When the last parameter in 'None', the buffer bound to the GL_ELEMENT_ARRAY_BUFFER will be used.
        gl.glDrawElements(gl.GL_TRIANGLES, 36, gl.GL_UNSIGNED_INT, None)

    def scaling(self, x):
        self.scale = glm.vec3(x)
        # Set the transform uniform to self.transform
        gl.glUniformMatrix4fv(transformation_location, 1, False, glm.value_ptr(self.get_transformation()))
        # Draw the cube with an element array.
        # When the last parameter in 'None', the buffer bound to the GL_ELEMENT_ARRAY_BUFFER will be used.
        gl.glDrawElements(gl.GL_TRIANGLES, 36, gl.GL_UNSIGNED_INT, None)

    def draw(self):
        gl.glUniform3fv(color_location, 1, glm.value_ptr(self.color))
        # Set the transform uniform to self.transform
        gl.glUniformMatrix4fv(transformation_location, 1, False, glm.value_ptr(self.get_transformation()))
        # Draw the cube with an element array.
        # When the last parameter in 'None', the buffer bound to the GL_ELEMENT_ARRAY_BUFFER will be used.
        gl.glDrawElements(gl.GL_TRIANGLES, 36, gl.GL_UNSIGNED_INT, None)


class Camera:
    def __init__(self, position=None, target=None, up=None):
        self.position = position or glm.vec3(0.0)
        self.target = target or glm.vec3(0.0, 0.0, 1.0)
        self.up = up or glm.vec3(0.0, 1.0, 0.0)

    def get_view(self):
        return glm.lookAt(self.position, self.target, self.up)


# Initialize GLUT ------------------------------------------------------------------|
glut.glutInit()
glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)

# Create a window
screen_size = glm.vec2(512, 512)
glut.glutCreateWindow("Soccer Game")
glut.glutReshapeWindow(int(screen_size.x), int(screen_size.y))

# set initial variables for the score
score = 0
passed_time = 0.0


# Set callback functions
def display():
    # compute the time which passed
    global passed_time
    delta_time = time.perf_counter() - passed_time
    passed_time += delta_time

    # Clear screen
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    gl.glUniformMatrix4fv(projection_location, 1, False, glm.value_ptr(perspective_projection))

    # Rotate the camera around the z-axis
    # camera_rotation = glm.rotate(glm.mat4x4(), glm.radians(time.perf_counter() * 42.0), glm.vec3(0.0, 1.0, 0.0))

    gl.glUniformMatrix4fv(view_location, 1, False, glm.value_ptr(camera.get_view()))

    # sets the direction of the player
    direction = glm.vec3(0.0)

    keyboard_interaction(direction)

    # update the velocity of the player
    player.position += player.velocity * delta_time
    player.translate(player.position)
    player.velocity *= 0.96

    # rounding the values to avoid issues with too small numbers
    ball.velocity.y = round(ball.velocity.y, 4)
    ball.velocity.x = round(ball.velocity.x, 4)
    ball.velocity.z = round(ball.velocity.z, 4)

    # player
    player.velocity.y = round(player.velocity.y, 4)
    player.velocity.x = round(player.velocity.x, 4)
    player.velocity.z = round(player.velocity.z, 4)

    check_collision(delta_time, direction)
    check_goal_collision(direction)
    # draw the objects
    ground.draw()
    # 0.0 0.5 0.0
    goal_left.draw()
    # 0.0 1.0 0.0
    goal_right.draw()
    # 0.0 1.0 0.0

    wall_left.draw()
    # 1.0 1.0 0.0

    wall_right.draw()
    # 1.0 1.0 0.0
    wall_side_right.draw()
    # 0.5 0.0 0.0
    wall_side_left.draw()
    # 0.5 0.0 0.0
    # color = (gl.GLfloat * 3)()
    # gl.glGetUniformfv(shader_program, color_location, color)
    # print(*color)
    wall_backside.draw()
    # 0.0 0.0 0.0
    obstacle.draw()

    player.draw()
    # 0.5 0.5 0.0

    ball.draw()
    # 0.0 0.0 1.0

    # Swap the buffer we just drew on with the one showing on the screen
    glut.glutSwapBuffers()


glut.glutDisplayFunc(display)
glut.glutIdleFunc(display)


def keyboard_interaction(direction):
    # modifies the direction via keyboard input
    if b'w' in pressed_keys:
        direction += glm.vec3(0, 0, 2)
    if b's' in pressed_keys:
        direction -= glm.vec3(0, 0, 2)
    if b'd' in pressed_keys:
        direction -= glm.vec3(2, 0, 0)
    if b'a' in pressed_keys:
        direction += glm.vec3(2, 0, 0)
    if b'e' in pressed_keys:
        direction += glm.vec3(0, 2, 0)
    if b'q' in pressed_keys:
        direction -= glm.vec3(0, 2, 0)
    # do the following if one of these keys are pressed
    if len(pressed_keys.intersection((b'w', b'a', b's', b'd'))) != 0:
        # set the speed of the player
        velocity = 8.0
        # set the direction of the player
        direction = glm.normalize(direction)
        player.velocity = direction * velocity


def check_collision(delta_time, direction, ):
    # check the collision with the ground or if the numbers gets too small
    if check_collision(ball, ground) or ball.position.y < 0.01:
        ball.position.y = 0.0
        ball.velocity *= 0.96

    # if ball is in the air gravity will decrease the height of the object
    else:
        ball.velocity += ball.gravity * delta_time

    ball.position += ball.velocity * delta_time
    ball.translate(ball.position)

    if check_collision(obstacle, ball):
        ball.position = glm.vec3(-5, 0, -10)
        ball.velocity *= 0

    if check_collision(obstacle, player):
        player.velocity = direction * -(glm.normalize(player.position) * 40.0)

    if check_collision(player, ball):
        # changes the direction of the ball + adds velocity
        ball.velocity = (glm.normalize(ball.position - player.position) * 7.0 - ball.gravity * 0.5)

    # check collision with the surrounding
    if check_collision(player, wall_right) or check_collision(player, wall_left) or \
            check_collision(player, wall_side_right) or check_collision(player, wall_side_left):
        # change the direction and velocity after collision
        player.velocity = direction * -(glm.normalize(player.position) * 40.0)

    # check collision player and goal right
    if check_collision(goal_right, player):
        # change the direction and velocity after collision
        player.velocity = direction * -(glm.normalize(goal_right.position - player.position) * 40.0)

    # check collision player goal left
    if check_collision(goal_left, player):
        player.velocity = direction * -(glm.normalize(goal_left.position - player.position) * 40.0)

def check_goal_collision(direction):
    # check collision with the goal
    if check_collision(ball, goal_left) or check_collision(ball, wall_right) \
            or check_collision(ball, wall_side_left) or check_collision(ball, wall_side_right):
        # change the direction and velocity after collision
        ball.velocity = direction * -(glm.normalize(ball.position) * 20.0)

    if goal_left.position.x < ball.position.x < goal_right.position.x and ball.position.z > goal_right.position.z:
        global score
        score += 1
        ball.position = glm.vec3(-5, 0, -10)
        ball.velocity *= 0.0

    if ball.position.z < wall_backside.position.z or ball.position.z > wall_right.position.z or ball.position.z > wall_left.position.z:
        ball.position = glm.vec3(-5, 0, -10)
        ball.velocity *= 0


# adds the possibility to increase / decrease the windows of the game and it resize
def resize(width, height):
    gl.glViewport(0, 0, width, height)
    screen_size.x = width
    screen_size.y = height
    global perspective_projection
    perspective_projection = glm.perspective(glm.radians(45.0), screen_size.x / screen_size.y, 0.1, 100.0)


# activate the function
glut.glutReshapeFunc(resize)


def check_collision(object1, object2):  # AABB - AABB collision
    # Collision x-axis?
    collision_x = object1.position.x + (object1.scale.x * 2) >= object2.position.x and object2.position.x + (
            object2.scale.x * 2) >= object1.position.x

    #  Collision y-axis?
    collision_y = object1.position.y + (object1.scale.y * 2) >= object2.position.y and object2.position.y + (
            object2.scale.y * 2) >= object1.position.y

    #  Collision z-axis?
    collision_z = object1.position.z + (object1.scale.z * 2) >= object2.position.z and object2.position.z + (
            object2.scale.z * 2) >= object1.position.z

    # Collision only if on all three axes
    return collision_x and collision_y and collision_z


# creates a set for the keys to be pressed at the same time
pressed_keys = set()


# Callback for any keyboard up (when you release the key) input that has an ASCII equivalent
def keyboard_up_input(key, x, y):
    pressed_keys.remove(key)


# enables the user to change the position of the camera via keyboard input
def handle_special_keypress(key, x, y):
    if key == GLUT_KEY_LEFT and not camera.position.x == 24:
        camera.position += glm.vec3(10.0, 0.0, 0.0)

    if key == GLUT_KEY_RIGHT and not camera.position.x == -26:
        camera.position -= glm.vec3(10.0, 0.0, 0.0)

    if key == GLUT_KEY_UP and not camera.position.y == 60:
        camera.position += glm.vec3(0.0, 10.0, 0.0)

    if key == GLUT_KEY_DOWN and not camera.position.y == 0:
        camera.position -= glm.vec3(0.0, 10.0, 0.0)


glut.glutKeyboardUpFunc(keyboard_up_input)
glut.glutSpecialFunc(handle_special_keypress)


def keyboard_input(key, x, y):
    pressed_keys.add(key)

    if key == b'-':
        player.scale -= glm.vec3(0.1)
        player.scaling(player.scale)

    if key == b'+':
        player.scale += glm.vec3(0.1)
        player.scaling(player.scale)

    if key == b'r':
        ball.position = glm.vec3(-5, 0, -10)
        ball.velocity *= 0

    if key == b'\x1b':
        print("The score is ", score)
        sys.exit()


glut.glutKeyboardFunc(keyboard_input)

# Creating a Shader Program -------------------------------------------------------|
# Compile shaders [shorthand]
vertex_shader = shaders.compileShader("""
attribute vec3 position;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 transformation;
uniform vec3 color;

varying vec3 frag_color;

void main()
{
    //  Because the transformation matrix is 4x4, we have to construct a vec4 from position, so we an multiply them
    vec4 pos = vec4(position, 1.0);
    gl_Position = projection * view * transformation * pos;
    frag_color = color;
}
""", gl.GL_VERTEX_SHADER)

fragment_shader = shaders.compileShader("""
varying vec3 frag_color;

void main()
{
    gl_FragColor = vec4(frag_color, 1.0);
}
""", gl.GL_FRAGMENT_SHADER)

# Compile the program [shorthand]
shader_program = shaders.compileProgram(vertex_shader, fragment_shader)

# Set the program we just created as the one in use
gl.glUseProgram(shader_program)

# Creating Data Buffers -----------------------------------------------------------|

# Create the vertex data. It is 8 3D-coordinates (corners of a square)
vertex_data = np.array(
    [
        (1, 1, 1), (-1, 1, 1), (-1, -1, 1), (1, -1, 1),
        (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1),
    ],
    dtype=np.float32
)
# Get properties of the data container
data_count = vertex_data.shape[1]  # 3, the count of floats per vertex
data_stride = vertex_data.strides[0]  # 12, bytes to skip for the next vertex data
data_offset = gl.ctypes.c_void_p(0)  # 0, beginning offset

# Request a buffer slot from GPU
vertex_buffer = gl.glGenBuffers(1)

# gets the position location
position_location = gl.glGetAttribLocation(shader_program, "position")

# Describe how the position attribute will parse this buffer
# 1. First, tell where the data will be read from
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vertex_buffer)
# 2. Second, tell how the data should be read and where to be sent for this case, therefore 0)
gl.glVertexAttribPointer(position_location, data_count, gl.GL_FLOAT, False, data_stride, data_offset)

# Enable the attribute from position_location
gl.glEnableVertexAttribArray(position_location)

# Send vertex data (which is on CPU memory) to vertex buffer (which is on GPU memory)
gl.glBufferData(gl.GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, gl.GL_STATIC_DRAW)

# Create the element data. It is an indexing of the vertex data. The indexes will be grouped by 3 to create triangles.
element_data = np.array(
    [
        0, 1, 2, 2, 3, 0,
        0, 3, 4, 4, 5, 0,
        0, 5, 6, 6, 1, 0,
        1, 6, 7, 7, 2, 1,
        7, 4, 3, 3, 2, 7,
        4, 7, 6, 6, 5, 4,
    ],
    dtype=np.uint32
)

element_buffer = gl.glGenBuffers(1)

# Unlike other buffers, it is bound to the GL_ELEMENT_ARRAY_BUFFER
gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, element_buffer)
gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, element_data.nbytes, element_data, gl.GL_STATIC_DRAW)

# Get the transformation location
transformation_location = gl.glGetUniformLocation(shader_program, "transformation")

# Get the view location
view_location = gl.glGetUniformLocation(shader_program, "view")

# Get the projection location
projection_location = gl.glGetUniformLocation(shader_program, "projection")

# Get the color location
color_location = gl.glGetUniformLocation(shader_program, "color")

# Configure GL -----------------------------------------------------------------------|

# Enable depth test
gl.glEnable(gl.GL_DEPTH_TEST)

# Accept fragment if it is closer to the camera than the former one
gl.glDepthFunc(gl.GL_LESS)

# Create Camera and Game Objects -----------------------------------------------------|

perspective_projection = glm.perspective(glm.radians(45.0), screen_size.x / screen_size.y, 0.1, 100.0)

camera = Camera(position=glm.vec3(4.0, 30.0, -40.0), target=glm.vec3(0.0))

player = (
    GameObject(
        position=glm.vec3(0, 0, -10),
        scale=glm.vec3(1),
        color=glm.vec3(0.5, 0.5, 0.0)
    )
)

ground = (
    GameObject(
        position=glm.vec3(0, -101, 0),
        scale=glm.vec3(100),
        color=glm.vec3(0.0, 0.5, 0.0)
    )
)

ball = (
    GameObject(
        position=glm.vec3(-5, 0, -10),
        scale=glm.vec3(1),
        gravity=glm.vec3(0.0, -10.0, 0.0),
        color=glm.vec3(0.0, 0.0, 1.0)
    )
)

goal_left = (
    GameObject(
        position=glm.vec3(-5, 0, 30),
        scale=glm.vec3(1),
        color=glm.vec3(0.0, 1.0, 0.0)
    )
)
goal_right = (
    GameObject(
        position=glm.vec3(5, 0, 30),
        scale=glm.vec3(1),
        color=glm.vec3(0.0, 1.0, 0.0)
    )
)

wall_left = (
    GameObject(
        position=glm.vec3(15, 0, 30),
        scale=glm.vec3(9.0, 1.0, 1.0),
        color=glm.vec3(1.0, 1.0, 0.0)
    )
)

wall_right = (
    GameObject(
        position=glm.vec3(-15, 0, 30),
        scale=glm.vec3(-9.0, 1.0, 1.0),
        color=glm.vec3(1.0, 1.0, 0.0)
    )
)
wall_side_right = (
    GameObject(
        position=glm.vec3(-25, 0, 6),
        scale=glm.vec3(1.0, 1.0, 25.0),
        color=glm.vec3(0.5, 0.0, 0.0)
    )
)

wall_side_left = (
    GameObject(
        position=glm.vec3(25, 0, 6),
        scale=glm.vec3(1.0, 1.0, 25.0),
        color=glm.vec3(0.5, 0.0, 0.0)
    )
)

wall_backside = (
    GameObject(
        position=glm.vec3(0, 0, -18),
        scale=glm.vec3(24.0, 1.0, 1.0),
        color=glm.vec3(0.0, 0.0, 0.0)
    )
)

obstacle = (
    GameObject(
        position=glm.vec3(0, 0, 0),
        scale=glm.vec3(1.5, 1.5, 1.5),
        color=glm.vec3(0.0, 0.0, 0.0)
    )
)

# Start the main loop
glut.glutMainLoop()
