# Project Buildup History: Online Retail Customer Clustering

- Repository: `online-retail-customer-clustering`
- Category: `data_science`
- Subtype: `clustering`
- Source: `project_buildup_2021_2025_daily_plan_extra.csv`
## 2022-08-01 - Day 3: Data preprocessing

- Task summary: Returned to Online Retail Customer Clustering after finishing a long stretch on product case study work. The retail transaction dataset needed more preprocessing than initially expected — there were cancelled orders mixed into the transaction log that should not count toward customer behavior features. Identified them by the negative quantity values and the invoice codes starting with C. Removed them and recalculated the per-customer aggregates. The customer count changed noticeably after cleaning so had to update the exploratory counts throughout the notebook.
- Deliverable: Cancelled orders removed. Customer aggregates recalculated. Count updated throughout.
## 2022-08-01 - Day 3: Data preprocessing

- Task summary: Quick fix late in the day: the country filter was using a loose string match that was accidentally including a few rows from other regions. Tightened the filter to an exact match.
- Deliverable: Country filter tightened. A few incorrectly included rows removed.
## 2022-08-08 - Day 4: RFM feature construction

- Task summary: Built the RFM (Recency, Frequency, Monetary) feature matrix today. Recency was computed relative to the last transaction date in the dataset, frequency as the count of distinct invoice numbers per customer, and monetary as total spend. All three needed log transformation before clustering because the distributions were extremely right-skewed — a small number of very high-value customers were dominating the scale. Plotted the transformed distributions to confirm they were reasonable.
- Deliverable: RFM matrix built. Log transforms applied. Distributions confirmed reasonable.
## 2022-10-10 - Day 5: K-Means clustering

- Task summary: Ran the K-Means clustering on the RFM features today. Used the elbow method and silhouette scores to select k — both pointed toward 4 clusters as a reasonable choice though 3 was defensible too. Went with 4 since the resulting segments were more interpretable from a business standpoint. Labeled the clusters based on their centroid positions: Champions (high recency, frequency, and value), Loyal Customers, At-Risk, and Lost. Plotted the segment profiles as radar charts.
- Deliverable: 4-cluster K-Means solution selected. Segments labeled and radar charts added.
## 2022-10-10 - Day 5: K-Means clustering

- Task summary: The cluster assignments were sensitive to initialization so added random seed and ran the stability check with multiple inits. Results were stable across 10 runs with the chosen k.
- Deliverable: Clustering stability confirmed across 10 initializations.
## 2022-10-10 - Day 5: K-Means clustering

- Task summary: Added a transition matrix concept — estimating how customers might move between segments over time if current trends continue. Mostly exploratory but adds an interesting forward-looking dimension to the analysis.
- Deliverable: Segment transition matrix added as exploratory analysis.
## 2022-11-14 - Day 6: Business interpretation

- Task summary: Shifted the focus of the clustering work to business interpretation today. The technical clustering is done — now the question is what actions each segment should trigger. Wrote up a playbook for each of the four segments: what marketing approach makes sense, what retention risk level they represent, and what the expected value of converting a customer between segments is. This required making some assumptions about margin and conversion rates but documented all of them.
- Deliverable: Segment playbook written. Retention recommendations per cluster documented.
## 2022-11-14 - Day 6: Business interpretation

- Task summary: Added a one-page dashboard summary showing cluster sizes, average RFM values per cluster, and the top recommended action. Intended as the deliverable for a non-technical stakeholder.
- Deliverable: One-page cluster summary added for stakeholder delivery.
## 2022-12-19 - Day 7: Portfolio finalization

- Task summary: Final pass on the Online Retail Clustering project for portfolio purposes. The notebook was strong analytically but the intro was too technical. Rewrote the first two cells to lead with the business question and why segmenting customers by RFM behavior matters. Moved the technical deep-dives to later cells. Also made all chart fonts larger since the earlier version was too small to read in a screenshot.
- Deliverable: Intro rewritten for business audience. Chart fonts enlarged for readability.
## 2022-12-19 - Day 7: Portfolio finalization

- Task summary: Added a GitHub Actions badge to the README even though this project doesn't have CI — just a placeholder for consistency with the rest of the portfolio. Will add actual tests when there's time.
- Deliverable: README badges added for visual consistency.
