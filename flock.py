import pygame  as p
import math as m
import random 
from pygame import Vector2, color, event, math, surface
from pygame.draw import circle, ellipse
import sys
import time 
##from time import clock
from numpy.ma import angle, arccos
import numpy as np




p.init()

#----------- screen size --------

w = 800
h = 750
#----------- color -------------
white = (255, 255, 255)
lila = (255, 0, 255)
blue = (0, 0, 200)
rouge = (255, 0, 0)
orange = (255, 165, 0)
vert = (0, 255, 0)

scr = p.display.set_mode((w, h))
scr.fill(white)


#----------------- Boids and predator Class----------

class Boid(p.sprite.Sprite):

    def __init__(self,vel,x ,y, w =800, h =750):
        p.sprite.Sprite.__init__(self)
        

        self.pos = Vector2(x, y)
        self.radius = 5
        dir = (np.random.rand(2) - 0.5)*2
        self.vel = Vector2(*dir)
        dir = (np.random.rand(2) - 0.5)/2
        self.acc = Vector2(*dir)
        self.w = w
        self.h = h
        self.max_vel = 3
        self.radius_vision = 50
        self.area = scr.get_rect()
        self.ave_pos = Vector2(0,0)
        self.maximal_force = 0.05
        
    def update(self):
        
        if self.pos.x > self.w:
            self.pos.x = 0
        elif self.pos.x < 0:
                self.pos.x = self.w

        if self.pos.y > self.h:
            self.pos.y = 0
        elif self.pos.y < 0:
            self.pos.y = self.h

        self.getNpos()
        
        
    def getNpos(self):
        self.vel += self.acc
        self.pos += self.vel
        if np.linalg.norm(self.vel) > self.max_vel:
            self.vel = self.vel/ np.linalg.norm(self.vel)* self.max_vel
        self.acc = Vector2(*np.zeros(2))
       
    def draw(self):
        p.draw.circle(scr, lila, (int(self.pos.x), int(self.pos.y)), self.radius)

    def draw_predator(self):
        p.draw.circle(scr, orange, (int(self.pos.x), int(self.pos.y)), self.radius)



    def align(self): 
        new_vector = Vector2(0,0)
        ave_pos = Vector2(0,0)
        
       
        z=0
        for boid in boidlist:
            if np.linalg.norm(boid.pos - self.pos) < self.radius_vision:
                ave_pos +=boid.vel
                z += 1
        if z > 0:
            ave_pos/=z
            ave_pos = Vector2(*ave_pos)
            ave_pos = (ave_pos / np.linalg.norm(ave_pos)* self.max_vel) 
            new_vector = ave_pos - self.vel
            
        return new_vector
    
    def cohesion(self):
        new_vector = Vector2(0,0)
        k = 0
        main_point =Vector2(0,0)
        for boid in boidlist:
            if np.linalg.norm(boid.pos - self.pos) < self.radius_vision:
                main_point += boid.pos
                k += 1
        if k > 0:
            main_point /= k
            main_point = Vector2(*main_point)
            approaching = main_point - self.pos
            if np.linalg.norm(approaching) > 0:
                approaching = (approaching / np.linalg.norm(approaching))/ self.max_vel
            new_vector = approaching - self.vel
            if np.linalg.norm(new_vector) > self.maximal_force:
                new_vector = (new_vector / np.linalg.norm(new_vector))* self.maximal_force
        return new_vector

    def separation(self):
        new_vector = Vector2(0,0)
        r = 0
        ave_vector = Vector2(0,0)
        
        for boid in boidlist:
            distance = np.linalg.norm(boid.pos - self.pos)
            if self.pos != boid.pos and distance < self.radius_vision:
                proximity = self.pos - boid.pos
                proximity /= distance
                ave_vector += proximity
                r += 1
        
        if r > 0:
            ave_vector /= r
            ave_vector = Vector2(*ave_vector)
            if np.linalg.norm(new_vector) > 0:
                ave_vector = (ave_vector / np.linalg.norm(new_vector))* self.max_vel
            new_vector = ave_vector - self.vel
            if np.linalg.norm(new_vector) > self.maximal_force:
                new_vector = (new_vector / np.linalg.norm(new_vector))* self.maximal_force
        return new_vector

    def avoid_obstacles(self):
        ave_vector = Vector2(0,0)
        avoid_vision = 115
        pos_obj = Vector2(220,220)
        distance = np.linalg.norm(self.pos - pos_obj)
        distance = (self.pos - pos_obj).length()
        if self.pos != pos_obj and distance < avoid_vision:
            collision = self.pos - pos_obj
            collision /= distance
            ave_vector += collision

        return ave_vector

    def avoid_predator(self):
       
        avoid_predator_vision = 40
        ave_vector = Vector2(0,0)
        
        for boid in boidlist:
            boid.draw()
            for px in predatorlist:
                distance = (self.pos - px.pos).length()
                
                if  self.pos != px.pos and distance < avoid_predator_vision:
                    survive = self.pos - px.pos
                    survive /= distance
                    ave_vector +=survive
        return ave_vector    

    

    def hunting(self):
        self.radius = 15
        hungry_velocity_increment = (np.random.rand(2) - 0.5)
        self.acc = Vector2(*hungry_velocity_increment)
        self.max_vel = 5
        hunting_vision = 28
        for boid in boidlist:
            boid.draw()
            for px in predatorlist:
                if np.linalg.norm(boid.pos - px.pos) < hunting_vision:
                    print(hungry_velocity_increment)
                    print(boid.pos, px.pos)
                    boidlist.remove(boid)
                    



    def predator_avoid_object(self):

        ave_vector = Vector2(0,0)
        avoid_vision = 115
        pos_obj = Vector2(220,220)
        distance = np.linalg.norm(self.pos - pos_obj)
        distance = (self.pos - pos_obj).length()
        if self.pos != pos_obj and distance < avoid_vision:
            collision = self.pos - pos_obj
            collision /= distance
            ave_vector += collision
        return ave_vector


    def apply_predator_procedure(self):
        self.hunting()
       
        avoid = self.predator_avoid_object()
       
        self.acc += avoid

    def apply_procedure(self):
        alingment = self.align()
        cohesion = self.cohesion()
        separation = self.separation()
        collision = self.avoid_obstacles()
        avoid = self.avoid_predator()
        self.acc += alingment
        self.acc += cohesion
        self.acc += separation 
        self.acc += collision
        self.acc += avoid
       
