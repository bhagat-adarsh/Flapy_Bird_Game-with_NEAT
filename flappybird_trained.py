import pygame
import neat
import time
import os
import random
pygame.font.init()  # Initialize the font module
WIN_WIDTH = 600
WIN_HEIGHT = 800

GEN = 0

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird3.png")))]


PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)  # Font for displaying score

class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5 # frames to switch bird images means their flapping 

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0 #which image are we showing
        self.img = self.IMGS[0] #reference to the bird images
        
    #the co-ordinate system for pygame starts from the top left corner thus we need to use negative to go up
    
    def jump(self):
        self.vel = -10.5
        self.tick_count = 0#after every time we jump our tick count turns back to 0
        self.height = self.y # stores the height of the bird when it jumps
    #suppose per jump the bird goes up by 10.5 pixels, 
    #-10.5 +1.5 = -9 amd so on, thus the bird will go up and then come down
    
    def move(self):
        self.tick_count += 1
                                          #|
                                          #V#gravity
        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2 # displacement formula (S=vt)
        
        if d >= 16:#(TErminal Velocity) if the bird goes up by more than 16 pixels then it will be capped at 16
            d = d/abs(d) #if the displacement is more than 16 then we cap it at 16 (tan kai wapas niche a limit is defined here)
        if d < 0:
            d -= 2
        self.y = self.y + d

        if d<0 or self.y<self.height + 50:
            if self.tilt < self.MAX_ROTATION:#mundi kharchane ke liye chatak! chatak!
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:#tapaknai sai backana
                self.tilt -= self.ROT_VEL


    def draw(self,win):
        self.img_count += 1

        #how many frames have passed since the last image was shown
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count >= self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0 #reset karega image count

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt) #centering the image after rotation
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)   
        win.blit(rotated_image, new_rect.topleft) #blit the rotated image on the window

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 200  # Gap between the top and bottom pipes
    VEL = 5  # Speed of the pipes

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100
        
        self.top = 0

        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL # Move the pipes to the left
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))




    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x -bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)


        if t_point or b_point:
            return True
        
        return False

class Base():
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH


        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH


    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))



def draw_window(win, birds,pipes,base,score,gen):
    win.blit(BG_IMG, (0, 0))  # Draw background ==blit

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render(f"Score: {score}", 1, (255, 255, 255))  # Render the score text
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))  # Draw the score text at the top right corner

    text = STAT_FONT.render(f"Gen: {gen}", 1, (255, 255, 255))  # Render the score text
    win.blit(text, (10, 10))  

    base.draw(win)  
    for bird in birds:
        bird.draw(win)  
    pygame.display.update()  # Update the display


def main(genomes, config):
    global GEN
    GEN += 1
    birds = []
    ge = []
    nets = []
#cauz genome is a kind of tupyles
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0  # Initialize fitness for each genome
        ge.append(g)



    base = Base(730)
    pipes = [Pipe(700)]  
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))  # Create a window
    pygame.display.set_caption("Flappy Bird")  # Set the window title
    clock = pygame.time.Clock()  # Create a clock to control the frame r
    
    score = 0

    run = True
    while run:
        clock.tick(30)
        for even in pygame.event.get():
            if even.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()  

        pipe_ind = 0

        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()            
            ge[x].fitness += 0.1#less fitness kyu ki 30 times chalega
            
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            
            if output[0] > 0.5:
                bird.jump()



        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1  # Penalize the genome for collision
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)


                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()
        if add_pipe:
            score +=1
    
            for g in ge:
                g.fitness += 5  # Reward the genome for passing a pipe
            pipes.append(Pipe(700))
        for r in rem:
            pipes.remove(r)


        for x,bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)


        base.move()
        draw_window(win, birds,pipes,base,score,GEN)
        

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                 neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                   config_path)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run (main,50)

# Run the NEAT algorithm for 50 generations
# This function initializes the NEAT algorithm and runs it for a specified number of generations
#fitness function for neat all it those is set the fitness for our birds how many generations are we gonna run,
#  (basically how far are we going to move in the game)




if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)#pahle load phir config file mai n joining bsics of setting NEAT
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)