import os
import pygame as pg


#makes sure the font and mixer(sound) parts are working
if not pg.font:
      print("Fonts disabled")
if not pg.mixer:
      print("sound disabled")


#function to load images at a described scale (default is 1)
def load_image(name, colorkey=None, scale=1):
      #get image filename and path
      fullname = os.path.join(data_dir, name)
      #using the full path of the image, open it and store data to 'image'
      image = pg.image.load(fullname)


      #calculate the size of the image
      size = image.get_size()
      #then begin storing the data based on the scale
      size = (size[0] * scale, size[1] * scale)
      image = pg.transform.scale(image, size)

      image = image.convert()
      if colorkey is not None:
            if colorkey == -1:
                  colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pg.RLEACCEL)
      return image, image.get_rect()


#function to load sounds
def load_sound(name):
      class NoneSound:
            def play(self):
                  pass

      if not pg.mixer or not pg.mixer.get_init():
            return NoneSound()

      fullname = os.path.join(data_dir, name)
      sound = pg.mixer.Sound(fullname)

      return sound

class Player_Two(pg.sprite.Sprite):
      #player cursor (glove) 

      def __init__(self):
            pg.sprite.Sprite.__init__(self)
            #call pygame's sprite initializer
            self.image, self.rect = load_image("security_textures/glove.png", -1, scale=0.08)
            self.cursor_offset = (-64, -64)
            self.clicking = False

      def update(self):
            #fist move based on position
            pos = pg.mouse.get_pos()
            self.rect.topleft = pos
            self.rect.move_ip(self.cursor_offset)
            if self.clicking:
                  #gives small visual clue to user that they have clicked mouse by shifting image down and right
                  self.rect.move_ip(10, 20)

      def click(self, target):
            #if user clicks, get a small hitbox and return it (if sprite is in hitbox, will spin image)
            if not self.clicking:
                  self.clicking = True
                  hitbox = self.rect.inflate(-5, -5)
                  return hitbox.colliderect(target.rect)

      def unclick(self):
            #reset click
            self.clicking = False

class Player_One(pg.sprite.Sprite):
      def __init__(self):
            #call pygame's sprite initializer
            pg.sprite.Sprite.__init__(self)
            self.image, self.rect = load_image("security_textures/camera.png", -1, scale=0.25)
            screen = pg.display.get_surface()

            #get area of screen
            self.area = screen.get_rect()
            #starting coord of sprite
            self.rect.topleft = 64, 64


            self.disabled = False
            self.facingLeft = False

      def update(self, x, y):
            #if clicked, call spin, otherwise, keep calling walk
            if self.disabled:
                  self._spin(x, y)
            else:
                  self._walk(x, y)

      def _walk(self, x, y):
            #rotate playerOne
            newpos = self.rect.move(x, y)
            if not self.area.contains(newpos):
                  #if any of the borders of the player sprite is outside of bounds, reset the bounds
                  if newpos[0] < 0:
                        newpos[0] = 0
                  if newpos[0] > 1025:
                        newpos[0] = 1025
                  if newpos[1] < 0:
                        newpos[1] = 0
                  if newpos[1] > 465:
                        newpos[1] = 465
                  
            #if the sprite moves to the left and is not already facing left, flip the image and set facingLeft to True
            if x < 0 and self.facingLeft == False:
                        self.image = pg.transform.flip(self.image, True, False)
                        self.facingLeft = True
            #else if the sprite moves to the right, flip the image and set facingLeft to False
            elif x > 0 and self.facingLeft == True:
                        self.image = pg.transform.flip(self.image, True, False)
                        self.facingLeft = False

            #after the coord has been evaluated to be valid, set the position to the newpos
            self.rect = newpos


      def _spin(self, x, y):
            center = self.rect.center
            #if the sprite was clicked, move at half speed, rotate sprite, and reset once a full 360 has occured 
            newpos = self.rect.move(x/2,y/2)
            self.disabled = self.disabled + 12
            if self.disabled >= 360:
                  self.disabled = False
                  self.image = self.original
            else:
                  rotate = pg.transform.rotate
                  self.image = rotate(self.original, self.disabled)
            self.rect = self.image.get_rect(center=center)
            self.rect = newpos

      def clicked(self):
            #limits spamming the disable feature
            if not self.disabled:
                  self.disabled = True
                  self.original = self.image