class Obstacles():
        
    def __init__(self, x, y, w, h, color):

        self.color = color
        self.rect = p.Rect(x,y,h,w)
        self.obs_size = ellipse(scr, color, self.rect)
        self.pos = Vector2(x,y)
        
        random.randint(10,700), random.randint(100,650)
    
    def draw(self):

        p.draw.ellipse(scr, self.color, self.rect)



''' 
    def hunting(self, boidlist):
        hunting_vision = 100
        new_pos = Vector2(0,0)
        boids_ave_pos =Vector2(0,0)
        hunting_vector= Vector2(0,0)
        z=0
        for boid in boidlist:
            if np.linalg.norm(boid.pos - self.pos) < self.hunting_vision:
                boids_ave_pos +=boid.vel
                z += 1
        if z > 0:
            boids_ave_pos/=z
            boids_ave_pos = Vector2(*boids_ave_pos)
            boids_ave_pos = (boids_ave_pos / np.linalg.norm(boids_ave_pos)* self.max_vel) 
            hunting_vector = boids_ave_pos - self.vel
        return hunting
 '''


clock = p.time.Clock()

#------------------------ list of objects -----------------------

b0 = Boid(Vector2(2,15).normalize(), random.randint(10,700), random.randint(100,650))
b1 = Boid(Vector2(76,35).normalize(), random.randint(20,500), random.randint(210,320))
b2 = Boid(Vector2(120,540).normalize(), random.randint(35,67), random.randint(67, 430))
b3 = Boid(Vector2(22,28).normalize(), random.randint(90,700), random.randint(100,650))
b4 = Boid(Vector2(4,67).normalize(), random.randint(145,700), random.randint(100,650))
b5 = Boid(Vector2(86,64).normalize(), random.randint(190,700), random.randint(100,650))
b6 = Boid(Vector2(2,15).normalize(), random.randint(10,700), random.randint(100,650))
b7 = Boid(Vector2(102,15).normalize(), random.randint(10,700), random.randint(100,650))
b8 = Boid(Vector2(45,15).normalize(), random.randint(10,700), random.randint(100,650))
b9 = Boid(Vector2(2,15).normalize(), random.randint(10,700), random.randint(100,650))
b10 = Boid(Vector2(2,15).normalize(), random.randint(10,700), random.randint(100,650))
boidlist = [b0, b1, b2, b3, b4, b5, b6, b7, b8, b9, b10]

obt1 = Obstacles(160,160,120,120, (blue))

ObjectList = [obt1]

p0 = Boid(Vector2(300,400).normalize(), random.randint(10,35), random.randint(1,60))
predatorlist = [p0]

#------------------Main Loop-----------------------------------------------
while True:

    for event in p.event.get():
        if(event.type == p.QUIT or (event.type == p.KEYDOWN and event.key == p.K_ESCAPE)):
            
            sys.exit()
    time = clock.tick(30)
    scr.fill(white)
    for pre in predatorlist:
        pre.update()
        pre.draw_predator()
        pre.getNpos()
        pre.apply_predator_procedure()
    for obj in ObjectList:
        obj.draw()   
    for boid in boidlist:
        boid.update()
        boid.draw()
        boid.getNpos()
        boid.apply_procedure()
    p.display.update()
       

