#CARlA 9.8 win 10
#22 - 04 - 2020
#HTX Roskilde


import glob
import os
import sys

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

import weakref
import random
import numpy as np
import math
import pygame


from pygame.locals import K_a
from pygame.locals import K_d
from pygame.locals import K_s
from pygame.locals import K_w

from pygame.locals import K_ESCAPE
from pygame.locals import K_r


# Display dimensions
# Dimension as integers
display_width = 1920//2
display_height = 1080//2


class radar:
    def __init__(self, player):
        self.sensor = None
        self.player = player
        self._control = carla.VehicleControl()
        world = self.player.get_world()
        self.debug = world.debug

        # Varibles for the emergency brake
        self.emergency = False
        self.koncentration  = 0
        self.depth = None

        #Scearch for the right sensor in the libary
        bp = world.get_blueprint_library().find('sensor.other.radar')
        
    
        #Vertical field of view in degrees.
        bp.set_attribute('vertical_fov', str(15))
        
        # Set camera loction on the car
        # Change the angle (pitch)
        transform = carla.Transform(carla.Location(x=2.5, z=0.5),carla.Rotation(pitch=1))
        self.sensor = world.spawn_actor(bp,transform, attach_to=self.player)

        self.sensor.listen(lambda radar_data: self.process_data(radar_data))

    
    def process_data(self, radar_data):
        
        rotation_listen = radar_data.transform.rotation
         # Get data for sensor
        for detect in radar_data:
            self.depth = detect.depth

            
            # Check if emergency brake is necessary 
            self.emergency_brake()

            # -- Points on screen ----------------------------------------------------------

            # Creat a vektor, where y = 0 and z = 0
            location = carla.Vector3D(x=detect.depth-1)
            
             #Azimuth angle in radians. Converter to degrees
            azimuth = math.degrees(detect.azimuth)
            #Altitude angle in radians. Converter to degrees
            altitude  = math.degrees(detect.altitude)
            
            #carla.Rotation
            # pitch = Degrees around the Y-axis
            # yaw  = Degrees around the Z-axis.
            # roll = Degrees around the X-axis.
            # All varibles are float
            
            #Transform the vector location with the correct values

            carla.Transform(
                carla.Location(),
                carla.Rotation(
                    pitch=rotation_listen.pitch + altitude,
                    yaw=rotation_listen.yaw + azimuth,
                    roll=rotation_listen.roll)).transform(location)

            # Draw the points on the screen
            #draw_point(self, location, size=0.1f, color=(255,0,0), life_time=-1.0f)
            self.debug.draw_point(
                location = radar_data.transform.location + location,
                size= 0.06,
                life_time= 0.06)

            
    def get_speed(self):
        #Returns the actor's velocity vector
        v = self.player.get_velocity()
        # Calutate the speed in m/s
        # kmt = m/s * 3.6
        ms = int(math.sqrt(v.x**2 + v.y**2 + v.z**2))
        return ms

    def braking_distance(self):
        # Get the speed of the car
        ms = self.get_speed()
        
        #constant value a 
        # a = acceleration
        a = 5.8

        #braking distance
        # S = v^2/(2*a)
        length = (ms**2 )/(2*a)
       
        return length

    def emergency_brake(self):
        # Get length and speed
        length = self.braking_distance()
        speed = self.get_speed()
       
        # It doesn't work very well in low and high speed
        # It needs to have a high enough concentration to act
        if speed > 2.77 and speed < 20:
            if length + 1> self.depth :
                self.koncentration += 1
            
                if self.koncentration == 50:
                    #activate emergency brake
                    self.emergency = True
                    print("BRAKE NOW")
                        
            else:
                self.koncentration = 0
                
            if self.emergency == True:
                #Stop car immediatelt
                self.player.apply_control(carla.VehicleControl(throttle=0, steer=0, brake=1))
   
            
    
