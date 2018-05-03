import pygame
import pygame.event
from pygame.locals import *
import time
import os
import os.path
from PIL import Image

from multiprocessing import Process

from gameweb import app
import ctypes

K_a = 267  # /
K_b = 268  # *    
K_o = 269  # -    
K_s = 9 # tab
K_x = 256 # 0 
K_y = 271 # enter

# don't let windows ui scale setting affect pygame screen content
try:
    ctypes.windll.user32.SetProcessDPIAware()
except AttributeError:
    pass

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
XDATA = """  ###     ###
   ###   ###         
    ### ###          
     #####           
      ###             
     #####           
    ### ###          
   ###   ###
  ###     ###
""".splitlines()


MEMES = []

for dirname, dirnames, filenames in os.walk('./memes'):
    if dirname.startswith('./memes/'):
        if filenames:
            MEMES.append(dirname[-1])

print(MEMES)

def buzz(side, silent=False):
    if side == 'A':
        posx = 0
    elif side == 'B':
        posx = 1920/2
    if not silent:
        play_sound('sounds/buzz.wav')
    pygame.draw.rect(screen, (0,255,0), (posx,0,1920/2,15))
    pygame.display.flip()

def reset_buzz_state():
    pygame.draw.rect(screen, (0,0,0), (0,0,1920,15))
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
        xstart = 250
        xinc_mod = 1
    elif pos == 'R':
        xstart = 1920 - 250
        xinc_mod = -1
    ystart = 1000

    for xoff in range(times):
        y = ystart
        xoffset = 14*8*xoff
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


def add_text(pos, text):
    """print text on the given position"""
    img = FONT.render(text.upper(), 1, (0,255,0))
    print(pos)
    pygame.draw.rect(BG, (0,0,0), (pos[0], pos[1], 60*len(text), 80))
    BG.blit(img, pos)
    screen.blit(BG, pos, (pos[0], pos[1], pos[0]+(60*len(text)), pos[1]+80))
    pygame.display.flip()

def print_line(line, text=(LINELEN - 6) * '_', points='--', anim=True):
    """Prints text in the given line"""
    previmg = None
    is_sum = False
    if text == 'SUMME':
        is_sum = True
        line = CURRENT_SLOTS + 1
    if not is_sum and (line > CURRENT_SLOTS):
        return


    if anim and not is_sum:
        REVEAL_EFFECT_1.play()
    for pos in range(LINELEN):
        display_points = '--'
        if pos == LINELEN-1:
            display_points = points
        if not is_sum and anim and pos == LINELEN - 1:
            REVEAL_EFFECT_2.play()
        txtpart = text[:pos]    
        if is_sum:
            prtxt = ' '* (LINELEN - 9) + txtpart + ' ' + display_points
        else:
            prtxt = str(line)+'.' + txtpart + (LINELEN - 6 - len(txtpart)) * '_' + ' ' + display_points
        img = FONT.render(prtxt.upper(), 1, (0,255,0))
        if previmg is not None:
            previmg.fill((0,0,0))
            BG.blit(previmg, (40,120*line))
        BG.blit(img, (40, 120*line))
        screen.blit(BG, (0, 16), (0,16,1920,930))
        previmg = img
        if anim:
            pygame.display.flip()
            time.sleep(0.05)
    if not anim:
        pygame.display.flip()


def prepare_round(num, game):
    global CURRENT_SLOTS
    game.reset_round()
    game.multiplier = num
    play_sound('sounds/intro.wav')
    show_image('images/pig{}.jpg'.format(num), GRAYSCALE, True)
    for x in range(num):
        play_sound('sounds/pig.wav')
        time.sleep(0.5)
    #time.sleep(4)
    clear()
    BG.fill((0, 0, 0))
    slots = {1:6, 2:5, 3:4}[num]
    CURRENT_SLOTS = slots
    for x in range(0, slots):
        print_line(x+1, anim=False)
    game.print_team_points()
    game.print_total_points()


PRINTLINE = USEREVENT+1
TIMERTICK = USEREVENT+2
REVEAL_EFFECT_1 = pygame.mixer.Sound('sounds/reveal.wav')
REVEAL_EFFECT_2 = pygame.mixer.Sound('sounds/reveal2.wav')

NP_NUMS = list(range(257,263))

screen = pygame.display.set_mode((1920, 1080))#, pygame.FULLSCREEN)
pygame.mouse.set_visible(False)
pygame.display.set_caption('Hackerspaceduell')
pygame.time.set_timer(TIMERTICK, 250)
FONT = pygame.font.Font('myfont.otf', 80)
# Fill background
BG = pygame.Surface(screen.get_size())
BG = BG.convert()
BG.fill((0, 0, 0))

def post_print_line_event(line, text, points, game):
    prl_event = pygame.event.Event(PRINTLINE, line=line, text=text, points=points, game=game)
    print("posting event")
    pygame.event.post(prl_event) 
    
    
def handle_print_line_event(event):
    print_line(event.line, event.text, event.points)
    event.game.add_points(event.points)
    print_line(7, 'SUMME', '{:>2}'.format(int(event.game.total_points/event.game.multiplier)), False)
    screen.blit(BG, (0, 16), (0,16,1920,930))
    pygame.display.flip()


def check_for_message(game):
    rm_file = False
    if not os.path.isfile('message'):
        return
    with open('message') as msgfile:
        msg = msgfile.read().strip()
        if msg:
            post_print_line_event(int(msg[0]), msg[1:-2], msg[-2:], game)
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
        if self.wrong < 3:
            play_sound('sounds/fail.wav')
            self.wrong += 1
            add_x(self.pos, self.wrong)




