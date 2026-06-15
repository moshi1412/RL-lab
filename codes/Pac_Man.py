import numpy as np
import time
import tkinter as tk
from PIL import Image, ImageTk
import random

UNIT = 100
Map_H = 5
Map_W = 5

map_state = np.array([
    [ 0,  1,  2,  3,  4],
    [ 5,  6,  7,  8,  9],
    [10, 11, 12, 13, 14],
    [15, 16, 17, 18, 19],
    [20, 21, 22, 23, 24]
])

def grid_to_canvas(col, row):
    origin = np.array([UNIT / 2, UNIT / 2])
    return origin[0] + col * UNIT, origin[1] + row * UNIT

class Map(tk.Tk, object):
    def __init__(self):
        super(Map, self).__init__()
        self.action_space = ['u', 'd', 'l', 'r']
        self.n_actions = len(self.action_space)
        self.title('Pac-Man')
        self.geometry('{0}x{1}+400+50'.format(Map_W * UNIT, Map_H * UNIT))
        self.bean_positions = [(0, 2), (2, 3)]
        self.ghosts = [
            {'row': 1, 'col': 2, 'type': 'static'},
            {'row': 2, 'col': 1, 'type': 'static'},
            {'row': 3, 'col': 3, 'type': 'static'},
        ]
        self._build_map()

    def _build_map(self):
        self.canvas = tk.Canvas(self, bg='white', height=Map_H * UNIT, width=Map_W * UNIT)
        for c in range(0, Map_W * UNIT, UNIT):
            self.canvas.create_line(c, 0, c, Map_H * UNIT)
        for r in range(0, Map_H * UNIT, UNIT):
            self.canvas.create_line(0, r, Map_W * UNIT, r)

        origin = np.array([UNIT / 2, UNIT / 2])
        IMG_SIZE = (80, 80)
        def load_img(path):
            return ImageTk.PhotoImage(Image.open(path).resize(IMG_SIZE, Image.Resampling.LANCZOS))

        self.bm_beans = load_img("./beans.png")
        self.bm_ghost = load_img("./ghost.png")
        self.bm_person = load_img("./pac-man.png")
        self.bm_flag = load_img("./destination.png")


        self.flag = self.canvas.create_image(origin[0]+UNIT*4, origin[1]+UNIT*4,
                                              image=self.bm_flag, tag="destination")

        # 豆子
        self.bean_items = []
        for i, (row, col) in enumerate(self.bean_positions):
            cx, cy = grid_to_canvas(col, row)
            item = self.canvas.create_image(cx, cy, image=self.bm_beans, tag="bean%d" % i)
            self.bean_items.append(item)

        
        self.ghost_items = []
        for i, g in enumerate(self.ghosts):
            cx, cy = grid_to_canvas(g['col'], g['row'])
            item = self.canvas.create_image(cx, cy, image=self.bm_ghost, tag="ghost%d" % i)
            self.ghost_items.append(item)

        # 吃豆人，初始位置(0,0)
        cx, cy = grid_to_canvas(0, 0)
        self.person = self.canvas.create_image(cx, cy, image=self.bm_person)
        self.canvas.pack()

    def reset(self):
        self.update()
        # time.sleep(0.1)
        self.canvas.delete(self.person)

        self.bean_positions = [(0, 2), (2, 3)]
        for item in self.bean_items:
            self.canvas.delete(item)
        self.bean_items = []
        for i, (row, col) in enumerate(self.bean_positions):
            cx, cy = grid_to_canvas(col, row)
            item = self.canvas.create_image(cx, cy, image=self.bm_beans, tag="bean%d" % i)
            self.bean_items.append(item)

        self.ghosts = [
            {'row': 1, 'col': 2, 'type': 'static'},
            {'row': 2, 'col': 1, 'type': 'static'},
            {'row': 3, 'col': 3, 'type': 'static'},
        ]
        for i, g in enumerate(self.ghosts):
            self.canvas.delete(self.ghost_items[i])
            cx, cy = grid_to_canvas(g['col'], g['row'])
            item = self.canvas.create_image(cx, cy, image=self.bm_ghost, tag="ghost%d" % i)
            if i < len(self.ghost_items):
                self.ghost_items[i] = item
            else:
                self.ghost_items.append(item)

        cx, cy = grid_to_canvas(0, 0)
        self.person = self.canvas.create_image(cx, cy, image=self.bm_person)
        self.render()
        return self.get_state()

    def get_state(self):
        """返回状态 (row, col, remaining_beans)"""
        row, col = self._get_pacman_grid_pos()
        return (row, col, len(self.bean_positions))

    def _get_pacman_grid_pos(self):
        coords = self.canvas.coords(self.person)
        col = min(int(coords[0] / UNIT), Map_W - 1)
        row = min(int(coords[1] / UNIT), Map_H - 1)
        return row, col

    def _check_ghost_collision(self):
        row, col = self._get_pacman_grid_pos()
        for g in self.ghosts:
            if row == g['row'] and col == g['col']:
                return True
        return False

    def step(self, action):
        """执行动作，返回 (next_state, reward, done)"""
        s = self.canvas.coords(self.person)
        base_action = np.array([0, 0])
        cost = -1  

        
        if action == 0:  
            if s[1] >= UNIT:
                base_action[1] -= UNIT
            else:
                #惩罚 -10位置不变
                return self.get_state(), -10, False
        elif action == 1:  
            if s[1] < (Map_H - 1) * UNIT:
                base_action[1] += UNIT
            else:
                return self.get_state(), -10, False
        elif action == 2:
            if s[0] >= UNIT:
                base_action[0] -= UNIT
            else:
                return self.get_state(), -10, False
        elif action == 3:  
            if s[0] < (Map_W - 1) * UNIT:
                base_action[0] += UNIT
            else:
                return self.get_state(), -10, False

        self.canvas.move(self.person, base_action[0], base_action[1])
        self.render()
        row, col = self._get_pacman_grid_pos()
        reward = cost
        #TODO
        if (row, col) in self.bean_positions:
            reward += 100       # 奖励多少啊
            self.bean_positions.remove((row, col))#清空
            idx = 0
            
            
            #补充
            while idx < len(self.bean_items):
                item = self.bean_items[idx]
                coords = self.canvas.coords(item)
                bean_col = int(coords[0] / UNIT)
                bean_row = int(coords[1] / UNIT)
                if (bean_row, bean_col) == (row, col):
                    self.canvas.delete(item)
                    self.bean_items.pop(idx)
                else:
                    idx += 1

        # TODO 
        if self._check_ghost_collision():
            reward -= 5            # 惩罚-5足矣
            return self.get_state(), reward, True

        # TODO 
        if row == 4 and col == 4:
            if len(self.bean_positions) == 0:
                reward += 500     # 高额
            else:
                reward -= 10       
            return self.get_state(), reward, True

        return self.get_state(), reward, False

    def render(self):
        time.sleep(0.1)
        self.update()
        # time.sleep(0.1)


