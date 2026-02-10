Cleaning Engine

Cleaning Engine is a simple internal web tool designed to help users clean and standardize raw CSV datasets quickly and consistently. Instead of manually fixing column names, null values, duplicates, or formatting issues, the tool provides a structured workflow where the user can upload a file, apply selected cleaning operations, and download finalized outputs in one place. This project was created as part of an internship to support faster data preparation and smoother reporting or analysis workflows.
What this tool can do
Upload raw CSV files through a web interface
Standardize column names into a clean consistent format
Normalize null values and handle missing data properly
Trim unwanted spaces and clean text fields
Standardize company names for better consistency
Detect and standardize date columns
Convert numeric columns into proper numeric types
Remove empty rows
Remove duplicate records
Generate a Power BI-ready export (optional)
Generate a comparison report between raw vs cleaned data (optional)
Outputs generated after cleaning
Cleaned CSV file (final cleaned dataset)
Power BI formatted CSV (optional export for dashboards)
Comparison report CSV (optional report showing key differences and changes)

How to use the application

Upload a CSV file
Select the required cleaning operations (or use “Select All”)
Click on Run Cleaning
Download the output files directly from the app

Technologies used

Python
Pandas
Streamlit
Modular cleaning pipeline built using reusable operations

Author

Made by Shanvi Shetty
Internship Project — Cleaning Engine