class Game(object):
    team_a = None
    team_b = None
    team_on_turn = None
    total_points = 0
    buzzed = False
    multiplier = 1

    def __init__(self):
        self.team_a = Team('Left team', 'L')
        self.team_b = Team('Right team', 'R')
        with open('points.txt','r') as pointsfile:
            pa, pb = pointsfile.read().splitlines()
            self.team_a.points = int(pa)
            self.team_b.points = int(pb)


    def team_on_turn_answered_wrong(self):
        if self.team_on_turn is not None:
            self.team_on_turn.wrong_answer()

    def reset_round(self):
        self.team_on_turn = None
        self.team_a.wrong = 0
        self.team_b.wrong = 0
        self.total_points = 0
        self.buzzed = False

    def finish_round(self):
        if self.team_on_turn is None:
            return
        self.team_on_turn.points += self.total_points
        self.print_team_points()
        self.reset_round()
        self.print_total_points()

    def print_team_points(self):
        with open('points.txt','w') as pointsfile:
            for pts in (self.team_a.points, self.team_b.points):
                pointsfile.write(str(pts) + '\n')

        add_text((60,1000), '{:<3}'.format(self.team_a.points))
        add_text((1920-240,1000), '{:>3}'.format(self.team_b.points))

    def add_points(self, points):
        self.total_points += (int(points) * self.multiplier)
        self.print_total_points()

    def print_total_points(self):
        add_text((960-60,1000), '{:^3}'.format(self.total_points))

def main():
    game = Game()
    fullscreen = True
    global screen
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                webserver.terminate()
                return
            if event.type == PRINTLINE:
                handle_print_line_event(event)
            if event.type == TIMERTICK:
                check_for_message(game)
            if event.type == KEYDOWN:
                if event.key == 266: #np .
                    play_sound('sounds/intro.wav')
                if event.key == K_q:
                    return
                if event.key == K_f:
                    if pygame.display.get_driver()=='x11':
                        pygame.display.toggle_fullscreen()
                    else:
                        acopy=screen.copy()                    
                        if fullscreen:
                            screen=pygame.display.set_mode((1920,1080))
                            fullscreen = False
                        else:
                            screen=pygame.display.set_mode((1920,1080), pygame.FULLSCREEN)
                            fullscreen = True
                            screen.blit(acopy, (0,0))                    
                            pygame.display.update()
                if event.key == K_a:
                    if not game.buzzed:
                        game.buzzed = True
                        buzz('A')
                        game.team_on_turn = game.team_a
                if event.key == K_b:
                    if not game.buzzed:
                        game.buzzed = True
                        buzz('B')
                        game.team_on_turn = game.team_b
                if event.key == K_s:
                    if not game.buzzed:
                        game.buzzed = True
                        buzz('A', True)
                        game.team_on_turn = game.team_a
                if event.key == K_o:
                    if not game.buzzed:
                        game.buzzed = True
                        buzz('B', True)
                        game.team_on_turn = game.team_b

                if event.key == 8:
                    game.buzzed = False
                    reset_buzz_state()                


                if event.key == K_x:
                    game.team_on_turn_answered_wrong()
                if event.key == K_y:
                    play_sound('sounds/fail.wav')
                if event.key == 263: 
                    prepare_round(1, game)
                if event.key == 264: 
                    prepare_round(2, game)
                if event.key == 265: 
                    prepare_round(3, game)

                if event.key == 270: # np +
                    game.finish_round()


                if event.key == K_d:
                    prev = screen.copy()
                    play_sound('sounds/ccc.wav')
                    show_image('images/datenknoten.jpg')
                if event.key == K_w:
                    prev = screen.copy()
                    play_sound('sounds/wat.wav')
                    show_image('images/wat.jpg', GRAYSCALE)
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
                
                if event.key == K_c:
                    cur = 'prev' 
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
                    def togg_cyb(cur):
                        if cur == 'prev':
                            prev_to_cyb()
                            return 'cyb'
                        else:
                            cyb_to_prev()
                            return 'prev'
                    for delay in [0.1,0.2,0.1,0.2,0.5,0.3,0.1,0.5]:
                        cur = togg_cyb(cur)
                        time.sleep(delay)
                    pygame.mixer.fadeout(300)

                if event.key in NP_NUMS:
                    meme = str(NP_NUMS.index(event.key) + 1)
                    prev = screen.copy()
                    if meme in MEMES:
                        sndfile = 'memes/{}/sound.wav'.format(meme)
                        imgfile = 'memes/{}/image.jpg'.format(meme)
                        if os.path.isfile(sndfile):
                            play_sound(sndfile)
                        if os.path.isfile(imgfile):
                            show_image(imgfile, GRAYSCALE)
                print(event.key)
            if event.type == KEYUP:
                if event.key in [K_n,K_l, K_k, K_d, K_w, K_p, K_v, K_m, K_c] + NP_NUMS:
                    screen.blit(prev, (0,0))
                    pygame.display.flip()
                    pygame.mixer.fadeout(300)

print("""

WELCOME TO 100HACKERFRAGEN SCREEN

Keys:

  Game conrols:

    a ... Left Buzzer
    s ... Left Buzzer - silent
    b ... Right Buzzer
    o ... Right Buzzer - silent
    r ... Reset Buzzer

    1,2,3 ... Init round

    0 ... Finish round

    x ... wrong answer for last buzzed team
    y ... wrong answer without displaying "x" 

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
