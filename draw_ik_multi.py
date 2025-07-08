import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches
from matplotlib import transforms
from PIL import Image, ImageChops

# Set up the figure
fig, ax = plt.subplots(figsize=(8, 6))  # Ensure ax is a matplotlib Axes object

# Define parameters
L1 = 3.0  # Length of first segment
L2 = 2.5  # Length of second segment
q1 = 30   # Angle of first segment (degrees)
q2 = 45   # Angle of second segment relative to first (degrees)
width = 0.3  # Width of segments

q1_rad = np.deg2rad(q1)
q2_rad = np.deg2rad(q2)

# Calculate joint and end effector positions for original arm
joint_x = L1 * np.cos(q1_rad)
joint_y = L1 * np.sin(q1_rad)
end_x = joint_x + L2 * np.cos(q1_rad + q2_rad)
end_y = joint_y + L2 * np.sin(q1_rad + q2_rad)

# Draw original arm (solid)
rect1 = Rectangle((0, -width/2), L1, width, angle=q1, rotation_point='xy',
                  facecolor='salmon', edgecolor='darkred', linewidth=2, alpha=1.0)
t2 = transforms.Affine2D().rotate_deg(q1 + q2).translate(joint_x, joint_y) + ax.transData
rect2 = Rectangle((0, -width/2), L2, width, transform=t2,
                  facecolor='lightgreen', edgecolor='darkgreen', linewidth=2, alpha=1.0)
ax.add_patch(rect1)
ax.add_patch(rect2)
ax.add_patch(plt.Circle((joint_x, joint_y), 0.15, color='black', zorder=5, alpha=1.0))
ax.add_patch(plt.Circle((0, 0), 0.15, color='black', zorder=5, alpha=1.0))

# Draw dashed lines for original arm
extend_ratio = 0.8
ext_x = (L1 + extend_ratio * L1) * np.cos(q1_rad)
ext_y = (L1 + extend_ratio * L1) * np.sin(q1_rad)
ax.plot([0, ext_x], [0, ext_y], 'k--', linewidth=1, alpha=0.5)
ax.plot([joint_x, end_x], [joint_y, end_y], 'k--', linewidth=1, alpha=0.5)

# Draw angle arcs for original arm
arc1_radius = 0.8
# arc1 = mpatches.Arc((0, 0), 2*arc1_radius, 2*arc1_radius, angle=0, theta1=0, theta2=q1, linestyle='--', color='black', linewidth=1.5)
# ax.add_patch(arc1)
arc2_radius = 0.6
arc2 = mpatches.Arc((joint_x, joint_y), 2*arc2_radius, 2*arc2_radius, angle=q1, theta1=0, theta2=q2, linestyle='--', color='black', linewidth=1.5)
ax.add_patch(arc2)

# Add angle labels for original arm
# ax.text(0.9, 0.15, r'$q_1$', fontsize=14, fontweight='bold')
q2_label_r = arc2_radius + 0.25
q2_label_angle = q1 + q2/2
q2_label_x = joint_x + q2_label_r * np.cos(np.deg2rad(q2_label_angle))
q2_label_y = joint_y + q2_label_r * np.sin(np.deg2rad(q2_label_angle))
ax.text(q2_label_x, q2_label_y, r'$|q_2|$', fontsize=14, fontweight='bold')

# Draw coordinate axes
ax.arrow(-0.5, 0, 5.5, 0, head_width=0.1, head_length=0.1, fc='gray', ec='gray')
ax.arrow(0, -0.5, 0, 5, head_width=0.1, head_length=0.1, fc='gray', ec='gray')
ax.text(5.1, -0.2, 'x', fontsize=14, color='gray')
ax.text(-0.2, 4.7, 'y', fontsize=14, color='gray')

# Add frame labels
ax.text(end_x-0.2, end_y + 0.3, r'Frame $F_2$', fontsize=12, fontweight='bold', color='darkgreen', bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.7))
ax.text(-0.5, -0.5, r'Frame $F_0$', fontsize=12, fontweight='bold', color='black', bbox=dict(boxstyle="round,pad=0.3", facecolor='wheat', alpha=0.7))
ax.text(joint_x + 0.1, joint_y - 0.5, r'Frame $F_1$', fontsize=12, fontweight='bold', color='black', bbox=dict(boxstyle="round,pad=0.3", facecolor='wheat', alpha=0.7))

# --- Symmetric arm (about F0F2) ---
# Vector from F0 to F2
v_f0f2 = np.array([end_x, end_y])
# Unit vector
v_unit = v_f0f2 / np.linalg.norm(v_f0f2)
# Perpendicular unit vector
v_perp = np.array([-v_unit[1], v_unit[0]])
# Distance from F0 to F1 (original)
d_f0f1 = np.linalg.norm([joint_x, joint_y])
# Project F1 onto F0F2
proj_len = np.dot([joint_x, joint_y], v_unit)
proj_point = proj_len * v_unit
# F1' is symmetric to F1 about F0F2
f1_vec = np.array([joint_x, joint_y])
f1_sym = proj_point - (f1_vec - proj_point)
joint_x2, joint_y2 = f1_sym
# F2' is the same as F2 (end effector)
# Draw symmetric arm (semi-transparent)

