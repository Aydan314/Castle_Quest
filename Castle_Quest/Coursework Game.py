import pygame
import random
import sys
import datetime

pygame.init()

path=sys.path[0]
file_path=path+'\\Game files\\'

image_path=path+'\\Asset Images\\' #lets the game know where its files are currently located
sys.path.append(file_path)
from Game_Objects import *  #objects and functions needed for the game are imported

file=open(file_path+'asset list.txt','r+') #opens the file that keeps track of all valid items in the game
asset_list=file.read().split(',')
file.close()

bubble_sort(asset_list) #ensures the list is in alphabetical order
update_file('asset list',asset_list,True)

big_font=pygame.font.SysFont('ocr a extended',80)
font=pygame.font.SysFont('ocr a extended',40)
small_font=pygame.font.SysFont('ocr a extended',15)

leave_game=False
current_user=None

global onScreen_collision_list
onScreen_collision_list=[]

leave_game=boot_screen()

if not leave_game:
    menu_info=run_main_menu(current_user,None) #displays the main menu when first run
    leave_game, current_user, game_position, current_level, screen_width, screen_height = menu_info

if not leave_game:
    file_name='Game Levels'
    player_file='Player Levels'
    player=player(round(screen_width/2),600,current_user) #player object is created via the GAME OBJECTS

    if current_user.fps_30:
        framerate_adjustment=change_framerate(30)
        
    else:
        framerate_adjustment=change_framerate(60)

    if game_position != 'settings':
        if game_position in ['editor','user level']:
            level=load_level(player_file,current_level,player)
        else:
            level=load_level(file_name,current_level,player)
    
        collision_list, nonCollision_list = level #information from the level object is set as local variables
        
        adjust_level(player,800-win.get_width(),800-win.get_height(),True) #adjusts the level to fit the screen

        onScreen_collision_list = collision_list

    distance_travelled=0 #initial values for the game are defined
    cloud_cooldown=0
    jump_value=40
    gravity_value=1

    can_right=True
    can_left=True
    jumping=False

    frame_count=0
    prev_time=0
    previous_time=0
    frames=0
    attack_cooldown=60//framerate_adjustment
    colour_num=0

    font=pygame.font.SysFont('ocr a extended',20)

    screen_width, screen_height = win.get_width(), win.get_height()

    red_tint=create_tint(screen_width,screen_height) #transparent red surface from when player is damaged

    play_button=button(5,5,pygame.image.load(image_path+'play.png'),(100,200,100)) #level editor GUI objects are defined
    help_button=button(80,5,pygame.image.load(image_path+'help.png'),(100,200,200))
    sun_button=button(5,5,pygame.image.load(image_path+'sunny icon.png'),(100,100,200))
    rain_button=button(5,5,pygame.image.load(image_path+'rain icon.png'),(100,100,200))
    snow_button=button(5,5,pygame.image.load(image_path+'snow icon.png'),(100,100,200))
    
    search_bar=textbox(5,600,50,(320,500),(230,230,230))
    search_text=font.render('- Search For Assets Here -',1,(255,255,255))
    text_edit=textbox(5,600,50,(80,500),(230,230,230))
    cursor='dirt'
    asset_type='tile'

    continue_button=button(0,200,big_font.render('  CONTINUE   ',1,(255,250,250)),(240,140,50)) #GUI objects for the pause menu
    settings_button=button(0,300,big_font.render('  SETTINGS   ',1,(255,250,250)),(240,130,50))
    main_menu_button=button(0,400,big_font.render('  MAIN MENU  ',1,(255,250,250)),(240,120,50))
    exit_button=button(0,500,big_font.render('  EXIT GAME  ',1,(255,250,250)),(240,110,50))
    editor_button=button(0,600,big_font.render('  EDITOR     ',1,(255,250,250)),(240,100,50))

    if game_position in ['game','user level']: #decides whether to run the game
        in_game=True
    else:
        in_game=False

    delete_cooldown=0
    deletion_cooldown=10//framerate_adjustment
    placement_cooldown=10//framerate_adjustment
    delete_mode=False
    main_menu=False
    
