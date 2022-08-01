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
