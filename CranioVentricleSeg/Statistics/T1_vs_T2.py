import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import wilcoxon

# load data
file_path = "/data/scratch/r116411/data/final_segmentation_metrics_cluster_bootstrap.xlsx"
output_path = "/trinity/home/r116411/repositories/TM2_ventrikels_inference/CranioVentricleSeg/metric_evaluation/paired_statistics_T1vsT2.xlsx"

t1 = pd.read_excel(file_path, sheet_name="T1_v2.0_metrics")
t2 = pd.read_excel(file_path, sheet_name="v2.0_metrics")

# rename columns 
t2 = t2.rename(columns={
    "case": "case",
    "dice_RV": "RV_dice",
    "dice_3V": "3V_dice",
    "dice_4V": "4V_dice",
    "dice_CSP": "CSP_dice",
    "dice_LV": "LV_dice",
    "dice_TOTAL": "TOTAL_dice"
})

t1 = t1.rename(columns={
    "Name": "case",
    "Right ventricle": "RV_dice",
    "Third ventricle": "3V_dice",
    "Fourth ventricle": "4V_dice",
    "CSP": "CSP_dice",
    "Left ventricle": "LV_dice",
    "Total ventricles": "TOTAL_dice"
})

cols = ["case", "RV_dice", "3V_dice", "4V_dice", "CSP_dice", "LV_dice", "TOTAL_dice"]

t1 = t1[cols]
t2 = t2[cols]

# fix duplicaten (folds)
t1 = t1.groupby("case").mean().reset_index()
t2 = t2.groupby("case").mean().reset_index()

# merge overlap
merged = pd.merge(t1, t2, on="case", suffixes=("_T1", "_T2"))

print("aantal unieke cases:", len(merged))

metrics = ["RV_dice", "3V_dice", "4V_dice", "CSP_dice", "LV_dice", "TOTAL_dice"]

results = []

for m in metrics:

    x = merged[f"{m}_T1"]
    y = merged[f"{m}_T2"]

    # drop NaNs
    mask = ~(x.isna() | y.isna())
    x = x[mask]
    y = y[mask]

    if len(x) == 0:
        p = np.nan
        ci_low = np.nan
        ci_high = np.nan
        diff_mean = np.nan
        mean_t1 = np.nan
        mean_t2 = np.nan
    else:
        # wilcoxon
        if np.all(x == y):
            p = 1.0
        else:
            stat, p = wilcoxon(x, y, zero_method="wilcox")

        # verschil
        diff = y - x
        diff_mean = diff.mean()

        # ci
        ci_low = np.percentile(diff, 2.5)
        ci_high = np.percentile(diff, 97.5)

        # median
        import pandas as pd
import numpy as np
from scipy.stats import wilcoxon

# load data
file_path = "/data/scratch/r116411/data/final_segmentation_metrics_cluster_bootstrap.xlsx"
output_path = "/trinity/home/r116411/repositories/TM2_ventrikels_inference/CranioVentricleSeg/metric_evaluation/paired_statistics_T1vsT2.xlsx"

t1 = pd.read_excel(file_path, sheet_name="T1_v2.0_metrics")
t2 = pd.read_excel(file_path, sheet_name="v2.0_metrics")

# rename columns 
t2 = t2.rename(columns={
    "case": "case",
    "dice_RV": "RV_dice",
    "dice_3V": "3V_dice",
    "dice_4V": "4V_dice",
    "dice_CSP": "CSP_dice",
    "dice_LV": "LV_dice",
    "dice_TOTAL": "TOTAL_dice"
})

t1 = t1.rename(columns={
    "Name": "case",
    "Right ventricle": "RV_dice",
    "Third ventricle": "3V_dice",
    "Fourth ventricle": "4V_dice",
    "CSP": "CSP_dice",
    "Left ventricle": "LV_dice",
    "Total ventricles": "TOTAL_dice"
})

cols = ["case", "RV_dice", "3V_dice", "4V_dice", "CSP_dice", "LV_dice", "TOTAL_dice"]

t1 = t1[cols]
t2 = t2[cols]

# fix duplicaten (folds)
median_t1 = np.median(x)
median_t2 = np.median(y)

