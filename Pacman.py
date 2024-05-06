from superwires import games, color
import json
import random

games.init(screen_width=1000, screen_height=800, fps=100)

SPEED_X = 17
SPEED_Y = 14


class Pacman(games.Sprite):
    """Создаем пакмана"""
    image_1 = games.load_image('image/Pacman.png')
    image_2 = games.load_image('image/Pacman2.png')
    #звук гибели пакмана
    game_over = games.load_sound('music/game over.wav')
    step_x = SPEED_X
    step_y = SPEED_Y
    walk = True
    images_animation = ['image/Pacman_did_1.png',
                        'image/Pacman_did_2.png',
                        'image/Pacman_did_3.png',
                         'image/Pacman_did_4.png',
                         'image/Pacman_did_5.png',
                         'image/Pacman_did_6.png']



    def __init__(self, x, y, game):
        super().__init__(x=x, y=y, image=Pacman.image_1)
        games.screen.add(self)
        self.game = game
        self.slowdown = Game.acceleration

    def update(self):
        self.slowdown -=1
        if self.slowdown == 0:
            self.slowdown = Game.acceleration
            if games.keyboard.is_pressed(games.K_LEFT):
                self.x -= Pacman.step_x
                if self.frame():# если не входит в массив поля
                    self.x += Pacman.step_x
                self.angle = 0 #угол поворота
                self.gob() #меняет картинку "открыть рот"
            if games.keyboard.is_pressed(games.K_RIGHT):
                self.x += Pacman.step_x
                if self.frame():
                    self.x -= Pacman.step_x
                self.angle = 180
                self.gob()
            if games.keyboard.is_pressed(games.K_UP):
                self.y -= Pacman.step_y
                if self.frame():
                    self.y += Pacman.step_y
                self.angle = 90
                self.gob()
            if games.keyboard.is_pressed(games.K_DOWN):
                self.y += Pacman.step_y
                if self.frame():
                    self.y -= Pacman.step_y
                self.angle = 270
                self.gob()
            #включить перемещение пакмана везде
            if games.keyboard.is_pressed(games.K_5):
                if Pacman.walk:
                    Pacman.walk = False
                else:
                    Pacman.walk = True

            # проход через стену
            if self.y == 376:
                if self.x == 16: self.x = 662
                if self.x == 696: self.x = 50

            #записывает все шаги из массива в файл (для отладки)
            if games.keyboard.is_pressed(games.K_SPACE):
                with open('file4.txt', 'w') as fw:
                    json.dump(Game.place_write, fw)

            # если столкнется с призраком
            for sprite in self.overlapping_sprites:
                #если призрак синий
                if sprite.ghost_run:
                    for ghost in self.overlapping_sprites:
                        Ghost200(x_=ghost.x, y_=ghost.y-50)
                        ghost.die()
                        Game.score.value += 200

                #если призрак нормального цвета
                else:
                    Pacman.game_over.play()
                    #уничтожаем всех приведений и пакмана
                    Pacman.advance(self)
                    # анимация гибели пакмана
                    animation = games.Animation(images=Pacman.images_animation, x=self.x, y=self.y,
                                                repeat_interval=30, n_repeats=1, is_collideable=False)
                    games.screen.add(animation)
                    Timer(secund=3, game=self.game, func=2)
                    # - жизнь
                    Life(-1, self)

            #если все съел, то переход на следующий уровень
            if Eat.sum == 0:
                Pacman.advance(self)
                self.game.advance()

            #выводим координаты пакмана для отладки
            Game.text.value = str(self.x) + ' : ' + str(self.y)

    def advance(self):
        Ghost.ghost_run = False
        self.destroy()
        Game.red.destroy()
        Game.pink.destroy()
        Game.blue.destroy()
        Game.orange.destroy()


    def frame(self):
        """проверяет координаты по которым можно передвигаться"""
        if Pacman.walk:
            xy = [self.x, self.y]
            if xy not in Game.place:
               return True

    open_gob = False

    def gob(self):
        """ меняет картинку с каждым шагом "открыть рот"""
        if Pacman.open_gob:
            self.image = Pacman.image_1
            Pacman.open_gob = False
        else:
            self.image = Pacman.image_2
            Pacman.open_gob = True
        #записываем передвижения пакмана в массив (для отладки)
        Game.place_write.append([self.x, self.y])

