import pygame
pygame.init()
win=pygame.display.set_mode((300,300))
pygame.display.set_caption('animation tester')
position=0
#images=[pygame.image.load('character idle 0.png'),pygame.image.load('character walking 0.png'),pygame.image.load('character walking 0.png'),pygame.image.load('character walking 0.png'),
        #pygame.image.load('character idle 0.png'),pygame.image.load('character walking 1.png'),pygame.image.load('character walking 1.png'),pygame.image.load('character walking 1.png')]
images=[pygame.image.load('archer 0.png'),pygame.image.load('archer 1.png'),pygame.image.load('archer 2.png')]
run=True
while run:
    win.fill((255,255,255))
    image=images[position]
    win.blit(image,(20,20))
    pygame.display.update()
    pygame.time.delay(100)
    
    if position != len(images)-1:
        position+=1
    else:
        position=0
        
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run=False

pygame.quit()
        
