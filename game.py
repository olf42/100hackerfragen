import pygame
import pygame.event
from pygame.locals import *
import time
import os
import os.path
from PIL import Image

pygame.mixer.init(44200, -16, 2, 512)
pygame.init()

FONT = None
LINELEN = 32
BG = None
BUZZED = False

MONO = 1
GRAYSCALE = 2

def buzz(side):
    if side == 'A':
        posy = 0
    elif side == 'B':
        posy = 400
    play_sound('sounds/buzz.wav')
    pygame.draw.rect(screen, (0,255,0), (posy,430,400,50))
    pygame.display.flip()

def reset_buzz_state():
    pygame.draw.rect(screen, (0,0,0), (0,430,800,50))
    pygame.display.flip()


def play_sound(fn):
    pygame.mixer.Sound(fn).play()


def clear():
    # clear the screen
    pygame.draw.rect(screen, (0,0,0), (0,0,800,480))
    pygame.display.flip()


def load_image(fn):
    # loads image, convert to grayscale and resize to screen size
    img = Image.open(fn).convert('L')
    if img.size != (800,480):
        img = img.resize((800,480))
    print("image {} loaded".format(fn))
    return img


def show_image(fn, mode=MONO):
    clear()
    img = load_image(fn)
    for x in range(0, 800, 6):
        for y in range(0, 480, 6):
            px = img.getpixel((x,y))
            if mode == MONO:
                if px < 100:
                    px = 255
                else:
                    px = 0
            pygame.draw.rect(screen, (0, px, 0), (x,y,3,3))
        time.sleep(0.005)
        pygame.display.flip()


def print_line(line, text=(LINELEN - 6) * '_', points='--', anim=True):
    """Prints text in the given line"""
    previmg = None
    print("printing line")
    if anim:
        REVEAL_EFFECT_1.play()
    for pos in range(LINELEN):
        display_points = '--'
        if anim and pos == LINELEN-1:
            display_points = points
            REVEAL_EFFECT_2.play()
        txtpart = text[:pos]    
        prtxt = str(line)+'.' + txtpart + (LINELEN - 6 - len(txtpart)) * '_' + ' ' + display_points
        img = FONT.render(prtxt.upper(), 1, (0,255,0))
        if previmg is not None:
            previmg.fill((0,0,0))
            BG.blit(previmg, (40,50*line))
        BG.blit(img, (40, 50*line))
        screen.blit(BG, (0, 0))
        previmg = img
        if anim:
            pygame.display.flip()
            time.sleep(0.05)
    if not anim:
        pygame.display.flip()


round_id_to_num_of_rounds = lambda x: -x+7


def prepare_round(round_id):
    for x in range(1, round_id_to_num_of_rounds(round_id) + 1):
        print_line(x, anim=False)


PRINTLINE = USEREVENT+1
TIMERTICK = USEREVENT+2
REVEAL_EFFECT_1 = pygame.mixer.Sound('sounds/reveal.wav')
REVEAL_EFFECT_2 = pygame.mixer.Sound('sounds/reveal2.wav')

#screen = pygame.display.set_mode((800, 480), pygame.FULLSCREEN)
screen = pygame.display.set_mode((800, 480))
pygame.mouse.set_visible(False)
pygame.display.set_caption('Hackerspaceduell')
pygame.time.set_timer(TIMERTICK, 250)
FONT = pygame.font.SysFont('myfont', 32)
# Fill background
BG = pygame.Surface(screen.get_size())
BG = BG.convert()
BG.fill((10, 10, 10))
prepare_round(1)


def post_print_line_event(line, text, points):
    prl_event = pygame.event.Event(PRINTLINE, line=line, text=text, points=points)
    print("posting event")
    pygame.event.post(prl_event) 
    
    
def handle_print_line_event(event):
    print_line(event.line, event.text, event.points)
    screen.blit(BG, (0, 0))
    pygame.display.flip()


def check_for_message():
    rm_file = False
    if not os.path.isfile('message'):
        return
    with open('message') as msgfile:
        msg = msgfile.read().strip()
        if msg:
            post_print_line_event(int(msg[0]), msg[1:-2], msg[-2:])
            rm_file = True
    if rm_file:
        os.unlink('message')


def main():
    buzzed = False
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == PRINTLINE:
                handle_print_line_event(event)
            if event.type == TIMERTICK:
                print("checking")
                check_for_message()
            if event.type == KEYDOWN:
                if event.key == K_q:
                    return
                if event.key == K_f:
                    pygame.display.toggle_fullscreen()
                if event.key == K_a:
                    if not buzzed:
                        buzzed = True
                        buzz('A')
                if event.key == K_b:
                    if not buzzed:
                        buzzed = True
                        buzz('B')
                if event.key == K_r:
                    buzzed = False
                    reset_buzz_state()                
                if event.key == K_d:
                    show_image('images/datenknoten.jpg')
                if event.key == K_p:
                    show_image('images/pesthoernchen.jpg')
                if event.key == K_v:
                    play_sound('sounds/tetris.wav')
                    show_image('images/putin.jpg', GRAYSCALE)
                if event.key == K_m:
                    play_sound('sounds/merkel.wav')
                    show_image('images/merkel.jpg', GRAYSCALE)
if __name__ == '__main__': main()