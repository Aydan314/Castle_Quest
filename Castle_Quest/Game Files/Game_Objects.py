import pygame
import random
import sys
import math
import datetime

if __name__ != '__main__': #only run when in use with another program
    pygame.init()
    
    global screen_width, screen_height
    screen_width=800
    screen_height=800 #defines the initial screen dimensions
    
    win=pygame.display.set_mode((screen_width,screen_height),pygame.RESIZABLE) #creates the game window
    pygame.display.set_caption('- Castle Quest -')
    
    clock=pygame.time.Clock() #defines the framerate module from pygame
    global frame_rate
    frame_rate=60
    global framerate_adjustment
    framerate_adjustment=1

    global path, file_path, image_path
    path=sys.path[0]
    file_path=path+'\\Game files\\'
    image_path=path+'\\Asset Images\\' #defines where to find all the files for the game

    global onScreen_collision_list
    onScreen_collision_list=[]

    pygame.display.set_icon(pygame.image.load(image_path+'game icon.png'))

class user:
    '''holds the data of the user'''
    def __init__(self,username,password,data,settings):
        self.username=username
        self.password=password
        self.data=data
        self.update_settings(settings)
        self.creator_levels=None
        self.game_levels=None
        self.first_load=True

    def update_settings(self,settings):
        settings=settings.split(',')
        self.settings=settings
        self.display_fps=bool(int(settings[0]))
        self.fps_30=bool(int(settings[1]))

class prompt:
    '''informs the user of what something does'''
    def __init__(self,x,y,text,colour):
        self.text=text
        self.x=x
        self.y=y
        self.colour=colour
        self.dark_colour=(colour[0]-10,colour[1]-10,colour[2]-10)
        self.font=pygame.font.SysFont('ocr a extended',30)
        self.height=0
        self.width=0
        self.initialize()
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)

    def draw(self,win):
        index=0
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        pygame.draw.rect(win,self.colour,self.rect)
        pygame.draw.rect(win,self.dark_colour,self.rect,4)
        
        for item in self.text: #renders each line of text
            line=self.font.render(item,1,(255,255,255))
            win.blit(line,(self.x,self.y+(line.get_height()*index)))
            index+=1

    def initialize(self):
        index=0
        for item in self.text:
            line=self.font.render(item,1,(255,255,255))
            self.height+=line.get_height()

            line_width=line.get_width()
            
            if line_width > self.width: #finds the longest line size
                self.width=line_width
        
        
        

class button:
    '''allows interaction'''
    def __init__(self,x,y,icon,colour):
        self.x=x
        self.y=y
        self.icon=icon
        self.colour=colour
        self.dark_colour=(colour[0]-10,colour[1]-10,colour[2]-10)
        self.light_colour=(colour[0]+10,colour[1]+10,colour[2]+10)
        self.width=icon.get_width()+4
        self.height=icon.get_height()+4
        self.box=pygame.Rect(self.x,self.y,self.width,self.height)
        self.highlighted=False
        self.clicked=False
        self.cooldown=30

    def draw(self,win):
        self.box=pygame.Rect(self.x,self.y,self.width,self.height)

        mouse_point=get_mouse()

        if mouse_point.colliderect(self.box): #changes button colour when mouse is above
            pygame.draw.rect(win,self.light_colour,self.box)
            pygame.draw.rect(win,self.colour,self.box,5)
            self.highlighted=True
            if pygame.mouse.get_pressed()[0] and self.cooldown == 0: #detects if the mouse has clicked on the button
                self.clicked=True
                self.cooldown=30
        else:
            pygame.draw.rect(win,self.colour,self.box)
            pygame.draw.rect(win,self.dark_colour,self.box,5)
            self.highlighted=False

        if self.cooldown != 0: #prevents the button from being pressed in rapid succession 
            self.cooldown-=1

        win.blit(self.icon,(self.x+2,self.y+2))

class switch(button):
    '''set a state of on or off to a value'''
    def __init__(self,x,y,icon,colour,state):
        super().__init__(x,y,icon,colour)
        self.indicator_size=self.icon.get_height()//2
        self.width+=self.indicator_size
        self.box=pygame.Rect(self.x,self.y,self.width,self.height)
        self.state=state
        

    def draw(self,win):
        self.box=pygame.Rect(self.x,self.y,self.width,self.height)
        mouse_point=get_mouse()
        Ypos=self.y+(self.height-self.indicator_size)//2

        if mouse_point.colliderect(self.box): #changes button colour when mouse is above
            pygame.draw.rect(win,self.light_colour,self.box)
            pygame.draw.rect(win,self.colour,self.box,5)
            self.highlighted=True
            if pygame.mouse.get_pressed()[0] and self.cooldown == 0: #detects if the mouse has clicked on the button
                self.state=not self.state
                self.clicked=True
                self.cooldown=30
        else:
            pygame.draw.rect(win,self.colour,self.box)
            pygame.draw.rect(win,self.dark_colour,self.box,5)
            self.highlighted=False

        if self.state:
            pygame.draw.rect(win,(255,255,255),((self.x+self.width)-(self.indicator_size*1.5),Ypos,self.indicator_size,self.indicator_size),5)
            pygame.draw.rect(win,(255,255,255),((self.x+self.width)-((self.indicator_size*1.5)-5),Ypos+5,self.indicator_size-10,self.indicator_size-10))
        else:
            pygame.draw.rect(win,(230,230,230),((self.x+self.width)-(self.indicator_size*1.5),Ypos,self.indicator_size,self.indicator_size),5)

        if self.cooldown != 0: #prevents the button from being pressed in rapid succession 
            self.cooldown-=1

        win.blit(self.icon,(self.x+2,self.y+2))
        
        