# 计算 F0F1' 的方向和法向量
dir_f0f1p = f1_sym - np.array([0, 0])
dir_f0f1p_unit = dir_f0f1p / np.linalg.norm(dir_f0f1p)
normal = np.array([-dir_f0f1p_unit[1], dir_f0f1p_unit[0]])  # 法向量

# Rectangle 的 anchor 应该是 (0, 0)，然后整体平移 -width/2 * normal
rect1_sym_xy = -width/2 * normal
rect1_sym_angle = np.rad2deg(np.arctan2(dir_f0f1p_unit[1], dir_f0f1p_unit[0]))
rect1_sym = Rectangle(rect1_sym_xy, L1, width, angle=rect1_sym_angle, rotation_point='xy',
                      facecolor='salmon', edgecolor='darkred', linewidth=2, alpha=0.3)
ax.add_patch(rect1_sym)

t2_sym = transforms.Affine2D().rotate_deg(np.rad2deg(np.arctan2(end_y-joint_y2, end_x-joint_x2))).translate(joint_x2, joint_y2) + ax.transData
rect2_sym = Rectangle((0, -width/2), L2, width, transform=t2_sym, facecolor='lightgreen', edgecolor='darkgreen', linewidth=2, alpha=0.3)
ax.add_patch(rect2_sym)
ax.add_patch(plt.Circle((joint_x2, joint_y2), 0.15, color='black', zorder=5, alpha=0.3))
ax.add_patch(plt.Circle((0, 0), 0.15, color='black', zorder=5, alpha=0.3))
# Dashed lines for symmetric arm
ax.plot([0, joint_x2], [0, joint_y2], 'k--', linewidth=1, alpha=0.2)
ax.plot([joint_x2, end_x], [joint_y2, end_y], 'k--', linewidth=1, alpha=0.2)
# Joint frame label for symmetric arm
ax.text(joint_x2 + 0.1, joint_y2 - 0.5, r'Frame $F_1^\prime$', fontsize=12, fontweight='bold', color='black', alpha=0.5, bbox=dict(boxstyle="round,pad=0.3", facecolor='wheat', alpha=0.3))

# 1. 绘制 F0F1' 的延长线
f0 = np.array([0, 0])
f1p = np.array([joint_x2, joint_y2])
dir_f0f1p = f1p - f0
dir_f0f1p_unit = dir_f0f1p / np.linalg.norm(dir_f0f1p)
# 延长线终点（可根据画布大小调整倍数）
line_len = np.linalg.norm(dir_f0f1p) * 1.5
end_ext = f0 + dir_f0f1p_unit * line_len
ax.plot([f0[0], end_ext[0]], [f0[1], end_ext[1]], color='orange', linestyle=':', linewidth=2, alpha=0.7)

# 2. 标注 -q2
# 计算 -q2 的角度中点
arc2_radius = 0.6
neg_q2_label_r = arc2_radius + 0.25
neg_q2_label_angle = np.rad2deg(np.arctan2(end_y - joint_y2, end_x - joint_x2)) - q2/2
neg_q2_label_x = joint_x2 + neg_q2_label_r * np.cos(np.deg2rad(neg_q2_label_angle))
neg_q2_label_y = joint_y2 + neg_q2_label_r * np.sin(np.deg2rad(neg_q2_label_angle))
ax.text(neg_q2_label_x-0.5, neg_q2_label_y+0.4, r'$-|q_2|$', fontsize=14, fontweight='bold', color='purple')

# 计算起点和终点角度
theta_end = np.rad2deg(np.arctan2(joint_y2, joint_x2))  # F₀F₁'方向
theta_start = np.rad2deg(np.arctan2(end_y - joint_y2, end_x - joint_x2))  # F₁'F₂方向

# 计算顺时针夹角
arc_extent = (theta_end - theta_start) % 360

# 画弧线（仿照q1、q2的画法）
arc_r = 0.6
arc_negq2 = mpatches.Arc((joint_x2, joint_y2), 2*arc_r, 2*arc_r,
                         angle=0, theta1=theta_start, theta2=theta_end,
                         linestyle='--', color='purple', linewidth=1.5)
ax.add_patch(arc_negq2)

# Set equal aspect ratio
ax.set_aspect('equal')
ax.set_xlim(-1.5, 6)
ax.set_ylim(-1.5, 6)
ax.set_xticks([])
ax.set_yticks([])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig("images/2link-arm-ik-multi.png", dpi=300, bbox_inches='tight', pad_inches=0, facecolor='white')
plt.close() 

# 用Pillow自动裁剪
im = Image.open("images/2link-arm-ik-multi.png").convert("RGB")
bg = Image.new("RGB", im.size, (255, 255, 255))
diff = ImageChops.difference(im, bg)
bbox = diff.getbbox()
if bbox:
    im_cropped = im.crop(bbox)
    im_cropped.save("images/2link-arm-ik-multi.png")