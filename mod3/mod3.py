# --- IMPORT LIBRARIES ---
import pandas as pd
import numpy as np
import re 
from textblob import TextBlob
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity

# --- LOAD DATA ---
# Replace with your filename
df = pd.read_csv("stock_tweets.csv")

# --- DATA PREPROCESSING ---
# Ensure Date is datetime type for proper sorting
df['Date'] = pd.to_datetime(df['Date'])

# --- SENTIMENT ANALYSIS ---
df['sentiment'] = df['Tweet'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)

# --- SORT & PREPARE FOR PRICE CHANGE CALCULATION ---
df = df.sort_values(by=['Stock', 'Date'])

# --- COMPUTE DAILY PRICE CHANGE PERCENTAGE ---
df['Price_Change_%'] = df.groupby('Stock')['Price'].pct_change() * 100

# Drop first rows per stock that have NaN in Price_Change_%
df = df.dropna(subset=['Price_Change_%'])

# --- DEFINE PRICE MOVEMENT DIRECTION ---
def label_movement(x):
    if x > 0:
        return 'Rise'
    elif x < 0:
        return 'Decline'
    else:
        return 'No Change'

df['Movement'] = df['Price_Change_%'].apply(label_movement)

# --- CLEAN TEXT FUNCTION ---
def clean_tweet(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+', '', text)  # remove links
    text = re.sub(r'[^a-z\s]', '', text)        # remove punctuation/numbers
    text = re.sub(r'\s+', ' ', text).strip()    # remove extra whitespace
    return text

df['Clean_Tweet'] = df['Tweet'].apply(clean_tweet)

# --- TOKENIZE AND COUNT WORDS ---
# Separate positive & negative tweets
positive_tweets = df[df['sentiment'] > 0]['Clean_Tweet']
negative_tweets = df[df['sentiment'] < 0]['Clean_Tweet']

# Get top words
positive_words = " ".join(positive_tweets).split()
negative_words = " ".join(negative_tweets).split()

top10_positive = Counter(positive_words).most_common(10)
top10_negative = Counter(negative_words).most_common(10)

# Convert to DataFrames for easy plotting
pos_df = pd.DataFrame(top10_positive, columns=['Word', 'Count'])
neg_df = pd.DataFrame(top10_negative, columns=['Word', 'Count'])

# --- NORMALIZATION ---
scaler = MinMaxScaler()
df[['Sentiment_norm', 'PriceChange_norm']] = scaler.fit_transform(df[['sentiment', 'Price_Change_%']])

# --- CLUSTERING TO FIND PATTERNS ---
X = df[['Sentiment_norm', 'PriceChange_norm']]
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(X)

# --- VISUALIZATION 1: SENTIMENT VS PRICE CHANGE ---
plt.figure(figsize=(8,6))
sns.scatterplot(
    data=df, x='sentiment', y='Price_Change_%', hue='Movement',
    palette={'Rise':'green', 'Decline':'red', 'No Change':'gray'}
)
plt.title("Tweet Sentiment vs Stock Price Change (%)")
plt.xlabel("Tweet Sentiment (−1 = Negative, +1 = Positive)")
plt.ylabel("Daily Price Change (%)")
plt.axvline(0, color='black', linestyle='--')
plt.axhline(0, color='black', linestyle='--')
plt.show()

# --- VISUALIZATION 2: CLUSTER PATTERNS ---
plt.figure(figsize=(8,6))
sns.scatterplot(
    data=df, x='Sentiment_norm', y='PriceChange_norm', hue='Cluster', palette='viridis'
)
plt.title("KMeans Clustering: Sentiment vs Price Change")
plt.xlabel("Normalized Sentiment")
plt.ylabel("Normalized Price Change")
plt.show()

# --- CORRELATION ANALYSIS ---
corr = df['sentiment'].corr(df['Price_Change_%'])
print(f"Correlation between Tweet Sentiment and Price Change: {corr:.3f}")

# --- SUMMARY TABLE ---
summary = df.groupby('Movement')[['sentiment', 'Price_Change_%']].mean().reset_index()
print("\nAverage Sentiment and Price Change by Movement:")
print(summary)

# --- COSINE SIMILARITY ANALYSIS FOR TOP 10 MOST SIMILAR TWEETS ---
# Extract the normalized features used for clustering
features = df[['Sentiment_norm', 'PriceChange_norm']].values

# Compute pairwise cosine similarity (1 = identical, 0 = orthogonal)
cosine_sim_matrix = cosine_similarity(features)

# Function: get top 10 most similar tweets for a given tweet index
def get_top_similar_cosine(index, top_n=10):
    # Reset index to ensure proper integer indexing
    df_reset = df.reset_index(drop=True)
    sims = cosine_sim_matrix[index]
    top_indices = np.argsort(sims)[::-1][1:top_n+1]  # sort descending, skip itself
    result = df_reset.iloc[top_indices][['Tweet', 'Stock', 'sentiment', 'Price_Change_%', 'Cluster', 'Sentiment_norm', 'PriceChange_norm']].copy()
    result['Cosine_Similarity'] = sims[top_indices]
    return result

# Choose a random query tweet to analyze
query_idx = np.random.choice(len(df))
query_tweet = df.iloc[query_idx]
similar_cosine_df = get_top_similar_cosine(query_idx)

print(f"\n--- Query Tweet ---")
print(query_tweet[['Tweet', 'Stock', 'sentiment', 'Price_Change_%', 'Cluster']])

print("\nTop 10 Most Similar Tweets (by Cosine Similarity):")
print(similar_cosine_df)

# --- VISUALIZE COSINE SIMILARITY RELATIONSHIPS ---
plt.figure(figsize=(9,7))

# Background: all tweets
sns.scatterplot(
    data=df, x='Sentiment_norm', y='PriceChange_norm',
    color='lightgray', alpha=0.5, label='All Data'
)

# Highlight top 10 cosine-similar tweets
sns.scatterplot(
    data=similar_cosine_df, x='Sentiment_norm', y='PriceChange_norm',
    color='blue', s=70, label='Top 10 Cosine-Similar'
)

# Highlight query tweet
query_point = pd.DataFrame([{
    'Sentiment_norm': query_tweet['Sentiment_norm'], 
    'PriceChange_norm': query_tweet['PriceChange_norm']
}])
sns.scatterplot(
    data=query_point, x='Sentiment_norm', y='PriceChange_norm',
    color='red', s=120, label='Query Tweet'
)

plt.title("Top 10 Most Similar Tweets (Cosine Similarity)", fontsize=14)
plt.xlabel("Normalized Sentiment")
plt.ylabel("Normalized Price Change")
plt.legend()
plt.show()

# --- ADDITIONAL VISUALIZATION: TOP WORDS ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

# Positive words
sns.barplot(data=pos_df, x='Count', y='Word', ax=ax1, palette='Greens_r')
ax1.set_title('Top 10 Words in Positive Sentiment Tweets')
ax1.set_xlabel('Frequency')

# Negative words
sns.barplot(data=neg_df, x='Count', y='Word', ax=ax2, palette='Reds_r')
ax2.set_title('Top 10 Words in Negative Sentiment Tweets')
ax2.set_xlabel('Frequency')

plt.tight_layout()
plt.show()
