import pygame
import pygame.event
from pygame.locals import *
import time
import os
import os.path
from PIL import Image

from multiprocessing import Process

from gameweb import app

webserver = Process(target=app.run, kwargs=dict(host='0.0.0.0'))
webserver.start()

pygame.mixer.init(44100, -16, 2, 512)
pygame.init()

FONT = None
LINELEN = 32
BG = None
BUZZED = False
FG = (0,255,0)
RED = (255,0,0)
MONO = 1
GRAYSCALE = 2
CURRENT_SLOTS = 0
XDATA = """###         ###          
 ###       ###
  ###     ###        
   ###   ###         
    ### ###          
     #####           
      ###             
     #####           
    ### ###          
   ###   ###
  ###     ###
 ###       ###
###         ###""".splitlines()

def buzz(side):
    if side == 'A':
        posx = 0
    elif side == 'B':
        posx = 1920/2
    play_sound('sounds/buzz.wav')
    pygame.draw.rect(screen, (0,255,0), (posx,1080-80,1920/2,1080))
    pygame.display.flip()

def reset_buzz_state():
    pygame.draw.rect(screen, (0,0,0), (0,1080-80,1920,1080))
    pygame.display.flip()


def play_sound(fn):
    pygame.mixer.Sound(fn).play()


def clear():
    # clear the screen
    pygame.draw.rect(screen, (0,0,0), (0,0,1920,1080))
    pygame.display.flip()


def load_image(fn):
    # loads image, convert to grayscale and resize to screen size
    img = Image.open(fn).convert('L')
    if img.size != (1920,1080):
        img = img.resize((1920,1080))
    return img


def add_x(pos, times):
    if pos == 'L':
        xstart = 50
        xinc_mod = 1
    elif pos == 'R':
        xstart = 1920 - 50
        xinc_mod = -1
    ystart = 800

    for xoff in range(times):
        y = ystart
        xoffset = 16*8*xoff
        for line in XDATA:
            x = xstart + (xoffset * xinc_mod)
            for c in line:
                if c == '#':
                    pygame.draw.rect(screen, RED, (x,y,6,6))
                x += (xinc_mod * 8)
            y += 8

    pygame.display.flip()



def show_image(fn, mode=MONO, anim=False):
    clear()
    img = load_image(fn)
    for x in range(0, 1920, 7):
        for y in range(0, 1080, 7):
            px = img.getpixel((x,y))
            if mode == MONO:
                if px < 100:
                    px = 255
                else:
                    px = 0
            pygame.draw.rect(screen, (0, px, 0), (x,y,6,6))
        if anim:
            pygame.display.flip()
    pygame.display.flip()


def print_line(line, text=(LINELEN - 6) * '_', points='--', anim=True):
    """Prints text in the given line"""
    if line > CURRENT_SLOTS:
        return
    previmg = None
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
            BG.blit(previmg, (40,120*line))
        BG.blit(img, (40, 120*line))
        screen.blit(BG, (0, 0))
        previmg = img
        if anim:
            pygame.display.flip()
            time.sleep(0.05)
    if not anim:
        pygame.display.flip()


def prepare_round(num):
    global CURRENT_SLOTS
    show_image('images/pig{}.jpg'.format(num), GRAYSCALE, True)
    for x in range(num):
        play_sound('sounds/pig.wav')
        time.sleep(0.5)
    time.sleep(4)
    clear()
    BG.fill((0, 0, 0))
    slots = {1:6, 2:5, 3:4}[num]
    CURRENT_SLOTS = slots
    for x in range(0, slots):
        print_line(x+1, anim=False)


PRINTLINE = USEREVENT+1
TIMERTICK = USEREVENT+2
REVEAL_EFFECT_1 = pygame.mixer.Sound('sounds/reveal.wav')
REVEAL_EFFECT_2 = pygame.mixer.Sound('sounds/reveal2.wav')

screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
#screen = pygame.display.set_mode((1920, 1080))
pygame.mouse.set_visible(False)
pygame.display.set_caption('Hackerspaceduell')
pygame.time.set_timer(TIMERTICK, 250)
FONT = pygame.font.SysFont('myfont', 80)
# Fill background
BG = pygame.Surface(screen.get_size())
BG = BG.convert()
BG.fill((0, 0, 0))

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


class Team(object):
    points = 0
    wrong = 0
    pos = ''

    def __init__(self, name, pos):
        self.pos = pos
        self.name = name
        self.points = 0
        self.wrong = 0

    def wrong_answer(self):
        play_sound('sounds/fail.wav')
        self.wrong += 1
        add_x(self.pos, self.wrong)




