import pygame
import pygame.event
from pygame.locals import *
import time
import os
import os.path

pygame.init()

FONT = None
LINELEN = 32
BG = None


def print_line(line, text=(LINELEN - 6) * '_', points='--', anim=True):
    """Prints text in the given line"""
    previmg = None
    print("printing line")
    if anim:
        REVEAL_EFFECT_1.play()
        time.sleep(0.5)
    for pos in range(LINELEN):
        display_points = '--'
        if anim and pos == LINELEN-1:
            display_points = points
            REVEAL_EFFECT_2.play()
            time.sleep(0.5)
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
REVEAL_EFFECT_1 = pygame.mixer.Sound('reveal.wav')
REVEAL_EFFECT_2 = pygame.mixer.Sound('reveal2.wav')

screen = pygame.display.set_mode((800, 480), pygame.FULLSCREEN)
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

if __name__ == '__main__': main()