class user_slot:
    '''a button to represent a user'''
    def __init__(self,x,y,width,height,main_text,sub_text,colour,user,preview=None):
        self.x=x
        self.y=y
        self.width=width
        self.height=height
        self.main_text=main_text
        self.sub_text=sub_text
        self.box=(self.x,self.y,self.width,self.height)
        self.font=pygame.font.SysFont('ocr a extended',self.height//3)
        self.smallfont=pygame.font.SysFont('ocr a extended',self.height//4)
        self.colour=colour
        self.dark_colour=(colour[0]-10,colour[1]-10,colour[2]-10)
        self.light_colour=(colour[0]+10,colour[1]+10,colour[2]+10)
        self.clicked=False
        self.highlighted=False
        self.user=user
        self.cooldown=30
        self.preview=preview

    def draw(self,win):
        self.font=pygame.font.SysFont('ocr a extended',self.height//3)
        self.smallfont=pygame.font.SysFont('ocr a extended',self.height//4)
        self.box=(self.x,self.y,self.width,self.height)

        mouse_point=get_mouse()
        
        if mouse_point.colliderect(self.box): #changes the colour if the mouse is above
            pygame.draw.rect(win,self.light_colour,self.box)
            self.highlighted=True
            if pygame.mouse.get_pressed()[0] and self.cooldown == 0: #detects mouse click on the button
                self.clicked=True
                self.cooldown=30

        else:
            pygame.draw.rect(win,self.colour,self.box)
            self.highlighted=False


        if self.cooldown != 0:
            self.cooldown-=1
        
        title=self.font.render(self.main_text,1,(0,0,0)) #displays the username
        win.blit(title,(self.x,self.y))
        
        subtitle=self.smallfont.render(self.sub_text,1,(50,50,255)) #displays additional information
        win.blit(subtitle,(self.x,self.y+title.get_height()))

        if subtitle.get_width() > title.get_width():
            max_len=subtitle.get_width()
        else:
            max_len=title.get_width()
            
        if self.preview is not None: #if the GUI slot requires an image of the level
            preview_rect=(self.x+max_len+20,self.y,self.width-max_len-20,self.height)
            pygame.draw.rect(win,(255,255,255),preview_rect)

            adjustment=self.height-100 #adjusts the preview to the bottom of the GUI slot
            if adjustment < 0:
                adjustment=0
            
            for item in self.preview:
                position=(preview_rect[0]+item[1][0],(self.y+item[1][1])+adjustment-10) #each images position is moved to be level with the slot
                if position[0]+item[0].get_width() < self.x+self.width and position[1] > self.y and position[1]+item[0].get_height() < self.y+self.height: #if this position is within the preview box
                    win.blit(item[0],position) #the item is drawn

            pygame.draw.rect(win,(205,205,205),(preview_rect[0],preview_rect[1]+3,preview_rect[2]-3,preview_rect[3]-6),4)

        pygame.draw.rect(win,self.dark_colour,self.box,3)

    def change_colour(self,colour):
        self.colour=colour
        self.dark_colour=(colour[0]-10,colour[1]-10,colour[2]-10)
        self.light_colour=(colour[0]+10,colour[1]+10,colour[2]+10)
        

class textbox:
    '''allows the user to type'''
    def __init__(self,x,y,height,width_parameters,colour):
        self.x=x
        self.y=y
        self.min_width=width_parameters[0]
        self.max_width=width_parameters[1]
        self.width=self.min_width
        self.height=height
        self.box=pygame.Rect(self.x,self.y,self.width,self.height)
        self.colour=colour
        self.active_colour=(colour[0]-10,colour[1]-10,colour[2]-10)
        self.light_colour=(colour[0]+10,colour[1]+10,colour[2]+10)
        self.text=''
        self.active=False
        self.font=pygame.font.SysFont('ocr a extended',self.height//2)
        self.final_text=None
        self.clicked=False
        self.highlighted=False

    def draw(self,win,events):
        self.box=pygame.Rect(self.x,self.y,self.width,self.height)
        self.clicked=False
        text=self.font.render(self.text,1,(0,0,0))

        if self.active:
            pygame.draw.rect(win,self.light_colour,self.box)
            pygame.draw.rect(win,self.colour,self.box,3)
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE: #removes the last character off the string
                        self.text=self.text[:-1]
                        
                    elif event.key == pygame.K_RETURN: #finalizes the text and resets the textbox
                        self.active=False
                        if self.text == '':
                            self.final_text=None
                        else:
                            self.final_text=self.text
                        self.text=''
                        self.width=self.min_width
                        text=self.font.render(self.text,1,(0,0,0))
                            
                    elif event.key != pygame.K_TAB and event.key != pygame.K_ESCAPE: #adds the keystrokes to a string
                        if self.width <= self.max_width: #prevents anymore characters being added if the textbox is full
                            self.text+=event.unicode
        else:
            pygame.draw.rect(win,self.colour,self.box)
            pygame.draw.rect(win,self.active_colour,self.box,3)

        mouse_point=get_mouse()
        self.highlighted=False
        if mouse_point.colliderect(self.box): #changes colour if the mouse is above it
            pygame.draw.rect(win,self.light_colour,self.box)
            self.highlighted=True
            if pygame.mouse.get_pressed()[0]: #detects the mouse click and allows user to now type
                self.active=True
                self.clicked=True
                        
        if self.min_width < text.get_width(): #textbox will resize with the text if it exceeds its origional size
            self.width=text.get_width()+5

        if text.get_width() <= self.max_width and text.get_width() >= self.min_width: #keeps track of the textbox width
            self.width=text.get_width()
            
        win.blit(text,(self.x+5,self.y+5))

    def get_text(self):
        return self.final_text

class confirmation_box:
    '''ensures the user wants to preform an action'''
    def __init__(self,x,y,text,colour):
        self.x=x
        self.y=y
        self.colour=colour
        self.dark_colour=(colour[0]-10,colour[1]-10,colour[2]-10)
        self.font=pygame.font.SysFont('ocr a extended',30)
        self.text=self.font.render(text,1,(255,255,255))
        self.width=self.text.get_width()
        self.height=self.text.get_height()+100
        self.yes_button=button(self.x+10,self.y+self.text.get_height()+50,self.font.render(' Yes ',1,(255,255,255)),(100,240,100))
        self.no_button=button(self.x+self.width-90,self.y+self.text.get_height()+50,self.font.render(' No ',1,(255,255,255)),(240,100,100))
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        self.confirmation=None

    def draw(self,win):
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        
        self.yes_button.x, self.yes_button.y = self.x+10, self.y+self.text.get_height()+50
        self.no_button.x, self.no_button.y = self.x+self.width-90, self.y+self.text.get_height()+50
        
        pygame.draw.rect(win,(self.colour),(self.rect))
        pygame.draw.rect(win,(self.dark_colour),(self.rect),4)
        win.blit(self.text,(self.x,self.y))
        self.no_button.draw(win)
        self.yes_button.draw(win)

        if self.yes_button.clicked:
            self.confirmation=True
            self.yes_button.clicked=False
            
        if self.no_button.clicked:
            self.confirmation=False
            self.no_button.clicked=False

    def mouse_inside(self):
        mouse_point=get_mouse()
        if mouse_point.colliderect(self.rect):
            return True
        
        return False

        
                    
                    

class player:
    '''able to traverse the level'''
    def __init__(self,x,y,user):
        self.facing='right'
        self.user=user
        self.x=x
        self.y=y
        self.distance_travelled=0
        self.respawn_height=0
        self.respawn_distance=0
        self.cameraY=0
        self.spawnY=720
        self.camera_moved=0
        self.death_message='Oops'
        self.level_tick=0
        self.won=False
        self.game_paused=False
        self.level_adjusted=[0,0]
        self.level=None
        self.file=None
        self.key=False
        self.trophies_collected=0
        self.available_trophies=0
        self.weather='sunny'
        self.score=0
        self.time=0
        
        self.speed=1
        self.base_speed=4
        self.max_speed=6
        self.acceleration=0.01
        self.speed_increase=0
        self.crouch_speed=2
        self.gravity_value=1
        
        self.moving=False
        self.has_momentum=False
        self.crouching=False
        self.in_air=False
        self.in_liquid=False
        
        self.default_height=140
        self.default_width=60
        self.crouch_height=90
        self.crouch_width=80
        self.crouch_cooldown=0
        self.height=140
        self.width=60
        
        self.idle_cooldown=0
        self.walk_cooldown=0
        self.frame=0
        
        self.walking=[pygame.image.load(image_path+'character idle 0.png').convert_alpha(),pygame.image.load(image_path+'character walking 0.png').convert_alpha(), #holds the walking animation of the player
                      pygame.image.load(image_path+'character walking 0.png').convert_alpha(),pygame.image.load(image_path+'character walking 0.png').convert_alpha(),
                      pygame.image.load(image_path+'character idle 1.png').convert_alpha(),pygame.image.load(image_path+'character walking 1.png').convert_alpha(),
                      pygame.image.load(image_path+'character walking 1.png').convert_alpha(),pygame.image.load(image_path+'character walking 1.png').convert_alpha()]
        
        self.image=pygame.image.load(image_path+'character idle 0.png').convert_alpha(),pygame.image.load(image_path+'character idle 1.png').convert_alpha() #holds the idle animation of the player
        self.crouch_image=pygame.image.load(image_path+'character crouching 0.png').convert_alpha(),pygame.image.load(image_path+'character crouching 1.png').convert_alpha() #holds the crouching animation of the player
        self.jumping_image=pygame.image.load(image_path+'character jumping.png').convert_alpha()
        
        self.cape=[pygame.image.load(image_path+'character cape 0.png').convert_alpha(),pygame.image.load(image_path+'character cape 1.png').convert_alpha(),pygame.image.load(image_path+'character cape 2.png').convert_alpha(),
                   pygame.image.load(image_path+'character cape 3.png').convert_alpha()] #holds the cape animation
        
        self.cape_cooldown=0
        self.cape_frame=0

        self.max_health=6
        self.health=self.max_health
        self.health_bounce=0
        self.hurt_animation=0
        self.knockback=0
        self.knockback_direction=None

        self.heart_full=pygame.image.load(image_path+'heart full.png').convert_alpha()
        self.heart_half=pygame.image.load(image_path+'heart half.png').convert_alpha()
        self.heart_empty=pygame.image.load(image_path+'heart empty.png').convert_alpha()
        
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height) #hitboxes from the pygame library used to calculate collisions
        self.down_rect=pygame.Rect(self.x,self.y,self.width,self.height+1)
        self.up_rect=pygame.Rect(self.x,self.y-10,self.width,self.height+5)
        self.left_rect=pygame.Rect(self.x-5,self.y,self.width+5,self.height)
        self.right_rect=pygame.Rect(self.x,self.y,self.width+5,self.height)
        self.jump_rect=pygame.Rect(self.x,self.y-10,self.width,self.height+10)
        self.depth_rect=pygame.Rect(self.x,self.y,self.width,self.height+100)
        self.range_rect=pygame.Rect(self.x-400,self.y-200,self.width+800,self.height+400)
        self.liquid_rect=pygame.Rect(self.x,self.y,self.width,self.height-20)
        
    def draw(self,win):
        self.jump_rect=pygame.Rect(self.x,self.y-10,self.width,self.height+10)
        self.down_rect=pygame.Rect(self.x,self.y,self.width,self.height+1) #updates the players hitboxes when they are drawn to the screen
        self.up_rect=pygame.Rect(self.x,self.y-10,self.width,self.height+5)
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        self.left_rect=pygame.Rect(self.x-self.speed*framerate_adjustment,self.y,self.width+self.speed*framerate_adjustment,self.height)
        self.right_rect=pygame.Rect(self.x,self.y,self.width+self.speed*framerate_adjustment,self.height)
        self.depth_rect=pygame.Rect(self.x,self.y,self.width,self.height+100)
        self.range_rect=pygame.Rect(self.x-400,self.y-200,self.width+800,self.height+400)
        self.liquid_rect=pygame.Rect(self.x,self.y,self.width,self.height-20)
        
        #pygame.draw.rect(win,(233,0,0),self.range_rect,1)
        #pygame.draw.rect(win,(233,200,0),self.rect,1)
        cape_adjustment=0
        
        if self.hurt_animation != 0:
            self.hurt_animation-=1

        if self.cape_cooldown == 0: #ensures the cape animation isnt too fast
            self.cape_frame+=1
            self.cape_cooldown=8/framerate_adjustment
        else:
            self.cape_cooldown-=1

        if self.cape_frame > len(self.cape)-1:
            self.cape_frame=0

        if self.crouching:
            self.up_rect=pygame.Rect(self.x,self.y-40,self.width,self.height+45)
            if self.moving:
                if self.frame > len(self.crouch_image)-1:
                    self.frame=0

                character=self.crouch_image[self.frame]
                
                if self.crouch_cooldown == 0: #makes sure the animation is not too fast
                    self.frame+=1
                    self.crouch_cooldown=10/framerate_adjustment
                else:
                    self.crouch_cooldown-=1
            else:
                character=self.crouch_image[0]

        elif self.in_air:
            character=self.jumping_image
            
        elif self.moving:
            if self.frame == 4: #adjusts the cape to the bobbing height
                    cape_adjustment=4
                    
            if self.frame > len(self.walking)-1:
                self.frame=0
                    
            character=self.walking[self.frame]
            
            if self.walk_cooldown == 0: #the speed of the animation is linked to the players current speed
                self.frame+=1
                self.walk_cooldown=round((10//self.speed)/framerate_adjustment)
            else:
                self.walk_cooldown-=1
            
        else:
            if self.frame > len(self.image)-1:
                self.frame=0
            if self.frame == 1: #adjusts the cape to the players bobbing height
                cape_adjustment=4
                
            character=self.image[self.frame]

            if self.idle_cooldown == 0: #switches the frames at a slow rate as they are idle
                self.frame+=1
                self.idle_cooldown=60/framerate_adjustment
            else:
                self.idle_cooldown-=1

        if self.facing == 'left':
            character=pygame.transform.flip(character,True,False)
            cape=pygame.transform.flip(self.cape[self.cape_frame],True,False)
            win.blit(cape,((self.x-12)+self.width,self.y+10+cape_adjustment+self.height//3)) #cape is moved to still be on the players back
        else:
            win.blit(self.cape[self.cape_frame],((self.x+12)-self.cape[self.cape_frame].get_width(),self.y+10+cape_adjustment+self.height//3))
        win.blit(character,(self.x,self.y))
        
    def harm_player(self,damage,entity):
        self.health-=damage
        self.hurt_animation=40//framerate_adjustment
        if class_type(entity) in ['enemy','turret']:
            self.knockback=8
            self.knockback_direction=entity.facing

    def reset(self):
        self.max_health=6
        self.health=self.max_health
        self.trophies_collected=0
        self.respawn_height=0
        self.spawnY=720
        self.cameraY=0
        self.key=False
        self.score=0
        self.time=0
        
        

class enemy:
    '''seeks out and hurts the player'''
    def __init__(self,x,y,varient,grid_cursor):
        self.x=x
        self.y=y
        self.varient=varient
        self.fileX=x
        self.fileY=y
        self.image=pygame.image.load(image_path+varient+' 0.png').convert_alpha()
        self.walking=[pygame.image.load(image_path+varient+' 0.png').convert_alpha(),pygame.image.load(image_path+varient+' 1.png').convert_alpha(),
                      pygame.image.load(image_path+varient+' 2.png').convert_alpha()] #holds the enemies walk cycle
        
        self.height=self.image.get_height()
        self.width=self.image.get_width()
        self.respawn_height=0
        self.camera_moved=0
        self.spawnY=0
        
        self.initialize(grid_cursor)
        
        self.offscreen=False
        
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height) #various hitboxes to check collisions
        self.left_rect=pygame.Rect(self.x,self.y,self.width,self.height)
        self.right_rect=pygame.Rect(self.x,self.y,self.width,self.height)
        self.up_rect=pygame.Rect(self.x,self.y-10,self.width,self.height+5)
        self.down_rect=pygame.Rect(self.x,self.y,self.width,self.height+1)
        self.jump_rect=pygame.Rect(self.x,self.y,self.width,self.height)
        self.depth_rect=pygame.Rect(self.x,self.y,self.width,self.height+100)
        self.edge_left_rect=pygame.Rect(self.x,self.y+self.height,self.width//2,screen_height)
        self.edge_right_rect=pygame.Rect(self.x+self.width//2,self.y+self.height,self.width//2,screen_height)
        
        
        self.crouching=False
        
        self.dead=False
        self.font=pygame.font.SysFont('ocr a extended',20)
        self.text=self.font.render(self.varient.capitalize(),1,(255,255,255))
        
        self.frame=0
        self.frame_cooldown=0
        self.facing='right'

        self.projectile_type='arrow'
        if self.varient == 'snowman':
            self.projectile_type='snowball'
        elif self.varient == 'magma king':
            self.projectile_type='fireball'

    def draw(self,win,player):
        self.rect=pygame.Rect(self.x+10,self.y,self.width-20,self.height)
        self.left_rect=pygame.Rect(self.x-self.speed*framerate_adjustment,self.y,self.width+self.speed*framerate_adjustment,self.height)
        self.right_rect=pygame.Rect(self.x+self.speed*framerate_adjustment,self.y,self.width-self.speed*framerate_adjustment,self.height)
        self.up_rect=pygame.Rect(self.x,self.y-10,self.width,self.height+5)
        self.down_rect=pygame.Rect(self.x,self.y,self.width,self.height+1)
        self.jump_rect=pygame.Rect(self.x,self.y-40,self.width,self.height+40)
        self.depth_rect=pygame.Rect(self.x,self.y,self.width,self.height+100)
        self.edge_left_rect=pygame.Rect(self.x,self.y+self.height,self.width//2,screen_height)
        self.edge_right_rect=pygame.Rect(self.x+self.width//2,self.y+self.height,self.width//2,screen_height) #hitboxes updated
        
        #pygame.draw.rect(win,(255,0,0),self.edge_left_rect,1)
        #pygame.draw.rect(win,(255,200,0),self.edge_right_rect,1)
        
        if not self.death_animation:
            if not player.game_paused:
                self.check_for_death(player)
                self.handle_movements(player)
                
                if self.varient not in ['archer','snowman']: #if the enemy has a melee attack
                    if self.rect.colliderect(player.rect):
                        player.death_message=self.varient+' brutally murdered you'
                        if self.varient == 'magma king':
                            player.harm_player(20,self)
                            
                        elif self.cooldown == 0 and not player.won: #it will attack the player
                            player.harm_player(self.damage,self)
                            self.cooldown=60//framerate_adjustment

                                
                            
                if self.varient in ['archer','snowman','magma king']:
                    if self.cooldown == 0:
                        if player.x < self.x: #if the enemy has a ranged attack it will shoot at the player
                            nonCollision_list.append(projectile(self.x,self.y+self.width//2,self.projectile_type,1,self,(player.x,player.y),(None,None)))
                        else:
                            nonCollision_list.append(projectile(self.x,self.y+self.width//2,self.projectile_type,-1,self,(player.x,player.y),(None,None)))
                        self.cooldown=120//framerate_adjustment
                    

            if self.cooldown != 0:
                self.cooldown-=1

            if self.frame_cooldown != 0:
                self.frame_cooldown-=1

            if self.frame_cooldown == 0:
                self.frame+=1
                self.frame_cooldown=10//framerate_adjustment

            if self.frame > len(self.walking)-1:
                self.frame=0

            image=self.walking[self.frame]
            
            if self.facing == 'left':
                image=pygame.transform.flip(self.walking[self.frame],True,False)

            win.blit(image,(self.x,self.y))

            win.blit(self.text,(self.x+(self.width//2-self.text.get_width()//2),self.y-self.text.get_height()-22))
            pygame.draw.rect(win,(255,40,40),(self.x,self.y-20,self.width,10))
            pygame.draw.rect(win,(40,255,40),(self.x,self.y-20,round(self.width*(self.health/self.total_health)),10))
            pygame.draw.rect(win,(255,255,255),(self.x,self.y-20,self.width,10),1)

        else:
            image=pygame.transform.rotate(self.image,(30-self.death_duration)) #makes the enemy fall down as a death animation
            win.blit(image,(self.x,self.y))
            if self.death_duration != 0:
                self.death_duration-=1
            else:
                self.dead=True
                player.score+=self.score
                nonCollision_list.append(score_indicator(self.x,self.y,self.score)) #displays the score gained by the player after killing the enemy
            
            

        #pygame.draw.rect(win,(200,0,0),(self.rect),1)

    def check_for_death(self,player):
        for item in nonCollision_list:
            if class_type(item) == 'returning_projectile': #checks if the player has thrown their weapon at the enemy
                if item.rect.colliderect(self.rect) and not item.dealt_damage and not self.dead:
                    self.health-=1
                    self.knockback=4*framerate_adjustment
                    self.knockback_direction=item.direction
                    self.hit_animation=10//framerate_adjustment
                    item.dealt_damage=True
                              
        if self.health <= 0:
            self.death_animation=True
            
        if self.y > player.camera_moved+screen_height+self.height*2+400: #checks if the enemy has fallen below the level
            for item in nonCollision_list:
                if class_type(item) == 'enemy':
                    if item == self:
                        self.dead=True

    def handle_movements(self,player):
        collisions=(check_collisions(collision_list,self)) #collisions with the level are found
        collision_checks=collisions[0]
        collided_items=collisions[1]

        roof_item=collided_items[0] #collisions stored as variables
        ground_item=collided_items[1]
        left_item=collided_items[2]
        right_item=collided_items[3]
        roof_level=collisions[2]

        roof_contact=collision_checks[0]
        ground_contact=collision_checks[1]
        can_left=collision_checks[2]
        can_right=collision_checks[3]

        jump_data=handle_jumping(self,self.jumping,ground_contact,ground_item,roof_contact,roof_level,self.jump_value)
        self.jump_value=jump_data[0]
        self.jumping=jump_data[1]

        

        collision_values=self.check_for_others() #checks if another enemy is occupying the same space
        enemy_left=collision_values[0]
        enemy_right=collision_values[1]
        enemy_both = enemy_right and enemy_left
        
        if enemy_both:
            self.can_track=collision_values[2] #decides if the enemy should track the player
        else:
            self.can_track=True
            
            if self.varient in ['archer','snowman','magma king'] and self.rect.colliderect(player.range_rect): #if the archer is in range of the player they stop
                self.can_track=False

        edge_info=self.check_on_edge() #prevents an enemy jumping out of the level

        if not edge_info[0] or not edge_info[1]:
            can_left, can_right = edge_info

        if self.can_track:
            if can_left and player.x < self.x and not enemy_left: #moves the enemy towards the player
                self.x-=self.speed*framerate_adjustment
                self.facing='left'

            elif can_right and player.x > self.x and not enemy_right:
                self.x+=self.speed*framerate_adjustment
                self.facing='right'

            if player.y < self.y-(player.height-self.height) or enemy_left or enemy_right:
                if ground_contact and not roof_contact:
                    self.jumping=True

        else:
            if self.varient in ['archer','snowman','magma king']:
                if player.x > self.x: #if the enemy is ranged it will just face the player
                    self.facing='right'
                else:
                    self.facing='left'

            else:
                direction_list=['left','right','stationary'] #allows the enemy to randomly wander
                if random.randint(1,60) == 1:
                    self.direction=random.choice(direction_list)
                    
                if self.direction == 'left' and can_left:
                    self.x-=self.speed*framerate_adjustment
                    self.facing='left'
                elif self.direction == 'right' and can_right:
                    self.x+=self.speed*framerate_adjustment
                    self.facing='right'
    
    def check_for_others(self):
        contact_left=False
        contact_right=False
        can_track=True
        for item in nonCollision_list:
            if not item.offscreen:
                if class_type(item) == 'enemy' and item != self and not item.dead: #checks if the enemies are bunching up
                    if item.can_track:
                        can_track=False
                    if self.left_rect.colliderect(item.rect):
                        contact_left=True
                    if self.right_rect.colliderect(item.rect):
                        contact_right=True
                    
        return contact_left,contact_right,can_track

    def initialize(self,grid_cursor):
        self.health=4
        self.speed=2
        self.damage=1
        self.score=100
        
        if self.varient == 'stone golem':
            self.health=8
            self.speed=1
            self.damage=2
            self.score=200

        elif self.varient == 'archer':
            self.score=150

        elif self.varient == 'snowman':
            self.score=150
            self.health=2
            self.damage=2

        elif self.varient == 'mummy':
            self.score=150
            self.health=6

        elif self.varient == 'magma king':
            self.score=1000
            self.health=25
            self.speed=1
            self.damage=2
            
            
        self.total_health=self.health
        self.death_animation=False
        self.death_duration=30
        self.direction='left'
        self.facing='left'
        self.can_track=False
        self.jumping=False
        self.jump_value=1
        self.gravity_value=1
        self.cooldown=0
        self.knockback=0
        self.knockback_direction=None

        if grid_cursor: #if the enemy has just been placed in the level editor its start position is different
            self.initialX, self.initialY = grid_cursor
        else:
            self.initialX=self.x
            self.initialY=self.y


    def check_on_edge(self):
        can_left, can_right = False, False

        global onScreen_collision_list
        
        for item in onScreen_collision_list: #finds if there are any collideable tiles below the enemy
            if not item.dead and not item.offscreen:
                if item.rect.colliderect(self.edge_left_rect):
                    can_left=True

                if item.rect.colliderect(self.edge_right_rect):
                    can_right=True

        return can_left, can_right
                
                

    def reset(self):
        self.x=self.initialX
        self.y=self.initialY
        self.dead=False
        self.offscreen=False
        self.initialize(None)
            
                
                    
        
     

class tile:
    '''collidable level asset'''
    def __init__(self,x,y,varient,grid_cursor):
        self.x=x
        self.y=y
        self.varient=varient
        self.image=pygame.image.load(image_path+varient+'.png').convert_alpha() #stores the image for faster access
        self.width=self.image.get_width()-8
        self.height=self.image.get_height()-8
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height) #hitbox from the pygame library
        self.offscreen=False
        self.dead=False
        self.initialX=grid_cursor[0]
        self.initialY=grid_cursor[1]

    def draw(self,win):
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        win.blit(self.image,(self.x-4,self.y-4))
        #pygame.draw.rect(win,(233,200,0),self.rect,1)

class solid_obsticle(tile):
    '''collidable obsticle that harms the player'''
    def __init__(self,x,y,varient,grid_cursor):
        super().__init__(x,y,varient,grid_cursor)
        self.hurt_rect=pygame.Rect(self.x-4,self.y-4,self.width+8,self.height+8)
        self.cooldown=0
        self.harming_player=False
        self.dead=False
        
    def draw(self,win,player):
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        self.hurt_rect=pygame.Rect(self.x-4,self.y-4,self.width+8,self.height+8)
        if self.hurt_rect.colliderect(player.left_rect) or self.hurt_rect.colliderect(player.right_rect): #harms the player if in contact
            self.harming_player=self.can_harm()
            
            if self.cooldown == 0 and self.can_harm():
                player.harm_player(1,self)
                self.cooldown=30//framerate_adjustment
            player.death_message='You got impaled'

        else:
            self.harming_player=False
        
        if self.cooldown != 0: #controls the rate at which the player is harmed
            self.cooldown-=1
    
        win.blit(self.image,(self.x-4,self.y-4))

    def can_harm(self):
        global onScreen_collision_list
        
        for item in onScreen_collision_list: #checks if another asset of the same type is already harming the player
            if class_type(item) == class_type(self):
                if item != self and item.harming_player:
                    return False
            
        return True

class unstable_tile:
    '''will break the more the player stays on it'''
    def __init__(self,x,y,varient,grid_cursor):
        self.x=x
        self.y=y
        self.initialX=grid_cursor[0]
        self.initialY=grid_cursor[1]
        self.varient=varient
        self.image=[pygame.image.load(image_path+varient+' 0.png').convert_alpha(),pygame.image.load(image_path+varient+' 1.png').convert_alpha(),
                    pygame.image.load(image_path+varient+' 2.png').convert_alpha(),pygame.image.load(image_path+varient+' 3.png').convert_alpha()] #stores the images for faster access
        
        self.width=self.image[0].get_width()
        self.height=self.image[0].get_height()
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height) #hitbox from the pygame library
        self.offscreen=False
        self.dead=False
        self.break_cooldown=10//framerate_adjustment
        self.reappear_cooldown=300//framerate_adjustment
        self.break_stage=0

    def draw(self,win,player):
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        if not self.dead:
            if player.down_rect.colliderect(self.rect):
                self.break_cooldown-=1 #if the player is touching the block it cracks 
                
            if self.break_cooldown < 0:
                self.break_cooldown=10//framerate_adjustment
                self.break_stage+=1 #the block will start to crack

            if self.break_stage == 4:
                self.dead=True
                
            if not self.dead:
                win.blit(self.image[self.break_stage],(self.x,self.y))

        else:
            self.reappear_cooldown-=1
            if self.reappear_cooldown == 0: #once broken it will appear again after a cooldown
                self.reappear_cooldown=300//framerate_adjustment
                self.reset()

    def reset(self):
        self.dead=False
        self.break_cooldown=10//framerate_adjustment
        self.break_stage=0

class door():
    '''prevents the player moving forward until a condition is met'''
    def __init__(self,x,y,varient,grid_cursor):
        self.x=x
        self.y=y
        self.varient=varient
        self.image=pygame.image.load(image_path+varient+'.png').convert_alpha() #stores the image for faster access
        self.width=self.image.get_width()
        self.height=self.image.get_height()
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height) #hitbox from the pygame library
        self.offscreen=False
        self.dead=False
        self.initialX=grid_cursor[0]
        self.initialY=grid_cursor[1]
        self.open_image=pygame.image.load(image_path+self.varient+' open.png').convert_alpha()

    def draw(self,win,player):
        self.rect=pygame.Rect(self.x+12,self.y,self.width-24,self.height)
        if not self.dead:
            win.blit(self.image,(self.x,self.y))
            
            if self.rect.colliderect(player.right_rect) or self.rect.colliderect(player.left_rect):
                if self.varient == 'locked door': #needs a key to open
                    if player.key:
                        player.key=False
                        self.dead=True #the door is no longer a collideable asset
                elif self.varient == 'trophy door': #needs all trophies to be collected
                    if player.trophies_collected == player.available_trophies:
                        self.dead=True #the door is no longer a collideable asset
                    
                else:
                    self.dead=True

        else:
            win.blit(self.open_image,(self.x,self.y))

        #pygame.draw.rect(win,(255,0,0),(self.rect),1)


    def reset(self):
        self.dead=False
            
        
        

class platform:
    '''allows player to jump through and land on top'''
    def __init__(self,x,y,varient,grid_cursor):
        self.x=x
        self.y=y
        self.varient=varient
        self.image=pygame.image.load(image_path+varient+'.png').convert_alpha() #stores the image for faster access
        self.width=self.image.get_width()
        self.height=self.image.get_height()
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height) #hitbox from the pygame library
        self.offscreen=False
        self.dead=False
        self.initialX=grid_cursor[0]
        self.initialY=grid_cursor[1]

    def draw(self,win):
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        win.blit(self.image,(self.x,self.y))
    

class decor:
    '''non collidable level asset'''
    def __init__(self,x,y,varient,grid_cursor):
        self.x=x
        self.y=y
        self.varient=varient
        self.image=pygame.image.load(image_path+varient+'.png').convert_alpha() #stores the image for faster access
        self.width=self.image.get_width()
        self.height=self.image.get_height()
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        self.offscreen=False
        self.dead=False
        self.initialX=grid_cursor[0]
        self.initialY=grid_cursor[1]

    def draw(self,win):
        win.blit(self.image,(self.x,self.y))
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)

class front_decor(decor):
    '''the player will appear behind this decor'''
    def __init__(self,x,y,varient,grid_cursor):
        super().__init__(x,y,varient,grid_cursor)

class turret(decor):
    '''will shoot at the player if in range'''
    def __init__(self,x,y,varient,grid_cursor):
        super().__init__(x,y,varient,grid_cursor)
        self.cooldown=60//framerate_adjustment
        self.facing='left'
        self.active_image=pygame.image.load(image_path+varient+' active.png').convert_alpha()
        self.damage=1
        
    def draw(self,win,player):
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)

        direction=1
        self.facing='left'
        
        in_range=self.rect.colliderect(player.range_rect)
        if in_range: #the turret lights up when it is able to shoot
            image=self.active_image
            if player.x > self.x:
                image=pygame.transform.flip(self.active_image,True,False)
                direction=-1
                self.facing='right'
        else:
            image=self.image
            if player.x > self.x:
                image=pygame.transform.flip(self.image,True,False)
                direction=-1
                self.facing='right'
            
        if not player.game_paused: 
            if self.cooldown == 0:
                if in_range:
                    self.cooldown=60//framerate_adjustment
                    nonCollision_list.append(projectile(self.x,self.y+self.width//2,'arrow',direction,self,(player.x,self.y+self.width//2),(None,None))) #shoots at the player
            else:
                self.cooldown-=1
            
        win.blit(image,(self.x,self.y))

class liquid:
    '''a liquid that harms the player'''
    def __init__(self,x,y,varient,grid_cursor):
        self.x=x
        self.y=y
        self.varient=varient
        self.image=[pygame.image.load(image_path+varient+' 0.png').convert_alpha(),pygame.image.load(image_path+varient+' 1.png').convert_alpha(),
                    pygame.image.load(image_path+varient+' 2.png').convert_alpha(),pygame.image.load(image_path+varient+' 3.png').convert_alpha()] #stores the liquid animation
        self.width=self.image[0].get_width()
        self.height=self.image[0].get_height()
        self.offscreen=False
        self.cooldown=0
        self.frame=0
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height-4)
        self.harming_player=False
        self.initialX=grid_cursor[0]
        self.initialY=grid_cursor[1]

    def draw(self,win,player):
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height-4)
        self.frame=round((player.level_tick%80)/20)-1 #synchronises the animation of all liquids
        win.blit(self.image[self.frame],(self.x,(self.y+8)-round(8*math.sin(player.level_tick/20)))) #draws the image as bobbing up and down like a liquid
        
        if self.rect.colliderect(player.liquid_rect):
            self.harming_player=self.can_harm()
            if self.cooldown == 0 and self.can_harm(): #if the player falls in the liquid they take damage if not already being damaged
                player.harm_player(2,self)
                self.cooldown=60//framerate_adjustment
                
            player.death_message='Do not swim in that'
        else:
            self.harming_player=False
            

        if self.cooldown != 0:
            self.cooldown-=1

    def can_harm(self):
        for item in nonCollision_list: #checks if another asset of the same type is already harming the player
            if class_type(item) == class_type(self):
                if item != self and item.harming_player and not item.offscreen:
                    return False
            
        return True

class goal(decor):
    '''an objective for the player to reach to complete the level'''
    def __init__(self,x,y,varient,grid_cursor):
        super().__init__(x,y,varient,grid_cursor)
        self.height=self.image.get_height()
        self.width=self.image.get_width()
        self.rect=pygame.Rect(self.x+self.width//4,self.y,self.width-self.width//2,self.height)
        self.frame=0
        self.cooldown=0
        self.flag_images=[pygame.image.load(image_path+'checkpoint flag 0.png').convert_alpha(),pygame.image.load(image_path+'checkpoint flag 1.png').convert_alpha(),
                          pygame.image.load(image_path+'checkpoint flag 2.png').convert_alpha(),pygame.image.load(image_path+'checkpoint flag 3.png').convert_alpha()] #holds the flag animation #holds the flag animation
        self.collision=False
        self.victory_animation=100

    def draw(self,win,player):
        self.rect=pygame.Rect(self.x+self.width//4,self.y,self.width-self.width//2,self.height)
        win.blit(self.image,(self.x,self.y))

        if not player.game_paused:
            if self.rect.colliderect(player.rect):
                self.collision=True

            if self.collision:
                self.victory_animation-=1 #if the player reaches the goal the victory animation plays
                fireworks_done=True
                for item in nonCollision_list: #checks if all fireworks have exploded
                    if not item.offscreen and item.varient == 'firework':
                        fireworks_done=False
                    
                if self.victory_animation < 0 and fireworks_done: #resets once the player has won
                    player.won=True
                    self.victory_animation=100
                    self.collision=False

                if self.victory_animation % 10 == 0 and self.victory_animation >= 0 and not player.won: #creates a wave of fireworks above the goal
                    nonCollision_list.append(rising_decor(self.x+round(self.width*(self.victory_animation/(100))),self.y,'firework',(None,None)))


        win.blit(self.flag_images[self.frame],(self.x+self.width//2+12,self.y)) #animates the flag
        
        if self.cooldown == 0: #keeps the animation at a constant rate
            self.frame+=1
            self.cooldown=10/framerate_adjustment
        else:
            self.cooldown-=1
            
        if self.frame > len(self.flag_images)-1:
            self.frame=0
        
    

class Item(decor):
    '''can be picked up by the player'''
    def __init__(self,x,y,varient,grid_cursor):
        super().__init__(x,y,varient,grid_cursor)
        self.height=self.image.get_height()
        self.width=self.image.get_width()
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        self.collision=False
        self.number=0

    def draw(self,win,player):
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        if not self.collision:
            win.blit(self.image,(self.x,(self.y-8*math.sin(self.number))-8))
            self.number+=0.1*framerate_adjustment
            if self.rect.colliderect(player.rect) and not player.game_paused:
                if self.varient == 'health' and player.health < player.max_health: 
                    player.health+=2 #heals the player by the appropriate amount
                    
                    if player.health > player.max_health:
                        player.health=player.max_health
                        
                    self.collision=True

                elif self.varient == 'heart':
                    player.max_health+=2 #increases the players max health
                    player.health=player.max_health
                    self.collision=True

                elif self.varient == 'trophy':
                    player.trophies_collected+=1 #adds a trophy to the players collection
                    self.collision=True
                    nonCollision_list.append(score_indicator(self.x,self.y,50))
                    player.score+=50

                elif self.varient == 'key' and not player.key:
                    player.key=True #the player is able to open locked doors
                    self.collision=True
                
                
        

class rotating_obsticle(decor):
    '''a non collidable rotating obsticle'''
    def __init__(self,x,y,varient,grid_cursor):
        super().__init__(x,y,varient,grid_cursor) #inherits from the decor class
        self.rotation=0
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        self.speed=4
        self.direction=1
        self.cooldown=0

    def draw(self,win,player):
        self.rect=pygame.Rect(self.x+16,self.y,self.width-32,self.height)
        self.rotation-=round(6*framerate_adjustment) #increments rotation value
        image=pygame.transform.rotate(self.image,self.rotation) #rotates the image
        win.blit(image,((self.x-(image.get_width()//2))+self.width//2,(self.y-(image.get_height()//2))+self.height//2))
        global onScreen_collision_list
        
        for item in onScreen_collision_list: #changes the direction if the obsticle hits something
            if not item.offscreen:
                if item.rect.colliderect(self.rect):
                    if item.y > self.y:
                        self.direction=-1
                    else:
                        self.direction=1
                    break

        if self.rect.colliderect(player.rect) and self.cooldown == 0: #harms the player
            player.harm_player(2,self)
            self.cooldown=60//framerate_adjustment
            player.death_message='You were sliced in two'

        if self.cooldown != 0: #controls the rate at which the player is harmed
            self.cooldown-=1

        self.y+=(self.speed*framerate_adjustment)*self.direction #moves the obsticle

class plant_decor(decor):
    '''a non collidable leaf particle emitter'''
    def __init__(self,x,y,varient,grid_cursor):
        super().__init__(x,y,varient,grid_cursor) #inherits from the decor class

    def draw(self,win):
        win.blit(self.image,(self.x,self.y))
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        if random.randint(1,100) == 1: # 1/100 chance of emitting a leaf particle
            nonCollision_list.append(precipitation(random.randint(self.x,self.x+self.width),random.randint(self.y,self.y+(self.height)//2),'leaf',(None,None))) #particle object is added to the level

class interactable_plant(decor):
    '''a plant that will react to the player walking past'''
    def __init__(self,x,y,varient,grid_cursor):
        super().__init__(x,y,varient,grid_cursor) #inherits from decor class
        self.adjustment=0
        self.width=self.image.get_width()
        self.height=self.image.get_height()
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        self.animation=0
        self.in_animation=False

    def draw(self,win,player):
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        if self.rect.colliderect(player.rect) or self.check_enemy_collision(): #detects when animation should play
            if not self.in_animation:
                self.animation=5
                self.in_animation=True
        else:
            if self.animation <= 0: #resets whan animation is done
                self.in_animation=False
                self.animation=0
                self.adjustment=0

        if self.in_animation and self.animation > 0:
            self.adjustment=round(self.adjustment-math.sin(self.animation)) #creates a smooth angle to sway the plant to
            self.animation-=0.4*framerate_adjustment

        image=pygame.transform.rotate(self.image,self.adjustment) #plant is swayed 
        win.blit(image,(self.x,self.y))

    def check_enemy_collision(self):
        '''detects if another entity is interacting with the plant'''
        for item in nonCollision_list:
            if not item.offscreen and (class_type(item) == 'enemy' or class_type(item) == 'returning_projectile'):
                if self.rect.colliderect(item.rect):
                    return True
        return False

class checkpoint(decor):
    '''a place where players progress is saved within the level'''
    def __init__(self,x,y,varient,grid_cursor):
        super().__init__(x,y,varient,grid_cursor)
        self.width=self.image.get_width()
        self.height=self.image.get_height()
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        self.active=False
        self.flag_adjustment=6*self.height//10
        self.flag_height=self.y+self.flag_adjustment
        self.frame=0
        self.cooldown=0
        self.flag_images=[pygame.image.load(image_path+'checkpoint flag 0.png').convert_alpha(),pygame.image.load(image_path+'checkpoint flag 1.png').convert_alpha(),
                          pygame.image.load(image_path+'checkpoint flag 2.png').convert_alpha(),pygame.image.load(image_path+'checkpoint flag 3.png').convert_alpha()] #holds the flag animation #holds the flag animation

    def draw(self,win,player):
        self.flag_height=self.y+self.flag_adjustment
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        win.blit(self.image,(self.x,self.y))
        
        win.blit(self.flag_images[self.frame],(self.x+self.width//2+4,self.flag_height)) #animates the flag
        if self.cooldown == 0: #keeps the animation at a constant rate
            self.frame+=1
            self.cooldown=10/framerate_adjustment
        else:
            self.cooldown-=1
            
        if self.frame > len(self.flag_images)-1:
            self.frame=0

        if not self.active:
            if self.rect.colliderect(player.rect): #detects if player is near
                self.active=True
                player.respawn_distance=0
                player.respawn_height=0
                player.spawnY=self.initialY
                player.cameraY=player.camera_moved
                

        else:
            if self.flag_height > self.y: #raises the flag
                self.flag_adjustment-=round(4*framerate_adjustment)
                
    def reset(self):
        self.active=False
        self.flag_adjustment=6*self.height//10
        self.flag_height=self.y+self.flag_adjustment
        
            
        
class precipitation(decor):
    '''falls from the sky disapears when in collision'''
    def __init__(self,x,y,varient,grid_cursor):
        super().__init__(x,y,varient,grid_cursor) #inherits from the decor class
        self.speed=random.randint(1,2) #random speed is given for some visual variety
        self.dead=False
        self.animation=None
        self.splash_image=pygame.image.load(image_path+'raindrop splash.png').convert_alpha()

    def draw(self,win):
        self.x+=round(self.speed*framerate_adjustment)
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)

        if self.varient in ['raindrop 0','raindrop 1','raindrop 2']: #rain will fall faster
            self.y+=round(4*self.speed*framerate_adjustment)
        else:
            self.y+=round(2*self.speed*framerate_adjustment)
                
        win.blit(self.image,(self.x,self.y))



            
            

class particle(decor):
    '''a non collision moving decoration'''
    def __init__(self,x,y,varient,grid_cursor):
        super().__init__(x,y,varient,grid_cursor) #inherits from the decor class
        self.speed=random.randint(1,2) #random speed is given for some visual variety
        self.dead=False

    def draw(self,win):
        self.x+=round(self.speed*framerate_adjustment)
              
        win.blit(self.image,(self.x,self.y))
    

class rising_decor(decor):
    '''upwards moving decoration'''
    def __init__(self,x,y,varient,grid_cursor):
        super().__init__(x,y,varient,grid_cursor) #inherits from the decor class
        self.speed=4
        self.distance_travelled=0
        self.duration=random.randint(20,40)//framerate_adjustment #takes a random amount of time to explode
        self.total_duration=self.duration
        self.max_distance=random.randint(240,300) #travels upwards by a random amount
        self.explosion=0
        self.explosion_animation=[pygame.image.load(image_path+'firework explosion 3.png').convert_alpha(),pygame.image.load(image_path+'firework explosion 2.png').convert_alpha(),
                                  pygame.image.load(image_path+'firework explosion 1.png').convert_alpha(),pygame.image.load(image_path+'firework explosion 0.png').convert_alpha()] #holds the explosion animation
        self.dead=False

    def draw(self,win):
        if self.varient == 'firework' and self.distance_travelled > self.max_distance:
            self.explosion=True
            self.image=self.explosion_animation[round((self.duration/self.total_duration)*3)] #firework explodes

        if not self.explosion:
            self.y-=round(self.speed*framerate_adjustment)
            self.distance_travelled+=self.speed*framerate_adjustment
        else:
            self.duration-=1

        if self.duration == 0:
            self.dead=True
            
        win.blit(self.image,(self.x,self.y))

class returning_projectile(decor):
    '''used to fire at enemies'''
    def __init__(self,x,y,varient,direction,shooter,coordinates,grid_cursor):
        super().__init__(x,y,varient,grid_cursor) #inherits from the decor class
        self.height=self.image.get_height()
        self.width=self.image.get_width()
        self.speed=16
        self.Yspeed=self.speed
        self.return_value=0
        self.direction=direction
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        self.shooter=shooter #holds the object that shot the projectile
        self.collision=False
        self.dealt_damage=False
        self.secondX=coordinates[0] #holds the destination
        self.secondY=coordinates[1]
        self.angle=math.atan2((self.y-self.secondY),(self.x-self.secondX)) #calculates the angle of travel
        self.spin=0
        self.return_strength=0.25

    def draw(self,win,player):
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        self.x-=round(math.cos(self.angle)*self.speed*framerate_adjustment) #travels along the angle
        self.y-=round(math.sin(self.angle)*self.speed*framerate_adjustment)
        
        self.speed-=self.return_strength*framerate_adjustment

        self.spin+=16*framerate_adjustment

        if self.speed < 0:
            self.angle=math.atan2((player.y-self.y),(player.x-self.x))
        
        self.check_collision(player)
        image=pygame.transform.rotate(self.image,self.spin) #spins the projectile
        win.blit(image,((self.x-(image.get_width()//2))+self.width//2,self.y))

    def check_collision(self,player):
        global onScreen_collision_list
        
        if self.speed < 0 and self.rect.colliderect(player.rect):
            self.collision=True

        elif self.speed < -100 or self.speed > 100: #if the projectile has accelerated to a high amount it is removed
            self.collision=True
            
        for item in onScreen_collision_list:
            if not item.offscreen and class_type(item) not in ['platform'] and not item.dead:
                if self.rect.colliderect(item.rect):
                    if not self.dealt_damage:
                        self.speed*=-1 #projectile is bounced
                        self.dealt_damage=True
                    else:
                        if self.speed < -16:
                            self.collision=True #if the projectile has already bounced it is removed

        for item in nonCollision_list:
            if not item.offscreen and class_type(item) in ['enemy'] and not item.dead:
                if self.rect.colliderect(item.rect):
                    if not self.dealt_damage: #if the projectile has not already hit an enemy
                        self.speed*=-1

class projectile(decor):
    '''used to fire at enemies'''
    def __init__(self,x,y,varient,direction,shooter,coordinates,grid_cursor):
        super().__init__(x,y,varient,grid_cursor) #inherits from the decor class
        self.height=self.image.get_height()
        self.width=self.image.get_width()
        self.speed=16
        self.Yspeed=self.speed
        self.return_value=0
        self.direction=direction
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        self.shooter=shooter #holds the object that shot the projectile
        self.collision=False
        self.secondX=coordinates[0] #holds the destination
        self.secondY=coordinates[1]
        self.angle=math.atan2((self.y-self.secondY),(self.x-self.secondX)) #calculates the angle of travel
        self.spin=0
        self.gravity_value=0

    def draw(self,win,player):
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        if not player.game_paused:
            self.x-=round(math.cos(self.angle)*self.speed*framerate_adjustment) #projectile travels along the angle
            self.y-=round(math.sin(self.angle)*self.speed*framerate_adjustment)

            self.y+=self.gravity_value
            self.gravity_value+=0.05*framerate_adjustment

        angle=math.degrees(self.angle)
        image=pygame.transform.rotate(self.image,angle) #image is angled the same as its path

        image=pygame.transform.flip(image,True,False)
        
        self.check_collision(player)
        win.blit(image,((self.x-(image.get_width()//2))+self.width//2,self.y))

    def check_collision(self,player):
        global onScreen_collision_list
        
        if self.rect.colliderect(player.rect) and class_type(self.shooter) in ['enemy','turret']: #if an enemy shot it the player is harmed
            self.collision=True
            player.harm_player(self.shooter.damage,self.shooter)
            player.death_message='You were shot to death'
            if self.shooter.varient == 'snowman':
                player.death_message='You were frostbitten'
            elif self.shooter.varient == 'magma king':
                player.death_message='Bit too toasty!'

        elif self.speed < -100 or self.speed > 100: #if the projectile is travelling too fast it is removed
            self.collision=True
            
        for item in onScreen_collision_list:
            if not item.offscreen and class_type(item) not in ['platform'] and not item.dead:
                if self.rect.colliderect(item.rect): #checks if it has hit a solid object
                    self.collision=True

        for item in nonCollision_list:
            if not item.offscreen and class_type(item) in ['enemy'] and not item.dead and class_type(self.shooter) == 'player':
                if self.rect.colliderect(item.rect): #checks if it hit an enemy
                    self.collision=True

class rotating_decor(decor):
    '''class used for spinning decorations'''
    def __init__(self,x,y,varient,grid_cursor):
        super().__init__(x,y,varient,grid_cursor) #inherits from decor
        self.rotating_image=pygame.image.load(image_path+self.varient+' blades.png').convert_alpha() #stores the blades image
        self.rotation=0
        
    def draw(self,win):
        self.rotation-=round(1*framerate_adjustment) #increments rotation value
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        win.blit(self.image,(self.x,self.y))
        rotating_image=pygame.transform.rotate(self.rotating_image,self.rotation) #rotates the blades
        win.blit(rotating_image,(self.x+self.width//2-(rotating_image.get_width()//2),self.y-rotating_image.get_height()//2+self.height//10))

class sign(decor):
    '''a non collision text displayer'''
    def __init__(self,x,y,varient,text,grid_cursor):
        super().__init__(x,y,varient,grid_cursor) #inherits from the decor class
        font=pygame.font.SysFont('ocr a extended',30)
        text=text.strip('\n')
        self.text=font.render(text,1,(255,255,255))
        self.width=self.image.get_width()
        self.height=self.image.get_height()
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        self.in_range=False
        self.text_pos=((self.x-self.text.get_width()//2)+self.width//2,self.y-self.text.get_height())
        
    def draw(self,win,player):
        self.text_pos=(round((self.x-self.text.get_width()//2)+self.width//2),round(self.y-self.text.get_height())) #position where the text is drawn
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
        
        if self.rect.colliderect(player.rect): #detects if player is near
            self.in_range=True
        else:
            self.in_range=False
            
        win.blit(self.image,(self.x,self.y))

    def update_text(self,file_name,current_level,new_text):
        font=pygame.font.SysFont('ocr a extended',30)
        self.text=font.render(new_text,1,(255,255,255))
        edit_asset(file_name,current_level,class_type(self),self.varient,self.initialX,self.initialY,new_text)
        

class Background:
    '''class used to hold level information to return to the calling program'''
    def __init__(self,background,background_dimensions):
        self.background=background
        self.original_background=background
        self.background_dimensions=background_dimensions

class score_indicator:
    '''displays when a player has gained score'''
    def __init__(self,x,y,score):
        self.score=score
        self.x=x
        self.y=y
        self.font=pygame.font.SysFont('ocr a extended',25,True,True) #makes the text bold and italic
        self.text=self.font.render('+'+str(self.score)+' Pts',1,(0,255,255))
        self.width=self.text.get_width()
        self.height=self.text.get_height()
        self.dead=False
        self.time=100//framerate_adjustment
        self.number=0
        self.varient=str(self.score)
        self.offscreen=False

    def draw(self,win):
        self.text=self.font.render('+'+str(self.score)+' Pts',1,(0,235+round(20*math.sin(self.number)),255))
        self.y-=1
        win.blit(self.text,(self.x,self.y))
        self.number+=0.5*framerate_adjustment #causes the text to flash

        self.time-=1
        if self.time == 0:
            self.dead=True
    

def bubble_sort(array):
    '''sorts an array into accending order'''
    swap_made=False
    i=0
    while i < len(array)-1:
        if array[i][array[i].find('.'):] > array[i+1][array[i+1].find('.'):]:
            value1=array[i]
            value2=array[i+1]
            array[i]=value2
            array[i+1]=value1
            swap_made=True
        i+=1
    if swap_made:
        bubble_sort(array)
    return array

def initiate_login():
    '''returns a list of user objects containing their data'''
    file=open(file_path+'Player Data.txt')
    read_file=file.read()
    file.close()
    read_file=read_file.split('\n') #reads in the data from the file
    
    user_list=[]
    for item in read_file: #each entry in the file is split into its data
        item=item.split('|')
        if len(item) > 1:
            user_list.append(user(item[0],item[1],item[2],item[3])) #user objects are created containing this data

    return user_list

def username_taken(username,user_list):
    '''checks if a username is already taken'''
    for item in user_list:
        if item.username == username:
            return True
    return False

def reset_user(username,current_user):
    '''resets the users progress in the built in level'''
    file=open(file_path+'Player Data.txt')
    read_file=file.readlines()
    file.close()

    index=0
    for item in read_file:
        split_item=item.split('|') #line is split up
        if split_item[0] == username:
            read_file[index]=split_item[0]+'|'+split_item[1]+'|'+'Level 0|0,0|\n' #default user account is writen to the same line
        index+=1

    update_file('Player data',read_file,False)

    current_user.data='Level 0'

def get_level_stats(user,level_type,level_name):
    '''returns the highest score and fastest time
    the user has acheived in that level'''
    file=open(file_path+'Player Data.txt')
    read_file=file.readlines()
    file.close()
    
    for item in read_file:
        split_item=item.split('|')
        if split_item[0] == user.username: #locates the user in the file
            levels_completed=split_item[4].strip('\n')
            levels_completed=levels_completed.split(',')
            
            for item in levels_completed: #locates the required level within the players completed levels
                level_info=item.split('.')
                if level_info[0] == level_type and level_info[1] == level_name:
                    return level_info[2], level_info[3]
                
    return None, None
            
    

def store_level_stats(user,level_type,level_name,score,time):
    '''stores the score and completion time of a level'''
    file=open(file_path+'Player Data.txt')
    read_file=file.readlines()
    file.close()
    
    change_made=False
    index=0
    for item in read_file:
        split_item=item.split('|')
        if split_item[0] == user.username: #locates the user in the file
            levels_completed=split_item[4].strip('\n')
            levels_completed=levels_completed.split(',')
            
            if levels_completed[0] == '': #prevents an empty value from being stored
                del levels_completed[0]
                
            found_level=False

            lev_index=0
            for level in levels_completed:
                if level_type+'.'+level_name+'.' in level:
                    level_stats=level.split('.')
                    found_level=True
                    if int(level_stats[2]) < score or int(level_stats[3]) > time: #if the new score is higher or new time lower
                        if int(level_stats[2]) > score:
                            score=level_stats[2]

                        if int(level_stats[3]) < time:
                            time=level_stats[3]
                            
                        levels_completed[lev_index]=level_stats[0]+'.'+level_stats[1]+'.'+str(score)+'.'+str(time) #new bests are stored
                        change_made=True
                    break
                
                lev_index+=1

            if not found_level:
                levels_completed.append(level_type+'.'+level_name+'.'+str(score)+'.'+str(time)) #if the level hasnt been played before it is added
                change_made=True
                
            break           
        index+=1

    if change_made:
        level_list=''
        Index=0
        for item in levels_completed:
            if Index != len(levels_completed)-1: #ensures the levels are split by comma correctly
                level_list+=item+','
            else:
                level_list+=item
            Index+=1
            
        read_file[index]=split_item[0]+'|'+split_item[1]+'|'+split_item[2]+'|'+split_item[3]+'|'+level_list+'\n' #players line in the file is updated
        
        update_file('player data',read_file,False)
            
    
    
    

def change_setting(user,setting_index,setting_value):
    '''resets the users progress in the built in level'''
    file=open(file_path+'Player Data.txt')
    read_file=file.readlines()
    file.close()

    setting_value=str(setting_value)

    index=0
    for item in read_file:
        split_item=item.split('|')
        if split_item[0] == user.username: #locates the user in the file
            settings_list=(split_item[3].strip('\n')).split(',')
            settings_list[setting_index]=setting_value

            new_settings=''
            list_index=0
            for item in settings_list: #the users settings are changed and converted into a string
                if list_index != len(settings_list)-1:
                    new_settings+=item+','
                else:
                    new_settings+=item
                list_index+=1
                 
            read_file[index]=split_item[0]+'|'+split_item[1]+'|'+split_item[2]+'|'+new_settings+'|'+split_item[4]+'\n' #users line in the file is changed
        index+=1

    update_file('Player data',read_file,False)

    update_settings(user)

    

def update_settings(current_user):
    '''locates the user from the file and updates their settings'''
    file=open(file_path+'player data.txt')
    read_file=file.readlines()
    file.close()
    
    for item in read_file:
        split_item=item.split('|')
        if split_item[0] == current_user.username: #user is located in the file
            current_user.update_settings(split_item[3])
            break
    
            

def validate_user(user,password,user_list):
    '''checks if the password for that user is valid'''
    index=0
    for item in user_list: #checks through every user
        if item.username == user:
            if item.password == password: #decides if password is correct
                return True
            else:
                return False
    return False

def create_user(user_list,username,password,data):
    '''writes a new user to the file'''
    file=open(file_path+'Player Data.txt','a')
    for item in user_list:
        if item.username == username: #stops repeat usernaes from being added
            return False

    file.write(username+'|'+password+'|'+data+'|0,0|\n') #new user is added to file
    file.close()
    return True

def delete_user(user_list,user):
    '''removes a user from the file'''
    file=open(file_path+'Player Data.txt')
    read_file=file.read()
    file.close()
    read_file=read_file.split('\n')
    
    index=0
    for item in user_list: #finds the user to be deleted
        if item.username == user:
            read_file.pop(index) #user is deleted from file
            user_list.pop(index)
            break
        index+=1

    open(file_path+'Player Data.txt','w').write('') #file is wiped
    file=open(file_path+'Player Data.txt','a')
    for line in read_file: #new contents are wrote
        if line != '': #prevents empty lines
            file.write(line+'\n')

    file.close()

    return user_list

def boot_screen():
    '''displays once the game is launched'''
    font=pygame.font.SysFont('ocr a extended',80,True)
    small_font=pygame.font.SysFont('ocr a extended',20,True)

    file=open(file_path+'Game Levels.txt') #stores the game levels
    read_file=file.readlines()
    file.close()

    editor_file=open(file_path+'player Levels.txt') #stores the player levels
    editor_read=editor_file.readlines()
    editor_file.close()

    global game_levels
    game_levels=[]
    global editor_previews
    editor_previews=[]
    index=0
    editor_index=0
    
    for i in range(0,255,2):
        leave_game=get_events()[1]
        screen_width, screen_height = win.get_width(), win.get_height()
        
        win.fill((255,255,255))
        text=font.render('=CASTLE QUEST=',1,(i,i,i))
        sub_text=small_font.render('- Hope You Enjoy :) -',1,(i,i,i))

        position=(screen_width//2-text.get_width()//2,screen_height//2-text.get_height()) #finds the centre of the screen
        win.blit(text,position)
        win.blit(sub_text,(screen_width//2-sub_text.get_width()//2,position[1]+text.get_height()))

        loading_barY=position[1]+text.get_height()+sub_text.get_height()+20
        loading_barWidth=text.get_width()
        loading_barX=screen_width//2-loading_barWidth//2 #finds the placement for the loading bar
        
        pygame.draw.rect(win,(i,i,i),(loading_barX,loading_barY,loading_barWidth,40),2)
        pygame.draw.rect(win,(i,i,i),(loading_barX,loading_barY,round(loading_barWidth*(i/255)),40))

        clock.tick(60)
        pygame.display.flip()

        if index < len(read_file):
            game_levels, index = preload_game_levels(game_levels,index,read_file) #creates a list of available levels as buttons
            
        elif editor_index < len(editor_read):
            editor_previews, editor_index = preload_editor_previews(editor_previews,editor_index) #creates a list of previews of levels
            

        if leave_game:
            break

    return leave_game

def preload_game_levels(button_list,index,read_file):
    '''loads all the level slots that appear in the main game'''
    preview=create_preview('game levels',index)
    item=read_file[index]
        
    button_list.append(user_slot(win.get_width()//2,index*100,400,100,item[:item.find('.')],'- Level '+str(index)+' -',(220+20*(index%2),140+20*(index%2),50+20*(index%2)),None,preview))
    index+=1

    return button_list, index

def preload_editor_previews(editor_previews,index):
    '''loads all the previews for the editor levels'''
    preview=create_preview('player levels',index)
    editor_previews.append(preview)
    
    index+=1
    return editor_previews, index
    

def draw_points(player,offset,colour_num):
    '''displays the players current score'''
    colour_num+=0.025*framerate_adjustment
    
    screen_width, screen_height = win.get_width(), win.get_height()
    
    font=pygame.font.SysFont('ocr a extended',40,True,True)
    
    points=font.render('SCORE: '+str(player.score),1,(0,round(215+40*math.sin(colour_num)),255))
    
    win.blit(points,(screen_width-(points.get_width()+offset+20),15))

    pygame.draw.line(win,(0,round(215+40*math.cos(colour_num)),255),(screen_width-(points.get_width()+offset+20),15),(screen_width-(offset+20),15),4)
    pygame.draw.line(win,(0,round(215+40*math.cos(colour_num)),255),(screen_width-(points.get_width()+offset+20),points.get_height()+15),(screen_width-(offset+20),points.get_height()+15),4)

    
    return colour_num

           
def draw_health(player):
    '''animates the players health to the screen'''
    health_amount=player.health
    player.health_bounce+=(0.08+(0.03*(player.max_health-player.health)))*framerate_adjustment #controls the rate of bounce
    for i in range(0,player.max_health//2):
        if health_amount >= 2: #calculates what state the heart icon should be
            win.blit(player.heart_full,(6+(i*81),round(5+(5*math.sin(player.health_bounce))))) #bounces the heart using sin
        elif health_amount >= 1:
            win.blit(player.heart_half,(6+(i*81),round(5+(5*math.sin(player.health_bounce)))))
        else:
            win.blit(player.heart_empty,(6+(i*81),round(5+(5*math.cos(player.health_bounce))))) #bounces the heart using cos to show its empty
        health_amount-=2 #keeps track of each heart drawn

def game_window(player,collision_list,nonCollision_list,screen_width,screen_height,red_tint,game_paused,current_level,game_position):
    '''draws the level and the player and updates offscreen assets'''
    if player.weather == 'rain': #sets the various background gradients
        win.fill((170,160,160))
        pygame.draw.rect(win,(175,165,165),(0,round(screen_height*(1/3)),screen_width,round(screen_height*(1/3))))
        pygame.draw.rect(win,(180,170,170),(0,round(screen_height*(2/3)),screen_width,round(screen_height*(2/3))))

    elif player.weather == 'snow':
        win.fill((220,220,220))
        pygame.draw.rect(win,(225,225,225),(0,round(screen_height*(1/3)),screen_width,round(screen_height*(1/3))))
        pygame.draw.rect(win,(230,230,230),(0,round(screen_height*(2/3)),screen_width,round(screen_height*(2/3))))

    else:
        win.fill((160,170,255))
        pygame.draw.rect(win,(165,175,255),(0,round(screen_height*(1/3)),screen_width,round(screen_height*(1/3))))
        pygame.draw.rect(win,(170,180,255),(0,round(screen_height*(2/3)),screen_width,round(screen_height*(2/3))))
    
    clock.tick(frame_rate) #constant framerate is maintained
    text_list=[]
    player.level_tick+=1*framerate_adjustment #used to map asset movement to
    player.game_paused=game_paused
    layer1=[]
    layer2=[]
    
    
    index=0
    for item in nonCollision_list:
        item.offscreen=False
        if (item.x < -item.width or item.x > screen_width+item.width or item.y < -item.height or item.y > screen_height+item.height) and class_type(item) not in ['returning_projectile','precipitation']: #calculates if an asset is offscreen
            item.offscreen=True
            if class_type(item) in ['particle','rising_decor','projectile','score_indicator']: #if items class type is a particle or projectile it will be deleted from the level as it is offscreen
                nonCollision_list.pop(index)
            
        else:
            if class_type(item) in ['interactable_plant','checkpoint','rotating_obsticle','Item','returning_projectile','goal','turret','projectile']: #interactable assets are given the players data
                if not item.dead:
                    item.draw(win,player)
                    if class_type(item) in ['Item','returning_projectile','projectile']:
                        if item.collision:
                            if class_type(item) == 'Item':
                                item.dead=True
                                item.collision=False
                            else:
                                nonCollision_list.pop(index)
                                        

            elif class_type(item) in ['enemy']:
                if item.y < screen_height and not item.dead:
                    layer1.append(item)  
                    if item.knockback != 0:
                        knockback(item,item.knockback,item.knockback_direction)
                else:
                    item.offscreen=True
                
            elif class_type(item) in ['sign']:
                item.draw(win,player)
                if item.in_range: #if player is near the text is displayed
                    text_list.append((item.text,item.text_pos))
                    
            elif class_type(item) in ['liquid','front_decor']: #liquids drawn after player
                layer2.append(item)

            elif class_type(item) in ['rising_decor','particle','precipitation','score_indicator']:
                item.draw(win)
                if item.dead:
                    nonCollision_list.pop(index)

                if (item.x < -320 or item.x > screen_width or item.y < -item.height or item.y > screen_height+item.height) and class_type(item) == 'precipitation':
                    item.offscreen=True
                    nonCollision_list.pop(index)
                
            else:
                item.draw(win) #asset is drawn to the game window
        index+=1

    player.draw(win)

    for item in layer1:
        item.draw(win,player)

    for item in layer2: #items drawn infront of the player
        if class_type(item) in ['front_decor']:
            item.draw(win)
        else:
            item.draw(win,player)

    global onScreen_collision_list
    onScreen_collision_list=[]
                
    for item in collision_list:
        item.offscreen=False
        if item.x < -item.width or item.x > screen_width+item.width or item.y < -80 or item.y > screen_height+160: #calculates if an asset is offscreen
            item.offscreen=True
        else:
            onScreen_collision_list.append(item)
            if class_type(item) in ['solid_obsticle','unstable_tile','door']: #interactable assets are given the players data
                item.draw(win,player)
            else:
                item.draw(win) #asset is drawn to the game window

    for item in text_list: #draws text infront of everything
        win.blit(item[0],item[1])

    if player.knockback != 0:
        knockback(player,player.knockback,player.knockback_direction)

    if player.hurt_animation != 0:
        red_tint.fill((250,0,0,2*player.hurt_animation*framerate_adjustment))
        win.blit(red_tint,(0,0))

    if player.won and not game_paused:
        level_complete(player,current_level,game_position)
        player.game_paused=False

    if not game_paused:
        draw_health(player) #players health is displayed
        
        if player.available_trophies != 0:
            trophy_image=pygame.image.load(image_path+'trophy.png').convert_alpha()
            position=(screen_width-trophy_image.get_width()-10,screen_height-trophy_image.get_height()-5)
            win.blit(trophy_image,position)

            font=pygame.font.SysFont('ocr a extended',40,True)
            trophy_text=font.render(str(player.trophies_collected)+'/'+str(player.available_trophies),1,(255,255,30))
            win.blit(trophy_text,(position[0]-trophy_text.get_width()-5,position[1]+20)) #displays the players trophy progress

            pygame.draw.line(win,(255,255,0),(position[0]-trophy_text.get_width(),screen_height-4),(position[0]+trophy_image.get_width()-5,screen_height-4),4)

        if player.key:
            key=pygame.image.load(image_path+'key.png').convert_alpha()
            win.blit(key,(5,screen_height-key.get_height()-5)) #displays the player has a key
            pygame.draw.line(win,(255,255,0),(5,screen_height-4),(key.get_width()+5,screen_height-4),4)

def help_page(player,red_tint,win):
    '''Displays information about the level editor'''
    font=pygame.font.SysFont('ocr a extended',60)
    small_font=pygame.font.SysFont('ocr a extended',30)
    help_text=font.render('- HOW TO USE -',1,(255,255,255))
    back_button=button(0,0,pygame.image.load(image_path+'back.png'),(100,100,200))
    information=['- Use WASD or ARROR KEYS to move around','- Press DELETE to toggle between place and delete mode',
                 '- Point and click the mouse to place/delete','- Type in an asset and hit ENTER to select an item',
                 '- Press ESCAPE to bring up the menu','- Progress is autosaved after each click']
    run=True
    leave_game=False
    while run and not leave_game:
        win.fill((200,200,200))

        level_info=level_events(player,red_tint,win)
        leave_game=not level_info[0]
        red_tint=level_info[4]
        
        screen_width, screen_height = win.get_width(), win.get_height()
        
        pygame.draw.rect(win,(100,100,100),(0,0,screen_width,100)) #draws a bar across the top of the screen 
        pygame.draw.rect(win,(100,100,100),(0,screen_height-100,screen_width,100))

        win.blit(help_text,(screen_width//2-help_text.get_width()//2,10))

        back_button.draw(win)
        if back_button.clicked:
            run=False
            back_button.clicked=False

        index=0
        for item in information: #displays the information line by line
            text=small_font.render(item,1,(255,255,255))
            win.blit(text,(5,105+(index*text.get_height())))
            index+=1
            
        pygame.display.flip()
        clock.tick(60)

    return leave_game, red_tint

def settings_menu(user,main_menu):
    '''allows the user to change their preferances for the game'''
    global framerate_adjustment
    font=pygame.font.SysFont('ocr a extended',60)
    settings_text=font.render('- SETTINGS -',1,(255,255,255))
    
    confirm_reset=confirmation_box(0,0,'Are you sure?',(140,140,140)) #GUI components are defined
    back_button=button(0,0,pygame.image.load(image_path+'back.png'),(100,100,200))
    
    reset_button=button(0,110,font.render(' Reset Progress ',1,(255,255,255)),(240,140,50))
    reset_info=prompt(0,0,('Resets your progress in the','main game your custom levels remain'),(180,180,180))
    
    fps_switch=switch(0,200,font.render('   Show FPS    ',1,(255,255,255)),(240,130,50),bool(int(user.settings[0])))
    fps_info=prompt(0,0,('Shows how many frames','are being displayed per second'),(180,180,180))
    
    fps_30_switch=switch(0,290,font.render('  30 FPS Mode  ',1,(255,255,255)),(240,120,50),bool(int(user.settings[1])))
    fps_30_info=prompt(0,0,('Sets the framerate to 30','good for a potato PC'),(180,180,180))
        
    show_confirmation=False
    run=True
    leave_game=False
    while run and not leave_game:
        current_events=get_events() 
        leave_game = current_events[1]
        mouse_pos=pygame.mouse.get_pos()

        screen_width, screen_height = win.get_width(), win.get_height()

        reset_button.x=(screen_width-reset_button.width)//2 #buttons are positioned in centre of screen
        fps_switch.x=(screen_width-fps_switch.width)//2
        fps_30_switch.x=(screen_width-fps_30_switch.width)//2

        win.fill((200,200,200))
        
        pygame.draw.rect(win,(100,100,100),(0,0,screen_width,100)) #draws a bar across the top of the screen 
        pygame.draw.rect(win,(100,100,100),(0,screen_height-100,screen_width,100))

        win.blit(settings_text,(screen_width//2-settings_text.get_width()//2,10))
        
        back_button.draw(win)
        reset_button.draw(win)
        fps_switch.draw(win)
        fps_30_switch.draw(win)

        if back_button.clicked:
            run=False
            back_button.clicked=False

        if fps_switch.highlighted: #shows the prompt if mouse is above the button
            fps_info.x, fps_info.y = mouse_pos
            fps_info.draw(win)
            if fps_switch.clicked:
                change_setting(user,0,int(fps_switch.state))
                fps_switch.clicked=False
                
        elif fps_30_switch.highlighted:
            fps_30_info.x, fps_30_info.y = mouse_pos
            fps_30_info.draw(win)
            if fps_30_switch.clicked:
                change_setting(user,1,int(fps_30_switch.state))
                fps_30_switch.clicked=False
        
        elif reset_button.highlighted:
            reset_info.x, reset_info.y = mouse_pos
            reset_info.draw(win)
            if reset_button.clicked:
                show_confirmation=True
                reset_button.clicked=False

        if show_confirmation: #displays a confirmation for resetting a user
            confirm_reset.x=reset_button.x+reset_button.width
            confirm_reset.y=reset_button.y
            confirm_reset.draw(win)
            if confirm_reset.confirmation is not None:
                if confirm_reset.confirmation:
                    reset_user(user.username,user)
                    run=False
                    main_menu=True
                    
                show_confirmation=False
                confirm_reset.confirmation=None
            

        pygame.display.flip()
        clock.tick(60)

    if user.fps_30: #framerate is set to the correct value
        framerate_adjustment=change_framerate(30)
    else:
        framerate_adjustment=change_framerate(60)

    return leave_game, main_menu
        

def pause_menu(continue_button,settings_button,main_menu_button,exit_button,editor_button,game_position,player,red_tint):
    '''a menu to display within the level giving options to navigate the game'''
    leave_game=False
    paused=True
    main_menu=False
    in_game=True
    
    font=pygame.font.SysFont('ocr a extended',60)
    small_font=pygame.font.SysFont('ocr a extended',20)

    game_tips=('TIP: Crouch to get through small areas.','TIP: The way forward is not always forward.',
               'TIP: Stand near signs to view their text','TIP: Point and click the mouse to throw a hammer')  #holds some tips to display in the menu
    
    pause_text=font.render('- GAME PAUSED -',1,(255,255,255))
    pause_tip=small_font.render(random.choice(game_tips),1,(255,255,255))
    
    while paused and not leave_game:
        game_events=level_events(player,red_tint,win) #checks for any changes in window size or quitting via GAME OBJECTS
        run, screen_width, screen_height, events, red_tint = game_events
        leave_game = not run
        game_window(player,collision_list,nonCollision_list,screen_width,screen_height,red_tint,True,None,game_position) #displays the game in the background
        
        pygame.draw.rect(win,(100,100,100),(0,0,screen_width,100)) #draws rectangles across the top and bottom of the screen
        pygame.draw.rect(win,(100,100,100),(0,screen_height-100,screen_width,100))
        pygame.draw.rect(win,(130,130,130),(0,0,screen_width,100),10)
        pygame.draw.rect(win,(130,130,130),(0,screen_height-100,screen_width,100),10)

        win.blit(pause_text,((screen_width-pause_text.get_width())//2,10))
        win.blit(pause_tip,((screen_width-pause_tip.get_width())//2,screen_height-pause_tip.get_height()-50))
        
        continue_button.draw(win) #GUI components drawn
        settings_button.draw(win)
        main_menu_button.draw(win)
        exit_button.draw(win)
        
        if game_position == 'editor': #editor button added if playing the game via the editor
            editor_button.draw(win)
            
            if editor_button.clicked:
                for item in collision_list: #resets the camera back to the player
                    item.x-=player.distance_travelled
                    item.y-=player.camera_moved
                for item in nonCollision_list:
                    item.x-=player.distance_travelled
                    item.y-=player.camera_moved

                reset_level(player)

                player.distance_travelled=0
                player.camera_moved=0
                player.respawn_distance=0
                    
                in_game=False
                paused=False
                
                editor_button.clicked=False

        if continue_button.clicked: #buttons purposes are defined
            paused=False
            continue_button.clicked=False

            if game_position == 'editor level':
                in_game=False
                
    
        elif main_menu_button.clicked:
            paused=False
            main_menu_button.clicked=False
            
            main_menu=True

        elif settings_button.clicked:
            leave_game, main_menu = settings_menu(player.user,False)
            settings_button.clicked=False
            if main_menu:
                paused=False

        elif exit_button.clicked:
            leave_game=True
        
        pygame.display.flip()

    return leave_game, screen_width, screen_height, main_menu, in_game, red_tint

def run_main_menu(current_user,player):
    '''handles the execution of the main menu'''
    leave_game=False
    sin_number=0
    run_menu=True
    
    big_font=pygame.font.SysFont('ocr a extended',80)
    small_font=pygame.font.SysFont('ocr a extended',15)
    
    play_button=button(0,350,big_font.render('    PLAY    ',1,(255,250,250)),(240,140,50)) #GUI buttons are defined
    designer_button=button(0,450,big_font.render('  DESIGNER  ',1,(255,250,250)),(240,130,50))
    settings_button=button(0,550,big_font.render('  SETTINGS  ',1,(255,250,250)),(240,120,50))
    exit_button=button(0,650,big_font.render('    EXIT    ',1,(255,250,250)),(240,110,50))
    
    menu_background=Background(pygame.image.load(image_path+'plains background.png'),(1080,720)) #background for the menu is defined 
    menu_background.background=resize_background(win.get_width(),win.get_height(),menu_background) #background adjusted to the screen size
    
    credit_text=small_font.render('-An A-Level Project By Aydan Kirk-',1,(255,255,255))
    game_title=pygame.image.load(image_path+'Game Title.png')
    
    animation_num=0
    if current_user is None:
        animation_num=600 #if game has just been loaded the title will drop down
    
    while run_menu and not leave_game:
        events=get_events()
        screen_width, screen_height = events[2][0], events[2][1]

        if menu_background.background.get_width() < screen_width or menu_background.background.get_height() < screen_height: #handles the resizing of the background
            menu_background.background=resize_background(win.get_width(),win.get_height(),menu_background)

        menu_info=main_menu(play_button,designer_button,settings_button,exit_button,menu_background,credit_text,game_title,events,sin_number,current_user,player,animation_num) #menu is displayed
        
        run_menu, leave_game, game_position, current_user, level_index, animation_num, sin_number = menu_info
    
    return leave_game, current_user, game_position, level_index, screen_width, screen_height

    

def main_menu(play_button,designer_button,settings_button,exit_button,menu_background,credit_text,game_title,events,sin_number,current_user,player,animation_num):
    '''displays the main menu and returns the state of the game parameters'''
    run=True
    leave_game=False
    level_index=None
    game_position='main menu'
    
    win.blit(menu_background.background,(0,0)) #menu is drawn to the screen

    screen_width, screen_height = win.get_width(), win.get_height()

    win.blit(credit_text,(5,screen_height-credit_text.get_height()))
    win.blit(game_title,((screen_width-game_title.get_width())//2,(20+(10*math.sin(sin_number)))-animation_num))
    
    if animation_num > 2:
        animation_num/=1.05 #drops the title down
    else:
        sin_number+=0.1 #used to bob the title up and down
        
        play_button.draw(win)
        designer_button.draw(win)
        settings_button.draw(win)
        exit_button.draw(win)

    play_button.x=(screen_width-play_button.width)//2 #GUI buttons are adjusted to the centre of the screen
    designer_button.x=(screen_width-designer_button.width)//2
    settings_button.x=(screen_width-settings_button.width)//2
    exit_button.x=(screen_width-exit_button.width)//2

    if events[2][2] != 0 or events[2][3] != 0: #if there has been a change in the screen size background is adjusted
        menu_background.background=resize_background(screen_width,screen_height,menu_background)

    if events[1] or exit_button.clicked:
        leave_game=True
        run=False

    if play_button.clicked:
        if not current_user: #if the user isnt logged in they are shown the login menu
            login_info=run_login()
            current_user, leave_game, run = login_info

        else:
            run=False

        if current_user and not leave_game:
            menu_info=level_select_menu(player,current_user) #levels to select to play are shown
            leave_game, run, level_index = menu_info
            
        game_position='game'
        play_button.clicked=False
        
        

    elif designer_button.clicked:
        if not current_user: #if the user isnt logged in they are shown the login menu
            login_info=run_login()
            current_user, leave_game, run = login_info
            
        else:
            run=False

        if current_user and not leave_game:
            menu_info=creator_level_menu(player,current_user) #levels to select to play are shown
            leave_game, run, level_index, enable_edit = menu_info
            
            if enable_edit:
                game_position='editor'
            else:
                game_position='user level'
            
        designer_button.clicked=False

    elif settings_button.clicked:
        if not current_user: #if the user isnt logged in they are shown the login menu
            login_info=run_login()
            current_user, leave_game, run = login_info
            
        else:
            run=False

        if current_user and not leave_game:
            leave_game, main_menu=settings_menu(current_user,True)

        game_position='settings'

        settings_button.clicked=False
        
    
    pygame.display.flip()
    clock.tick(60)
    
    return run, leave_game, game_position, current_user, level_index, animation_num, sin_number

def run_login():
    '''handles the execution of the login system'''
    leave_game=False
    user_list=initiate_login() #use the GAME OBJECTS to create a list of user objects
    
    font=pygame.font.SysFont('ocr a extended',40)
    continue_button=button(0,0,font.render('  - Continue -  ',1,(255,255,255)),(100,200,100)) #the GUI objects are defined
    create_button=button(0,0,font.render('  - Add New User -  ',1,(255,255,255)),(100,200,100))
    delete_button=button(0,0,pygame.image.load(image_path+'cross.png'),(200,100,100))
    username_textbox=textbox(0,200,100,(600,600),(240,240,240))
    password_textbox=textbox(0,520,100,(600,600),(240,240,240))
    back_button=button(0,0,pygame.image.load(image_path+'back.png'),(100,100,200))
    confirm_delete=confirmation_box(0,0,'Are you sure?',(140,140,140))
    
    go_back=False
    password_valid=False
    in_menu=True
    while in_menu and not leave_game and not go_back:
        username_text='Enter The Username You Would Like To Use'
        password_text='Enter The Password For This Account'
            
        button_list=update_login_page(user_list) #creates a list of all the GUI objects
        scroll_value=1
        scroll_cooldown=0

        login_active=True
        delete_item=None
        while login_active and not leave_game and not go_back:
            current_events=get_events() #handles leaving and screen resizing via GAME OBJECTS
            leave_game, screen_width, screen_height = current_events[1], current_events[2][0], current_events[2][1]
            
            login_data=login_page(button_list,delete_button,user_list,create_button,back_button,scroll_value,scroll_cooldown,confirm_delete,delete_item) #displays the login page and returns the event data
            button_list, new_user, scroll_value, scroll_cooldown, selected_user, go_back, delete_item = login_data
            
            if selected_user:
                login_active=False

            while new_user and not leave_game:
                current_events=get_events() #handles leaving and screen resizing via GAME OBJECTS
                leave_game, screen_width, screen_height = current_events[1], current_events[2][0], current_events[2][1]
                
                page_data=new_user_page(username_textbox,password_textbox,current_events[0],username_text,password_text,continue_button,user_list,back_button,button_list) #displays the create account page
                new_user, button_list = page_data #event data is assigned to variables
                create_button.clicked=False

        password_box=textbox(0,400,100,(600,600),(240,240,240))
        password_active=True
        while not leave_game and password_active and not go_back:
            current_events=get_events() #handles leaving and screen resizing via GAME OBJECTS
            leave_game, screen_width, screen_height = current_events[1], current_events[2][0], current_events[2][1]

            password_info=password_page(password_box,current_events[0],password_text,continue_button,selected_user,back_button) #password page is shown
            password_active, password_valid = password_info
            
        if password_valid: #only allows access if the password is correct
            in_menu=False

    return selected_user, leave_game, in_menu
        
    
    
    

def update_login_page(user_list):
    '''returns a list of user slots from a list of user objects'''
    i=1
    button_list=[]
    for user in user_list:
        button_list.append(user_slot(200,i*102,400,100,user.username,user.data,(100+(20*(i%2)),100+(20*(i%2)),100+(20*(i%2))),user)) #buttons colour is alternated for variety
        i+=1

    return button_list

def login_page(button_list,delete_button,user_list,create_button,back_button,scroll_value,scroll_cooldown,confirm_delete,delete_item):
    '''displays a list of users to sign in to'''
    font=pygame.font.SysFont('ocr a extended',50)
    password_textbox=textbox(0,520,100,(600,600),(240,240,240))
    continue_button=button(0,0,font.render('  - Delete Account -  ',1,(255,255,255)),(200,100,100))
    
    win.fill((200,200,200))
    selected_user=None

    scroll_up, scroll_down = False, False
        
    current_events=get_events() #handles leaving and screen resizing via GAME OBJECTS
    leave_game, events = current_events[1], current_events[0]
    
    for event in current_events[0]:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                scroll_up=True
            elif event.button == 5:
                scroll_down=True

    key=pygame.key.get_pressed()
    if key[pygame.K_UP] or scroll_up  and scroll_cooldown == 0: #handles the scrolling of the user list if it is too big to see on screen
        if scroll_value < 1 and len(button_list) > 6:
            scroll_value+=1
            scroll_cooldown=30
    elif key[pygame.K_DOWN] or scroll_down and scroll_cooldown == 0: #handles the scrolling of the user list if it is too big to see on screen
        if scroll_value > -len(button_list)+7 and len(button_list) > 6:
            scroll_value-=1
            scroll_cooldown=30

    if scroll_cooldown != 0: #prevents scrolling too fast
        scroll_cooldown-=1
        
    new_user=False
    index=scroll_value
        
    for item in button_list: #all GUI components are drawn
        item.draw(win)
        item.width=screen_width//2 #adjusts the layout to the screen
        item.x=screen_width//4
        item.height=screen_height//8
        item.y=(screen_height//8+3)*index
        if create_button.highlighted:
            if create_button.clicked:
                new_user=True
            
        elif item.highlighted: #draws a delete button over the selected user
            delete_button.x=(item.width+screen_width//4)-delete_button.width-5
            delete_button.y=item.y+(item.height-delete_button.height)//2
            delete_button.draw(win)

            if delete_button.clicked:
                delete_item=item
                delete_button.clicked=False
                item.clicked=False

            elif item.clicked:
                selected_user=item.user
                    
        index+=1

    if confirm_delete.confirmation is not None: 
        if confirm_delete.confirmation:
            run=True
            leave_game=False
            while run and not leave_game:
                current_events=get_events()
                events, leave_game = current_events[0], current_events[1]
                password_info=password_page(password_textbox,events,'Enter password to delete account',continue_button,delete_item.user,back_button)
                run, password_valid = password_info
                
            if password_valid:
                user_list=delete_user(user_list,delete_item.main_text) #user is deleted from file
                button_list=update_login_page(user_list) #GUI is updated
                if len(button_list) > 6: #scrolls to the new length of the list
                    scroll_value+=1

                create_button.cooldown=30
                create_button.clicked=False
                    
        delete_button.clicked=False
        confirm_delete.confirmation=None
        delete_item=None

    if delete_item is not None: #confirmation requested from the user
        confirm_delete.y=delete_item.y
        confirm_delete.x=delete_item.x+delete_item.width
        confirm_delete.draw(win)
        delete_button.draw(win)
        
    go_back=False
    if back_button.clicked:
        go_back=True
        back_button.clicked=False

    pygame.draw.rect(win,(50,50,80),(0,0,screen_width,100))
    pygame.draw.rect(win,(60,60,90),(0,0,screen_width,100),4)
    header_text=font.render('- SELECT A PLAYER -',1,(255,255,255))
    win.blit(header_text,(screen_width//2-header_text.get_width()//2,10))
        
    create_button.x=screen_width//2-create_button.width//2 #adjusts the create button to the screen
    create_button.y=screen_height-create_button.height-5
    create_button.draw(win)

    back_button.draw(win)
    clock.tick(60)
    
    pygame.display.flip()
    return button_list, new_user, scroll_value, scroll_cooldown, selected_user, go_back ,delete_item

def password_page(password_textbox,events,password_text,continue_button,current_user,back_button):
    '''adds a layer of security to a users account'''
    win.fill((200,200,200))
    run=True
    password_valid=False
    font=pygame.font.SysFont('ocr a extended',32)
    enter_text=font.render('Press ENTER to confirm',1,(255,255,255))

    password_textbox.x=screen_width//2-password_textbox.width//2 #adjusts the layout to the screen
    continue_button.x=screen_width//2-continue_button.width//2
    continue_button.y=screen_height-continue_button.height-5

    password_textbox.draw(win,events)

    pygame.draw.rect(win,(50,50,80),(0,screen_height-100,screen_width,100))
    pygame.draw.rect(win,(60,60,90),(0,screen_height-100,screen_width,100),4)

    if back_button.clicked:
        run=False
        back_button.clicked=False

    if len(password_textbox.text) > 0:
        win.blit(enter_text,(screen_width//2-enter_text.get_width()//2,password_textbox.y+100))
    
    if password_textbox.get_text():
        password=password_textbox.get_text()
        if password == current_user.password: #validates the password
            password_text='Password Valid'
            password_valid=True
        else:
            password_text='Password Incorrect Please Try Again'

    if password_textbox.get_text() and password == current_user.password: 
        continue_button.draw(win) #the option to continue is shown
        if continue_button.clicked:
            run=False
            
    password_heading=font.render(password_text,1,(0,0,0))

    win.blit(password_heading,(screen_width//2-password_heading.get_width()//2,300))

    pygame.draw.rect(win,(50,50,80),(0,0,screen_width,100))
    pygame.draw.rect(win,(60,60,90),(0,0,screen_width,100),4)

    back_button.draw(win)
        
    pygame.display.flip()
    return run, password_valid

def new_user_page(username_textbox,password_textbox,events,username_text,password_text,continue_button,user_list,back_button,button_list):
    '''allows the user to create a new account'''
    win.fill((200,200,200))
    run=True
    font=pygame.font.SysFont('ocr a extended',32)
    enter_text=font.render('Press ENTER to confirm',1,(255,255,255))
    
    username_textbox.x=screen_width//2-username_textbox.width//2 #adjusts the layout to the screen
    password_textbox.x=screen_width//2-password_textbox.width//2
    continue_button.x=screen_width//2-continue_button.width//2
    continue_button.y=screen_height-continue_button.height-5

    username_textbox.draw(win,events)
    password_textbox.draw(win,events)

    pygame.draw.rect(win,(50,50,80),(0,screen_height-100,screen_width,100))
    pygame.draw.rect(win,(60,60,90),(0,screen_height-100,screen_width,100),4)

    if username_textbox.clicked and password_textbox.active: #prevents the user typing in 2 textboxes at the same time
        password_textbox.active=False
    if password_textbox.clicked and username_textbox.active:
        username_textbox.active=False

    if back_button.clicked:
        run=False
        back_button.clicked=False

    if len(username_textbox.text) > 0:
        win.blit(enter_text,(screen_width//2-enter_text.get_width()//2,username_textbox.y+100))
    if len(password_textbox.text) > 0:
        win.blit(enter_text,(screen_width//2-enter_text.get_width()//2,password_textbox.y+100))
    
    if username_textbox.get_text():
        username=username_textbox.get_text()
        if '|' in username:
            username_text='Username is invalid'
        elif not username_taken(username,user_list): #validates the username
            username_text='Your Username Is: '+username
        else:
            username_text='Sorry '+username+' Has Been Taken'

    if password_textbox.get_text():
        password=password_textbox.get_text()
        if '|' in password:
            password_text='Invalid password'
        elif len(password) > 5: #validates the password
            password_text='Your Password Is: '+password
        else:
            password_text='Password must be longer than 5 characters'

    if username_textbox.get_text() and password_textbox.get_text() and not username_taken(username,user_list) and len(password) > 5 and '|' not in password and '|' not in username: #if the password and username are filled in and valid
        continue_button.draw(win) #the option to finalize the account is shown
        if continue_button.clicked:
            create_user(user_list,username,password,'Level 0') #new user is added
            user_list.append(user(username,password,'Level 0','0,0'))
            button_list=update_login_page(user_list)
            username_textbox.final_text=None #values are reset for next time a user is added
            password_textbox.final_text=None
            continue_button.clicked=False
            run=False
            
    username_heading=font.render(username_text,1,(0,0,0))
    password_heading=font.render(password_text,1,(0,0,0))

    win.blit(username_heading,(screen_width//2-username_heading.get_width()//2,110))
    win.blit(password_heading,(screen_width//2-password_heading.get_width()//2,420))

    pygame.draw.rect(win,(50,50,80),(0,0,screen_width,100))
    pygame.draw.rect(win,(60,60,90),(0,0,screen_width,100),4)

    back_button.draw(win)
        
    pygame.display.flip()
    return run, button_list

def create_preview(file_name,level_index):
    '''creates a list for a small image of the level'''
    preview=[]
    collision_list, nonCollision_list=load_level(file_name,level_index,None)
    max_x, min_x, max_y, min_y = 8000, 80, 880, -800

    used_images={}
    
    for item in collision_list:
        image_found=False
        if item.x <= max_x and item.x >= min_x and item.y <= max_y and item.y >= min_y:
            if item.varient in used_images: #if an image for an asset has already been loaded then it doesnt need loading again
                image_found=True

            if not image_found: #a new image needs loading 
                try:
                    image=pygame.image.load(image_path+item.varient+'.png').convert_alpha()
                except:
                    image=pygame.image.load(image_path+item.varient+' 0.png').convert_alpha()

                image=pygame.transform.scale(image,(image.get_width()//8,image.get_height()//8)) #image is scaled down to fit in the level slot
                used_images.update({item.varient:image}) #new image is stored incase it is used again

            else:
                image=used_images[item.varient] #stored image for that asset is assigned

            if item.x+image.get_width() <= max_x and item.y+image.get_height() <= max_y: #if the images position is within the preview window it is added  
                preview.append((image,(item.x//8,item.y//8)))

    for item in nonCollision_list:
        image_found=False
        if item.x <= max_x and item.x >= min_x and item.y <= max_y and item.y >= min_y:
            if item.varient in used_images: #if an image for an asset has already been loaded then it doesnt need loading again
                image_found=True

            if not image_found:
                try:
                    image=pygame.image.load(image_path+item.varient+'.png').convert_alpha()
                except:
                    image=pygame.image.load(image_path+item.varient+' 0.png').convert_alpha()
                    
                image=pygame.transform.scale(image,(image.get_width()//8,image.get_height()//8)) #image is scaled down to fit in the level slot
                used_images.update({item.varient:image}) #new image is stored incase it is used again

            else:
                image=used_images[item.varient]

            if item.x+image.get_width() <= max_x and item.y+image.get_height() <= max_y: #if the images position is within the preview window it is added  
                preview.append((image,(item.x//8,item.y//8)))

    return preview
    
def level_select_menu(player,user):
    '''displays the list of levels available to play'''
    level_select=True
    leave_game=False
    level_index=None

    lock=pygame.image.load(image_path+'lock.png')

    if player:
        player.health=player.max_health #resets the player attributes when switching levels
        player.knockback=0
        player.knockback_direction=None
        player.knockback_animation=0
        
    levels_completed=int(user.data.strip('Level'))
    
    back_button=button(0,0,pygame.image.load(image_path+'back.png'),(100,100,200))
    
    button_list=game_levels

    font=pygame.font.SysFont('ocr a extended',50)

    click_cooldown=10//framerate_adjustment
    
    scroll_cooldown=0
    scroll_value=1
    
    while level_select and not leave_game:
        scroll_up, scroll_down = False, False
        if click_cooldown != 0:
            click_cooldown-=1
        
        current_events=get_events() #handles leaving and screen resizing via GAME OBJECTS
        leave_game, screen_width, screen_height = current_events[1], current_events[2][0], current_events[2][1]
        for event in current_events[0]:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    scroll_up=True
                elif event.button == 5:
                    scroll_down=True
        
        key=pygame.key.get_pressed()
        if key[pygame.K_UP] or scroll_up and scroll_cooldown == 0: #handles the scrolling of the user list if it is too big to see on screen
            if scroll_value < 1 and len(button_list) > 6:
                scroll_value+=1
                scroll_cooldown=30
        elif key[pygame.K_DOWN] or scroll_down and scroll_cooldown == 0: #handles the scrolling of the user list if it is too big to see on screen
            if scroll_value > -len(button_list)+7 and len(button_list) > 6:
                scroll_value-=1
                scroll_cooldown=30

        if scroll_cooldown != 0: #prevents scrolling too fast
            scroll_cooldown-=1
            
    
        index=scroll_value
        
        win.fill((150,150,150))

        screen_width, screen_height = win.get_width(), win.get_height()

        draw_stat=False

        for item in button_list:
            item.clicked=False
            level_locked=False
            if item.y > -item.height and item.y < win.get_height():
                item.draw(win)
                
            item.width=screen_width//2 #adjusts the layout to the screen
            item.x=screen_width//4
            item.height=screen_height//8
            item.y=(screen_height//8+3)*index

            actual_index=index-scroll_value

            if actual_index > levels_completed:
                level_locked=True
                win.blit(lock,((item.x+item.width)-lock.get_width()-5,(item.y+item.height)-lock.get_height()-5))
                item.change_colour((100,100,100))
            else:
                item.change_colour((220+20*(index%2),140+20*(index%2),50+20*(index%2)))

            if item.highlighted:
                max_score, best_time = get_level_stats(user,'Game',item.main_text)
                name='- '+item.main_text.upper()+' -'
                draw_stat=True

            if item.clicked and not level_locked and click_cooldown == 0:
                level_index=index-scroll_value
                level_select=False
                
            index+=1

        if draw_stat: 
            level_prompt=prompt(0,0,[name,'Highscore: '+str(max_score),'Best Time: '+str(best_time)],(200,200,200))
            level_prompt.x, level_prompt.y = pygame.mouse.get_pos()
            level_prompt.draw(win)

        go_back=False
        if back_button.clicked: #exits the menu if back button is pressed
            go_back=True
            back_button.clicked=False
            level_select=False

        pygame.draw.rect(win,(50,50,80),(0,0,screen_width,100))
        pygame.draw.rect(win,(60,60,90),(0,0,screen_width,100),4)
        header_text=font.render('- SELECT A LEVEL -',1,(255,255,255))
        win.blit(header_text,(screen_width//2-header_text.get_width()//2,10))

        back_button.draw(win)

        clock.tick(60)
        pygame.display.flip()
        
    return leave_game, go_back, level_index

def update_level_list(current_user,update_preview):
    '''returns a list of level slots from the custom levels'''
    file=open(file_path+'Player Levels.txt')
    read_file=file.readlines()
    file.close()
    global editor_previews
    
    if update_preview:
        editor_previews=[]
    
    my_list=[]
    button_list=[]
    index=0
    for item in read_file: #creates a list of available levels as buttons
        if item != '\n':
            if update_preview:
                preview=create_preview('player levels',index)
                editor_previews.append(preview)
            else:
                preview=editor_previews[index]
            
            if '|' in item:
                level_info=item[:item.find('|')]
            else:
                level_info=item.strip('\n')
                
            level_info=level_info.split('.')
            
            if level_info[1] == current_user.username:
                my_list.append(user_slot(win.get_width()//2,index*100,400,100,level_info[0],'- By '+level_info[1]+' -',(240,140,70),index,preview)) #adds to the top of the list
            else:
                button_list.append(user_slot(win.get_width()//2,index*100,400,100,level_info[0],'- By '+level_info[1]+' -',(120,200,200),index,preview))

            index+=1

    return my_list+button_list

def creator_level_menu(player,current_user):
    '''displays the list of levels available to play'''
    level_select=True
    leave_game=False
    level_index=None
    can_edit=False
    delete_item=None

    if player:
        player.health=player.max_health #resets the player attributes when switching levels
        player.knockback=0
        player.knockback_direction=None
        player.knockback_animation=0

    font=pygame.font.SysFont('ocr a extended',50)
    small_font=pygame.font.SysFont('ocr a extended',40)
    
    back_button=button(0,0,pygame.image.load(image_path+'back.png'),(100,100,200))
    create_button=button(0,0,small_font.render('  - Create New Level -  ',1,(255,255,255)),(100,200,100))
    
    locked_create_button=button(0,0,small_font.render('  - Create New Level -  ',1,(255,255,255)),(100,100,100))
    lock_icon=pygame.image.load(image_path+'lock.png').convert_alpha()

    locked=False
    
    if (get_level_stats(current_user,'Game','Victory Volcano')) == (None, None):
        locked=True
    
    continue_button=button(0,0,font.render('  - Create Level -  ',1,(255,255,255)),(100,200,100))
    level_textbox=textbox(0,340,100,(600,600),(240,240,240))
    delete_button=button(0,0,pygame.image.load(image_path+'cross.png'),(200,100,100))
    confirm_delete=confirmation_box(0,0,'Are you sure?',(140,140,140))
    locked_prompt=prompt(0,0,['You must complete all the main levels','before you can create your own!'],(200,200,200))

    if current_user.creator_levels is None:
        if current_user.first_load:
            button_list=update_level_list(current_user,False)
            current_user.first_load=False
        else:
            button_list=update_level_list(current_user,True)
        current_user.creator_levels=button_list  
    else:
        button_list=current_user.creator_levels

    scroll_cooldown=0
    scroll_value=1
    click_cooldown=10//framerate_adjustment
    
    while level_select and not leave_game:
        scroll_up, scroll_down = False, False

        if click_cooldown != 0:
            click_cooldown-=1
        
        current_events=get_events() #handles leaving and screen resizing via GAME OBJECTS
        leave_game, events = current_events[1], current_events[0]
        
        for event in current_events[0]:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    scroll_up=True
                elif event.button == 5:
                    scroll_down=True
                    
        key=pygame.key.get_pressed()
        if key[pygame.K_UP] or scroll_up and scroll_cooldown == 0: #handles the scrolling of the user list if it is too big to see on screen
            if scroll_value < 1 and len(button_list) > 6:
                scroll_value+=1
                scroll_cooldown=30
        elif key[pygame.K_DOWN] or scroll_down and scroll_cooldown == 0: #handles the scrolling of the user list if it is too big to see on screen
            if scroll_value > -len(button_list)+7 and len(button_list) > 6:
                scroll_value-=1
                scroll_cooldown=30

        if scroll_cooldown != 0: #prevents scrolling too fast
            scroll_cooldown-=1
    
        index=scroll_value
        
        win.fill((150,150,150))
        
        screen_width, screen_height = win.get_width(), win.get_height()
        show_stat=False
        for item in button_list:
            item.clicked=False
            if item.y > -item.height and item.y < win.get_height():
                item.draw(win)
                
            item.width=screen_width//2 #adjusts the layout to the screen
            item.x=screen_width//4
            item.height=screen_height//8
            item.y=(screen_height//8+3)*index

            edit_enabled=check_edit_enabled(index-scroll_value,current_user.username,button_list)
            
            if item.highlighted:
                show_stat=True
                max_score, best_time=get_level_stats(current_user,'Editor',item.main_text)
                name='- '+item.main_text.upper()+' -'
                
                if edit_enabled:
                    delete_button.x=(item.width+screen_width//4)-delete_button.width-5
                    delete_button.y=item.y+(item.height-delete_button.height)//2
                    delete_button.draw(win)
                    
                    if delete_button.clicked:
                        delete_item=item
                        delete_button.clicked=False
                        item.clicked=False
                    
                    elif item.clicked and click_cooldown == 0:
                        level_index=item.user
                        level_select=False
                        can_edit=check_edit_enabled(index-scroll_value,current_user.username,button_list)
                    
                elif item.clicked and not create_button.highlighted and click_cooldown == 0:
                    level_index=item.user
                    level_select=False
                    can_edit=check_edit_enabled(index-scroll_value,current_user.username,button_list)

            index+=1

        if show_stat:
            level_prompt=prompt(0,0,[name,'Highscore: '+str(max_score),'Best Time: '+str(best_time)],(200,200,200))
            level_prompt.x, level_prompt.y = pygame.mouse.get_pos()
            level_prompt.draw(win)

        if delete_item is not None: #confirmation from the user requested
            confirm_delete.x=delete_item.x+delete_item.width
            confirm_delete.y=delete_item.y
            confirm_delete.draw(win)
            delete_button.draw(win)

        if confirm_delete.confirmation is not None: #if the user has chosen yes or no
            if confirm_delete.confirmation: #if yes the level is deleted
                delete_level(delete_item.main_text)
                button_list=update_level_list(current_user,True)
                current_user.creator_levels=None
                
            delete_item=None
            confirm_delete.confirmation=None

        go_back=False
        if back_button.clicked: #exits the menu if back button is pressed
            go_back=True
            back_button.clicked=False
            level_select=False

        if create_button.clicked:
            level_info=new_level_page(level_textbox,'Enter the name of your level',continue_button,current_user,back_button)
            leave_game, level_name = level_info
            create_button.clicked=False

            if level_name is not None:
                create_level('Player Levels',level_name,current_user.username)

                button_list=update_level_list(current_user,True)
                current_user.creator_levels=None
            
                level_select=False
                can_edit=True

                for item in button_list:
                    if item.main_text == level_name:
                        level_index=item.user
                        break

        pygame.draw.rect(win,(50,50,80),(0,0,screen_width,100))
        pygame.draw.rect(win,(60,60,90),(0,0,screen_width,100),4)
        header_text=font.render('- SELECT A LEVEL -',1,(255,255,255))
        win.blit(header_text,(screen_width//2-header_text.get_width()//2,10))

        if locked:
            locked_create_button.x=screen_width//2-create_button.width//2 #adjusts the create button to the screen
            locked_create_button.y=screen_height-create_button.height-5
            locked_create_button.draw(win)
            win.blit(lock_icon,(locked_create_button.x+locked_create_button.width-lock_icon.get_width(),locked_create_button.y+locked_create_button.height-lock_icon.get_height()))
            if locked_create_button.highlighted:
                locked_prompt.x, locked_prompt.y = pygame.mouse.get_pos()
                locked_prompt.y-=100
                locked_prompt.draw(win)

        else:
            create_button.x=screen_width//2-create_button.width//2 #adjusts the create button to the screen
            create_button.y=screen_height-create_button.height-5
            create_button.draw(win)

        back_button.draw(win)

        clock.tick(60)
        pygame.display.flip()

        
    return leave_game, go_back, level_index, can_edit

def new_level_page(level_textbox,level_text,continue_button,current_user,back_button):
    '''creates a new user created level'''
    run=True
    leave_game=False
    font=pygame.font.SysFont('ocr a extended',32)
    enter_text=font.render('Press ENTER to confirm',1,(255,255,255))
    level_name=None
    
    while run and not leave_game:
        win.fill((200,200,200))

        current_events=get_events() #handles leaving and screen resizing via GAME OBJECTS
        leave_game, events = current_events[1], current_events[0]
        screen_width, screen_height = win.get_width(), win.get_height()
        
        level_textbox.x=screen_width//2-level_textbox.width//2 #adjusts the layout to the screen
        continue_button.x=screen_width//2-continue_button.width//2
        continue_button.y=screen_height-continue_button.height-5

        level_textbox.draw(win,events)

        pygame.draw.rect(win,(50,50,80),(0,screen_height-100,screen_width,100))
        pygame.draw.rect(win,(60,60,90),(0,screen_height-100,screen_width,100),4)

        if len(level_textbox.text) > 0:
            win.blit(enter_text,(screen_width//2-enter_text.get_width()//2,level_textbox.y+100))
        
        if level_textbox.get_text():
            level_name=level_textbox.get_text()
            level_text='Your level will be called: '+level_name

        if not valid_level_name(level_name):
            level_text='This level name is already in use'

        if level_textbox.get_text() and valid_level_name(level_name):
            continue_button.draw(win) #the option to continue is shown
            if continue_button.clicked:
                run=False
                continue_button.clicked=False
                level_textbox.final_text=''

        if back_button.clicked:
            run=False
            back_button.clicked=False
            level_textbox.final_text=''
            level_name=None
                
        level_heading=font.render(level_text,1,(0,0,0))

        win.blit(level_heading,(screen_width//2-level_heading.get_width()//2,300))

        pygame.draw.rect(win,(50,50,80),(0,0,screen_width,100))
        pygame.draw.rect(win,(60,60,90),(0,0,screen_width,100),4)

        back_button.draw(win)
            
        pygame.display.flip()
        
    return leave_game, level_name

def create_level(file_name,username,level_name):
    '''writes a new user to the file'''
    file=open(file_path+file_name+'.txt','a')
    file.write(username+'.'+level_name+'.sunny\n') #new level is added to file
    file.close()

def delete_level(level):
    '''removes a level from the file'''
    file=open(file_path+'Player Levels.txt')
    read_file=file.read()
    file.close()
    read_file=read_file.split('\n')
    
    index=0
    for item in read_file: #finds the level to be deleted
        if item != '\n' and item != '':
            if '|' in item:
                item=item[:item.find('|')]
            else:
                item=item.strip('\n')

            item=item.split('.')
            
            if item[0] == level:
                read_file.pop(index) #level is deleted from file
                break
            
        index+=1

    open(file_path+'Player Levels.txt','w').write('') #file is wiped
    file=open(file_path+'Player Levels.txt','a')
    
    for line in read_file: #new contents are wrote
        if line != '': #prevents empty lines
            file.write(line+'\n')

    file.close()

    file=open(file_path+'player data.txt')
    read_file=file.readlines()
    file.close()

    index=0
    for item in read_file:
        if 'Editor.'+level+'.' in item: #finds if the deleted level is within each players data
            split_item=item.split('|')
            completed_levels=split_item[4]
            completed_levels=completed_levels.strip('\n')
            completed_levels=completed_levels.split(',')
            updated_list=''

            if len(completed_levels) > 1:
                level_ind=0
                for entry in completed_levels: #goes through the list of the players completed levels
                    split_entry=entry.split('.')
                    
                    if split_entry[1] != level: #the level is added to the new list of completed levels if it isnt being deleted
                        if level_ind != len(completed_levels)-1:
                            updated_list+=entry+','
                        else:
                            updated_list+=entry

                    level_ind+=1

                if updated_list[-1] == ',':
                    updated_list=updated_list.strip(',')


            read_file[index]=split_item[0]+'|'+split_item[1]+'|'+split_item[2]+'|'+split_item[3]+'|'+updated_list+'\n' #players line in the file is updated

        index+=1
        
    update_file('player data',read_file,False)
                    

def valid_level_name(level_name):
    '''checks if a level name has already been used or is valid'''
    if level_name is None:
        return True
    
    elif '|' in level_name:
        return False
    
    file=open(file_path+'Player Levels.txt')
    read_file=file.readlines()
    file.close()

    for item in read_file:
        item_data=item[:item.find('|')]
        item_name=item_data.split('.')[0]
        if item_name == level_name:
            return False
        
    return True

def check_edit_enabled(index,username,button_list):
    '''checks if a custom level belongs to that user'''
    author=button_list[index].sub_text
    author=author.replace(' -','')
    author=author.replace('- By ','')
    
    if author == username:
        return True
    else:
        return False
    
    

def load_level(name,level,player):
    '''loads the contents of a file into a level object'''
    global collision_list
    collision_list=[]
    global nonCollision_list
    nonCollision_list=[]
    
    file=open(file_path+name+'.txt') #file is interpreted
    read_file=file.readlines()[level]
    
    asset_list=read_file.split('|') #each asset is stored in a list in the file

    level_data=asset_list[0]
    level_data=level_data.split('.')
    
    if player is not None:
        player.reset()
        player.available_trophies=0
        
        player.current_level=level
        player.current_file=name
        
        player.weather=level_data[2]
    
    for item in asset_list:
        collision_list, nonCollision_list = add_to_level(item,collision_list,nonCollision_list,None,player)

    return collision_list, nonCollision_list

def add_to_level(item,collision_list,nonCollision_list,grid_cursor,player):
    split_item=item.split('.') #each assets information is seperated by fullstop
    
    if grid_cursor is None: #if not placed via level editor initial position is defined
        try:
            grid_cursor=(int(split_item[2]),int(split_item[3]))
        except:
            grid_cursor=(None,None)
        
    if split_item[0] == 'platform':
        collision_list.append(platform(int(split_item[2]),int(split_item[3]),split_item[1],grid_cursor))
    elif split_item[0] == 'tile':
        collision_list.append(tile(int(split_item[2]),int(split_item[3]),split_item[1],grid_cursor))
    elif split_item[0] == 'door':
        collision_list.append(door(int(split_item[2]),int(split_item[3]),split_item[1],grid_cursor))
    elif split_item[0] == 'decor':
        nonCollision_list.append(decor(int(split_item[2]),int(split_item[3]),split_item[1],grid_cursor))
    elif split_item[0] == 'front_decor':
        nonCollision_list.append(front_decor(int(split_item[2]),int(split_item[3]),split_item[1],grid_cursor))
    elif split_item[0] == 'turret':
        nonCollision_list.append(turret(int(split_item[2]),int(split_item[3]),split_item[1],grid_cursor))
    elif split_item[0] == 'liquid':
        nonCollision_list.append(liquid(int(split_item[2]),int(split_item[3]),split_item[1],grid_cursor))
    elif split_item[0] == 'plant_decor':
        nonCollision_list.append(plant_decor(int(split_item[2]),int(split_item[3]),split_item[1],grid_cursor))
    elif split_item[0] == 'interactable_plant':
        nonCollision_list.append(interactable_plant(int(split_item[2]),int(split_item[3]),split_item[1],grid_cursor))
    elif split_item[0] == 'rotating_decor':
        nonCollision_list.append(rotating_decor(int(split_item[2]),int(split_item[3]),split_item[1],grid_cursor))
    elif split_item[0] == 'checkpoint':
        nonCollision_list.append(checkpoint(int(split_item[2]),int(split_item[3]),split_item[1],grid_cursor))
    elif split_item[0] == 'solid_obsticle':
        collision_list.append(solid_obsticle(int(split_item[2]),int(split_item[3]),split_item[1],grid_cursor))
    elif split_item[0] == 'unstable_tile':
        collision_list.append(unstable_tile(int(split_item[2]),int(split_item[3]),split_item[1],grid_cursor))
    elif split_item[0] == 'rotating_obsticle':
        nonCollision_list.append(rotating_obsticle(int(split_item[2]),int(split_item[3]),split_item[1],grid_cursor))
    elif split_item[0] == 'enemy':
        nonCollision_list.append(enemy(int(split_item[2]),int(split_item[3]),split_item[1],grid_cursor))
    elif split_item[0] == 'item':
        nonCollision_list.append(Item(int(split_item[2]),int(split_item[3]),split_item[1],grid_cursor))
        if split_item[1] == 'trophy':
            if player is not None:
                player.available_trophies+=1
    elif split_item[0] == 'sign':
        nonCollision_list.append(sign(int(split_item[2]),int(split_item[3]),split_item[1],split_item[4],grid_cursor))
    elif split_item[0] == 'goal':
        nonCollision_list.append(goal(int(split_item[2]),int(split_item[3]),split_item[1],grid_cursor))
        
    return collision_list,nonCollision_list

def adjust_camera(player,close_to_ground):
    '''moves the camera up or down according to the players position'''
    player_distance = player.y-screen_height//2
    if player.gravity_value > 20*(framerate_adjustment**2): #if player has a large acceleration camera speed is increased
        camera_speed=round(player.gravity_value)//framerate_adjustment
        if close_to_ground:
            camera_speed=camera_speed//8 #camera speed is smoother when near the ground
    else:
        camera_speed=(((player_distance)**2)//10000)
        
    if player.camera_moved < 0: #ensures the camera doesnt go under the level
        for item in collision_list:
            item.y-=player.camera_moved
        for item in nonCollision_list:
            item.y-=player.camera_moved
        player.y-=player.camera_moved
        player.camera_moved=0

    else:
        if player.y < screen_height//2 or player.camera_moved < 0 and player_distance**2 > 16000: #adjusts the camera upwards if the player is outside the central band of the screen
            for item in collision_list:
                item.y+=camera_speed*framerate_adjustment
            for item in nonCollision_list:
                item.y+=camera_speed*framerate_adjustment
            player.y+=camera_speed*framerate_adjustment
            player.camera_moved+=camera_speed*framerate_adjustment #stores how far the camera has moved so can be reset at death

        elif player.y > screen_height//2 and player.camera_moved > 0 and player_distance**2 > 16000: #adjusts the camera downwards if the player is outside the central band of the screen
            for item in collision_list:
                item.y-=camera_speed*framerate_adjustment
            for item in nonCollision_list:
                item.y-=camera_speed*framerate_adjustment
            player.y-=camera_speed*framerate_adjustment
            player.camera_moved-=camera_speed*framerate_adjustment #stores how far the camera has moved so can be reset at death

def scroll_level(speed,player,y_direction):
    '''moves the level at the given speed'''
    if not y_direction:
        for item in collision_list:
            item.x+=speed*framerate_adjustment
        for item in nonCollision_list:
            item.x+=speed*framerate_adjustment
            if class_type(item) in ['goal','checkpoint','Item','turret']:
                item.rect=pygame.Rect(item.x,item.y,item.width,item.height)
        player.moving=True
        player.distance_travelled+=speed*framerate_adjustment #records the players distance from the start
        player.respawn_distance+=speed*framerate_adjustment
    else:
        for item in collision_list:
            item.y+=speed*framerate_adjustment
        for item in nonCollision_list:
            item.y+=speed*framerate_adjustment
            if class_type(item) in ['goal','checkpoint','Item','turret']:
                item.rect=pygame.Rect(item.x,item.y,item.width,item.height)
        player.camera_moved+=speed*framerate_adjustment #records the players distance from the start

def get_level_name(file_name,index):
    '''finds the name of the current level'''
    file=open(file_path+file_name+'.txt')
    read_file=file.readlines()
    file.close()

    level_line=read_file[index]
    level_line=level_line.split('|')

    level_info=level_line[0].split('.')

    return level_info[0]

def level_complete(player,current_level,game_position):
    '''shows the player the victory screen'''
    screen_width=win.get_width()
    screen_height=win.get_height()
    
    font=pygame.font.SysFont('ocr a extended',screen_height//10)
    small_font=pygame.font.SysFont('ocr a extended',screen_height//20)
    
    death_text=font.render('- LEVEL COMPLETE -',1,(255,255,20))
    message_text=small_font.render('Well done :D',1,(255,255,255)) 
    
    for i in range(1,200,5): #animates the screen
        text_pos=(screen_width//2-death_text.get_width()//2,screen_height//2-death_text.get_height()//2)
        win.blit(death_text,text_pos)
        
        top_line=(text_pos[1]-death_text.get_height()//4)+20

        shade=pygame.Surface((screen_width,screen_height)) #darkens the screen
        if i < 50:
            shade.set_alpha(10)
            win.blit(shade,(0,0))

        pygame.draw.line(win,(255,255,0),((i*screen_width//100),top_line),(0,top_line),14) #draws 2 darker lines accross the screen
        pygame.draw.line(win,(255,255,0),(screen_width,(text_pos[1]+death_text.get_height())),(screen_width-(i*screen_width//100),(text_pos[1]+death_text.get_height())),14)
            
        pygame.draw.line(win,(255,255,80),((i*screen_width//100),top_line),(0,top_line),8) #draws 2 lighter lines across the screen
        pygame.draw.line(win,(255,255,80),(screen_width,(text_pos[1]+death_text.get_height())),(screen_width-(i*screen_width//100),(text_pos[1]+death_text.get_height())),8)

        message_pos=(screen_width//2-message_text.get_width()//2,text_pos[1]+death_text.get_height()) #displays the death message
        win.blit(message_text,message_pos)
            
        clock.tick(60)
        pygame.display.flip()

    red_tint=create_tint(win.get_width(),win.get_height())
    stat_font=pygame.font.SysFont('ocr a extended',60,True,True)
    shade.set_alpha(50)
    for i in range(1,100): #delays the players respawnin
        
        game_window(player,collision_list,nonCollision_list,screen_width,screen_height,red_tint,True,None,None)

        win.blit(shade,(0,0))
        
        text_pos=(screen_width//2-death_text.get_width()//2,screen_height//2-death_text.get_height()//2)
        win.blit(death_text,text_pos)
        
        top_line=(text_pos[1]-death_text.get_height()//4)+20

        message_pos=(screen_width//2-message_text.get_width()//2,text_pos[1]+death_text.get_height()) #displays the death message
        win.blit(message_text,message_pos)
        
        pygame.draw.line(win,(255,255,0),(screen_width,top_line),(0,top_line),14) #draws 2 darker lines accross the screen
        pygame.draw.line(win,(255,255,0),(screen_width,(text_pos[1]+death_text.get_height())),(0,(text_pos[1]+death_text.get_height())),14)
        
        pygame.draw.line(win,(255,255,80),(screen_width,top_line),(0,top_line),8) #draws 2 lighter lines across the screen
        pygame.draw.line(win,(255,255,80),(screen_width,(text_pos[1]+death_text.get_height())),(0,(text_pos[1]+death_text.get_height())),8)

        score=stat_font.render('Score: '+str(player.score),1,(0,255,255))
        time=stat_font.render('Completed in: '+str(player.time),1,(255,255,255))

        score_width=score.get_width()
        time_width=time.get_width()

        if i <= 40:
            win.blit(score,(round(i*(score_width/40)-score_width),text_pos[1]+death_text.get_height()+20))
            win.blit(time,(round(i*(time_width/40)-time_width),text_pos[1]+death_text.get_height()+80))
        else:
            win.blit(score,(0,text_pos[1]+death_text.get_height()+20))
            win.blit(time,(0,text_pos[1]+death_text.get_height()+80))
        
        clock.tick(60)
        pygame.display.flip()
        
    player.y=400
    for item in collision_list:
        item.x-=player.distance_travelled
        item.y-=player.camera_moved
    for item in nonCollision_list:
        item.x-=player.distance_travelled #level is reset back to the starting distance of 0
        item.y-=player.camera_moved
        
    player.distance_travelled=0
    player.respawn_distance=0
    player.camera_moved=0
    player.health=player.max_health

    if game_position != 'editor': #progress is recorded if the player is in the in-built levels
        if game_position == 'user level':
            store_level_stats(player.user,'Editor',get_level_name('Player Levels',current_level),player.score,player.time)
            
        else:
            file=open(file_path+'player data.txt')
            read_file=file.readlines()
            file.close()
            
            index=0
            for item in read_file:
                split_item=item.split('|')
                if player.user.username == split_item[0]: #current user is located in the file
                    break
                index+=1

            player_info=read_file[index].split('|')
            player_level=int(player_info[2][player_info[2].find('Level')+5:])
            
            if current_level+1 > player_level: #if the player has completed a higher level than their current one then it is updated
                player.user.data='Level '+str(current_level+1)
                read_file[index]=read_file[index].replace('Level '+str(player_level),'Level '+str(current_level+1))
                update_file('player data',read_file,False)
                
            store_level_stats(player.user,'Game',get_level_name('Game Levels',current_level),player.score,player.time)

    else:
        store_level_stats(player.user,'Editor',get_level_name('Player Levels',current_level),player.score,player.time)
        reset_level(player)

    

    
    

def death(player,death_message):
    '''handles the death of the player'''
    screen_width=win.get_width()
    screen_height=win.get_height()
    player.health=0
    player.hurt_animation=0
    player.knockback=0
    
    font=pygame.font.SysFont('ocr a extended',screen_height//10)
    small_font=pygame.font.SysFont('ocr a extended',screen_height//20)
    
    death_text=font.render('- YOU DIED -',1,(255,20,20))
    message_text=small_font.render(death_message,1,(255,255,255)) 
    
    for i in range(1,100,5): #animates the death screen
        text_pos=(screen_width//2-death_text.get_width()//2,screen_height//2-death_text.get_height()//2)
        win.blit(death_text,text_pos)
        
        top_line=(text_pos[1]-death_text.get_height()//4)+20

        shade=pygame.Surface((screen_width,screen_height)) #darkens the screen
        shade.set_alpha(10)
        win.blit(shade,(0,0))
        
        pygame.draw.line(win,(255,0,0),((i*screen_width//100),top_line),(0,top_line),14) #draws 2 darker lines accross the screen
        pygame.draw.line(win,(255,0,0),(screen_width,(text_pos[1]+death_text.get_height())),(screen_width-(i*screen_width//100),(text_pos[1]+death_text.get_height())),14)
        
        pygame.draw.line(win,(255,80,80),((i*screen_width//100),top_line),(0,top_line),8) #draws 2 lighter lines across the screen
        pygame.draw.line(win,(255,80,80),(screen_width,(text_pos[1]+death_text.get_height())),(screen_width-(i*screen_width//100),(text_pos[1]+death_text.get_height())),8)

        message_pos=(screen_width//2-message_text.get_width()//2,text_pos[1]+death_text.get_height()) #displays the death message
        win.blit(message_text,message_pos)
        
        clock.tick(60)
        pygame.display.flip()

    for i in range(1,50): #delays the players respawning
        pygame.draw.line(win,(255,0,0),(screen_width,top_line),(0,top_line),14)
        pygame.draw.line(win,(255,0,0),(screen_width,(text_pos[1]+death_text.get_height())),(0,(text_pos[1]+death_text.get_height())),14)
        
        pygame.draw.line(win,(255,80,80),(screen_width,top_line),(0,top_line),8)
        pygame.draw.line(win,(255,80,80),(screen_width,(text_pos[1]+death_text.get_height())),(0,(text_pos[1]+death_text.get_height())),8)
        
        clock.tick(60)
        pygame.display.flip()
        
    player.y=400
    #player.respawn_height-=player.height

    for item in collision_list:
        item.x-=player.respawn_distance
        item.y+=player.respawn_height
        if class_type(item) == 'unstable_tile':
            item.reset()
            
    for item in nonCollision_list:
        item.x-=player.respawn_distance #level is reset back to the starting distance of 0
        item.y+=player.respawn_height

    player.distance_travelled-=player.respawn_distance
    player.respawn_distance=0
    player.camera_moved+=player.respawn_height
    player.respawn_height=0
    player.health=player.max_health

def check_collisions(collision_list,player):
    '''checks for collisions at each side of the player and
       returns a list of boolean collisions and the objects that are colliding'''
    global onScreen_collision_list
    
    roof_item=None
    ground_item=None
    left_item=None
    right_item=None
    close_to_ground=False
    roof_level=0
    
    roof_contact=False
    ground_contact=False
    can_left=True
    can_right=True

    player.in_liquid=False
    for item in nonCollision_list: #checks if the player is in a liquid
        if not item.offscreen:
            if class_type(item) == 'liquid':
                if item.rect.colliderect(player.rect):
                    player.gravity_value=2 #players movements are decreased
                    player.speed=2
                    player.in_liquid=True

    for item in onScreen_collision_list:
        if not item.offscreen and not item.dead:
            if item.y > player.y:
                if player.down_rect.colliderect(item.rect):
                    if class_type(item) == 'platform':
                        if item.y+40*framerate_adjustment > player.y+player.height and not player.crouching:
                            ground_contact=True
                            ground_item=item #finds if the player is in contact with an asset beneath them
                    else:
                        ground_contact=True
                        ground_item=item #finds if the player is in contact with an asset beneath them
                    
            if item.y < player.y:
                if player.up_rect.colliderect(item.rect) and class_type(item) != 'platform':
                    roof_contact=True
                if player.jump_rect.colliderect(item.rect) and class_type(item) != 'platform':
                    roof_level=item.y+item.height #finds if the player is colliding with an asset above them

            if player.left_rect.colliderect(item.rect) and class_type(item) != 'platform': #checks for collisions to the left of the player
                can_left=False
                left_item=item
                
            if player.right_rect.colliderect(item.rect) and class_type(item) != 'platform': #checks for collisions to the right of the player
                can_right=False
                right_item=item

            if player.depth_rect.colliderect(item.rect):
                close_to_ground=True

    return (roof_contact, ground_contact, can_left, can_right), (roof_item, ground_item, left_item, right_item), roof_level, close_to_ground #list of boolean collisions and the item in collision

def level_events(player,red_tint,win):
    '''handles screen resizing and quiting the game'''
    events=pygame.event.get()
    screen_width, screen_height = win.get_width(), win.get_height()
    run=True
    for event in events:
        if event.type == pygame.QUIT: #detects if the player has pressed the red X
            run=False

        if event.type == pygame.VIDEORESIZE: #handles the resizing of the game window
            Screen_height_adjustment=screen_height-event.size[1]
            Screen_width_adjustment=screen_width-event.size[0]
            
            screen_width=event.size[0]
            screen_height=event.size[1]
            
            win=pygame.display.set_mode((screen_width,screen_height),pygame.RESIZABLE) #sets the window to the new size

            red_tint=create_tint(win.get_width(),win.get_height()) #creates a new transparent surface for when player is damaged
            
            adjust_level(player,Screen_width_adjustment,Screen_height_adjustment,False)
            
    return run, screen_width, screen_height, events, red_tint

def adjust_level(player,Screen_width_adjustment,Screen_height_adjustment,first_load):
    '''allows the level to be moved to fill the screen'''
    screen_width=win.get_width()
    screen_height=win.get_height()

    if player.y-Screen_height_adjustment < screen_height:
        player.y-=Screen_height_adjustment #player is moved to the same height relative to the screen
            
    for item in collision_list:
        item.y-=Screen_height_adjustment
        if first_load:
            item.x-=Screen_width_adjustment//2
        else:
            item.x+=screen_width//2-player.x

    for item in nonCollision_list: #all assets are moved as to be in the same place relative to the player
        item.y-=Screen_height_adjustment
        if class_type(item) == 'enemy':
            item.initialY-=Screen_height_adjustment
            
        if first_load:
            item.x-=Screen_width_adjustment//2
            
            if class_type(item) == 'enemy':
                item.initialX-=Screen_width_adjustment//2
        else:
            item.x+=screen_width//2-player.x

            if class_type(item) == 'enemy':
                item.initialX+=screen_width//2-player.x

    if first_load:
        player.level_adjusted[0]-=(Screen_width_adjustment//2) #player doesnt have to be taken into account when first loaded
        player.level_adjusted[1]-=(Screen_height_adjustment)

    else:
        player.level_adjusted[0]+=(screen_width//2-player.x)
        player.level_adjusted[1]-=(Screen_height_adjustment)

    player.x+=screen_width//2-player.x #player is moved to the middle of the new screen
    player.rect=pygame.Rect(player.x,player.y,player.width,player.height)

def resize_background(screen_width,screen_height,background):
    '''maintains the aspect ratio of an image whilst resizing it to the screen'''
    background_width=background.background_dimensions[0]
    background_height=background.background_dimensions[1]
    
    y_ratio=0
    x_ratio=0
    
    if screen_width < background_width: #keeps the background image in its origional ratio when the screen size changes
        y_ratio=screen_width-background_width
        
    if screen_height < background_height:
        x_ratio=screen_height-background_height

    background=pygame.transform.scale(background.original_background,(screen_width-y_ratio,screen_height-x_ratio)) #background is scaled accordingly
    return background


def get_events():
    '''detects screen resizing and leaving'''
    global screen_width, screen_height
    leave=False
    Screen_height_adjustment=0
    Screen_width_adjustment=0
    events=pygame.event.get()
    
    for event in events:
        if event.type == pygame.QUIT:
            leave=True
        if event.type == pygame.VIDEORESIZE:
            Screen_height_adjustment=screen_height-event.size[1]
            Screen_width_adjustment=screen_width-event.size[0]
            
            screen_width=event.size[0]
            screen_height=event.size[1]
            
            win=pygame.display.set_mode((screen_width,screen_height),pygame.RESIZABLE) #sets the window to the new size
            
    return events, leave,(screen_width,screen_height,Screen_width_adjustment,Screen_height_adjustment)
            

def handle_jumping(player,jumping,ground_contact,ground_item,roof_contact,roof_level,jump_value):
    '''handles the gravity and jumping of the player'''
    gravity_strength=1.25*framerate_adjustment #constants that can be tweaked to effect jump
    terminal_velocity=20*framerate_adjustment
    
    if roof_level == 0 and not player.in_liquid:
        max_jump=40*framerate_adjustment
        jump_strength=0.8**framerate_adjustment
        if not jumping:
            jump_value=max_jump
            
    else: #prevents the jump if player is in a confined space
        jump_strength=0.3**framerate_adjustment
        max_jump=10*framerate_adjustment
        
    if not jumping:
        if not ground_contact:
            player.in_air=True
            player.y+=round(player.gravity_value)
            if player.respawn_height < 720-player.spawnY:
                player.respawn_height+=round(player.gravity_value)
            else:
                player.respawn_height=720-player.spawnY
        
            if player.gravity_value < terminal_velocity:
                    player.gravity_value*=gravity_strength #player accelarates towards the ground

        else:
            if player.y+round(player.gravity_value)+player.height > ground_item.y:
                player.y=(ground_item.y-player.height) #the players position is set to the ground level
                player.gravity_value=1

    else:
        player.in_air=True
        if not roof_contact:
            if player.y-round(jump_value) > roof_level:
                player.y-=round(jump_value) #players jumping speed decelerates
                player.respawn_height-=round(jump_value)

            else:
                jumping=False
                jump_value=max_jump
                
            if jump_value > 0.1: 

                 jump_value*=jump_strength

            else: #once a very low jumping speed is reached the jump is complete
                jumping=False
                jump_value=max_jump

        else: #prevents players jumping through assets
            jump_value=max_jump
            
            jumping=False
    return jump_value, jumping #returns the changing values

def check_for_death(player):
    '''checks if the player should be dead'''
    key=pygame.key.get_pressed()
    if player.y > screen_width+player.camera_moved+2*player.height: #if the player falls under the map they die
        death(player,'Mind The Gap')
    if player.health <= 0: #when players health is 0 they die
        death(player,player.death_message)
    if key[pygame.K_k]:
        death(player,'Dead')

def knockback(player,amount,direction):
    '''moves the player back when hit'''
    collision_data=check_collisions(collision_list,player)
    collision_checks=collision_data[0]
    can_left=collision_checks[2]
    can_right=collision_checks[3]
    
    if player.knockback > 1:
        player.knockback*=(0.9)/framerate_adjustment
    else:
        player.knockback=0
        
    if direction == 'left' and can_left:
        if class_type(player) == 'player':
            scroll_level(round(amount*framerate_adjustment),player,False)
        else:
            player.x+=round(amount)

        player.rect=pygame.Rect(player.x,player.y,player.width,player.height)

        collision_data=check_collisions(collision_list,player)
        collision_checks=collision_data[0]
        can_left=collision_checks[2]

        if not can_left:
            for i in range(0,round(amount)): #moves the player 1 pixel at a time
                collision_data=check_collisions(collision_list,player)
                collision_checks=collision_data[0]
                can_left=collision_checks[2]

                if not can_left: #ensures the player doesnt get stuck in a block
                    if class_type(player) == 'player':
                        scroll_level(-1*framerate_adjustment,player,False)
                    else:
                        player.x-=1
                    break
                
                if class_type(player) == 'player':
                    scroll_level(1*framerate_adjustment,player,False)
                else:
                    player.x+=1

                player.rect=pygame.Rect(player.x,player.y,player.width,player.height)
            
    elif direction == 'right' and can_right:
        if class_type(player) == 'player':
            scroll_level(round(-amount*framerate_adjustment),player,False)
        else:
            player.x-=round(amount)

        player.rect=pygame.Rect(player.x,player.y,player.width,player.height)

        collision_data=check_collisions(collision_list,player)
        collision_checks=collision_data[0]
        can_right=collision_checks[3]

        if not can_right:
            for i in range(0,round(amount)): #moves the player 1 pixel at a time
                collision_data=check_collisions(collision_list,player)
                collision_checks=collision_data[0]
                can_right=collision_checks[3]

                if not can_right: #ensures the player doesnt get stuck in a block
                    if class_type(player) == 'player':
                        scroll_level(1*framerate_adjustment,player,False)
                    else:
                        player.x+=1
                    break
                
                if class_type(player) == 'player':
                    scroll_level(-1*framerate_adjustment,player,False)
                else:
                    player.x-=1

                player.rect=pygame.Rect(player.x,player.y,player.width,player.height)
                
    
def change_framerate(new):
    '''adjusts the games speed to the new framerate'''
    global framerate_adjustment
    framerate_adjustment=60/new
    global frame_rate
    frame_rate=new
    return framerate_adjustment

def display_framerate(frame_count,prev_time,frames):
    '''displays the frames per second'''
    font=pygame.font.SysFont('ocr a extended',50)
    frame_count+=1
    
    current_time=datetime.datetime.now().second
    if current_time != prev_time: #checks if a second has passed
        frames=frame_count #stores the frames shown in that second
        frame_count=0
        
    prev_time=current_time
    
    fps_text=font.render('FPS: '+str(frames)+'/'+str(frame_rate),1,(255,255,255)) #displays framerate
    win.blit(fps_text,(0,80))
    
    return frame_count,prev_time,frames

def display_time(previous_time,player):
    '''shows for how long the player has been in that level'''
    font=pygame.font.SysFont('ocr a extended',50)

    screen_width, screen_height = win.get_width(), win.get_height()

    time_icon=pygame.image.load(image_path+'time icon.png').convert_alpha()
    
    current_time=datetime.datetime.now().second
    if current_time != previous_time:
        player.time+=1
    previous_time=current_time

    time_text=font.render(str(player.time),1,(255,255,255))
    
    win.blit(time_text,(screen_width-time_text.get_width(),15))
    win.blit(time_icon,(screen_width-time_text.get_width()-time_icon.get_width(),5))

    return previous_time, time_text.get_width()+time_icon.get_width()

def get_mouse():
    '''creates a hitbox of the mouse'''
    mouse_pos=pygame.mouse.get_pos()
    mouse_point=pygame.Rect(mouse_pos[0],mouse_pos[1],1,1)
    return mouse_point
 
def class_type(asset):
    '''Returns the objects type e.g. tile or particle'''
    asset_type=str(asset.__class__)
    return (asset_type[asset_type.find('.')+1:-2])

def create_tint(screen_width,screen_height):
    '''returns a tinted surface'''
    tint = pygame.Surface((screen_width,screen_height),pygame.SRCALPHA)  #creates an empty per-pixel alpha Surface.
    tint = tint.convert_alpha()
    tint.fill((250,0,0,100))
    tint = tint.convert_alpha()
    return tint

def update_file(name,new_information,use_comma):
    '''writes an array to a file writing over the old one'''
    file=open(file_path+name+'.txt','w')
    file.write('') #resets the file
    file.close()
    file=open(file_path+name+'.txt','a')
    index=1
    for item in new_information: #writes the new information into the file
        if item != '':
            if use_comma:
                if index == len(new_information):
                    file.write(item)
                else:
                    file.write(item+',')
            else:
                file.write(item)
        index+=1
        
    file.close()

def store_asset(level,line_num,asset_type,asset_name,assetX,assetY):
    '''adds a new asset to the specified file'''
    assetX, assetY = str(assetX), str(assetY)
    file=open(file_path+level+'.txt')
    read_file=file.readlines()

    file.close()
    
    if asset_type in ['sign']:
        new_item='|'+asset_type+'.'+asset_name+'.'+assetX+'.'+assetY+'.Enter Text'
    else:
        new_item='|'+asset_type+'.'+asset_name+'.'+assetX+'.'+assetY

    read_file[line_num]=read_file[line_num].strip('\n')+new_item+'\n' #new item is added to the correct level in the file

    update_file(level,read_file,False)


def delete_asset(level,line_num,asset_type,asset_name,assetX,assetY):
    '''deletes an asset from the specified file'''
    assetX, assetY = str(assetX), str(assetY)
    asset_type=asset_type.lower()
    
    file=open(file_path+level+'.txt')
    read_file=file.readlines()
    read_line=read_file[line_num].split('|')
    file.close()
    
    deleted_item=asset_type+'.'+asset_name+'.'+assetX+'.'+assetY
    new_line=''
    
    index=0
    for item in read_line:
        if deleted_item in item:
            if index == len(read_line)-1: #end of the file has been reached
                new_line=new_line[:-1] #removes the comma at the end and doesnt add the last asset to be stored
        else:
            if index < len(read_line)-1:
                new_line=new_line+item+'|' #item isnt being deleted so is stored
            else:
                new_line=new_line+item #last item has been reached so no comma is added
        index+=1

    if '\n' not in new_line and line_num < len(read_file):
        new_line=new_line+'\n'

    read_file[line_num]=new_line #level is updated
    
    update_file(level,read_file,False) #level is stored

def edit_asset(level,line_num,asset_type,asset_name,assetX,assetY,new_data):
    '''edits an assets data from the specified file'''
    assetX, assetY = str(assetX), str(assetY)

    new_data=new_data.replace('|','')
    
    file=open(file_path+level+'.txt')
    read_file=file.readlines()
    read_line=read_file[line_num].split('|')
    file.close()

    edited_item=asset_type+'.'+asset_name+'.'+assetX+'.'+assetY
    new_line=''
    
    index=0
    for item in read_line:
        if edited_item in item:
            if index < len(read_line)-1:
                new_line=new_line+edited_item+'.'+new_data+'|' #item is found in the file and updated
            else:
                new_line=new_line+edited_item+'.'+new_data #no comma added as is end of level
        else:
            if index < len(read_line)-1:
                new_line=new_line+item+'|' #item is not the one to be edited so is added
            else:
                new_line=new_line+item
        index+=1

    if '\n' not in new_line and line_num < len(read_file):
        new_line=new_line+'\n'

    read_file[line_num]=new_line #changes are stored

    update_file(level,read_file,False)

def highlight_delete(position):
    '''finds the asset the mouse is over and highlights it'''
    cursor_position=pygame.Rect(position[0],position[1],1,1)
    deletion_asset=None

    for item in collision_list: #finds the asset the cursor is hovering over
        if cursor_position.colliderect(item.rect) and not item.offscreen:
            deletion_asset=item
            break
                
    if deletion_asset is None:
        for item in nonCollision_list:
            if cursor_position.colliderect(item.rect) and not item.offscreen:
                deletion_asset=item
                break

    if deletion_asset is not None: #if an asset is found it is highlighted in red
        delete_tint=create_tint(deletion_asset.width,deletion_asset.height)
        win.blit(delete_tint,(deletion_asset.x,deletion_asset.y))
        
    return deletion_asset

def remove_from_level(collision_list,nonCollision_list,deleted_item):
    '''removes an item from the level'''
    deleted=False
    index=0
    for item in collision_list: #lists are indexed through to find if it holds the item
        if item == deleted_item:
            collision_list.pop(index) #item is deleted
            deleted=True
            break
        index+=1

    if not deleted: #item can only be in one list so only one is checked    
        index=0
        for item in nonCollision_list:
            if item == deleted_item:
                nonCollision_list.pop(index) #item is deleted
                break
            index+=1
            
    return collision_list, nonCollision_list
    
def check_valid_placement(collision_list,nonCollision_list,placing_varient,position,varient_dimensions):
    '''checks if an asset can be placed'''
    varient_width, varient_height = varient_dimensions
    Xposition, Yposition = position
    
    if placing_varient == 'liquid': #adjusts the hitbox size of some assets
        varient_height-=4
        
    elif placing_varient in ['tile','solid_obsticle']:
        varient_width-=8
        varient_height-=8
        
    cursor_position=pygame.Rect(Xposition,Yposition,varient_width,varient_height)
    
    for item in collision_list:
        if cursor_position.colliderect(item.rect) and not item.offscreen:
            return False #trying to place anything in a solid block is invalid

    for item in nonCollision_list:
        if cursor_position.colliderect(item.rect) and not item.offscreen:
            if class_type(item) == placing_varient:
                return False #placing anything in itself is invalid
            if placing_varient in ['tile','solid_obsticle']:
                return False
            if class_type(item) in ['liquid']:
                return False

    return True

def reset_level(player):
    '''returns the level to its starting state'''
    for item in nonCollision_list:
        item.dead=False
        if class_type(item) in ['checkpoint','enemy']:
            item.reset()

    for item in collision_list:
        if class_type(item) in ['unstable_tile','door']:
            item.reset()

    player.reset()

def set_weather(weather,level):
    '''stores the new value for the weather in file'''
    file=open(file_path+'player levels.txt')
    read_file=file.readlines()
    file.close()
    
    current_level=read_file[level]
    level_data=current_level[:current_level.find('|')] #the levels data is found
    rest_of_file=current_level[current_level.find('|'):]
    level_data=level_data.split('.') #levels data is seperated

    read_file[level]=level_data[0]+'.'+level_data[1]+'.'+weather+rest_of_file

    update_file('player levels',read_file,False)
    
    
            
        
    
    
    
    