move = [[-1,0],[1,0],[0,-1],[0,1]]
beans = {(0,2),(2,3)}
ghosts = {(1,2),(2,1),(3,3)}
action_names = ['u', 'd', 'l', 'r']

class MC:
    def __init__(self):
        self.states = [(r,c,b) for r in range(5) for c in range(5) for b in [0,1,2]]
        self.V = {s: 0.0 for s in self.states}
        self.count = {s: 0 for s in self.states}
        self.gamma = 0.4
        self.epsilon = 0.7

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0,3)
        return self.get_best_action(state)

    def get_best_action(self, state):
        row, col, bean = state
        best_val = -float('inf')
        best_act = 0
        for a in range(4):
            nr = row + move[a][0]
            nc = col + move[a][1]
            if 0 <= nr < 5 and 0 <= nc < 5:
                nb = bean - 1 if (nr, nc) in beans and bean > 0 else bean
                next_s = (nr, nc, nb)
                val = self.V[next_s]
            else:
                val = -1e9   # 撞墙动作价值极低 虽然也不用这么低 但是不能卡墙
            if val > best_val:
                best_val = val
                best_act = a
        return best_act

    def update(self, episode):
        G = 0.0
        for state, reward in reversed(episode):
            G = reward + self.gamma * G
            self.count[state] += 1
            self.V[state] += (G - self.V[state]) / self.count[state]#只能增量算




    #可视化棋盘
    # def print_current_layer_value(self, bean_layer, current_pos):
    #     rp, cp, _ = current_pos
    #     print("\n======================================")
    #     print(f"剩余豆子:{bean_layer} | 当前位置:({rp},{cp})")
    #     print("     列0     列1     列2     列3     列4")
    #     for r in range(5):
    #         line = f"行{r}|"
    #         for c in range(5):
    #             v = self.V[(r,c,bean_layer)]
    #             flag = ""
    #             if r == rp and c == cp:
    #                 flag = "P"
    #             elif (r,c) in beans:
    #                 flag = "O"
    #             elif (r,c) in ghosts:
    #                 flag = "X"
    #             line += f' {flag}{v:5.1f}'
    #         print(line)
    #     print("======================================\n")
    
    #用于可视化
    def save_mc_memo(self):
        with open("mc_value_table.csv", "w") as f:
            f.write("row,col,remain_beans,value\n")
            for r in range(5):
                for c in range(5):
                    for rem in range(3):
                        val = self.V[(r, c, rem)]
                        f.write(f"{r},{c},{rem},{val:.4f}\n")
     

def train_mc(env, mc, episodes=200, window_size=10, delta_threshold=0.05):

    prev_V = mc.V.copy()          
    delta_history = []            
    success_history = []          

    for i in range(episodes):
        s = env.reset()
        episode = []            
        done = False

        while not done:
            a = mc.choose_action(s)
            s_next, r, done = env.step(a)
            episode.append((s_next, r))
          
            # mc.print_current_layer_value(s[2], s)
            # print(f"回合:{i+1} | 状态{s} | 动作:{action_names[a]} | 奖励:{r} | 下一状态:{s_next}")
            s = s_next

        # 成功
        success = (s[0] == 4 and s[1] == 4 and s[2] == 0)
        success_history.append(success)

        mc.update(episode)
        changes = [abs(mc.V[state] - prev_V[state]) for state in mc.states]
        avg_delta = sum(changes) / len(mc.states)
        delta_history.append(avg_delta)
        prev_V = mc.V.copy()        
        
        #   最近 window_size 个回合的变化量平均值小于阈值
        if len(delta_history) >= window_size:
            recent_deltas = delta_history[-window_size:]
            if sum(recent_deltas) / window_size < delta_threshold:
                print("收敛")
                break

    total_episodes = len(success_history)
    success_cnt = sum(success_history)
    success_rate = success_cnt / total_episodes * 100

    print(total_episodes)
    print(success_rate)

    mc.save_mc_memo()

