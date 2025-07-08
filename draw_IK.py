import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches
from matplotlib import transforms
from PIL import Image, ImageChops

# Set up the figure
fig, ax = plt.subplots(1, 1, figsize=(8, 6))

# Define parameters
L1 = 3.0
L2 = 2.5
q1 = 30
q2 = 45
width = 0.3

q1_rad = np.deg2rad(q1)
q2_rad = np.deg2rad(q2)

# Calculate joint and end effector positions
joint_x = L1 * np.cos(q1_rad)
joint_y = L1 * np.sin(q1_rad)
end_x = joint_x + L2 * np.cos(q1_rad + q2_rad)
end_y = joint_y + L2 * np.sin(q1_rad + q2_rad)

# Draw links
rect1 = Rectangle((0, -width/2), L1, width, angle=q1, rotation_point='xy',
                  facecolor='salmon', edgecolor='darkred', linewidth=2)
t2 = transforms.Affine2D().rotate_deg(q1 + q2).translate(joint_x, joint_y) + ax.transData
rect2 = Rectangle((0, -width/2), L2, width, transform=t2,
                  facecolor='lightgreen', edgecolor='darkgreen', linewidth=2)
ax.add_patch(rect1)
ax.add_patch(rect2)

# Draw circles
ax.add_patch(plt.Circle((joint_x, joint_y), 0.15, color='black', zorder=5))
ax.add_patch(plt.Circle((0, 0), 0.15, color='black', zorder=5))

# Draw dashed lines
extend_ratio = 0.8
ext_x = (L1 + extend_ratio * L1) * np.cos(q1_rad)
ext_y = (L1 + extend_ratio * L1) * np.sin(q1_rad)
ax.plot([0, ext_x], [0, ext_y], 'k--', linewidth=1, alpha=0.5)
ax.plot([joint_x, end_x], [joint_y, end_y], 'k--', linewidth=1, alpha=0.5)

# Draw auxiliary line: F0 to F2
ax.plot([0, end_x], [0, end_y], color='blue', linestyle=':', linewidth=2, label='F0-F2')

# Draw auxiliary perpendicular from F2 to F0F1 extension
v = np.array([joint_x, joint_y])
v_unit = v / np.linalg.norm(v)
p = np.array([end_x, end_y])
proj_len = np.dot(p, v_unit)
proj_point = proj_len * v_unit
ax.plot([end_x, proj_point[0]], [end_y, proj_point[1]], color='purple', linestyle='-.', linewidth=2, label='Perpendicular from F2')
ax.plot(proj_point[0], proj_point[1], 'o', color='purple', markersize=8, label='Foot of Perpendicular')

# 其余内容同原脚本
arc1_radius = 0.8
arc1 = mpatches.Arc((0, 0), 2*arc1_radius, 2*arc1_radius, angle=0, theta1=0, theta2=q1, linestyle='--', color='black', linewidth=1.5)
ax.add_patch(arc1)
arc2_radius = 0.6
arc2 = mpatches.Arc((joint_x, joint_y), 2*arc2_radius, 2*arc2_radius, angle=q1, theta1=0, theta2=q2, linestyle='--', color='black', linewidth=1.5)
ax.add_patch(arc2)
ax.text(0.9, 0.15, r'$q_1$', fontsize=14, fontweight='bold')
q2_label_r = arc2_radius + 0.25
q2_label_angle = q1 + q2/2
q2_label_x = joint_x + q2_label_r * np.cos(np.deg2rad(q2_label_angle))
q2_label_y = joint_y + q2_label_r * np.sin(np.deg2rad(q2_label_angle))
ax.text(q2_label_x, q2_label_y, r'$q_2$', fontsize=14, fontweight='bold')

a1_label_x = (L1/2) * np.cos(q1_rad) + 0.1
a1_label_y = (L1/2) * np.sin(q1_rad) - 0.25
ax.text(a1_label_x, a1_label_y, r'$a_1$', fontsize=13, color='darkred', ha='center', va='center')
a2_label_x = joint_x + (L2/2) * np.cos(q1_rad + q2_rad) + 0.3
a2_label_y = joint_y + (L2/2) * np.sin(q1_rad + q2_rad)
ax.text(a2_label_x, a2_label_y, r'$a_2$', fontsize=13, color='darkgreen', ha='center', va='center')
ax.arrow(-0.5, 0, 5.5, 0, head_width=0.1, head_length=0.1, fc='gray', ec='gray')
ax.arrow(0, -0.5, 0, 5, head_width=0.1, head_length=0.1, fc='gray', ec='gray')
ax.text(5.1, -0.2, 'x', fontsize=14, color='gray')
ax.text(-0.2, 4.7, 'y', fontsize=14, color='gray')
ax.text(end_x-0.2, end_y + 0.3, r'Frame $F_2$', fontsize=12, fontweight='bold', color='darkgreen', bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.7))
ax.text(-0.5, -0.5, r'Frame $F_0$', fontsize=12, fontweight='bold', color='black', bbox=dict(boxstyle="round,pad=0.3", facecolor='wheat', alpha=0.7))
ax.text(joint_x + 0.1, joint_y - 0.5, r'Frame $F_1$', fontsize=12, fontweight='bold', color='black', bbox=dict(boxstyle="round,pad=0.3", facecolor='wheat', alpha=0.7))
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
plt.savefig("images/2link-arm-IK.png", dpi=300, bbox_inches='tight', pad_inches=0, facecolor='white')
plt.close()

# 用Pillow自动裁剪
im = Image.open("images/2link-arm-IK.png").convert("RGB")
bg = Image.new("RGB", im.size, (255, 255, 255))
diff = ImageChops.difference(im, bg)
bbox = diff.getbbox()
if bbox:
    im_cropped = im.crop(bbox)
    im_cropped.save("images/2link-arm-IK.png")