class Eat(games.Sprite):
    """создает на поле еду"""
    # милисекунды мерцания больших кусков
    ms=games.screen.fps
    # милисекунды мерцания смена картинки
    ms_change = ms/2
    # переменная для хранения количества еды
    sum = 0
    def __init__(self, x_, y_, images, aggressor):
        super().__init__(x=x_, y=y_, image=images)
        Eat.sum +=1
        games.screen.add(self)
        self.aggressor = aggressor
        #определяем что спрайт не может сталкиваться с другими объектами
        self.is_collideable = False
        #если большой кусок, то задаем время для мигания
        if aggressor: self.ms = Eat.ms

    def update(self):

        #оставить один кусок (для отладки)
        #if Eat.sum >1:
        #    self.destroy()
        #    Eat.sum -=1
        #уничтожает спрайт "еда" если совпал с координатами пакмана
        if Game.pacman.x == self.x and Game.pacman.y == self.y:
            Game.eat.play()
            self.destroy()
            # начисляем очки
            Game.score.value += 10
            # если съест большой кусок, то добавим еще очков
            if self.aggressor:
                Game.score.value += 40
                #и перекрасим в другой цвет приведений
                Ghost.ghost_run = True
                #запустим таймер на 10 секунд
                Timer(secund=10, game=self, func=3)
                #поменяем музыку
                games.music.stop()
                Game.agressor.play(loops=2)
            Game.score.left = 800
            Eat.sum -=1
        # мерцание больших кусков
        if self.aggressor:
            self.ms -=1
            if self.ms == Eat.ms_change: self.image = games.load_image('image/big_eat2.png')
            if self.ms == 0:
                self.ms = Eat.ms
                self.image = games.load_image('image/big_eat.png')

        #обновление лучшего счета
        if int(Game.score.value) > int(Game.score_.value):
            Game.score_.value = Game.score.value