main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")

#initialize the window, set the resolution, title of the game, disable the mouse, and create a boolean variable to keep game running
pg.init()
screen = pg.display.set_mode((1280,720), pg.SCALED)
pg.display.set_caption("Operations Specialist")
pg.mouse.set_visible(False)
running = True

#create background assets for the game 
background = pg.Surface(screen.get_size())
background = background.convert()
background.fill((170, 238, 187))

#background text for the game mission/directive
#instead of the background image just being the color written above, it also ties the text to the background to minimize redundancy
if pg.font:
      font = pg.font.Font(None, 64)
      text = font.render("Disable the Camera and win!!!", True, (10, 10, 10))
      textpos = text.get_rect(centerx=background.get_width()/2, y=10)
      background.blit(text, textpos)

#after drawing the font to the background, redraw the window once to display the text
screen.blit(background, (0, 0))
pg.display.flip()

#all sound effects in game
opening_sound = load_sound("security_audio/opening.ogg")
whiff_sound = load_sound("security_audio/whiff.wav")
click_camera_sound = load_sound("security_audio/hit.wav")


#create an instance of the Player_One class and store it to playerOne
playerOne = Player_One()
#create an instance of the Player_Two class and store it to playerTwo
playerTwo = Player_Two()

#cast the sprites to an array
allsprites = pg.sprite.RenderPlain((playerOne, playerTwo))


clock = pg.time.Clock()

#play the opening song
opening_sound.play()

#initialize the hit and miss counters to 0 for the game
hit=0
miss=0


while running:

      #set frame rate
      clock.tick(45)

      #exits if hit or miss equals 10
      if hit >= 10:
                running = False
                winner = "Glove"
      elif miss >= 10:
            running = False
            winner = "Camera"
      
      #reset x and y inputs every frame
      x=0
      y=0

      for event in pg.event.get():
            #if user clicks the 'x' to close
            if event.type == pg.QUIT:
                  running = False
            #if the user presses 'ESCAPE', exit
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                  running = False
            #if mouse is clicked, check if it intercepts with the sprite
            elif event.type == pg.MOUSEBUTTONDOWN:
                  #if it does, play the hit sound effect, and make playerOne spin with .clicked()
                  if playerTwo.click(playerOne):
                        click_camera_sound.play()
                        #as long as the player is not disabled, add a click(prevents playerTwo spamming for points)
                        if not playerOne.disabled:
                              hit += 1
                        playerOne.clicked()
                  #otherwise, play the 'whiff' sound effect and add 1 to the miss counter
                  else:
                        whiff_sound.play()
                        miss+=1
            #unclick the mouse, as this is technically a separate input
            elif event.type == pg.MOUSEBUTTONUP:
                  playerTwo.unclick()


      #this sections is separate from the above keys so it can continously grab keys
      keys = pg.key.get_pressed()
      #move by x or y coord by 32 points every loop that it is pressed
      if keys[pg.K_w]:
            y -= 32
      if keys[pg.K_s]:
            y += 32
      if keys[pg.K_a]:
            x -= 32
      if keys[pg.K_d]:
            x += 32

      #updates the cursor every loop
      playerTwo.update()

      #updates the player every loop using the inputs
      playerOne.update(x, y)

      #paint the default background
      screen.blit(background, (0, 0))

      #overlay the hits counter
      hits_text = font.render(f"Hits: {hit}", True, (10, 10, 10))
      screen.blit(hits_text, (5, 10))

      #overlay the misses counter
      miss_text = font.render("Misses: " + str(miss), True, (10, 10, 10))
      screen.blit(miss_text, (1050, 10))

      #overlay the sprites of playerOne and cursor
      allsprites.draw(screen)
      #swap the image buffer
      pg.display.flip()

#display winner screen
screen.fill((170, 238, 187))
winner_text = font.render(f"{winner} won!", True, (10, 10, 10))
textpos = winner_text.get_rect(centerx=screen.get_width()/2, centery=screen.get_height()/2)
screen.blit(winner_text, textpos)
pg.display.flip()

pg.time.wait(3000)

pg.quit()





'''
with video games, a lot of the visual rendering is a lot like drawing
a flipbook page by page extremely fast

it displays the previously drawn image, while drawing next image as quickly as possible and by the end of the loop
flips the drawn image to the user's display
'''
