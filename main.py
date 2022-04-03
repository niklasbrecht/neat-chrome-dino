import pygame
import os
import random
import sys
import neat
import math

pygame.init()

# Display constants

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 500
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

RUNNING = [pygame.image.load(os.path.join("textures/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("textures/Dino", "DinoRun2.png"))]

SMALLCACTUS = [pygame.image.load(os.path.join("textures/Cactus", "SmallCactus1.png")),
               pygame.image.load(os.path.join(
                   "textures/Cactus", "SmallCactus2.png")),
               pygame.image.load(os.path.join("textures/Cactus", "SmallCactus3.png"))]

LARGECACTUS = [pygame.image.load(os.path.join("textures/Cactus", "LargeCactus1.png")),
               pygame.image.load(os.path.join(
                   "textures/Cactus", "LargeCactus2.png")),
               pygame.image.load(os.path.join("textures/Cactus", "LargeCactus3.png"))]

JUMPING = pygame.image.load(os.path.join("textures/Dino", "DinoJump.png"))

BACKGROUND = pygame.image.load(os.path.join("textures/Other", "Track.png"))

FONT = pygame.font.Font('freesansbold.ttf', 20)

# Classes

class Dino:

    x_Pos = 80
    y_Pos = 230
    jumpVelocity = 9

    def __init__(self, img=RUNNING[0]):
        self.image = img
        self.dinoRun = True
        self.dinoJump = False
        self.sjumpVelocity = self.jumpVelocity
        self.rect = pygame.Rect(self.x_Pos, self.y_Pos,
                                img.get_width(), img.get_height())
        self.color = (random.randint(0, 255), random.randint(
            0, 255), random.randint(0, 255))
        self.stepIndex = 0

    def jump(self):
        self.image = JUMPING
        if self.dinoJump:
            self.rect.y -= self.sjumpVelocity * 4
            self.sjumpVelocity -= 0.8
        if self.sjumpVelocity <= -self.jumpVelocity:
            self.dinoJump = False
            self.dinoRun = True
            self.sjumpVelocity = self.jumpVelocity

    def run(self):
        self.image = RUNNING[self.stepIndex // 5]
        self.rect.x = self.x_Pos
        self.rect.y = self.y_Pos
        self.stepIndex += 1

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.rect.x, self.rect.y))
        pygame.draw.rect(SCREEN, self.color, (self.rect.x,
                         self.rect.y, self.rect.width, self.rect.height), 2)
        for obstacle in obstacles:
            pygame.draw.line(SCREEN, self.color, (self.rect.x +
                             54, self.rect.y + 12), obstacle.rect.center, 2)

    def update(self):
        if self.dinoRun:
            self.run()
        if self.dinoJump:
            self.jump()
        if self.stepIndex >= 10:
            self.stepIndex = 0


class Obstacle:
    def __init__(self, image, numberOfCactus):
        self.image = image
        self.type = numberOfCactus
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= gameSpeed
        if self.rect.x <= -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image, numberOfCactus):
        super().__init__(image, numberOfCactus)
        self.rect.y = 260


class LargeCactus(Obstacle):
    def __init__(self, image, numberOfCactus):
        super().__init__(image, numberOfCactus)
        self.rect.y = 235


def remove(index):
    dinos.pop(index)


def distance(posA, posB):
    dx = posA[0] - posB[0]
    dy = posA[1] - posB[1]
    return math.sqrt(dx**2 + dy**2)

# Main

def eval_genomes(genomes, config):
    global gameSpeed, xPosBg, yPosBg, obstacles, dinos, ge, nets, points

    clock = pygame.time.Clock()
    points = 0
    xPosBg = 0
    yPosBg = 300
    gameSpeed = 20

    obstacles = []
    dinos = []
    ge = []
    nets = []

    for genome_id, genome in genomes:
        dinos.append(Dino())
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    def score():
        global points, gameSpeed
        points += 1
        if points % 100 == 0:
            gameSpeed += 1
        text = FONT.render(f'Points:  {str(points)}', True, (0, 0, 0))
        SCREEN.blit(text, (850, 30))

    def stats():
        global dinos, gameSpeed, ge
        text1 = FONT.render(f'Alive: {str(len(dinos))}', True, (0, 0, 0))
        text2 = FONT.render(f'Generation: {pop.generation+1}', True, (0, 0, 0))
        text3 = FONT.render(f'Speed: {str(gameSpeed)}', True, (0, 0, 0))

        SCREEN.blit(text1, (50, 400))
        SCREEN.blit(text2, (50, 420))
        SCREEN.blit(text3, (50, 440))

    def background():
        global xPosBg, yPosBg
        imageWidth = BACKGROUND.get_width()
        SCREEN.blit(BACKGROUND, (xPosBg, yPosBg))
        SCREEN.blit(BACKGROUND, (imageWidth + xPosBg, yPosBg))
        if xPosBg <= -imageWidth:
            xPosBg = 0
        xPosBg -= gameSpeed

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        SCREEN.fill((255, 255, 255))

        for dino in dinos:
            dino.update()
            dino.draw(SCREEN)

        if len(dinos) == 0:
            break

        if len(obstacles) == 0:
            randInt = random.randint(0, 1)
            if randInt == 0:
                obstacles.append(SmallCactus(
                    SMALLCACTUS, random.randint(0, 2)))
            if randInt == 1:
                obstacles.append(LargeCactus(
                    LARGECACTUS, random.randint(0, 2)))

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            for i, dino in enumerate(dinos):
                if dino.rect.colliderect(obstacle.rect):
                    ge[i].fitness += 1
                    remove(i)

        for i, dino in enumerate(dinos):
            ge[i].fitness += 0.1
            output = nets[i].activate((dino.rect.y, distance(
                (dino.rect.x, dino.rect.y), obstacle.rect.midtop)))
            if output[0] > 0.5 and dino.rect.y == dino.y_Pos:
                dino.dinoJump = True
                dino.dinoRun = False

        stats()
        score()
        background()
        clock.tick(30)
        pygame.display.update()


# NEAT SETUP

def run(configPath):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        configPath
    )
 
    pop = neat.Population(config)
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.run(eval_genomes, 500)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    configPath = os.path.join(local_dir, 'config.txt')
    run(configPath)