class Game(object):
    team_a = None
    team_b = None
    team_on_turn = None

    def __init__(self):
        self.team_a = Team('Left team', 'L')
        self.team_b = Team('Right team', 'R')

    def team_on_turn_answered_wrong(self):
        self.team_on_turn.wrong_answer()




def main():
    game = Game()
    buzzed = False
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                webserver.terminate()
                return
            if event.type == PRINTLINE:
                handle_print_line_event(event)
            if event.type == TIMERTICK:
                check_for_message()
            if event.type == KEYDOWN:
                if event.key == K_q:
                    webserver.terminate()
                    return
                if event.key == K_f:
                    pygame.display.toggle_fullscreen()
                if event.key == K_a:
                    if not buzzed:
                        buzzed = True
                        buzz('A')
                        game.team_on_turn = game.team_a
                if event.key == K_b:
                    if not buzzed:
                        buzzed = True
                        buzz('B')
                        game.team_on_turn = game.team_b
                if event.key == K_r:
                    buzzed = False
                    reset_buzz_state()                


                if event.key == K_x:
                    game.team_on_turn_answered_wrong()
                if event.key == K_1:
                    prepare_round(1)
                if event.key == K_2:
                    prepare_round(2)
                if event.key == K_3:
                    prepare_round(3)


                if event.key == K_d:
                    prev = screen.copy()
                    play_sound('sounds/ccc.wav')
                    show_image('images/datenknoten.jpg')
                if event.key == K_w:

                    prev = screen.copy()
                    play_sound('sounds/wat.wav')
                    show_image('images/wat.jpg', GRAYSCALE)
                if event.key == K_c:
                    prev = screen.copy()
                    play_sound('sounds/cyber.wav')
                    def cyb_to_prev():
                        show_image('images/cyber.jpg', GRAYSCALE)
                        pygame.display.flip()
                        screen.blit(prev, (0,0))
                        pygame.display.flip()
                    def prev_to_cyb():
                        screen.blit(prev, (0,0))
                        pygame.display.flip()
                        show_image('images/cyber.jpg', GRAYSCALE)
                        pygame.display.flip()
                    prev_to_cyb()
                    time.sleep(0.1)
                    cyb_to_prev()
                    time.sleep(0.2)
                    prev_to_cyb()
                    time.sleep(0.1)
                    cyb_to_prev()
                    time.sleep(0.2)
                    prev_to_cyb()
                    time.sleep(0.5)
                    cyb_to_prev()
                    time.sleep(0.3)
                    prev_to_cyb()
                    time.sleep(0.1)
                    cyb_to_prev()
                    time.sleep(0.5)

                    pygame.mixer.fadeout(300)


                if event.key == K_p:

                    prev = screen.copy()
                    play_sound('sounds/modem.wav')
                    show_image('images/pesthoernchen.jpg')
                if event.key == K_v:

                    prev = screen.copy()
                    play_sound('sounds/tetris.wav')
                    show_image('images/putin.jpg', GRAYSCALE)
                if event.key == K_m:

                    prev = screen.copy()
                    play_sound('sounds/merkel.wav')
                    show_image('images/merkel.jpg', GRAYSCALE)                

                if event.key == K_k:
                    prev = screen.copy()
                    #play_sound('sounds/merkel.wav')
                    show_image('images/facepalm.jpg', GRAYSCALE)
                if event.key == K_l:
                    prev = screen.copy()
                    play_sound('sounds/lol.wav')
                    show_image('images/lol.jpg', GRAYSCALE)                
                if event.key == K_n:
                    prev = screen.copy()
                    play_sound('sounds/nyan.wav')
                    show_image('images/nyan.jpg', GRAYSCALE)

            if event.type == KEYUP:
                if event.key in (K_n,K_l, K_k, K_d, K_w, K_p, K_v, K_m, K_c):
                    screen.blit(prev, (0,0))
                    pygame.display.flip()
                    pygame.mixer.fadeout(300)

print("""

WELCOME TO 100HACKERFRAGEN SCREEN

Keys:

  Game conrols:

    a ... Left Buzzer
    b ... Right Buzzer
    r ... Reset Buzzer

    1,2,3 ... Init round

    x ... wrong answer for last buzzed team

    q ... quit
    f ... toggle fullscreen


  Memes (Press and hold):

    d ... ccc
    w ... WAT
    c ... CYBER
    p ... BTX
    v ... putin
    m ... merkel
    k ... facepalm
    l ... lol
    n ... nyancat





    """)




if __name__ == '__main__': main()