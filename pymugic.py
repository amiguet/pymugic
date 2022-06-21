"""
PyTeapot module for drawing rotating cube using OpenGL as per
quaternion or yaw, pitch, roll angles received over serial port.

Modified to get data from MUGIC via OSC
"""

import time
import pygame
import math
from OpenGL.GL import (GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST, GL_LEQUAL,
                       GL_MODELVIEW, GL_NICEST, GL_PERSPECTIVE_CORRECTION_HINT, GL_PROJECTION,
                       GL_QUADS, GL_RGBA, GL_SMOOTH, GL_UNSIGNED_BYTE, glBegin, glClear,
                       glClearColor, glClearDepth, glColor3f, glDepthFunc, glDrawPixels, glEnable,
                       glEnd, glHint, glLoadIdentity, glMatrixMode, glRasterPos3d, glRotatef,
                       glShadeModel, glTranslatef, glVertex3f, glViewport)
from OpenGL.GLU import gluPerspective
from pygame.locals import DOUBLEBUF, KEYDOWN, K_ESCAPE, OPENGL, QUIT
from oscpy.server import OSCThreadServer

# True for using quaternions, false for using Euler angles; quaternions seems to work better
useQuat = True   
# Osc port
port = 4000
# GUI window size
window_size = (1280, 960)
# Datagram signature
types = [float if t == 'f' else int for t in 'fffffffffffffffffiiiiifi']
# Datagram structure
datagram = (
    'AX', 'AY', 'AZ', # accelerometer
    'EX', 'EY', 'EZ', # Euler angles
    'GX', 'GY', 'GZ', # Gyrometer
    'MX', 'MY', 'MZ', # Magnetometer
    'QW', 'QX', 'QY', 'QZ', # Quaternions
    'Battery', 'mV', # Battery state
    'calib_sys', 'calib_gyro', 'calib_accel', 'calib_mag', # Calibration state
    'seconds', # since last reboot
    'seqnum', # messagesequence number
)

osc = OSCThreadServer()
sock = osc.listen(address='0.0.0.0', port=port, default=True)
mugic = None
dirty = False

@osc.address(b'/mugicdata')
def callback(*values):

    global mugic
    global dirty

    values = [t(v) for t, v in zip(types, values)]

    mugic = {
        k: v
        for k, v in zip(datagram, values)
    }

    dirty = True


def main():
    global dirty
    video_flags = OPENGL | DOUBLEBUF
    while not mugic:
        print('Waiting for incoming data...')
        time.sleep(.5)
    print('Got first datagram, launching GUI :-)')
    pygame.init()
    pygame.display.set_mode(window_size, video_flags)
    pygame.display.set_caption("PyMugic IMU orientation visualization")
    resizewin(*window_size)
    init()
    frames = 0
    ticks = pygame.time.get_ticks()
    while 1:
        event = pygame.event.poll()
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            break
        if dirty: 
            draw()
            pygame.display.flip()
            dirty = False
            frames += 1
        else:
            time.sleep(.01)
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

    drawText((-2.6, 1.8, 2), f"PyMugic ({mugic['Battery']}%, {mugic['mV']}mV)", 35)
    drawText((-2.6, -2, 2), "Press Escape to exit.", 24)
    drawText((-2.6, -1.6, 2), f"Calibration: {mugic['calib_sys']}, {mugic['calib_gyro']}, {mugic['calib_accel']}, {mugic['calib_mag']}", 24)

    if(useQuat):
        w, nx, ny, nz = [mugic[k] for k in ['QW','QX','QY','QZ']]
        [yaw, pitch , roll] = quat_to_ypr([w, nx, ny, nz])
        drawText((-2.6, -1.8, 2), "(Using quaternions) Yaw: %f, Pitch: %f, Roll: %f" %(yaw, pitch, roll), 24)
        glRotatef(2 * math.acos(w) * 180.00/math.pi, -1 * nx, nz, ny)
    else:
        [yaw, pitch , roll] = [mugic[k] for k in ['EX','EY','EZ']]
        drawText((-2.6, -1.8, 2), "Yaw: %f, Pitch: %f, Roll: %f" %(yaw, pitch, roll), 24)
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
