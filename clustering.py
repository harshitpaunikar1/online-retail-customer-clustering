"""
Online retail customer clustering using K-Means and DBSCAN.
Segments customers by purchase behavior for targeted marketing strategies.
"""
import warnings
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

try:
    from sklearn.cluster import DBSCAN, KMeans
    from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score, silhouette_score
    from sklearn.preprocessing import RobustScaler, StandardScaler
    from sklearn.decomposition import PCA
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class CustomerFeatureBuilder:
    """
    Builds customer-level behavioral features from transaction records.
    Computes RFM, basket size, category diversity, and return rate.
    """

    def build(self, transactions: pd.DataFrame,
              customer_col: str = "customer_id",
              date_col: str = "invoice_date",
              amount_col: str = "total_amount",
              quantity_col: str = "quantity",
              product_col: Optional[str] = "product_category") -> pd.DataFrame:
        df = transactions.copy()
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        snapshot = df[date_col].max()

        rfm = df.groupby(customer_col).agg(
            recency_days=(date_col, lambda x: (snapshot - x.max()).days),
            frequency=(date_col, "count"),
            monetary=(amount_col, "sum"),
            avg_basket=(amount_col, "mean"),
            avg_quantity=(quantity_col, "mean") if quantity_col in df.columns else (amount_col, "mean"),
        ).reset_index()

        if product_col and product_col in df.columns:
            diversity = df.groupby(customer_col)[product_col].nunique().reset_index()
            diversity.columns = [customer_col, "category_diversity"]
            rfm = rfm.merge(diversity, on=customer_col, how="left")

        rfm["monetary"] = rfm["monetary"].clip(lower=0)
        return rfm


