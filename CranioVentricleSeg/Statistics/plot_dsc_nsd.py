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

# median values
dsc = np.array([0.94, 0.94, 0.84, 0.82, 0.00, 0.93])
nsd = np.array([0.99, 0.99, 0.97, 0.96, 0.00, 0.99])

# IQR (lower, upper → omzetten naar error bars)
dsc_lower = np.array([0.89, 0.89, 0.71, 0.74, 0.00, 0.89])
dsc_upper = np.array([0.97, 0.97, 0.86, 0.86, 0.47, 0.96])

nsd_lower = np.array([0.97, 0.96, 0.90, 0.94, 0.00, 0.97])
nsd_upper = np.array([1.00, 1.00, 0.99, 0.99, 0.72, 0.99])

# error bars 
dsc_err = [dsc - dsc_lower, dsc_upper - dsc]
nsd_err = [nsd - nsd_lower, nsd_upper - nsd]

x = np.arange(len(structures))

# plot
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=False)

# DSC
axes[0].bar(x, dsc, yerr=dsc_err, capsize=4)
axes[0].set_title("DSC (T2, v2.0)")
axes[0].set_xticks(x)
axes[0].set_xticklabels(structures, rotation=45, ha='right')
axes[0].set_ylabel("Score")
axes[0].set_ylim(0, 1.05)

# NSD
axes[1].bar(x, nsd, yerr=nsd_err, capsize=4)
axes[1].set_title("NSD (T2, v2.0)")
axes[1].set_xticks(x)
axes[1].set_xticklabels(structures, rotation=45, ha='right')
axes[1].set_ylim(0, 1.05)

plt.tight_layout()
plt.savefig("dsc_nsd_plot.png", dpi=300, bbox_inches='tight')
