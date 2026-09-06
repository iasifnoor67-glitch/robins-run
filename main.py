"""
Robin's Run
A Robin Hood themed endless runner game
Developed by: Muhammad Asif Noor
Special Thanks: Muhammad Yousaf
AY Studios
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
import random
import os

# ---------------------------------------------------------
# SOUND MANAGER — loads all game sounds once, safe if missing
# ---------------------------------------------------------
class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.base_path = os.path.join(os.path.dirname(__file__), 'assets', 'sounds')
        self.files = {
            'siren': 'siren.mp3',
            'music': 'music.mp3',
            'coin': 'coin.mp3',
            'jump': 'jump.mp3',
            'gameover': 'gameover.mp3',
        }
        for key, filename in self.files.items():
            path = os.path.join(self.base_path, filename)
            if os.path.exists(path):
                self.sounds[key] = SoundLoader.load(path)
            else:
                self.sounds[key] = None

    def play(self, key, loop=False, volume=1.0):
        sound = self.sounds.get(key)
        if sound:
            sound.loop = loop
            sound.volume = volume
            sound.play()

    def stop(self, key):
        sound = self.sounds.get(key)
        if sound:
            sound.stop()


sound_manager = SoundManager()


# ---------------------------------------------------------
# STUDIO / SPLASH SCREEN (AY Studios logo + credits)
# ---------------------------------------------------------
class SplashScreen(Screen):
    def on_enter(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        with layout.canvas.before:
            Color(0.05, 0.07, 0.12, 1)
            self.bg = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self.update_bg, size=self.update_bg)

        studio_label = Label(
            text="[color=3b82f6]A[/color][color=f5c518]Y[/color] [color=ffffff]Studios[/color]",
            markup=True,
            font_size='48sp',
            size_hint=(1, 0.5)
        )

        presents_label = Label(
            text="presents",
            font_size='16sp',
            color=(0.7, 0.7, 0.7, 1),
            size_hint=(1, 0.15)
        )

        credits_label = Label(
            text="Developed by: Muhammad Asif Noor\nSpecial Thanks: Muhammad Yousaf",
            font_size='14sp',
            color=(0.6, 0.6, 0.6, 1),
            size_hint=(1, 0.25),
            halign='center'
        )
        credits_label.bind(size=credits_label.setter('text_size'))

        layout.add_widget(Widget(size_hint=(1, 0.1)))
        layout.add_widget(studio_label)
        layout.add_widget(presents_label)
        layout.add_widget(credits_label)

        self.add_widget(layout)
        Clock.schedule_once(self.go_to_menu, 3)

    def update_bg(self, *args):
        self.bg.pos = self.children[0].pos
        self.bg.size = self.children[0].size

    def go_to_menu(self, dt):
        self.manager.current = 'menu'


# ---------------------------------------------------------
# MAIN MENU SCREEN
# ---------------------------------------------------------
class MenuScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)

        with layout.canvas.before:
            Color(0.08, 0.09, 0.15, 1)
            self.bg = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self.update_bg, size=self.update_bg)

        title = Label(
            text="Robin's Run",
            font_size='40sp',
            color=(0.96, 0.77, 0.09, 1),
            size_hint=(1, 0.3)
        )

        subtitle = Label(
            text="Steal from the rich. Run from the law.\nGive to the poor.",
            font_size='16sp',
            color=(0.8, 0.8, 0.8, 1),
            size_hint=(1, 0.2),
            halign='center'
        )
        subtitle.bind(size=subtitle.setter('text_size'))

        play_btn = Button(
            text="Play",
            font_size='24sp',
            size_hint=(1, 0.15),
            background_color=(0.23, 0.51, 0.96, 1)
        )
        play_btn.bind(on_release=self.start_game)

        credits_btn = Button(
            text="Credits",
            font_size='18sp',
            size_hint=(1, 0.12),
            background_color=(0.3, 0.3, 0.3, 1)
        )
        credits_btn.bind(on_release=self.show_credits)

        self.credits_label = Label(
            text="",
            font_size='13sp',
            color=(0.6, 0.6, 0.6, 1),
            size_hint=(1, 0.15)
        )

        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(play_btn)
        layout.add_widget(credits_btn)
        layout.add_widget(self.credits_label)

        self.add_widget(layout)

    def update_bg(self, *args):
        self.bg.pos = self.children[0].pos
        self.bg.size = self.children[0].size

    def show_credits(self, instance):
        self.credits_label.text = ("AY Studios\n"
                                     "Developed by: Muhammad Asif Noor\n"
                                     "Special Thanks: Muhammad Yousaf")

    def start_game(self, instance):
        self.manager.current = 'game'


# ---------------------------------------------------------
# GAME SCREEN — Endless Runner Logic
# ---------------------------------------------------------
class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player_y = 100
        self.player_x = 80
        self.player_width = 40
        self.player_height = 60
        self.velocity_y = 0
        self.gravity = -1200
        self.jump_strength = 550
        self.is_jumping = False
        self.ground_y = 100

        self.obstacles = []  # police cars (rects)
        self.coins = []      # money bags
        self.speed = 300
        self.score = 0
        self.distance_since_obstacle = 0
        self.distance_since_coin = 0
        self.game_over = False
        self.siren_cooldown = 0

        # start background music looping
        sound_manager.play('music', loop=True, volume=0.4)

        self.score_label = Label(
            text="Score: 0",
            font_size='20sp',
            pos=(10, Window.height - 40),
            size_hint=(None, None)
        )
        self.add_widget(self.score_label)

        self.status_label = Label(
            text="",
            font_size='28sp',
            color=(1, 0.3, 0.3, 1),
            pos=(Window.width / 2 - 100, Window.height / 2),
            size_hint=(None, None),
            size=(200, 50)
        )
        self.add_widget(self.status_label)

        Clock.schedule_interval(self.update, 1 / 60)
        Window.bind(on_touch_down=self.on_touch_down_window)

    def on_touch_down_window(self, window, touch):
        if not self.game_over:
            self.jump()
        else:
            self.restart()
        return True

    def jump(self):
        if not self.is_jumping:
            self.velocity_y = self.jump_strength
            self.is_jumping = True
            sound_manager.play('jump', volume=0.6)

    def restart(self):
        self.player_y = self.ground_y
        self.velocity_y = 0
        self.is_jumping = False
        self.obstacles = []
        self.coins = []
        self.score = 0
        self.speed = 300
        self.game_over = False
        self.status_label.text = ""
        sound_manager.play('music', loop=True, volume=0.4)

    def update(self, dt):
        if self.game_over:
            return

        # player physics
        self.velocity_y += self.gravity * dt
        self.player_y += self.velocity_y * dt
        if self.player_y <= self.ground_y:
            self.player_y = self.ground_y
            self.velocity_y = 0
            self.is_jumping = False

        # spawn obstacles (police cars)
        self.distance_since_obstacle += self.speed * dt
        if self.distance_since_obstacle > random.randint(220, 400):
            self.obstacles.append({
                'x': Window.width + 50,
                'y': self.ground_y,
                'w': 60,
                'h': 40
            })
            self.distance_since_obstacle = 0
            # play siren when a new police car appears, with cooldown
            if self.siren_cooldown <= 0:
                sound_manager.play('siren', volume=0.5)
                self.siren_cooldown = 2.5
        if self.siren_cooldown > 0:
            self.siren_cooldown -= dt

        # spawn coins (money bags)
        self.distance_since_coin += self.speed * dt
        if self.distance_since_coin > random.randint(150, 280):
            self.coins.append({
                'x': Window.width + 50,
                'y': self.ground_y + random.randint(60, 160),
                'r': 18
            })
            self.distance_since_coin = 0

        # move obstacles + collision
        for obs in self.obstacles[:]:
            obs['x'] -= self.speed * dt
            if obs['x'] < -100:
                self.obstacles.remove(obs)
                continue
            if self.check_collision(obs):
                self.end_game()

        # move coins + collection
        for coin in self.coins[:]:
            coin['x'] -= self.speed * dt
            if coin['x'] < -50:
                self.coins.remove(coin)
                continue
            if self.check_coin_collision(coin):
                self.coins.remove(coin)
                self.score += 10
                self.score_label.text = f"Score: {self.score}"
                sound_manager.play('coin', volume=0.7)

        # difficulty scaling
        self.speed += 5 * dt

        self.draw()

    def check_collision(self, obs):
        px1, py1 = self.player_x, self.player_y
        px2, py2 = px1 + self.player_width, py1 + self.player_height
        ox1, oy1 = obs['x'], obs['y']
        ox2, oy2 = ox1 + obs['w'], oy1 + obs['h']
        return px1 < ox2 and px2 > ox1 and py1 < oy2 and py2 > oy1

    def check_coin_collision(self, coin):
        px1, py1 = self.player_x, self.player_y
        px2, py2 = px1 + self.player_width, py1 + self.player_height
        cx, cy, r = coin['x'], coin['y'], coin['r']
        closest_x = max(px1, min(cx, px2))
        closest_y = max(py1, min(cy, py2))
        dist = ((cx - closest_x) ** 2 + (cy - closest_y) ** 2) ** 0.5
        return dist < r

    def end_game(self):
        self.game_over = True
        self.status_label.text = f"Caught!\nScore: {self.score}\nTap to restart"
        sound_manager.stop('music')
        sound_manager.play('gameover', volume=0.8)

    def draw(self):
        self.canvas.clear()
        with self.canvas:
            # sky
            Color(0.1, 0.12, 0.2, 1)
            Rectangle(pos=(0, 0), size=(Window.width, Window.height))

            # ground
            Color(0.2, 0.15, 0.1, 1)
            Rectangle(pos=(0, 0), size=(Window.width, self.ground_y))

            # player (robber silhouette - simple rect + head)
            Color(0.1, 0.1, 0.15, 1)
            Rectangle(pos=(self.player_x, self.player_y), size=(self.player_width, self.player_height))
            Color(0.9, 0.75, 0.6, 1)
            Ellipse(pos=(self.player_x + 8, self.player_y + self.player_height), size=(24, 24))

            # obstacles (police cars)
            for obs in self.obstacles:
                Color(0.8, 0.1, 0.1, 1)
                Rectangle(pos=(obs['x'], obs['y']), size=(obs['w'], obs['h']))
                Color(0.1, 0.1, 0.8, 1)
                Rectangle(pos=(obs['x'] + 10, obs['y'] + obs['h']), size=(15, 8))

            # coins (money bags)
            for coin in self.coins:
                Color(0.96, 0.77, 0.09, 1)
                Ellipse(pos=(coin['x'] - coin['r'], coin['y'] - coin['r']),
                         size=(coin['r'] * 2, coin['r'] * 2))

        # keep labels on top and positioned correctly
        self.score_label.pos = (10, Window.height - 40)
        self.status_label.pos = (Window.width / 2 - 100, Window.height / 2)
        self.canvas.add(self.score_label.canvas)
        self.canvas.add(self.status_label.canvas)


class GameScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        self.game_widget = GameWidget()
        self.add_widget(self.game_widget)


# ---------------------------------------------------------
# APP ENTRY POINT
# ---------------------------------------------------------
class RobinsRunApp(App):
    def build(self):
        Window.clearcolor = (0.05, 0.05, 0.08, 1)
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        sm.current = 'splash'
        return sm


if __name__ == '__main__':
    RobinsRunApp().run()