class Ghost(games.Sprite):
    """создает приведение"""
    image_1 = {1: games.load_image('image/ghost_red.png'),
              2: games.load_image('image/ghost_pink.png'),
              3: games.load_image('image/ghost_blue.png'),
              4: games.load_image('image/ghost_orange.png')}

    image_2 = {1: games.load_image('image/ghost_red2.png'),
              2: games.load_image('image/ghost_pink2.png'),
              3: games.load_image('image/ghost_blue2.png'),
              4: games.load_image('image/ghost_orange2.png')}

    image_blue_1 = games.load_image('image/ghost_run.png')
    image_blue_2 = games.load_image('image/ghost_run2.png')

    # время задержки выхода призраков
    ms = games.screen.fps*2 #2 секунды
    ms_iterat = ms

    #убегающие приведения
    ghost_run = False


    def __init__(self, x_, y_, colors, game):
        self.colors = colors
        super(Ghost, self).__init__(x=x_, y=y_, image=Ghost.image_1[colors])
        games.screen.add(self)
        self.game = game
        #погоня
        self.chase = False
        #приведение не убегает
        self.ghost_run = Ghost.ghost_run
        # картинка убегающие глаза
        self.die_image = False
        #если воскресился то цвет не менять
        self.resurrection = False
        #  True: движение по x, если False: по y
        self.direction = True

        # направление по x, y
        self.swap_x = random.choice([SPEED_X, -SPEED_X])
        self.swap_y = random.choice([SPEED_Y, -SPEED_Y])

        self.x_buf = 0
        self.y_buf = 0

        self.ms = Ghost.ms
        Ghost.ms += Ghost.ms_iterat

        # замедление, с какого раза сработает update
        self.slowdown = Game.acceleration + 3
        # если приведение синее, замедляем его еще на 5 пунктов
        self.slowdown_ghost_runs = Game.acceleration + 6


    def update(self):
        self.slowdown -= 1
        if self.slowdown == 0:
            # если приведение синее, замедляем приведение
            if self.ghost_run: self.slowdown = self.slowdown_ghost_runs
            else: self.slowdown = Game.acceleration + 3
            # тут необходимые действия
            if abs(self.x - Game.pacman.x) < 20 or abs(self.y - Game.pacman.y) < 20:
                self.go_to_pacman()
            else:
                self.go()

            # если пакман съел приведение, то возвращаться в домик
            if self.die_image:
                self.to_the_house()

        # проход через стену
        if self.y == 376:
            if self.x == 16: self.x = 662
            if self.x == 696: self.x = 50

        # выход из домика
        self.log_off()
        #если съел ли большой кусок, то приведения становятся синими
        self.ghost_runs()


    def go_to_pacman(self):
        """следование за пакманом"""
        # раскрасить приведение
        self.picture()

        # делаем положительный вектор движения
        self.swap_x = SPEED_X
        self.swap_y = SPEED_Y

        # по x
        # смотрим где пакман и идем к нему
        if self.x > Game.pacman.x:self.swap_x = -self.swap_x
        elif self.x < Game.pacman.x: self.swap_x = self.swap_x
        #приведение убегает от пакмана
        if self.ghost_run:
            self.x -= self.swap_x
            if self.frame(): self.x += self.swap_x
        # приведение бежит к пакману
        else:
            self.x += self.swap_x
            # если тупик
            if self.frame(): self.x -= self.swap_x

        # по y
        if self.y > Game.pacman.y: self.swap_y = -self.swap_y
        elif self.y < Game.pacman.y: self.swap_y = self.swap_y
        if self.ghost_run:
            self.y -= self.swap_y
            if self.frame(): self.y += self.swap_y
        else:
            self.y += self.swap_y
            # если тупик
            if self.frame():  self.y -= self.swap_y


    def go(self):
        """хождение приведений (до первого столкновения с препятствием, рандомно)"""
        # по x
        if self.direction:
            # раскрасить приведение
            self.picture()
            self.x += self.swap_x
            if self.frame():
                self.x -= self.swap_x
                self.swap_y = random.choice([SPEED_Y, -SPEED_Y])
                self.direction = False
        # по y
        if not self.direction:
            self.picture()
            self.y += self.swap_y
            if self.frame():
                self.y -= self.swap_y
                self.swap_x = random.choice([SPEED_X, -SPEED_X])
                self.direction = True


    def to_the_house(self):
        """вернуться в дом"""
        Game.eat.play()
        #координаты в домике
        self.swap_x = SPEED_X
        self.swap_y = SPEED_Y
        (h_x, h_y) = (356, 348)
        if self.x > h_x: self.swap_x = -self.swap_x
        elif self.x < h_x: self.swap_x = self.swap_x
        self.x += self.swap_x
        if self.y > h_y: self.swap_y = -self.swap_y
        elif self.y < h_y: self.swap_y = self.swap_y
        self.y +=self.swap_y
        if self.frame():
            (self.x, self.y) = (356, 334)


        # если в домике
        a = [self.x, self.y]
        if a in Game.place4:
            Game.text2.value = str(self.x) + 'x ' + str(self.y)
            # терерь приведение не убегающее
            self.ghost_run = False
            # теперь картинка не глаза
            self.die_image = False
            # значение что воскресился, теперь приведение не должно быть синее
            self.resurrection = True


    def ghost_runs(self):
        """если пакманом съден большой кусок, то меняем кождое приведение на синее"""
        if Ghost.ghost_run and self.resurrection == False:
            self.ghost_run = True
        elif not Ghost.ghost_run:
            self.ghost_run = False
            self.resurrection = False

    def die(self):
        """если пакман съел приведение"""
        Timer(secund=1, game=self.game, func=4)
        Game.eat_ghost.play()
        #отключаем условие смены картинок
        self.die_image = True
        # меняем картинку на глаза
        self.image = games.load_image('image/eyes.png')



    def frame(self):
        """проверяет координаты по которым нельзя передвигаться"""
        xy = [self.x, self.y]
        if xy not in Game.place and xy not in Game.place4:
           return True

    def log_off(self):
        """выход из домика"""
        self.ms -= 1
        if self.colors != 1 and self.ms == 0:
            (self.x, self.y) = (356.0, 334.0)

    change_picture = False

    def picture(self):
        """ меняет картинку с каждым шагом """
        #если не умер
        if not self.die_image:
            if Ghost.change_picture:
                if self.ghost_run: self.image = Ghost.image_blue_1
                else: self.image = Ghost.image_1[self.colors]
                Ghost.change_picture = False
            else:
                if self.ghost_run: self.image = Ghost.image_blue_2
                else: self.image = Ghost.image_2[self.colors]
                Ghost.change_picture = True