ci1_low = np.percentile(x, 2.5)
ci1_high = np.percentile(x, 97.5)

ci2_low = np.percentile(y, 2.5)
ci2_high = np.percentile(y, 97.5)

# merge overlap
merged = pd.merge(t1, t2, on="case", suffixes=("_T1", "_T2"))

print("aantal unieke cases:", len(merged))

metrics = ["RV_dice", "3V_dice", "4V_dice", "CSP_dice", "LV_dice", "TOTAL_dice"]

results = []

for m in metrics:

    x = merged[f"{m}_T1"]
    y = merged[f"{m}_T2"]

    # drop NaNs
    mask = ~(x.isna() | y.isna())
    x = x[mask]
    y = y[mask]

    if len(x) == 0:
        p = np.nan
        ci_low = np.nan
        ci_high = np.nan
        diff_mean = np.nan
        median_t1 = np.nan
        median_t2 = np.nan
    else:
        # wilcoxon
        if np.all(x == y):
            p = 1.0
        else:
            stat, p = wilcoxon(x, y, zero_method="wilcox")

        # difference
        diff = y - x
        diff_mean = diff.mean()

        # median + CI per model
        median_t1 = np.median(x)
        ci1_low = np.percentile(x, 2.5)
        ci1_high = np.percentile(x, 97.5)

        median_t2 = np.median(y)
        ci2_low = np.percentile(y, 2.5)
        ci2_high = np.percentile(y, 97.5)

    results.append({
        "metric": m,
        "T1": f"{median_t1:.2f} ({ci1_low:.2f}-{ci1_high:.2f})",
        "T2": f"{median_t2:.2f} ({ci2_low:.2f}-{ci2_high:.2f})",
        "p_value": p
    })

# output
df_results = pd.DataFrame(results)

print("\nresultaten:")
print(df_results)

df_results.to_excel(output_path, index=False)

print("\nopgeslagen naar:", output_path)




## PLOTS
# ---------- paired plot (TOTAL Dice)

x = merged["TOTAL_dice_T1"]
y = merged["TOTAL_dice_T2"]

plt.figure(figsize=(5,6))

# lijnen (patients)
for i in range(len(x)):
    plt.plot([1,2], [x.iloc[i], y.iloc[i]],
             color="gray", alpha=0.5)

# punten
plt.scatter([1]*len(x), x, color="blue", label="T1", s=20)
plt.scatter([2]*len(y), y, color="orange", label="T2", s=20)

# median
plt.scatter(1, x.median(), color="blue", s=100, edgecolor="black")
plt.scatter(2, y.median(), color="orange", s=100, edgecolor="black")

plt.xticks([1,2], ["T1", "T2"])
plt.ylabel("Dice coefficient")
plt.title("Paired comparison of the total dice")

plt.legend()
plt.tight_layout()
plt.show()


# ---------- Box  plot (all labels)


metrics = ["RV_dice", "3V_dice", "4V_dice", "CSP_dice", "LV_dice", "TOTAL_dice"]

plot_data = []

for m in metrics:
    for i in range(len(merged)):
        plot_data.append({
            "Dice": merged[f"{m}_T1"].iloc[i],
            "Model": "T1",
            "Structure": m.replace("_dice", "")
        })
        plot_data.append({
            "Dice": merged[f"{m}_T2"].iloc[i],
            "Model": "T2",
            "Structure": m.replace("_dice", "")
        })

df_plot = pd.DataFrame(plot_data)

order = ["RV", "LV", "3V", "4V", "CSP", "TOTAL"]

plt.figure(figsize=(11,6))

sns.boxplot(
    data=df_plot,
    x="Ventricle",
    y="Dice",
    hue="Model",
    order=order
)

# datapoints 
sns.stripplot(
    data=df_plot,
    x="Ventricle",
    y="Dice",
    hue="Model",
    order=order,
    dodge=True,
    alpha=0.35,
    color="black"
)

plt.title("Segmentation performance per ventricle, T1 vs T2")
plt.ylabel("Dice coefficient")

# Legend
handles, labels = plt.gca().get_legend_handles_labels()
plt.legend(handles[:2], labels[:2], title="Model")

plt.tight_layout()
plt.savefig("boxplot.png", dpi=300)
plt.show()