def demo_mc(env, mc):
    s = env.reset()
    steps = 0
    while steps < 100:
        a = mc.get_best_action(s)
        s, _, done = env.step(a)
        # mc.print_current_layer_value(s[2], s)
        steps += 1
        if done:
            break


class DP:
    def __init__(self):
        self.VALUE = [[[-1e3 for _ in range(3)] for __ in range(Map_W)] for ___ in range(Map_H)]
        self.best_action = [[[0 for _ in range(3)] for __ in range(Map_W)] for ___ in range(Map_H)]
        self.gamma = 0.9 

    def value_iteration(self):
        """值迭代算法"""
        for b in range(3):
            self.VALUE[4][4][b] = 100 if b == 0 else -100
        for (r, c) in ghosts:
            for b in range(3):
                self.VALUE[r][c][b] = -100

        for epoch in range(100):
            delta = 0
            for row in range(Map_H):
                for col in range(Map_W):
                    for remain_beans_num in range(3):
                        if (row == 4 and col == 4) or (row, col) in ghosts:
                            continue
                        max_v = -1e9
                        best_act = 0
                        for i in range(4):
                            nr = row + move[i][0]
                            nc = col + move[i][1]
                            if nr < 0 or nr >= Map_H or nc < 0 or nc >= Map_W:
                                v = -10        
                            else:
                                reward = -1      
                                new_remain = remain_beans_num
                                if (nr, nc) in beans and remain_beans_num > 0:
                                    reward += 10   # 吃豆奖励
                                    new_remain = remain_beans_num - 1
                                v = reward + self.gamma * self.VALUE[nr][nc][new_remain]
                            if v > max_v:
                                max_v = v
                                best_act = i
                        delta = max(delta, abs(max_v - self.VALUE[row][col][remain_beans_num]))
                        self.VALUE[row][col][remain_beans_num] = max_v
                        self.best_action[row][col][remain_beans_num] = best_act
            if delta < 1e-3:
                print(f"迭代收敛 {epoch+1} 轮")
                break

    def get_best_action(self, state):
        """根据当前状态获取最优动作"""
        row, col, b = state
        return self.best_action[row][col][b]

    # def print_current_layer_value(self, bean_layer, current_pos):
      
    #     row, col, _ = current_pos
    #     print("\n======================================")
    #     print(f"剩余豆子:{bean_layer} | 当前位置:({row},{col})")
    #     print("     列0     列1     列2     列3     列4")
    #     for row in range(5):
    #         line = f"行{row}|"
    #         for col in range(5):
    #             v = self.VALUE[row][col][bean_layer]
    #             flag = ""
    #             if row == row and col == col:
    #                 flag = "P"
    #             elif (row, col) in beans:
    #                 flag = "X"
    #             elif (row, col) in ghosts:  
    #                 flag = "O"
    #             line += f' {flag}{v:5.1f}'
    #         print(line)
    #     print("======================================\n")

    # def save_dp_memo(self):
    #     """保存动态规划备忘录"""
    #     with open("dp_value_table.csv", "w") as f:
    #         f.write("row,col,remain_beans,value\n")
    #         for row in range(Map_H):
    #             for col in range(Map_W):
    #                 for rem in range(3):
    #                     val = self.VALUE[row][col][rem]
    #                     f.write(f"{row},{col},{rem},{val:.4f}\n")
    #     with open("dp_best_action.csv", "w") as f:
    #         f.write("row,col,remain_beans,best_action(0=上,1=下,2=左,3=右)\n")
    #         for row in range(Map_H):
    #             for col in range(Map_W):
    #                 for rem in range(3):
    #                     act = self.best_action[row][col][rem]
    #                     f.write(f"{row},{col},{rem},{act}\n")
       

def train_dp(dp):
    dp.value_iteration()

def demo_dp(env, dp):
   
    s = env.reset()
    steps = 0
    total_reward = 0

    while steps < 100:
        dp.print_current_layer_value(s[2], s)
        a = dp.get_best_action(s)
        s_next, r, done = env.step(a)
        total_reward += r
        s = s_next
        steps += 1
        if done:
            break

    # dp.save_dp_memo()


if __name__ == '__main__':

    choice ='1'

    env = Map()

    if choice == '1':
        mc = MC()
        train_mc(env, mc)
        demo_mc(env, mc)
    elif choice == '2':
        dp = DC()
        train_dp(dp)
        demo_dp(env, dp)
   
    env.mainloop()