# import pygame
import time
import rewriteSound


class Audio:
    def __init__(self, robot):
        self.robot = robot

    def make_heartbeat_sound(self):
        while self.robot.main_running:
            if (self.robot.get_heartbeat_busy() and not self.robot.get_music_busy()):
                self.robot.set_music_busy(True)
                title = "/home/pi/Documents/TherapyPetRobot/sounds/heartbeat2"+".wav"
                pygame.mixer.music.load(title)
                pygame.mixer.music.play()
                time.sleep(random.randint(5, 10))
                self.robot.set_music_busy(False)
                self.robot.set_heartbeat_busy(False)

    def handle_barks(self, state):
        self.robot.get_writing_sound_state(state)
        rewriteSound.get_new_sound(state)
        self.robot.get_writing_sound_state(None)
        print("UPDATED SOUND: "+str(state))

    def bark():
        while self.robot.main_running:
        if (self.robot.get_bark_busy() and (self.robot.get_state() in range(0, 7)) and(self.robot.get_writing_sound_state() != self.robot.get_state()) and not self.robot.get_music_busy()):
            print("CURRENT STATE: "+str(self.robot.get_state()))
            print("STARTING: Bark")
            self.robot.set_bark_busy(True)
            current_state = self.robot.get_state()
            try:
                title = "/home/pi/Documents/TherapyPetRobot/sounds/new/sound_" + \
                    str(current_state)+".wav"
                a = pygame.mixer.Sound(title)
                pygame.mixer.Sound.play(a, fade_ms=3000)
                pygame.mixer.music.fadeout(3000)
                new_barks_thread = threading.Thread(
                    target=self.handle_barks, args=(current_state,))
                new_barks_thread.start()
                pygame.mixer.music.set_volume(1)
                if (a.get_length() > 3):
                    sleep_counter = random.randint(3, int(a.get_length()))
                else:
                    sleep_counter = 3
                print(sleep_counter)
                time.sleep(sleep_counter)
                self.robot.set_music_busy(False)
                self.robot.set_bark_busy(False)
                self.robot.set_tail_moves(False)
                print("STOPPING: Bark")
            except:
                for state in range(7):
                    rewriteSound.get_new_sound(state)
