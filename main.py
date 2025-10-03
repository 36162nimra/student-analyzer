from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Subjects to analyze
SUBJECTS = ['math score', 'reading score', 'writing score']

# ---------------- Load CSV ----------------
def load_data():
    """Load default CSV from data folder"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, 'data', 'StudentsPerformance.csv')
    df = pd.read_csv(csv_path)
    
    # Ensure 'Student' column exists
    if 'Student' not in df.columns:
        df.insert(0, 'Student', ['Student_' + str(i+1) for i in range(len(df))])
    return df

# ---------------- Compute statistics ----------------
def compute_stats(df):
    numeric = df[SUBJECTS]
    mean = numeric.mean().to_dict()
    median = numeric.median().to_dict()
    mode_df = numeric.mode()
    mode = mode_df.iloc[0].to_dict() if not mode_df.empty else {sub: None for sub in SUBJECTS}
    std = numeric.std().to_dict()
    return mean, median, mode, std

# ---------------- Top students ----------------
def top_students(df, subject='math score', n=5):
    return df.nlargest(n, subject)

# ---------------- Subjects needing improvement ----------------
def subjects_to_improve(df):
    mean = df[SUBJECTS].mean()
    overall = mean.mean()
    needs = mean[mean < overall].sort_values()
    return needs.to_dict()

# ---------------- Save charts ----------------
def save_charts(df):
    os.makedirs('static', exist_ok=True)

    # Histogram of math scores
    plt.figure(figsize=(8,5))
    plt.hist(df['math score'], bins=10, edgecolor='black', color='#3498db')
    plt.title("Math Score Distribution")
    plt.xlabel("Score")
    plt.ylabel("Number of Students")
    math_img = 'math_scores.png'
    plt.savefig(os.path.join('static', math_img))
    plt.close()

    # Bar chart of mean scores
    means = df[SUBJECTS].mean()
    plt.figure(figsize=(6,4))
    means.plot(kind='bar', color=['#e74c3c','#2ecc71','#f1c40f'])
    plt.title("Mean Score by Subject")
    plt.ylabel("Average Score")
    plt.ylim(0,100)
    mean_img = 'mean_scores.png'
    plt.savefig(os.path.join('static', mean_img))
    plt.close()

    return math_img, mean_img

# ---------------- Flask route ----------------
@app.route('/')
def index():
    df = load_data()
    mean, median, mode, std = compute_stats(df)
    top = top_students(df).to_dict(orient='records')
    needs = subjects_to_improve(df)
    math_img, mean_img = save_charts(df)

    return render_template('index.html',
                           mean=mean, median=median, mode=mode, std=std,
                           top=top, needs=needs,
                           math_img=math_img, mean_img=mean_img)

# ---------------- Run app ----------------
if __name__ == '__main__':
    app.run(debug=True)
