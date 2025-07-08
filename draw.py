import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches
from matplotlib import transforms
from PIL import Image, ImageChops

# Set up the figure
fig, ax = plt.subplots(1, 1, figsize=(8, 6))

# Define parameters
L1 = 3.0  # Length of first segment
L2 = 2.5  # Length of second segment
q1 = 30   # Angle of first segment (degrees)
q2 = 45   # Angle of second segment relative to first (degrees)
width = 0.3  # Width of segments

# Convert angles to radians
q1_rad = np.deg2rad(q1)
q2_rad = np.deg2rad(q2)

# Calculate joint position
joint_x = L1 * np.cos(q1_rad)
joint_y = L1 * np.sin(q1_rad)

# Calculate end effector position
end_x = joint_x + L2 * np.cos(q1_rad + q2_rad)
end_y = joint_y + L2 * np.sin(q1_rad + q2_rad)

# Create first segment (red)
rect1 = Rectangle((0, -width/2), L1, width, 
                  angle=q1, rotation_point='xy',
                  facecolor='salmon', edgecolor='darkred', linewidth=2)

# Create second segment (green)
# We need to transform the rectangle for the second segment
t2 = transforms.Affine2D().rotate_deg(q1 + q2).translate(joint_x, joint_y) + ax.transData
rect2 = Rectangle((0, -width/2), L2, width,
                  transform=t2,
                  facecolor='lightgreen', edgecolor='darkgreen', linewidth=2)

# Add rectangles to plot
ax.add_patch(rect1)
ax.add_patch(rect2)

# Draw joint circle
joint_circle = plt.Circle((joint_x, joint_y), 0.15, color='black', zorder=5)
ax.add_patch(joint_circle)

# Draw origin circle
origin_circle = plt.Circle((0, 0), 0.15, color='black', zorder=5)
ax.add_patch(origin_circle)

# Draw dashed lines along segments
extend_ratio = 0.8
ext_x = (L1 + extend_ratio * L1) * np.cos(q1_rad)
ext_y = (L1 + extend_ratio * L1) * np.sin(q1_rad)
ax.plot([0, ext_x], [0, ext_y], 'k--', linewidth=1, alpha=0.5)
ax.plot([joint_x, end_x], [joint_y, end_y], 'k--', linewidth=1, alpha=0.5)

# Draw angle arcs
arc1_radius = 0.8
arc1 = mpatches.Arc((0, 0), 2*arc1_radius, 2*arc1_radius, 
                    angle=0, theta1=0, theta2=q1, 
                    linestyle='--', color='black', linewidth=1.5)
ax.add_patch(arc1)

arc2_radius = 0.6
arc2 = mpatches.Arc((joint_x, joint_y), 2*arc2_radius, 2*arc2_radius, 
                    angle=q1, theta1=0, theta2=q2, 
                    linestyle='--', color='black', linewidth=1.5)
ax.add_patch(arc2)

# Add angle labels
ax.text(0.9, 0.15, r'$q_1$', fontsize=14, fontweight='bold')
q2_label_r = arc2_radius + 0.25
q2_label_angle = q1 + q2/2
q2_label_x = joint_x + q2_label_r * np.cos(np.deg2rad(q2_label_angle))
q2_label_y = joint_y + q2_label_r * np.sin(np.deg2rad(q2_label_angle))
ax.text(q2_label_x, q2_label_y, r'$q_2$', fontsize=14, fontweight='bold')

# Add segment labels
mid1_x = (L1/2) * np.cos(q1_rad)
mid1_y = (L1/2) * np.sin(q1_rad)
ax.text(mid1_x-0.5, mid1_y + 0.3, 'Link 1', fontsize=13, color='darkred', ha='center', va='center', fontweight='bold')
mid2_x = joint_x + (L2/2) * np.cos(q1_rad + q2_rad)
mid2_y = joint_y + (L2/2) * np.sin(q1_rad + q2_rad)
ax.text(mid2_x-0.6, mid2_y + 0.3, 'Link 2', fontsize=13, color='darkgreen', ha='center', va='center', fontweight='bold')

# Add segment length labels
# a_1 label (for Link 1)
a1_label_x = (L1/2) * np.cos(q1_rad) + 0.1
a1_label_y = (L1/2) * np.sin(q1_rad) - 0.25
ax.text(a1_label_x, a1_label_y, r'$a_1$', fontsize=13, color='darkred', ha='center', va='center')

# a_2 label (for Link 2)
a2_label_x = joint_x + (L2/2) * np.cos(q1_rad + q2_rad) + 0.3
a2_label_y = joint_y + (L2/2) * np.sin(q1_rad + q2_rad)
ax.text(a2_label_x, a2_label_y, r'$a_2$', fontsize=13, color='darkgreen', ha='center', va='center')

# Draw coordinate axes
ax.arrow(-0.5, 0, 5.5, 0, head_width=0.1, head_length=0.1, fc='gray', ec='gray')
ax.arrow(0, -0.5, 0, 5, head_width=0.1, head_length=0.1, fc='gray', ec='gray')

# Add axis labels
ax.text(5.1, -0.2, 'x', fontsize=14, color='gray')
ax.text(-0.2, 4.7, 'y', fontsize=14, color='gray')

# Add end effector position label
ax.text(end_x-0.2, end_y + 0.3, r'Frame $F_2$', fontsize=12, 
        fontweight='bold', color='darkgreen',
        bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.7))

# Add base frame label near the origin
ax.text(-0.5, -0.5, r'Frame $F_0$', fontsize=12,
        fontweight='bold', color='black',
        bbox=dict(boxstyle="round,pad=0.3", facecolor='wheat', alpha=0.7))

# Add joint frame label near the joint
ax.text(joint_x + 0.1, joint_y - 0.5, r'Frame $F_1$', fontsize=12,
        fontweight='bold', color='black',
        bbox=dict(boxstyle="round,pad=0.3", facecolor='wheat', alpha=0.7))

# Set equal aspect ratio
ax.set_aspect('equal')

# Set axis limits
ax.set_xlim(-1.5, 6)
ax.set_ylim(-1.5, 6)

# Remove default axes
ax.set_xticks([])
ax.set_yticks([])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

# Add grid
ax.grid(True, alpha=0.3, linestyle='--')

# Remove the plot title (delete or comment out this line)
# plt.title('Two-Link Robotic Arm Configuration', fontsize=16, pad=20)

plt.tight_layout()
plt.savefig("images/2link-arm.png", dpi=300, bbox_inches='tight', pad_inches=0, facecolor='white')
plt.close()

# 用Pillow自动裁剪
im = Image.open("images/2link-arm.png").convert("RGB")
bg = Image.new("RGB", im.size, (255, 255, 255))
diff = ImageChops.difference(im, bg)
bbox = diff.getbbox()
if bbox:
    im_cropped = im.crop(bbox)
    im_cropped.save("images/2link-arm.png")