class Ghost200(games.Sprite):
    """отображение 200 очков после съедания приведений"""
    images = games.load_image('image/200.png')
    def __init__(self, x_, y_,):
        super(Ghost200, self).__init__(x=x_, y=y_, image= Ghost200.images, is_collideable=False)
        games.screen.add(self)
        self.ms = games.screen.fps
    def update(self):
        self.ms -= 1
        if self.ms == 0:
            self.destroy()

class Timer (games.Sprite):
    def __init__(self, secund, game, func):
        super(Timer, self).__init__(x=0, y=0, image=games.load_image('image/dot.png'))
        games.screen.add(self)
        self.secund = secund*games.screen.fps
        self.game = game
        self.func = func

    def update(self):
        self.secund -= 1
        if self.secund == 0:
            if self.func == 1:
                self.game.next_lavel()
                self.destroy()
            elif self.func == 2:
                # создаем пакмана и приведения
                self.game.renewal()
                self.destroy()
            elif self.func == 3:
                #поменяем цвет призраков обратно
                Ghost.ghost_run = False
                Game.eat_ghost.stop()
                games.music.play(-1)
                self.destroy()


class Timepiece (games.Sprite):
    """хронометр"""
    time = games.Text(value=0, size=50, color=color.white, top=500, left=900, is_collideable=False)
    #games.screen.add(time)
    secunds = games.screen.fps
    def __init__(self):
        super(Timepiece, self).__init__(x=0, y=0, image=games.load_image('image/dot.png'))
        games.screen.add(self)
    def update(self):
        Timepiece.secunds -=1
        if Timepiece.secunds == 0:
            Timepiece.secunds = games.screen.fps
            Timepiece.time.value +=1


class Life(games.Sprite):
    """добавление (1), убавление(-1) жизней пакману"""
    images = games.load_image('image/Pacman2.png')
    width_life = 764
    lifes = {}
    i = 1
    def __init__(self, amount, game):
        self.game = game
        if amount > 0:
            super().__init__(x=Life.width_life, y=642, image=Life.images, is_collideable=False)
            Life.width_life += 51
            games.screen.add(self)
            Life.lifes[Life.i] = self
            Life.i +=1
        elif amount == -1:
            if Life.i > 1:
                Life.width_life -= 51
                Life.lifes[Life.i-1].destroy()
                Life.i -= 1
            else:
                Game.end(self.game)