class CustomerClusterer:
    """
    Clusters customers using K-Means with automatic k selection via silhouette score.
    Also supports DBSCAN for density-based outlier detection.
    """

    def __init__(self, max_k: int = 10, random_state: int = 42):
        self.max_k = max_k
        self.random_state = random_state
        self.scaler = None
        self.best_k: Optional[int] = None
        self.kmeans_model = None
        self._feature_cols: List[str] = []

    def _scale(self, X: np.ndarray) -> np.ndarray:
        self.scaler = RobustScaler()
        return self.scaler.fit_transform(X)

    def select_best_k(self, X_scaled: np.ndarray,
                       k_range: Optional[range] = None) -> pd.DataFrame:
        """Try k from 2 to max_k, return silhouette and Davies-Bouldin scores."""
        if k_range is None:
            k_range = range(2, min(self.max_k + 1, len(X_scaled)))
        records = []
        for k in k_range:
            km = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
            labels = km.fit_predict(X_scaled)
            sil = float(silhouette_score(X_scaled, labels))
            db = float(davies_bouldin_score(X_scaled, labels))
            ch = float(calinski_harabasz_score(X_scaled, labels))
            records.append({"k": k, "silhouette": round(sil, 4),
                            "davies_bouldin": round(db, 4),
                            "calinski_harabasz": round(ch, 1)})
        return pd.DataFrame(records)

    def fit_kmeans(self, df: pd.DataFrame, feature_cols: List[str]) -> np.ndarray:
        """Fit K-Means with optimal k and return cluster labels."""
        if not SKLEARN_AVAILABLE:
            raise RuntimeError("scikit-learn required.")
        self._feature_cols = feature_cols
        X = df[feature_cols].fillna(df[feature_cols].median()).values
        X_scaled = self._scale(X)
        scores = self.select_best_k(X_scaled)
        self.best_k = int(scores.loc[scores["silhouette"].idxmax(), "k"])
        self.kmeans_model = KMeans(n_clusters=self.best_k, random_state=self.random_state, n_init=10)
        labels = self.kmeans_model.fit_predict(X_scaled)
        return labels

    def fit_dbscan(self, df: pd.DataFrame, feature_cols: List[str],
                    eps: float = 0.5, min_samples: int = 5) -> np.ndarray:
        """Run DBSCAN and return cluster labels (-1 = outlier/noise)."""
        if not SKLEARN_AVAILABLE:
            raise RuntimeError("scikit-learn required.")
        X = df[feature_cols].fillna(df[feature_cols].median()).values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        db = DBSCAN(eps=eps, min_samples=min_samples)
        return db.fit_predict(X_scaled)

    def cluster_profiles(self, df: pd.DataFrame, labels: np.ndarray,
                          feature_cols: List[str]) -> pd.DataFrame:
        """Return cluster-level mean feature profiles sorted by monetary value."""
        df = df[feature_cols].copy()
        df["cluster"] = labels
        profile = df.groupby("cluster")[feature_cols].mean().round(2)
        if "monetary" in feature_cols:
            profile = profile.sort_values("monetary", ascending=False)
        return profile.reset_index()

    def cluster_sizes(self, labels: np.ndarray) -> pd.DataFrame:
        unique, counts = np.unique(labels, return_counts=True)
        return pd.DataFrame({
            "cluster": unique,
            "count": counts,
            "pct": (counts / len(labels) * 100).round(1),
        })

    def pca_projection(self, df: pd.DataFrame,
                        feature_cols: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        """Return 2D PCA projection for visualization (scores, explained_variance_ratio)."""
        if not SKLEARN_AVAILABLE:
            return np.zeros((len(df), 2)), np.array([0.5, 0.5])
        X = df[feature_cols].fillna(df[feature_cols].median()).values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        pca = PCA(n_components=2)
        scores = pca.fit_transform(X_scaled)
        return scores, pca.explained_variance_ratio_

    def segment_labels(self, profiles: pd.DataFrame) -> Dict[int, str]:
        """
        Assign human-readable segment names based on cluster monetary/frequency rank.
        """
        names = {0: "Champions", 1: "Loyal", 2: "At Risk", 3: "Casual", 4: "Lost"}
        if "monetary" in profiles.columns:
            ranked = profiles.sort_values("monetary", ascending=False)
            return {int(row["cluster"]): names.get(i, f"Segment {i}")
                    for i, (_, row) in enumerate(ranked.iterrows())}
        return {int(c): f"Cluster {c}" for c in profiles["cluster"]}


if __name__ == "__main__":
    np.random.seed(42)
    n = 1000
    dates = pd.date_range("2023-01-01", "2024-12-31", freq="h")
    transactions = pd.DataFrame({
        "customer_id": [f"C{i:04d}" for i in np.random.randint(1, 201, n)],
        "invoice_date": np.random.choice(dates, n),
        "total_amount": np.abs(np.random.lognormal(4.5, 1.2, n)).round(2),
        "quantity": np.random.randint(1, 20, n),
        "product_category": np.random.choice(["electronics", "clothing", "food", "home", "sports"], n),
    })

    builder = CustomerFeatureBuilder()
    customer_df = builder.build(transactions)
    print(f"Customer features built: {len(customer_df)} customers")
    print(customer_df.head(3).to_string(index=False))

    clusterer = CustomerClusterer(max_k=8)
    feature_cols = [c for c in ["recency_days", "frequency", "monetary",
                                 "avg_basket", "category_diversity"]
                    if c in customer_df.columns]
    labels = clusterer.fit_kmeans(customer_df, feature_cols)
    print(f"\nBest K: {clusterer.best_k}")

    customer_df["cluster"] = labels
    sizes = clusterer.cluster_sizes(labels)
    print("\nCluster sizes:")
    print(sizes.to_string(index=False))

    profiles = clusterer.cluster_profiles(customer_df, labels, feature_cols)
    print("\nCluster profiles:")
    print(profiles.to_string(index=False))

    segment_names = clusterer.segment_labels(profiles)
    print("\nSegment names:", segment_names)

    scores, evr = clusterer.pca_projection(customer_df, feature_cols)
    print(f"\nPCA variance explained: PC1={evr[0]:.2%}, PC2={evr[1]:.2%}")
