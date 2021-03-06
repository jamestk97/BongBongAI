import arcade
import game_core
import threading
import time
import game_map as ai
import numpy
from numpy import interp
from matplotlib import pyplot as plt
import collections
import sys
import copy

class Agent(threading.Thread):

    map = None
    counter = 0
    oldScore = -1
    old_stage = -1
    my_kill_grid = []
    old_kill_grid = None
    false_list = None
    fruit_count = 0

    def __init__(self, threadID, name, counter, show_grid_info=False):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.show_grid_info = show_grid_info

        self.game = []
        self.move_grid = []
        self.kill_grid = []
        self.isGameClear = False
        self.isGameOver = False
        self.current_stage = 0
        self.time_limit = 0
        self.total_score = 0
        self.total_time = 0
        self.total_life = 0
        self.tanuki_r = 0
        self.tanuki_c = 0
        #Define our own tracker of the last move the tanuki made
        self.tanuki_last = 0
        self.enemy_list = []



        self.level_initialized = [False for _ in range(9)]




    #############################################################
    #      YOUR SUPER COOL ARTIFICIAL INTELLIGENCE HERE!!!      #
    #############################################################
    def ai_function(self):
        print()
        print(self.counter)
        self.counter += 1


        if self.false_list is None:
            self.false_list = [[False for _ in range(len(self.kill_grid[0]))] for _ in range(len(self.kill_grid))]
        # To send a key stroke to the game, use self.game.on_key_press() method
        # Stage Information: Each stage is (rows x cols) = (12 x 20) cells
        # .	empty
        # 2	platform / left half-circle
        # 3	platform / right half-circle
        # 4	platform / rectangle
        # 5	platform / island
        # 6	ladder
        # 7	needle
        # #	target (100 points)
        # a	bonus (500 points)
        # b	bonus (1000 points)
        # c	enemy1 (always appear on the right)

        self.my_kill_grid = copy.deepcopy(self.false_list)
        for enemy in self.enemy_list:
            if enemy.isActive:
                r, c = enemy.get_gridRC()
                self.my_kill_grid[r][c] = True





        if self.old_kill_grid:
            for r in range(len(self.kill_grid)):
                for c in range(len(self.kill_grid[r])):
                    if self.kill_grid[r][c] != self.old_kill_grid[r][c]:
                        print('fail @ ', r, ' ', c)
                        flag = True
                        break
                else:
                    continue
                break
        else:
            print('init old')

        if self.oldScore != self.total_score\
                or self.old_stage != self.current_stage\
                or flag:
            self.map = ai.GameMap(self, self.my_kill_grid)
            if self.old_stage != self.current_stage:
                print('bad score check ', self.old_stage, ' ', self.current_stage)
                self.old_stage = self.current_stage
                self.map.redo_map(self.my_kill_grid)
            self.map.q_iteration(30, self.my_kill_grid)
            self.oldScore = self.total_score
            print('redo v')
            # print(self.my_kill_grid)


        # let's clear some bloat!
        tan_cell = self.map.state_grid[self.tanuki_r + 1][self.tanuki_c]

        # print('tan cell: (', self.tanuki_r, ', ', self.tanuki_c, ')')

        v_up = -sys.maxsize
        v_down = -sys.maxsize
        v_left = -sys.maxsize
        v_right = -sys.maxsize

        if tan_cell.t_up.valid_q():
            #print('can go up')
            v_up = self.map.state_grid[self.tanuki_r][self.tanuki_c].v
        if tan_cell.t_down.valid_q():
            #print('can go down')
            v_down = self.map.state_grid[self.tanuki_r + 2][self.tanuki_c].v
        if tan_cell.t_left == ai.TType.MOVE:
            v_left = self.map.state_grid[self.tanuki_r + 1][self.tanuki_c - 1].v
        if tan_cell.t_left == ai.TType.JUMP:
            v_left = self.map.state_grid[self.tanuki_r + 1][self.tanuki_c - 2].v
        if tan_cell.t_right == ai.TType.MOVE:
            v_right = self.map.state_grid[self.tanuki_r + 1][self.tanuki_c + 1].v
        if tan_cell.t_right == ai.TType.JUMP:
            v_right = self.map.state_grid[self.tanuki_r + 1][self.tanuki_c + 2].v

        print('left: ', v_left, ' ', tan_cell.t_left)
        print('right: ', v_right, ' ', tan_cell.t_right)
        print('up: ', v_up, ' ', tan_cell.t_up)
        print('down: ', v_down, ' ', tan_cell.t_down)
        print('r, c: ', self.tanuki_r, ' ', self.tanuki_c)


        #This will perform the chosen action for the given state and mdp analysis
        if max(v_left, v_right, v_down, v_up) >= 0:
            if v_left == max(v_left, v_right, v_down, v_up):
                if (not self.game.tanuki.isGoingLeft) or self.game.tanuki.isGoingUpDown:
                    self.game.on_key_press(arcade.key.LEFT, 0)
                if tan_cell.t_left == ai.TType.JUMP:
                    self.game.on_key_press(arcade.key.SPACE, 0)
                else:
                    self.game.on_key_press(arcade.key.LEFT, 0)
                self.tanuki_last = 1
            elif v_right == max(v_left, v_right, v_down, v_up):
                if self.game.tanuki.isGoingLeft or self.game.tanuki.isGoingUpDown:
                    self.game.on_key_press(arcade.key.RIGHT, 0)
                if tan_cell.t_right == ai.TType.JUMP:
                    self.game.on_key_press(arcade.key.SPACE, 0)
                else:
                    self.game.on_key_press(arcade.key.RIGHT, 0)
                self.tanuki_last = 2
            elif v_up == max(v_left, v_right, v_down, v_up):
                if not self.game.tanuki.isGoingUpDown:
                    self.game.on_key_press(arcade.key.UP, 0)
                self.game.on_key_press(arcade.key.UP, 0)
                self.tanuki_last = 3
            elif v_down == max(v_left, v_right, v_down, v_up):
                if not self.game.tanuki.isGoingUpDown:
                    self.game.on_key_press(arcade.key.DOWN, 0)
                self.game.on_key_press(arcade.key.DOWN, 0)
                self.tanuki_last = 4
        else:
            print("no move")



        self.old_kill_grid = self.my_kill_grid

    def print_q(self):
        fig = plt.figure(num=None, figsize=(30, 10), dpi=200, facecolor='w', edgecolor='k')
        ax = fig.add_subplot(111)
        #bx = fig.add_subplot(123)
        # I deserve to be ridiculed for this...
        the_table = ax.table(
                            cellText=self.map.state_grid,
                             # cellColours=[[self.map.state_colors[(self.map.state_grid[r][c]).cell_type]
                             #               for c in range(len(self.map.state_grid[r]))]
                             #               for r in range(len(self.map.state_grid))],
                             cellColours=[[(interp(self.map.state_grid[r][c].v,[-1, 1],[1, 0]), interp(self.map.state_grid[r][c].v,[-1, 1],[0, 1]), 0)
                                        for c in range(len(self.map.state_grid[r]))]
                                        for r in range(len(self.map.state_grid))],
                             loc='center')

        # the_other_table = bx.table(cellText=self.map.state_grid,
        #                      cellColours=[[self.map.state_colors[(self.map.state_grid[r][c]).cell_type]
        #                      for c in range(len(self.map.state_grid[r]))]
        #                      for r in range(len(self.map.state_grid))],
        #                      # cellColours=[[(interp(self.map.state_grid[r][c].v, [-1, 1], [1, 0]),
        #                      #                interp(self.map.state_grid[r][c].v, [-1, 1], [0, 1]), 0)
        #                      #               for c in range(len(self.map.state_grid[r]))]
        #                      #              for r in range(len(self.map.state_grid))],
        #                      loc='center')
        plt.savefig("v" + self.counter.__str__() + ".png")

    def run(self):
        print("Starting " + self.name)

        # os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50+320, 50)
        # pygame.init()

        # Prepare grid information display (can be turned off if performance issue exists)
        time.sleep(1)  # wait briefly so that main game can get ready

        # roughly every 50 milliseconds, retrieve game state (average human response time for visual stimuli = 25 ms)
        go = True
        while go and (self.game is not []):
            # Dispatch events from pygame window event queue
            if self.show_grid_info:
                pass
                # for event in pygame.event.get():
                #     if event.type == pygame.QUIT:
                #         go = False
                #         break

            # RETRIEVE CURRENT GAME STATE
            self.move_grid, self.kill_grid, \
                self.isGameClear, self.isGameOver, self.current_stage, self.time_limit, \
                self.total_score, self.total_time, self.total_life, self.tanuki_r, self.tanuki_c, self.enemy_list\
                = self.game.get_game_state()

            #Row coordinate regulizer, code doesn't work without it
            self.tanuki_r = self.tanuki_r - 1
            # if not self.level_initialized[self.current_stage - 1]:
            #     self.level_initialized[self.current_stage - 1] = True
            #     time.sleep(1)
            self.ai_function()
            self.tanuki_r += 1

            # Display grid information (can be turned off if performance issue exists)
            # if self.show_grid_info:
            #     for row in range(12):
            #         for col in range(20):
            #             c = self.move_grid[row][col] * 255 / 12
            #             arr[col, row] = (c, c, c)
            #         for col in range(20, 40):
            #             if self.kill_grid[row][col-20]:
            #                 arr[col, row] = (255, 0, 0)
            #             else:
            #                 arr[col, row] = (255, 255, 255)
            #
            #     # pygame.transform.scale(backscreen, screen_size, screen)
            #     # pygame.display.flip()

            # We must allow enough CPU time for the main game application
            # Polling interval can be reduced if you don't display the grid information
            time.sleep(0.08)

            #Gameover check so that code will stop when bot is finished with game
            if self.game.isGameOver or self.isGameClear:
                break

        print("Exiting " + self.name)


def main():
    ag = Agent(1, "to lose my mind", 1, True)
    ag.game = game_core.GameMain(ag)
    ag.start()

    ag.game.set_location(800, 400)

    #Uncomment below for recording
    #ag.game.isRecording = True
    #ag.game.replay('replay.rpy')  # You can specify replay file name or it will be generated using timestamp

    # Uncomment below to replay recorded play
    # ag.game.isReplaying = True
    # ag.game.replay('replay_clear.rpy')

    ag.game.reset()
    arcade.run()


if __name__ == "__main__":
    main()