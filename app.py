import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt

# === Load model dan scaler ===
model = joblib.load(r"D:\dashboard_datascience\model\xgb_model.joblib")
scaler = joblib.load(r"D:\dashboard_datascience\model\scaler.joblib")
all_features = joblib.load(r"D:\dashboard_datascience\model\all_features.joblib")

# === Top fitur penting ===
important_features = [
    'Curricular_units_1st_sem_approved',
    'Curricular_units_2nd_sem_approved',
    'Curricular_units_1st_sem_enrolled',
    'Curricular_units_2nd_sem_enrolled',
    'Curricular_units_1st_sem_grade',
    'Curricular_units_2nd_sem_grade',
    'Tuition_fees_up_to_date',
    'Scholarship_holder',
    'Gender'
]

# === Max value numerik ===
max_values = {
    "Curricular_units_1st_sem_approved": 26,
    "Curricular_units_1st_sem_enrolled": 26,
    "Curricular_units_1st_sem_grade": 100,
    "Curricular_units_2nd_sem_approved": 23,
    "Curricular_units_2nd_sem_enrolled": 23,
    "Curricular_units_2nd_sem_grade": 100,
}

# === Label user-friendly ===
feature_labels = {
    "Curricular_units_1st_sem_approved": "Jumlah Mata kuliah semester 1 yang lulus",
    "Curricular_units_2nd_sem_approved": "Jumlah Mata kuliah semester 2 yang lulus",
    "Curricular_units_1st_sem_enrolled": "Jumlah Mata kuliah semester 1 yang diambil",
    "Curricular_units_2nd_sem_enrolled": "Jumlah Mata kuliah semester 2 yang diambil",
    "Curricular_units_1st_sem_grade": "Rata-Rata nilai akhir semester 1",
    "Curricular_units_2nd_sem_grade": "Rata-Rata nilai akhir semester 2",
    "Tuition_fees_up_to_date": "Status Pembayaran UKT",
    "Scholarship_holder": "Penerima beasiswa",
    "Gender": "Jenis kelamin"
}

# === Fitur kategorikal dan numerikal ===
categorical_input = ['Tuition_fees_up_to_date', 'Scholarship_holder', 'Gender']
numerical_input = [f for f in important_features if f not in categorical_input]
numerical_all = list(scaler.feature_names_in_)
categorical_all = [f for f in all_features if f not in numerical_all]

# === Label map dropdown kategorikal ===
label_maps = {
    "Tuition_fees_up_to_date": {1: "Sudah", 0: "Belum"},
    "Scholarship_holder": {1: "Ya", 0: "Tidak"},
    "Gender": {1: "Laki-laki", 0: "Perempuan"}
}

# === UI Header ===
st.set_page_config(page_title="Prediksi Status Mahasiswa", layout="centered")
st.title("Prediksi Status Mahasiswa")
st.markdown("Masukkan data akademik & demografis mahasiswa di sidebar untuk memprediksi status akhir mereka.")

# === Sidebar Input ===
st.sidebar.header("Formulir Input Mahasiswa")
user_inputs = {}

for feat in important_features:
    label = feature_labels.get(feat, feat.replace("_", " ").title())
    if feat in categorical_input:
        options = list(label_maps[feat].values())
        selected = st.sidebar.selectbox(label, options, key=feat)
        user_inputs[feat] = {v: k for k, v in label_maps[feat].items()}[selected]
    else:
        max_val = max_values.get(feat, 100)
        user_inputs[feat] = st.sidebar.number_input(
            label,
            min_value=0.0,
            max_value=float(max_val),
            step=1.0,
            value=0.0,
            key=feat
        )

# === Buat dataframe input ===
input_df = pd.DataFrame([{f: 0 for f in all_features}])
for feat in important_features:
    input_df.at[0, feat] = user_inputs[feat]

# === Scaling numerik ===
scaled_numerik = pd.DataFrame(scaler.transform(input_df[numerical_all]), columns=numerical_all)
for feat in categorical_all:
    scaled_numerik[feat] = input_df[feat]
final_input = scaled_numerik[all_features]

# === Prediksi otomatis ===
pred_proba = model.predict_proba(final_input)[0]
pred_class = np.argmax(pred_proba)
label_map = {0: "Dropout", 1: "Enrolled", 2: "Graduate"}
colors = {"Dropout": "#e74c3c", "Enrolled": "#f1c40f", "Graduate": "#2ecc71"}

# === Hasil Prediksi ===
st.subheader("Hasil Prediksi")
pred_label = label_map[pred_class]
st.markdown(
    f"<h2 style='color:{colors[pred_label]}'>{pred_label}</h2>",
    unsafe_allow_html=True
)

# === Grafik Probabilitas ===
st.subheader("Grafik Probabilitas")
fig, ax = plt.subplots()
bar_colors = [colors[label_map[i]] for i in range(3)]
ax.bar(label_map.values(), pred_proba, color=bar_colors)
ax.set_ylabel("Probabilitas")
ax.set_ylim(0, 1.05)
ax.set_title("Prediksi Status Mahasiswa", fontsize=12)

for i, v in enumerate(pred_proba):
    ax.text(i, v + 0.02, f"{v:.2f}", ha='center', fontsize=10)

st.pyplot(fig)







