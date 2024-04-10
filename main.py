import arcade
import arcade.color
import random


SCREEN_TITLE = "RPG Battle Simulator"

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650

CHARACTER_SCALING = 2
TILE_SCALING = 0.5
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

PLAYER_MOVEMENT_SPEED = 10
GRAVITY = 1
PLAYER_JUMP_SPEED = 20


class MyGame(arcade.View):
    def __init__(self):
        super().__init__()

        self.tile_map = None

        self.scene = None

        self.player_sprite = None

        self.physics_engine = None

        self.camera_sprites = None

        self.camera_gui = None

        self.score = 0

        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT

        self.left_key_down = False
        self.right_key_down = False

    def setup(self):
        self.camera_sprites = arcade.Camera(self.width, self.height)
        self.camera_gui = arcade.Camera(self.width, self.height)

        map_name = ":resources:tiled_maps/map.json"

        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
        }

        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        self.score = 0

        arcade.set_background_color(arcade.color.SKY_BLUE)

        src = "images/left.png"
        self.player_sprite = arcade.Sprite(src, CHARACTER_SCALING)
        self.player_sprite.center_x = 128
        self.player_sprite.center_y = 128
        self.scene.add_sprite("Player", self.player_sprite)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["Platforms"]
        )

    def on_draw(self):
        self.clear()

        self.camera_sprites.use()

        self.scene.draw()

        self.camera_gui.use()

        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text,
                         start_x=10,
                         start_y=10,
                         color=arcade.csscolor.WHITE,
                         font_size=18)


    def update_player_speed(self):
        self.player_sprite.change_x = 0

        if self.left_key_down and not self.right_key_down:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.right_key_down and not self.left_key_down:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED


    def on_key_press(self, key, modifiers): 
        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED

        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_key_down = True
            self.update_player_speed()

        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_key_down = True
            self.update_player_speed()

        elif key == arcade.key.ESCAPE:
            pause = PauseView(self)
            self.window.show_view(pause)


    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_key_down = False
            self.update_player_speed()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_key_down = False
            self.update_player_speed()


    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera_sprites.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera_sprites.viewport_height / 2)

        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0

        player_centered = screen_center_x, screen_center_y
        self.camera_sprites.move_to(player_centered)


    def on_update(self, delta_time):
        self.physics_engine.update()

        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Coins"]
        )

        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            self.score += 1
        
        enemies_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Enemies"]
        )

        for enemy in enemies_hit_list:
            view = BattleView(self)
            self.window.show_view(view)
            enemy.remove_from_sprite_lists()

        self.center_camera_to_player()


    def on_resize(self, width, height):
        self.camera_sprites.resize(int(width), int(height))
        self.camera_gui.resize(int(width), int(height))


class BattleView(arcade.View):
    def __init__(self, my_game):
        super().__init__()
        self.my_game = my_game
    PLAYER_HEALTH = 30
    PLAYER_ATK = 10

    ENEMY_HEALTH = 30
    ENEMY_ATK = 5
    isPlayerTurn = True
    isEnemyGuarding = False

    def on_show(self):
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_GRAY)
        arcade.set_viewport(0, SCREEN_WIDTH -1, 0, SCREEN_HEIGHT -1)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("BATTLE!!!", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 150, arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Press A to advance.", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 120, arcade.color.WHITE, font_size=20, anchor_x="center")

        arcade.draw_text("Player", SCREEN_WIDTH / 2 -450, SCREEN_HEIGHT / 2, arcade.color.WHITE, font_size=50, anchor_x="left")
        arcade.draw_text(f"HP: {BattleView.PLAYER_HEALTH}", SCREEN_WIDTH / 2 - 450, SCREEN_HEIGHT / 2 - 100, arcade.color.WHITE, font_size=50, anchor_x="left")

        arcade.draw_text("Enemy", SCREEN_WIDTH / 2 + 450, SCREEN_HEIGHT / 2, arcade.color.WHITE, font_size=50, anchor_x="right")
        arcade.draw_text(f"HP: {BattleView.ENEMY_HEALTH}", SCREEN_WIDTH / 2 + 450, SCREEN_HEIGHT / 2 - 100, arcade.color.WHITE, font_size=50, anchor_x="right")

    def on_key_press(self, key, _modifiers):
        if BattleView.ENEMY_HEALTH == 0:
            arcade.set_background_color(arcade.color.SKY_BLUE)
            self.window.show_view(self.my_game)

        if key == arcade.key.A and BattleView.isPlayerTurn == True and BattleView.ENEMY_HEALTH > 0:
            if BattleView.isEnemyGuarding == False:
                BattleView.ENEMY_HEALTH -= BattleView.PLAYER_ATK
                BattleView.isPlayerTurn = False
            elif BattleView.isEnemyGuarding == True:
                BattleView.isEnemyGuarding = False
                BattleView.isPlayerTurn = False
            BattleView.on_draw(self)
        
        elif key == arcade.key.A and BattleView.isPlayerTurn == False:
            enemy_choice = random.randint(0,2)
            if enemy_choice == 1:
                BattleView.PLAYER_HEALTH -= BattleView.ENEMY_ATK
                BattleView.isPlayerTurn = True
                BattleView.on_draw(self)
            elif enemy_choice == 2:
                BattleView.isEnemyGuarding = True

            


class PauseView(arcade.View):
    def __init__(self, my_game):
        super().__init__()
        self.my_game = my_game

    def on_show_view(self):
        arcade.set_background_color(arcade.color.ORANGE)

    def on_draw(self):
        self.clear()
        player_sprite = self.my_game.player_sprite
        player_sprite.draw()
        
        arcade.draw_text("PAUSED", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50,
                         arcade.color.BLACK, font_size=50, anchor_x="center")
        
        arcade.draw_text("Press Esc. to return",
                         SCREEN_WIDTH / 2,
                         SCREEN_HEIGHT / 2,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")
        
    def on_key_press(self, key, _modifiers):
        if key == arcade.key.ESCAPE:
            arcade.set_background_color(arcade.color.SKY_BLUE)
            self.window.show_view(self.my_game)





def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = MyGame()
    window.show_view(start_view)
    start_view.setup()
    arcade.run()

if __name__ == "__main__":
    main()