# Generate a file to plot the dsc and nsd for T2 - data from Fold_metrics_segmentation.py 5-5 17:30

import matplotlib.pyplot as plt
import numpy as np

# labels
structures = [
    "Right ventricle",
    "Left ventricle",
    "3rd ventricle",
    "4th ventricle",
    "CSP",
    "Total"
]

x = np.arange(len(structures))

# median values
dsc = np.array([0.94, 0.94, 0.84, 0.82, 0.00, 0.93])
nsd = np.array([0.99, 0.99, 0.97, 0.96, 0.00, 0.99])

# IQR bounds
dsc_lower = np.array([0.89, 0.89, 0.71, 0.74, 0.00, 0.89])
dsc_upper = np.array([0.97, 0.97, 0.86, 0.86, 0.47, 0.96])

nsd_lower = np.array([0.97, 0.96, 0.90, 0.94, 0.00, 0.97])
nsd_upper = np.array([1.00, 1.00, 0.99, 0.99, 0.72, 0.99])

# kleuren (CSP grijs)
colors = ['black'] * len(structures)
colors[4] = 'lightgray'

# plot
fig, axes = plt.subplots(1, 2, figsize=(11, 4))

for i in range(len(structures)):
    # DSC
    axes[0].plot([i, i], [dsc_lower[i], dsc_upper[i]], color=colors[i], linewidth=2)
    axes[0].plot(i, dsc[i], marker='_', color=colors[i], markersize=12)

    # NSD
    axes[1].plot([i, i], [nsd_lower[i], nsd_upper[i]], color=colors[i], linewidth=2)
    axes[1].plot(i, nsd[i], marker='_', color=colors[i], markersize=12)

# styling
for ax, title in zip(axes, ["DSC (T2, v2.0)", "NSD (T2, v2.0)"]):
    ax.set_xticks(x)
    ax.set_xticklabels(structures, rotation=45, ha='right')
    ax.set_ylim(0, 1.05)
    ax.set_title(title)
    ax.set_ylabel("Score")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

plt.tight_layout()

# save 
plt.savefig("T2_v2_dsc_nsd_clean.png", dpi=300, bbox_inches='tight')

plt.close()