class carla_world:

    def __init__(self):
        self.client = None
        self.world = None
        self.camera = None
        self.car = None
        self.display = None
        self.image = None
        self.surface = None
        self.radar_sensor = None
        self.emergency = False
  
    def setup_car(self):
        # Search after Tesla model 3 in the bluebrint libary
        blueprint = self.world.get_blueprint_library().filter('model3')[0]
        # Set the color to Red
        blueprint.set_attribute('color','140,0,0')

        # Set spawn point a random place on the map
        spawn_point = random.choice(self.world.get_map().get_spawn_points())

        #Spawn the actor car
        self.car = self.world.spawn_actor(blueprint, spawn_point)


    def setup_camera(self):
        #Find camera in the bluebrint libary
        camera_bp = self.world.get_blueprint_library().find('sensor.camera.rgb')
        # Image width in pixels
        camera_bp.set_attribute('image_size_x', str(display_width))
        # Image height in pixels
        camera_bp.set_attribute('image_size_y', str(display_height))

        # Set camera loction on the car
        # Change the angle (pitch)
        camera_transform = carla.Transform(carla.Location(x=-5.5, z=2.8), carla.Rotation(pitch=-15))
        #Spawn the actor camera
        self.camera = self.world.spawn_actor(camera_bp, camera_transform, attach_to=self.car)

        #Listen to the camera sensor and get image
        self.camera.listen(lambda image: self.get_image(image))

        
    def control(self, car,emergency):
        self.emergency = emergency

        #Get keyboard input
        keys = pygame.key.get_pressed()
        # Get control of the actor car
        control = car.get_control()
        
        # Default value 0  
        control.throttle = 0

         # Steering control
        if keys[K_a]:
            # Move left
            control.steer = max(-1., min(control.steer - 0.05, 0))
        elif keys[K_d]:
            # Move right
            control.steer = min(1., max(control.steer + 0.05, 0))
        else:
            control.steer = 0

        # Speed control
        if keys[K_w]:
            # Move forward
            control.throttle = 0.7
            control.reverse = False
        elif keys[K_s]:
            # Move backward
            control.throttle = 1
            control.reverse = True


        # Eixt simulation
        if keys[K_ESCAPE]:
            return True

        #Start radar (emergency brake)
        elif keys[K_r]:
            print("radar")
            self.radar_control()

        # Apply the input for the user to the car
        car.apply_control(control)
        

    def radar_control(self):
        # Start radar sensor
        if self.radar_sensor is None:
            self.radar_sensor = radar(self.car)

        # Stop sensor if radar sensor already started
        elif self.radar_sensor.sensor is not None:
            #Destroy sensor
            self.radar_sensor.sensor.destroy()
            self.radar_sensor = None
        
    
    def get_image(self, image):
        self.image = image

        # If image is none it is not possible to get a surfave
        if self.image is not None:
            #Creat a array 
            # Use np.dtyper("uint8") = unsigned integer (0 to 255)
            array = np.frombuffer(self.image.raw_data, dtype=np.dtype("uint8"))
            # Reshape the array so it fit the display
            array = np.reshape(array, (self.image.height, self.image.width, 4))
            #Change the array to three colums
            array = array[:, :, :3]
            array = array[:, :, ::-1]
            #print(array)
            #Copy array to a new surface
            self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))

    def render(self, display):
        
        if self.surface == None:
            return
        else:
            # Render the surface on the display
            display.blit(self.surface, (0, 0))
        
            # Update display
            pygame.display.flip()
        
    def game_loop(self):
        
        try:
            pygame.init()

            # Find server 
            self.client = carla.Client('localhost', 2000)
            self.client.set_timeout(5.0)
            self.world = self.client.get_world()

            # Spawn car and camera
            self.setup_car()
            self.setup_camera()

           
            # Create a display surface
            self.display = pygame.display.set_mode((display_width, display_height))
            pygame_clock = pygame.time.Clock()


            while True:
                # Check user input              
                if self.control(self.car, self.emergency):
                     return

                #Max fps 30
                pygame_clock.tick_busy_loop(30)

                # Render camera image
                self.render(self.display)
                
                # Internally interact with the rest of the operating system
                pygame.event.pump()

               
                
                

        finally:
            # Destroy sensors
            self.camera.destroy()
            self.car.destroy()
            if self.radar_sensor is not None:
                self.radar_sensor.sensor.destroy()


            #Stop simulation
            pygame.quit()



def main():
    
    try:
        client = carla_world()
        client.game_loop()
    finally:
        print("Exit CARLA simulation")



main()
