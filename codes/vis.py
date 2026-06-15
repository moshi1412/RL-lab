import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# ===================== 配置 =====================
Map_H, Map_W = 5, 5
z_gap = 10000 # 越大间距越大！！！

beans = [(0,2), (2,3)]
ghosts = [(1,2), (2,1), (3,3)]
goal = (4,4)

# --- 读取 DP 价值表（用于显示数值）---
value_data = np.loadtxt("D:\learning\强化学习-编程\强化学习-编程\codes\mc_value_table.csv", delimiter=",", skiprows=1)
V = np.zeros((Map_H, Map_W, 3))
for row in value_data:
    r, c, rem, val = int(row[0]), int(row[1]), int(row[2]), row[3]
    V[r, c, rem] = val

# --- 读取最佳动作表，并生成最优路径 ---
def load_best_action(csv_file="dp_best_action.csv"):
    action = np.zeros((Map_H, Map_W, 3), dtype=int)
    with open(csv_file, 'r') as f:
        lines = f.readlines()[1:]
        for line in lines:
            r, c, rem, a = line.strip().split(',')
            r, c, rem, a = int(r), int(c), int(rem), int(a)
            action[r, c, rem] = a
    return action

def reconstruct_path(best_action, start_r=0, start_c=0, start_rem=2):
    path = []
    cur_r, cur_c, rem = start_r, start_c, start_rem
    moves = [(-1,0), (1,0), (0,-1), (0,1)]
    while True:
        path.append((cur_r, cur_c, rem))
        if (cur_r, cur_c) == goal or (cur_r, cur_c) in ghosts:
            break
        act = best_action[cur_r, cur_c, rem]
        dr, dc = moves[act]
        nr, nc = cur_r + dr, cur_c + dc
        if nr < 0 or nr >= Map_H or nc < 0 or nc >= Map_W:
            break
        if (nr, nc) in beans and rem > 0:
            rem -= 1
        cur_r, cur_c = nr, nc
    return path

best_action = load_best_action()
best_path = reconstruct_path(best_action)
path_set = set(best_path)

print("自动生成的最优路径：")
for i, (r,c,rem) in enumerate(best_path):
    print(f"Step {i}: ({r},{c}, rem={rem})")

# ===================== 绘图（已修复间距）=====================
fig = plt.figure(figsize=(15, 10))
ax = fig.add_subplot(111, projection='3d')
top_z = 3 * z_gap  # <-- 动态计算，不再固定

# --- 1. 绘制三层状态数值层 ---
for remain in [0, 1, 2]:
    z = remain * z_gap
    for i in range(Map_W + 1):
        ax.plot([i-0.5, i-0.5], [-0.5, 4.5], [z, z], color='gray', linewidth=0.6)
    for j in range(Map_H + 1):
        ax.plot([-0.5, 4.5], [j-0.5, j-0.5], [z, z], color='gray', linewidth=0.6)
    for r in range(Map_H):
        for c in range(Map_W):
            val = V[r, c, remain]
            color = 'blue' if (r,c,remain) in path_set else 'black'
            weight = 'bold' if (r,c,remain) in path_set else 'normal'
            ax.text(c, r, z, f"{val:.0f}", ha='center', va='center',
                    fontsize=11 if weight=='bold' else 9,
                    fontweight=weight, color=color)

# --- 2. 顶层棋盘 ---
for i in range(Map_W + 1):
    ax.plot([i-0.5, i-0.5], [-0.5, 4.5], [top_z, top_z], color='gray', linewidth=0.6, alpha=0.7)
for j in range(Map_H + 1):
    ax.plot([-0.5, 4.5], [j-0.5, j-0.5], [top_z, top_z], color='gray', linewidth=0.6, alpha=0.7)

# --- 3. 顶层物体标记 ---
for (r,c) in beans:
    ax.scatter(c, r, top_z, s=200, c='gold', marker='o', edgecolors='orange', linewidth=1.5,
               label='Bean' if (r,c)==beans[0] else "")
for (r,c) in ghosts:
    ax.scatter(c, r, top_z, s=200, c='red', marker='X', edgecolors='darkred', linewidth=2,
               label='Ghost' if (r,c)==ghosts[0] else "")
ax.scatter(goal[1], goal[0], top_z, s=300, c='lime', marker='*', edgecolors='darkgreen', linewidth=2, label='Goal')

# --- 4. 最优路径 ---
path_x = [p[1] for p in best_path]
path_y = [p[0] for p in best_path]
path_z = [p[2] * z_gap for p in best_path]
ax.plot(path_x, path_y, path_z, color='blue', linewidth=3, marker='o', markersize=8, label='Optimal Path')

# --- 5. 顶层路径投影 ---
top_path_coords = set((r,c) for (r,c,_) in best_path)
for (r,c) in top_path_coords:
    ax.scatter(c, r, top_z, s=120, c='none', edgecolors='blue', linewidth=2, marker='o')
for i in range(len(best_path)-1):
    r1,c1,_ = best_path[i]
    r2,c2,_ = best_path[i+1]
    ax.plot([c1,c2], [r1,r2], [top_z,top_z], color='blue', linestyle='dashed', linewidth=1.5, alpha=0.6)

# --- 6. 坐标与显示（关键修复） ---
ax.set_zlim(0, 1)  # <-- 让画布能放下扩大的间距
ax.set_xlabel('Column (X)', fontsize=12)
ax.set_ylabel('Row (Y)', fontsize=12)
ax.zaxis.set_rotate_label(False)
zlabel = ax.set_zlabel('Layer (Remaining Beans)', fontsize=12, labelpad=40)
# 往右偏移：正数=右，负数=左
ax.zaxis.set_label_coords(300, 300)
ax.set_xticks(range(Map_W))
ax.set_yticks(range(Map_H))
# Z 轴刻度位置
ax.set_zticks([0, z_gap, 2*z_gap, top_z])

# 👉 右移 Z 刻度标签（关键代码）
ax.tick_params(axis='z', which='major', pad=35)  # pad越大越往右
ax.set_zticklabels(['Remain 0', 'Remain 1', 'Remain 2', 'Top (Objects)'])

# 👉 右移 Z 标题
ax.zaxis.set_rotate_label(False)
ax.set_zlabel('Layer (Remaining Beans)', fontsize=12, labelpad=40)
ax.zaxis.set_label_coords(1.25, 0.5)
ax.view_init(elev=20, azim=-65)
ax.dist = 8
ax.xaxis.pane.fill = False
ax.yaxis.pane.fill = False
ax.zaxis.pane.fill = False
ax.grid(False)

handles, labels = ax.get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys(), loc='upper left', bbox_to_anchor=(1.05, 1))

plt.tight_layout()
plt.show()