class Game(object):
    # надпись лучший счет
    hiscore = games.Text(value='HI-SCORE', size=50, color=color.red, top=30, right=games.screen.width - 50, is_collideable=False)
    games.screen.add(hiscore)
    # сам лучший счет
    score_ = games.Text(value=10000, size=50, color=color.white, top=80, left=800, is_collideable=False)
    games.screen.add(score_)
    # текст с координатами пакмана для отладки
    text = games.Text(value=0, size=50, color=color.red, top=400, left=800, is_collideable=False)
    #games.screen.add(text)
    #текст для отдадки(под пакманом)
    text2 = games.Text(value=0, size=50, color=color.red, top=450, left=800, is_collideable=False)
    #games.screen.add(text2)
    #  счет
    score = games.Text(value=0, size=50, color=color.white, top=180, left=800, is_collideable=False)
    games.screen.add(score)
    # надпись уровень
    lavel_text = games.Text(value='1 UP', size=50, color=color.red, top=130, left=800, is_collideable=False)
    games.screen.add(lavel_text)
    # загрузка анимации перехода на новый уровень
    image_animation = ['image/place.png',
                        'image/place_wite.png']
    # загрузка звуков
    agressor = games.load_sound('music/agressor.wav')
    eat = games.load_sound('music/eat.wav')
    eat_ghost = games.load_sound('music/eat_ghost.wav')
    glass = games.load_sound('music/glass.wav')
    Start = games.load_sound('music/Start.wav')
    games.music.load('music/game.wav')

    # переменная для хранения массива передвижения пакмана для отладки
    place_write = [[]]

    # загружаем в place координаты по которым ходит пакман
    with open('file.txt', 'r') as fr:
        place = json.load(fr)
    # загружаем в place2 координаты исключающие расположение "еды"
    with open('file2.txt', 'r') as fr:
        place2 = json.load(fr)
    # загружаем в place3 координаты "больших кусков"
    with open('file3.txt', 'r') as fr:
        place3 = json.load(fr)
    # загружаем в place4 дополнительные координаты для приведений
    with open('file4.txt', 'r') as fr:
        place4 = json.load(fr)
    # загружаем лучший счет
    with open('score.txt', 'r') as fr:
        score_.value = json.load(fr)

    # значение ускорения игры, с каждым уровнем уменьшается (скорость игры увеличивается)
    acceleration = 10

    pacman = None
    red = None
    pink = None
    blue = None
    orange = None
    #уровень
    lavel = 0
    # список жизней пакмана
    life = []

    def __init__(self):
        # фон
        image = games.load_image('image/place.png')
        frame = games.Sprite(image=image, top=2, left=6, is_collideable=False)
        games.screen.add(frame)
        #создаем жизни в начале игры
        Life(2, self)

    def play(self):
        # начинаем иру
        Game.Start.play()
        self.advance()
        games.screen.mainloop()

    def advance(self):
        """сообщение о переходе на новый уровень"""
        # новый уровень
        Game.lavel += 1
        games.music.stop()
        Game.agressor.stop()
        if Game.lavel > 1:
            animation = games.Animation(images=Game.image_animation, top=2, left=6, repeat_interval=30,
                                        n_repeats=5, is_collideable=False)
            games.screen.add(animation)
            next_lavel_message = games.Message(value='Уровень '+str(self.lavel), size=100, color=color.red, x=350,
                                               y=games.screen.height / 2, lifetime=3 * games.screen.fps, is_collideable=False)
            games.screen.add(next_lavel_message)
        else:
            start_message = games.Message(value='READY', size=100, color=color.green, x=355,
                                          y=370, lifetime=4.2 * games.screen.fps,
                                          is_collideable=False)
            games.screen.add(start_message)
            Life(1, self)

        Timer(secund=4.2, game=self, func=1)

    def renewal(self):
        # загружаем пакмана
        Game.pacman = Pacman(x=356, y=572, game=self)             #(x=356, y=348, game=self y=572,)

        #создаем приведений
        Game.red = Ghost(x_=356.0, y_=334.0, colors=1, game=self)
        Game.pink = Ghost(x_=355.0, y_=376.0, colors=2, game=self)
        Game.blue = Ghost(x_=322.0, y_=376.0, colors=3, game=self)
        Game.orange = Ghost(x_=390.0, y_=376.0, colors=4, game=self)

        # время задержки выхода призраков
        Ghost.ms = games.screen.fps * 2  # 2 секунды


    def next_lavel(self):
        """переход на новый уровень"""
        # увеличиваем скорость игры каждый второй раунд
        if Game.lavel % 2 == 0:
            if Game.acceleration > 3: Game.acceleration -= 1
        # каждые 5 уровней прибавляем 1 жизнь
        if Game.lavel % 5 == 0:
            Life(1, self)
        # секундомер для отладки
        #Timepiece()
        # -жизнь
        #Game.pakman_life(self, -1)
        games.music.play(-1)
        # надпись уровеня
        Game.lavel_text.value = str(self.lavel)+' UP'
        #создаем еду и большие куски
        for y in range(40, 750, 28):
            for x in range(50, 700, 34):
                a = [x, y]
                if a in Game.place and a not in Game.place2:
                    Eat(x_=x, y_=y, images=games.load_image('image/eat.png'), aggressor=False)
                if a in Game.place3:
                    Eat(x_=x, y_=y, images=games.load_image('image/big_eat.png'), aggressor=True)

        self.renewal()

    def end(self):
        """закончить игру"""
        # записываем счет
        if int(Game.score.value) >= int(Game.score_.value):
            with open('score.txt', 'w') as fw:
                json.dump(Game.score.value, fw)
        # 3 секундное отображение game over
        end_message = games.Message(value='GAME OVER', size=100, color=color.red, x=350,
                                    y=games.screen.height / 2, lifetime=3 * games.screen.fps,
                                    after_death=games.screen.quit, is_collideable=False)
        games.screen.add(end_message)


def main():
    game = Game()
    game.play()

if __name__ == '__main__':
    main()
