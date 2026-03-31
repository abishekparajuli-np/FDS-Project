import pandas as pd
import numpy as np
from crossreferenceengine import CrossReferenceEngine
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# Initialize engine
print("[*] Initializing CrossReferenceEngine...")
engine = CrossReferenceEngine()
print("[OK] Engine ready\n")

# Load CSV files
print("[*] Loading news from CSV files...")
try:
    false_news = pd.read_csv("false.csv", on_bad_lines='skip')
    false_news = false_news[['title', 'text']].dropna()
    false_news = false_news[(false_news['title'].str.len() > 0) & (false_news['text'].str.len() > 0)]
    print(f"[OK] Loaded {len(false_news)} FAKE news articles")
except Exception as e:
    print(f"[!] Error: {e}")
    false_news = pd.DataFrame()

try:
    true_news = pd.read_csv("true.csv", on_bad_lines='skip')
    if 'text' not in true_news.columns and 'content' in true_news.columns:
        true_news['text'] = true_news['content']
    true_news = true_news[['title', 'text']].dropna()
    true_news = true_news[(true_news['title'].str.len() > 0) & (true_news['text'].str.len() > 0)]
    print(f"[OK] Loaded {len(true_news)} REAL news articles\n")
except Exception as e:
    print(f"[!] Error: {e}")
    true_news = pd.DataFrame()

# Sample if needed
SAMPLE_SIZE = 20 # Increased for better accuracy testing
CLASSIFICATION_THRESHOLD = 0.62  # Adjust this to change fake/real detection threshold (higher = stricter on REAL)if SAMPLE_SIZE and len(false_news) > SAMPLE_SIZE:
false_news = false_news.sample(n=SAMPLE_SIZE, random_state=42)
if SAMPLE_SIZE and len(true_news) > SAMPLE_SIZE:
    true_news = true_news.sample(n=SAMPLE_SIZE, random_state=42)

print(f"[*] Analyzing {len(true_news)} REAL + {len(false_news)} FAKE articles\n")

# Analyze articles
predictions = []
actual_labels = []

# Analyze fake news
print("=" * 70)
print("ANALYZING FAKE NEWS")
print("=" * 70)
for i, (idx, row) in enumerate(false_news.iterrows(), 1):
    title = str(row['title']).strip()
    text = str(row['text']).strip()
    
    if not title or not text:
        continue
    
    print(f"\n[{i}] {title[:60]}...")
    result = engine.analyze(title=title, content=text)
    verdict = result['verdict']
    score = result['final_score']
    print(f"    Score: {score:.4f} | Verdict: {verdict}")
    
    # Convert score to prediction using threshold (score >= threshold = REAL)
    prediction = 1 if score >= CLASSIFICATION_THRESHOLD else 0
    predictions.append(prediction)
    actual_labels.append(0)  # 0 = FAKE

# Analyze real news
print("\n" + "=" * 70)
print("ANALYZING REAL NEWS")
print("=" * 70)
for i, (idx, row) in enumerate(true_news.iterrows(), 1):
    title = str(row['title']).strip()
    text = str(row['text']).strip()
    
    if not title or not text:
        continue
    
    print(f"\n[{i}] {title[:60]}...")
    result = engine.analyze(title=title, content=text)
    verdict = result['verdict']
    score = result['final_score']
    print(f"    Score: {score:.4f} | Verdict: {verdict}")
    
    # Convert score to prediction using threshold (score >= threshold = REAL)
    prediction = 1 if score >= CLASSIFICATION_THRESHOLD else 0
    predictions.append(prediction)
    actual_labels.append(1)  # 1 = REAL

# Calculate accuracy
print("\n" + "=" * 70)
print("ACCURACY RESULTS")
print("=" * 70)

y_true = np.array(actual_labels)
y_pred = np.array(predictions)

accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred, zero_division=0)
recall = recall_score(y_true, y_pred, zero_division=0)
f1 = f1_score(y_true, y_pred, zero_division=0)
cm = confusion_matrix(y_true, y_pred)

print(f"\nAccuracy:  {accuracy*100:.2f}%")
print(f"Precision: {precision*100:.2f}%")
print(f"Recall:    {recall*100:.2f}%")
print(f"F1-Score:  {f1:.4f}")

print(f"\nConfusion Matrix:")
print(f"                 Predicted FAKE  Predicted REAL")
print(f"Actual FAKE:     {cm[0, 0]:3d}              {cm[0, 1]:3d}")
print(f"Actual REAL:     {cm[1, 0]:3d}              {cm[1, 1]:3d}")

print(f"\n[COMPLETE]")
print(f"\n[COMPLETE]")