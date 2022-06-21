"""
PyTeapot module for drawing rotating cube using OpenGL as per
quaternion or yaw, pitch, roll angles received over serial port.

Modified to get data from MUGIC via OSC
"""

import time
import pygame
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *
from oscpy.server import OSCThreadServer

useQuat = True   # set true for using quaternions, false for using Euler angles
port = 4000

types = [float if t == 'f' else int for t in 'fffffffffffffffffiiiiifi']

datagram = (
    'AX', 'AY', 'AZ', # accelerometer
    'EX', 'EY', 'EZ', # Euler angles
    'GX', 'GY', 'GZ', # Gyrometer
    'MX', 'MY', 'MZ', # Magnetometer
    'QW', 'QX', 'QY', 'QZ', # Quaternions
    'Battery', 'mV', # Battery state
    'calib_acc', 'calib_gyr', 'calib_mag', 'calib_X', # Calibration state
    'seconds', # since last reboot
    'seqnum', # messagesequence number
)

osc = OSCThreadServer()
sock = osc.listen(address='0.0.0.0', port=port, default=True)
mugic = None

@osc.address(b'/mugicdata')
def callback(*values):

    global mugic

    values = [t(v) for t, v in zip(types, values)]

    mugic = {
        k: v
        for k, v in zip(datagram, values)
    }


def main():
    video_flags = OPENGL | DOUBLEBUF
    while not mugic:
        print('Waiting for incoming data...')
        time.sleep(.5)
    pygame.init()
    screen = pygame.display.set_mode((640, 480), video_flags)
    pygame.display.set_caption("PyMugic IMU orientation visualization")
    resizewin(640, 480)
    init()
    frames = 0
    ticks = pygame.time.get_ticks()
    while 1:
        event = pygame.event.poll()
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            break
        draw()
        pygame.display.flip()
        frames += 1
    print("fps: %d" % ((frames*1000)/(pygame.time.get_ticks()-ticks)))


def resizewin(width, height):
    """
    For resizing window
    """
    if height == 0:
        height = 1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0*width/height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def init():
    glShadeModel(GL_SMOOTH)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)



def draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0, 0.0, -7.0)

    drawText((-2.6, 1.8, 2), f"PyMugic ({mugic['Battery']}%, {mugic['mV']}mV)", 18)
    drawText((-2.6, -2, 2), "Press Escape to exit.", 16)
    drawText((-2.6, -1.6, 2), f"Calibration: {mugic['calib_acc']}, {mugic['calib_gyr']}, {mugic['calib_mag']}, {mugic['calib_X']}", 16)

    if(useQuat):
        w, nx, ny, nz = [mugic[k] for k in ['QW','QX','QY','QZ']]
        [yaw, pitch , roll] = quat_to_ypr([w, nx, ny, nz])
        drawText((-2.6, -1.8, 2), "Yaw: %f, Pitch: %f, Roll: %f" %(yaw, pitch, roll), 16)
        glRotatef(2 * math.acos(w) * 180.00/math.pi, -1 * nx, nz, ny)
    else:
        [yaw, pitch , roll] = [mugic[k] for k in ['EX','EY','EZ']]
        drawText((-2.6, -1.8, 2), "Yaw: %f, Pitch: %f, Roll: %f" %(yaw, pitch, roll), 16)
        glRotatef(-roll, 0.00, 0.00, 1.00)
        glRotatef(pitch, 1.00, 0.00, 0.00)
        glRotatef(yaw, 0.00, 1.00, 0.00)

    # trying to represent acceleration somehow...
    # glTranslatef(0+mugic['AX']/10, 0.0+mugic['AY']/10, mugic['AZ']/10)
    glBegin(GL_QUADS)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(1.0, 0.2, -1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(1.0, 0.2, 1.0)

    glColor3f(1.0, 0.5, 0.0)
    glVertex3f(1.0, -0.2, 1.0)
    glVertex3f(-1.0, -0.2, 1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(1.0, -0.2, -1.0)

    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(-1.0, -0.2, 1.0)
    glVertex3f(1.0, -0.2, 1.0)

    glColor3f(1.0, 1.0, 0.0)
    glVertex3f(1.0, -0.2, -1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(1.0, 0.2, -1.0)

    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(-1.0, -0.2, 1.0)

    glColor3f(1.0, 0.0, 1.0)
    glVertex3f(1.0, 0.2, -1.0)
    glVertex3f(1.0, 0.2, 1.0)
    glVertex3f(1.0, -0.2, 1.0)
    glVertex3f(1.0, -0.2, -1.0)
    glEnd()


def drawText(position, textString, size):
    font = pygame.font.SysFont("Courier", size, True)
    textSurface = font.render(textString, True, (255, 255, 255, 255), (0, 0, 0, 255))
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    glRasterPos3d(*position)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

def quat_to_ypr(q):
    yaw   = math.atan2(2.0 * (q[1] * q[2] + q[0] * q[3]), q[0] * q[0] + q[1] * q[1] - q[2] * q[2] - q[3] * q[3])
    pitch = -math.asin(2.0 * (q[1] * q[3] - q[0] * q[2]))
    roll  = math.atan2(2.0 * (q[0] * q[1] + q[2] * q[3]), q[0] * q[0] - q[1] * q[1] - q[2] * q[2] + q[3] * q[3])
    pitch *= 180.0 / math.pi
    yaw   *= 180.0 / math.pi
    yaw   -= -0.13  # Declination at Chandrapur, Maharashtra is - 0 degress 13 min
    roll  *= 180.0 / math.pi
    return [yaw, pitch, roll]


if __name__ == '__main__':
    main()