run=True
while run and not leave_game:
    if main_menu: #the main menu is run if selected in the pause menu
        menu_info=run_main_menu(player.user,player)
        leave_game, current_user, game_position, current_level, screen_width, screen_height = menu_info
        
        framerate_adjustment=1
        if current_user.fps_30:
            framerate_adjustment=2

        if leave_game:
            break
            
        placement_cooldown=10//framerate_adjustment #prevents placing or deleting after clicking the mouse in th menu
        deletion_cooldown=10//framerate_adjustment
        attack_cooldown=60//framerate_adjustment
        screen_width, screen_height = win.get_width(), win.get_height()
        time=0

        player.y=600
        player.x=screen_width//2

        if current_level is not None: #if a level is selected from the menu it is loaded
            
            if game_position == 'editor':
                in_game=False #game isnt run if it is being edited
                level=load_level(player_file,current_level,player)
                
            elif game_position == 'user level':
                in_game=True
                level=load_level(player_file,current_level,player)
                
            else:
                in_game=True
                level=load_level(file_name,current_level,player)

            collision_list, nonCollision_list = level #information from the level object is set as local variables

            player.level_adjusted=[0,0]

            adjust_level(player,800-win.get_width(),800-win.get_height(),True) #adjusts the level to fit the screen

            onScreen_collision_list = collision_list

            player.distance_travelled=0 #player position is reset
            player.camera_moved=0
            player.respawn_distance=0


        red_tint=create_tint(screen_width,screen_height) #transparent red surface from when player is damaged
        
        if game_position != 'settings':
            main_menu=False
        
    key=pygame.key.get_pressed()

    mouse_pos=pygame.mouse.get_pos()
        
    if in_game and not leave_game and game_position != 'settings': #runs the game 
        if key[pygame.K_ESCAPE]: #brings up the pause menu
            pause_info=pause_menu(continue_button,settings_button,main_menu_button,exit_button,editor_button,game_position,player,red_tint)
            leave_game, screen_width, screen_height, main_menu, in_game, red_tint = pause_info
            
            framerate_adjustment=1
            if current_user.fps_30:
                framerate_adjustment=2
            
            placement_cooldown=10//framerate_adjustment
            deletion_cooldown=10//framerate_adjustment #cooldown after mouse click in the menu
            attack_cooldown=60//framerate_adjustment
            
        if player.won: #stops the game when the player has won
            in_game=False
            player.won=False
        
        random_gametick=random.randint(1,1000) #a random number to map random events to

        game_events=level_events(player,red_tint,win) #checks for any changes in window size or quitting via GAME OBJECTS
        
        run, screen_width, screen_height, events, red_tint = game_events #data is stored in variables for later use & returns transparent red surface for when player is hurt

        game_window(player,collision_list,nonCollision_list,screen_width,screen_height,red_tint,False,current_level,game_position) #game window is drawn via the GAME OBJECTS

        if current_user.display_fps:
            frame_info=display_framerate(frame_count,prev_time,frames)
            frame_count, prev_time, frames = frame_info

        previous_time, offset = display_time(previous_time,player)

        colour_num = draw_points(player,offset,colour_num)
        
        pygame.display.flip()
        
            
        if random_gametick <= 3 and cloud_cooldown == 0: # 3/1000 chance of creating a cloud per frame
            nonCollision_list.insert(0,particle(-80,random.randint(1,round(screen_height/4)),'cloud '+str(random.randint(0,2)),(None,None))) #cloud particle object is added to the level
            cloud_cooldown=100

        if random_gametick <= 200:
            if player.weather == 'snow':
                nonCollision_list.append(precipitation(random.randint(-320,screen_width-80),11,'snowflake '+str(random.randint(0,2)),(None,None))) #creates precipitation particles
            elif player.weather == 'rain':
                nonCollision_list.append(precipitation(random.randint(-320,screen_width-80),11,'raindrop '+str(random.randint(0,2)),(None,None)))

        if cloud_cooldown != 0 : #ensures clouds arent created too close together
            cloud_cooldown-=1

        check_for_death(player)

        player.in_air=False

        collision_data=check_collisions(collision_list,player) #collisions of player and collidables checked in the GAME OBJECTS
        
        collided_items=collision_data[1]
        collision_checks=collision_data[0]

        roof_item, ground_item, left_item, right_item = collided_items

        roof_level, close_to_ground = collision_data[2], collision_data[3]
        
        
        roof_contact, ground_contact, can_left, can_right = collision_checks #collisions from GAME OBJECTS are stored as variables

        adjust_camera(player,close_to_ground)

        jump_data=handle_jumping(player,jumping,ground_contact,ground_item,roof_contact,roof_level,jump_value) #GAME OBJECTS handles the players jumping motion
        jump_value, jumping = jump_data #values changed by the functions are stored and sent back in

        player.moving=False
        player.has_momentum=False

        if pygame.mouse.get_pressed()[0] and attack_cooldown == 0:
            if mouse_pos[0] > player.x: #creates an axe for the player to throw with a knockback direction
                nonCollision_list.append(returning_projectile(player.x,player.y,'axe','left','player',(mouse_pos[0],mouse_pos[1]),(None,None)))
            else:
                nonCollision_list.append(returning_projectile(player.x,player.y,'axe','right','player',(mouse_pos[0],mouse_pos[1]),(None,None)))
            attack_cooldown=60//framerate_adjustment

        if attack_cooldown != 0: #prevents spam attacking
            attack_cooldown-=1

        if key[pygame.K_SPACE] or key[pygame.K_UP] or key[pygame.K_w]:
            if ground_contact and not player.crouching: #can only jump if player is on the ground and not crouching
                jumping=True

        if key[pygame.K_DOWN] or key[pygame.K_RSHIFT] or key[pygame.K_s]:
            if can_right and ground_contact and not jumping: #stops crouching whilst mid air
                if not player.crouching: #only adjusts players height once
                    player.y+=player.height-player.crouch_height
                        
                player.crouching=True
                player.height=player.crouch_height
                player.width=player.crouch_width
            
        else: #keeps the player crouched if there is something above
            if not roof_contact:
                player.crouching=False
                player.height=player.default_height
                player.width=player.default_width

        if player.crouching:
            player.speed=player.crouch_speed #player slower when crouching
            player.has_momentum=False #player will not accelerate
            if roof_contact and not can_left and not can_right and ground_contact: #if a player is stuck in a block
                scroll_level((player.crouch_width+player.speed)-player.width,player,False) #players hitbox changes when crouching so adjustments must be made so player doesnt get stuck
        
        if key[pygame.K_LEFT] or key[pygame.K_a]:
            player.facing='left'
            player.has_momentum=True #allows player to accelerate
            if can_left:
                scroll_level(player.speed,player,False) #level is moved using the GAME OBJECTS
           
        elif key[pygame.K_RIGHT] or key[pygame.K_d]:
            player.facing='right'
            player.has_momentum=True #allows player to accelerate
            if can_right:
                scroll_level(-player.speed,player,False) #level is moved using the GAME OBJECTS

        if (key[pygame.K_LEFT] or key[pygame.K_a]) and (key[pygame.K_RIGHT] or key[pygame.K_d]): #the players acceleration is reset when changing directions quickly
            player.has_momentum=False

        if player.has_momentum:
            if player.speed < player.max_speed:
                player.speed+=round(player.speed_increase) #accelerates the player up to their top speed
                player.speed_increase+=player.acceleration*framerate_adjustment
                    
        else:
            player.speed=player.base_speed
            player.speed_increase=0
            
    elif not leave_game and game_position == 'editor':
        time=0
        game_events=level_events(player,red_tint,win) #checks for any changes in window size or quitting via GAME OBJECTS
        
        run, screen_width, screen_height, events, red_tint = game_events #data is stored in variables for later use & returns transparent red surface for when player is hurt

        game_window(player,collision_list,nonCollision_list,screen_width,screen_height,red_tint,True,current_level,game_position) #game window is drawn via the GAME OBJECTS
        play_button.draw(win)
        help_button.draw(win)
        
        sun_button.x=screen_width-sun_button.width*3 #sets the position of the button
        sun_button.y=5
        if sun_button.highlighted: #handles the sun weather setting button
            sun_button.y=0
            if sun_button.clicked:
                player.weather='sunny'
                sun_button.clicked=False
                set_weather('sunny',current_level)
                
        sun_button.draw(win)
        
        rain_button.x=screen_width-sun_button.width*2 #sets the position of the button
        rain_button.y=5
        if rain_button.highlighted: #handles the rain weather setting button
            rain_button.y=0
            if rain_button.clicked:
                player.weather='rain'
                rain_button.clicked=False
                set_weather('rain',current_level)
                
        rain_button.draw(win)
        
        snow_button.x=screen_width-sun_button.width #sets the position of the button
        snow_button.y=5
        if snow_button.highlighted: #handles the snow weather setting button
            snow_button.y=0
            if snow_button.clicked:
                player.weather='snow'
                snow_button.clicked=False
                set_weather('snow',current_level)
                
        snow_button.draw(win)

        x_distance=player.level_adjusted[0]+player.distance_travelled #stores the distance from (0,0) the camera has moved
        y_distance=player.level_adjusted[1]+player.camera_moved

        x_pos=round((80*(round(mouse_pos[0]/80))+(x_distance)%80)-80) #stores the position within the 80 x 80 grid
        y_pos=round((80*(round(mouse_pos[1]/80))+(y_distance)%80)-80)

        grid_cursor=(round(x_pos-x_distance),round(y_pos-y_distance))

        coordinates=font.render('[ '+str(grid_cursor[0])+' , '+str(grid_cursor[1])+' ]',1,(255,255,255))

        win.blit(coordinates,(screen_width-(coordinates.get_width()+5),screen_height-(coordinates.get_height()+5)))

        highlighting_interactable=False
        mouse=get_mouse()
        
        for item in nonCollision_list:
            if item.rect.colliderect(mouse) and class_type(item) in ['sign']: #detects if an interactable such as a sign is under the mouse
                highlighting_interactable=True
                
                text_edit.x, text_edit.y = (item.x-text_edit.width//2+40), item.y
                text_edit.draw(win,events) #draws a textbox on the sign to allow for editing its text
                
                win.blit(item.text,item.text_pos)
                
                if text_edit.final_text: #updates the signs text
                    item.update_text(player_file,current_level,text_edit.final_text)
                    text_edit.final_text=None   

        if key[pygame.K_DELETE] and delete_cooldown == 0:
            delete_mode=not delete_mode #toggles between place and delete mode
            delete_cooldown=20//framerate_adjustment

        if delete_cooldown != 0: #prevents switching to between delete mode and place mode too fast
            delete_cooldown-=1
            
        if deletion_cooldown != 0: #prevents deleting assets too fast
            deletion_cooldown-=1

        if placement_cooldown != 0: #prevents placing too fast
            placement_cooldown-=1

        if not search_bar.highlighted and not play_button.highlighted and not highlighting_interactable: #prevents editing the level when GUI components are in use
            if not rain_button.highlighted and not sun_button.highlighted and not snow_button.highlighted and not help_button.highlighted:
                if delete_mode:
                    selected_asset=highlight_delete(mouse_pos)
                    if pygame.mouse.get_pressed()[0] and selected_asset is not None:
                        if deletion_cooldown == 0:
                            if class_type(selected_asset) == 'enemy':
                                delete_asset(player_file,current_level,class_type(selected_asset),selected_asset.varient,selected_asset.fileX,selected_asset.fileY) #removes asset from the level file
                            else:
                                delete_asset(player_file,current_level,class_type(selected_asset),selected_asset.varient,selected_asset.initialX,selected_asset.initialY)
                                
                            collision_list, nonCollison_list = remove_from_level(collision_list,nonCollision_list,selected_asset) #removes the asset from the level list
                    
                            onScreen_collision_list = collision_list
                            
                            deletion_cooldown=10//framerate_adjustment
                
                else:
                    try:
                        cursor_image=pygame.image.load(image_path+cursor+' 0.png') #selects the image for the placing cursor
                    except:
                        cursor_image=pygame.image.load(image_path+cursor+'.png')
                    win.blit(cursor_image,(x_pos,y_pos))

                    if pygame.mouse.get_pressed()[0] and placement_cooldown == 0:
                        can_place=check_valid_placement(collision_list,nonCollision_list,asset_type,(x_pos,y_pos),(cursor_image.get_width(),cursor_image.get_height())) #prevents invalid placement such as blocks inside blocks
                        if can_place:
                            if asset_type == 'sign':
                                new_item=asset_type+'.'+cursor+'.'+str(x_pos)+'.'+str(y_pos)+'.Enter Text'
                            else:
                                new_item=asset_type+'.'+cursor+'.'+str(x_pos)+'.'+str(y_pos)
                                
                            store_asset(player_file,current_level,asset_type,cursor,grid_cursor[0],grid_cursor[1]) #adds the new item to the file snapping to the 80 x 80 grid
                            
                            collision_list, nonCollision_list = add_to_level(new_item,collision_list,nonCollision_list,grid_cursor,player) #adds the new item to the level list
                            
                            onScreen_collision_list = collision_list

                            placement_cooldown=10//framerate_adjustment
                        else:
                            pygame.draw.rect(win,(255,30,30),(x_pos,y_pos,cursor_image.get_width(),cursor_image.get_height()),4) #shows if placement is invalid
                        
            
        if search_bar.text == '':
            win.blit(search_text,(5,search_bar.y-(search_text.get_height()+5))) 
        else:
            y_value=search_bar.y #if something is being searched suggestions are shown
            valid_asset=False
            valid_item=''
            
            for item in asset_list:
                asset=item[item.find('.')+1:] #finds all the asset names
                if search_bar.text in asset:
                    asset_text=font.render(asset.capitalize(),1,(255,255,255))
                    
                    y_value-=asset_text.get_height()+2
                    win.blit(asset_text,(5,y_value))
                    
                if search_bar.text == asset: #validates the asset exists within the game
                    valid_asset=True
                    valid_item=item

        if search_bar.get_text() and valid_asset:
            cursor=valid_item[valid_item.find('.')+1:]
            asset_type=valid_item[:valid_item.find('.')] #cursor is set to the user defined asset
        
        search_bar.draw(win,events)
        frame_info=display_framerate(frame_count,prev_time,frames)
        pygame.display.flip()
            
        search_bar.y=screen_height-(search_bar.height+5)

        frame_count=frame_info[0]
        prev_time=frame_info[1]
        frames=frame_info[2]
        
        if not search_bar.active and not highlighting_interactable:

            if key[pygame.K_ESCAPE]:
                pause_info=pause_menu(continue_button,settings_button,main_menu_button,exit_button,editor_button,'editor level',player,red_tint)
                leave_game, screen_width, screen_height, main_menu, in_game, red_tint = pause_info

                framerate_adjustment=1
                if current_user.fps_30:
                    framerate_adjustment=2
            
                placement_cooldown=10//framerate_adjustment
                deletion_cooldown=10//framerate_adjustment #brings up the pause menu

            if key[pygame.K_LEFT] or key[pygame.K_a]:
                scroll_level(10,player,False) #level is moved using the GAME OBJECTS
                player.x+=10*framerate_adjustment
               
            elif key[pygame.K_RIGHT] or key[pygame.K_d]:
                scroll_level(-10,player,False) #level is moved using the GAME OBJECTS
                player.x-=10*framerate_adjustment

            if key[pygame.K_UP] or key[pygame.K_w]:
                scroll_level(10,player,True) #level is moved using the GAME OBJECTS
                player.y+=10*framerate_adjustment
               
            elif key[pygame.K_DOWN] or key[pygame.K_s]:
                if player.camera_moved > 0:
                    scroll_level(-10,player,True) #level is moved using the GAME OBJECTS
                    player.y-=10*framerate_adjustment

            if play_button.clicked: 
                for item in collision_list: #resets the camera back to the player
                    item.x-=player.respawn_distance
                    item.y-=player.camera_moved
                for item in nonCollision_list:
                    item.x-=player.respawn_distance
                    item.y-=player.camera_moved

                player.x-=player.respawn_distance
                player.y-=player.camera_moved

                player.camera_moved=0
                player.respawn_distance=0
                player.distance_travelled=0
                    
                in_game=True
                play_button.clicked=False

            elif help_button.clicked:
                leave_game, red_tint=help_page(player,red_tint,win)
                help_button.clicked=False
            

    else:
        time=0
        if game_position == 'game': #if the level is completed
            go_back=False
            
            level_info=level_select_menu(player,current_user) #returns to the level select menu
            leave_game, go_back, current_level = level_info
            attack_cooldown=60//framerate_adjustment

            player.distance_travelled=0 #player position is reset
            player.camera_moved=0
            player.respawn_distance=0
            
            if current_level is not None:
                level=load_level(file_name,current_level,player) #new level is loaded
                collision_list, nonCollision_list = level #information from the level object is set as local variables
                
                adjust_level(player,800-win.get_width(),800-win.get_height(),True) #adjusts the level to fit the screen

                onScreen_collision_list = collision_list
                
                in_game=True

            if go_back:
                main_menu=True

        elif game_position == 'user level':
            go_back=False
            
            level_info=creator_level_menu(player,current_user) #returns to the level select menu
            leave_game, go_back, current_level, can_edit = level_info
            attack_cooldown=60//framerate_adjustment

            player.distance_travelled=0 #player position is reset
            player.camera_moved=0
            player.respawn_distance=0
            
            if current_level is not None:
                level=load_level('player levels',current_level,player) #new level is loaded
                collision_list, nonCollision_list = level #information from the level object is set as local variables
                
                adjust_level(player,800-win.get_width(),800-win.get_height(),True) #adjusts the level to fit the screen

                onScreen_collision_list = collision_list
                
                if can_edit:
                    in_game=False
                    game_position='editor'

                else:
                    in_game=True

            if go_back:
                main_menu=True
            
    
        else:
            main_menu=True

                    
pygame.quit()
