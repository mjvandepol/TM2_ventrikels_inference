# This file does the statistical comparison of model T1 vs T2 on dice score, using Wilcoxon paired test
# Dice scores are calculated on the test set (n=25). Patient-level aggregation is done using the median
# Boxplot is generated automatically


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import wilcoxon


# ----------------------- Bootstrap CI
def bootstrap_ci_cluster(df, value_col, patient_col="patient", n_boot=1000):

    patients = df[patient_col].unique()
    medians = []

    for _ in range(n_boot):

        sampled_patients = np.random.choice(
            patients,
            size=len(patients),
            replace=True
        )

        sampled_df = pd.concat([
            df[df[patient_col] == p] for p in sampled_patients
        ])

        medians.append(sampled_df[value_col].median())

    return (
        np.percentile(medians, 2.5),
        np.percentile(medians, 97.5)
    )


# ----------------------- Load data
file_path = r"C:\Users\manon\iCloudDrive\Bestanden\TM Master\TM stage\TM3 EMC ventricles\TM2_ventrikels_inference-1\CranioVentricleSeg\Statistics&images\final_segmentation_metrics_cluster_bootstrap.xlsx"

t1 = pd.read_excel(file_path, sheet_name="T1_v2.0_metrics")
t2 = pd.read_excel(file_path, sheet_name="v2.0_metrics")


# ----------------------- Standardize column names
t2 = t2.rename(columns={
    "case": "case",
    "dice_RV": "RV",
    "dice_3V": "3V",
    "dice_4V": "4V",
    "dice_CSP": "CSP",
    "dice_LV": "LV",
    "dice_TOTAL": "TOTAL"
})

t1 = t1.rename(columns={
    "Name": "case",
    "Right ventricle": "RV",
    "Third ventricle": "3V",
    "Fourth ventricle": "4V",
    "CSP": "CSP",
    "Left ventricle": "LV",
    "Total ventricles": "TOTAL"
})


cols = ["case", "RV", "LV", "3V", "4V", "CSP", "TOTAL"]

t1 = t1[cols]
t2 = t2[cols]


# ----------------------- Keep only real cases
t1 = t1[t1["case"].str.match(r"^(C|M)_\d+", na=False)]
t2 = t2[t2["case"].str.match(r"^(C|M)_\d+", na=False)]


# ----------------------- Create patient ID
t1["patient"] = t1["case"].str.extract(r"(C_\d+|M_\d+)")
t2["patient"] = t2["case"].str.extract(r"(C_\d+|M_\d+)")


# ----------------------- Debug
print("\nBefore aggregation:")
print("T1 scans:", len(t1), "| unique patients:", t1["patient"].nunique())
print("T2 scans:", len(t2), "| unique patients:", t2["patient"].nunique())


# ----------------------- Aggregate per patient using median
t1_patient = t1.groupby("patient").median(numeric_only=True).reset_index()
t2_patient = t2.groupby("patient").median(numeric_only=True).reset_index()


print("\nAfter aggregation (patient-level):")
print("T1 patients:", len(t1_patient))
print("T2 patients:", len(t2_patient))


# ----------------------- Keep overlapping patients
merged = pd.merge(
    t1_patient,
    t2_patient,
    on="patient",
    suffixes=("_T1", "_T2")
)

print("\nAfter merge (overlapping patients):")
print("Number of patients used in analysis:", len(merged))


# ----------------------- Statistical comparison
structures = ["RV", "LV", "3V", "4V", "CSP", "TOTAL"]

results = []
p_values = {}

for s in structures:

    x = merged[f"{s}_T1"]
    y = merged[f"{s}_T2"]

    mask = ~(x.isna() | y.isna())

    x = x[mask]
    y = y[mask]

    patients_used = merged.loc[mask, "patient"]

    temp_t1 = pd.DataFrame({
        "patient": patients_used,
        "value": x
    })

    temp_t2 = pd.DataFrame({
        "patient": patients_used,
        "value": y
    })

    if len(x) > 0:
        stat, p = wilcoxon(x, y, zero_method="wilcox")
    else:
        p = np.nan

    # Bootstrap CI
    t1_ci_low, t1_ci_high = bootstrap_ci_cluster(
        temp_t1,
        value_col="value"
    )

    t2_ci_low, t2_ci_high = bootstrap_ci_cluster(
        temp_t2,
        value_col="value"
    )

    results.append({

        "Ventricle": s,

        "Median T1": np.median(x),
        "T1 CI low": t1_ci_low,
        "T1 CI high": t1_ci_high,

        "Median T2": np.median(y),
        "T2 CI low": t2_ci_low,
        "T2 CI high": t2_ci_high,

        "p-value": p
    })

    p_values[s] = p


df_results = pd.DataFrame(results)

print("\nStatistical results:")
print(df_results)


# ----------------------- Save Excel
output_path = r"C:\Users\manon\iCloudDrive\Bestanden\TM Master\TM stage\TM3 EMC ventricles\TM2_ventrikels_inference-1\CranioVentricleSeg\Statistics&images\paired_statistics_T1vsT2.xlsx"

df_results.to_excel(output_path, index=False)

print(f"\nExcel saved to:\n{output_path}")


# ----------------------- Format p-values
def format_p(p):
    if np.isnan(p):
        return "n/a"
    elif p < 0.001:
        return "p < 0.001"
    else:
        return f"p = {p:.3f}"


# ----------------------- Prepare plot data
plot_data = []

name_map = {
    "RV": "Right ventricle",
    "LV": "Left ventricle",
    "3V": "3rd ventricle",
    "4V": "4th ventricle",
    "CSP": "CSP",
    "TOTAL": "Total"
}

order = ["RV", "LV", "3V", "4V", "CSP", "TOTAL"]

for s in order:
    for i in range(len(merged)):

        plot_data.append({
            "Dice": merged[f"{s}_T1"].iloc[i],
            "Model": "T1",
            "Ventricle": name_map[s]
        })

        plot_data.append({
            "Dice": merged[f"{s}_T2"].iloc[i],
            "Model": "T2",
            "Ventricle": name_map[s]
        })

df_plot = pd.DataFrame(plot_data)
df_plot = df_plot.dropna()


# ----------------------- Boxplot
plt.figure(figsize=(10,6))
sns.set(style="whitegrid")

sns.boxplot(
    data=df_plot,
    x="Ventricle",
    y="Dice",
    hue="Model",
    order=[name_map[s] for s in order]
)

sns.stripplot(
    data=df_plot,
    x="Ventricle",
    y="Dice",
    hue="Model",
    dodge=True,
    alpha=0.35,
    color="black"
)

ax = plt.gca()

for i, s in enumerate(order):

    p = p_values.get(s, np.nan)

    subset = df_plot[df_plot["Ventricle"] == name_map[s]]
    y_max = subset["Dice"].max()

    y_pos = min(1.02, y_max + 0.05)

    ax.text(
        i,
        y_pos,
        format_p(p),
        ha='center',
        va='bottom',
        fontsize=10
    )

handles, labels = plt.gca().get_legend_handles_labels()
plt.legend(handles[:2], labels[:2], title="Model")

plt.ylabel("Dice coefficient")
plt.ylim(0,1.05)
plt.title("Segmentation performance per ventricle (patient-level)")

plt.tight_layout()

plt.savefig(
    r"C:\Users\manon\iCloudDrive\Bestanden\TM Master\TM stage\TM3 EMC ventricles\TM2_ventrikels_inference-1\CranioVentricleSeg\Statistics&images\boxplot_T1vsT2.png",
    dpi=300
)

plt.show()