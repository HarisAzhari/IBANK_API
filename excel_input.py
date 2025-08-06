import pandas as pd
import os
import time
from ibank import IBANScraper


def process_iban_excel():
    """Cross-check Swift codes by scraping IBANs from PC OEP Fail sheet"""

    # Check if file exists
    file_path = "RO Bank Key Analysis - updated(1).xlsx"
    sheet_name = "PC OEP Fail 31072025"

    if not os.path.exists(file_path):
        print(f"File {file_path} not found!")
        return

    try:
        # Read the Excel file from specific sheet
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        print("🔥 Swift Code Cross-Check Mission")
        print("=" * 50)

        # Display basic info about the dataframe
        print(f"Shape: {df.shape} (rows, columns)")
        print(f"Columns: {list(df.columns)}")

        # Check if IBAN IN PC column exists
        if "IBAN IN PC" not in df.columns:
            print("❌ No 'IBAN IN PC' column found in the Excel file!")
            print("Available columns:", list(df.columns))
            return

        # Get all IBANs for processing
        total_ibans = len(df["IBAN IN PC"].dropna())
        print(f"\n🎯 Processing all {total_ibans} IBANs for cross-check")

        # Initialize the scraper
        scraper = IBANScraper()

        # Work with the full dataframe
        result_df = df.copy()

        # Array to store failed rows for manual retry
        failed_rows = []

        print("\n🚀 Starting cross-check mission...")
        print("=" * 50)

        # Process each IBAN for cross-checking
        for i, row in result_df.iterrows():
            # Skip rows with missing IBAN
            if pd.isna(row["IBAN IN PC"]):
                continue

            iban = row["IBAN IN PC"]
            existing_swift = row["Swift Code in PC"]

            print(f"\n💫 Processing {i+1}/{len(result_df)}: {iban}")
            print(f"   📋 Current Swift in PC: {existing_swift}")

            # Scrape IBAN data
            iban_data = scraper.scrape_iban_info(iban)

            if iban_data:
                scraped_swift = iban_data.get("swift_bic_code", "N/A")

                # Cross-check if codes match
                codes_match = existing_swift == scraped_swift

                # Add new columns to the dataframe
                result_df.at[i, "Scraped_Swift_Code"] = scraped_swift
                result_df.at[i, "Swift_Codes_Match"] = "YES" if codes_match else "NO"
                result_df.at[i, "Scraped_Bank_Name"] = iban_data.get("bank_name", "N/A")
                result_df.at[i, "Scraped_Country"] = iban_data.get("country", "N/A")
                result_df.at[i, "Scraped_City"] = iban_data.get("city", "N/A")
                result_df.at[i, "Scraped_At"] = iban_data.get("scraped_at", "N/A")

                print(f"   🔍 Scraped Swift: {scraped_swift}")
                print(f"   {'✅ MATCH!' if codes_match else '❌ MISMATCH!'}")

            else:
                # Failed to scrape - add to failed rows array
                failed_row_info = {
                    "Row_Index": i,
                    "IBAN": iban,
                    "Existing_Swift": existing_swift,
                    "Gin": row["Gin"],
                    "PC_User_ID": row["Pc User ID"],
                    "Failed_At": time.strftime("%Y-%m-%d %H:%M:%S"),
                }
                failed_rows.append(failed_row_info)

                # Mark as failed in dataframe
                result_df.at[i, "Scraped_Swift_Code"] = "SCRAPE_FAILED"
                result_df.at[i, "Swift_Codes_Match"] = "FAILED"
                result_df.at[i, "Scraped_Bank_Name"] = "FAILED"
                result_df.at[i, "Scraped_Country"] = "FAILED"
                result_df.at[i, "Scraped_City"] = "FAILED"
                result_df.at[i, "Scraped_At"] = time.strftime("%Y-%m-%d %H:%M:%S")

                print(f"   ❌ Failed to scrape data - saved for manual retry")

            # Add a small delay to be respectful to the website
            time.sleep(3)

        # Save to new Excel file with cross-check results
        output_file = "Swift_Code_CrossCheck_Results.xlsx"
        result_df.to_excel(output_file, index=False)

        # Save failed rows to separate file for manual retry
        if failed_rows:
            failed_df = pd.DataFrame(failed_rows)
            failed_file = "Failed_IBANs_for_Manual_Retry.xlsx"
            failed_df.to_excel(failed_file, index=False)
            print(f"\n💔 Failed rows saved to: {failed_file}")

        print(f"\n🎉 Cross-check complete!")
        print("=" * 50)
        print(f"💾 Results saved to: {output_file}")
        print(f"📈 Total IBANs processed: {total_ibans}")

        # Count matches and mismatches
        matches = len(result_df[result_df["Swift_Codes_Match"] == "YES"])
        mismatches = len(result_df[result_df["Swift_Codes_Match"] == "NO"])
        failures = len(result_df[result_df["Swift_Codes_Match"] == "FAILED"])

        print(f"✅ Swift codes matching: {matches}")
        print(f"❌ Swift codes mismatched: {mismatches}")
        print(f"💔 Scraping failures: {failures}")

        # Show failed rows summary
        if failed_rows:
            print(f"\n🔥 Failed IBANs for manual retry:")
            print("=" * 40)
            for i, failed in enumerate(failed_rows, 1):
                print(
                    f"{i}. Row {failed['Row_Index']}: {failed['IBAN']} (GIN: {failed['Gin']})"
                )

        # Show sample comparison
        print(f"\n📋 Sample cross-check results:")
        comparison_cols = [
            "IBAN IN PC",
            "Swift Code in PC",
            "Scraped_Swift_Code",
            "Swift_Codes_Match",
        ]
        print(result_df[comparison_cols].head(10))

        return result_df, failed_rows

    except Exception as e:
        print(f"Error processing the Excel file: {e}")
        print("Make sure you have pandas and openpyxl installed:")
        print("pip install pandas openpyxl")
        return None


def read_iban_excel():
    """Read IBAN ROM.xlsx file and display all columns with first 3 elements"""

    # Check if file exists
    file_path = "IBAN ROM.xlsx"
    if not os.path.exists(file_path):
        print(f"File {file_path} not found!")
        return

    try:
        # Read the Excel file
        df = pd.read_excel(file_path)

        print("📊 IBAN ROM Excel File Analysis")
        print("=" * 50)

        # Display basic info about the dataframe
        print(f"Shape: {df.shape} (rows, columns)")
        print(f"Columns: {list(df.columns)}")
        print("\n" + "=" * 50)

        # Print first 3 elements from each column
        print("First 3 elements from each column:")
        print("-" * 40)

        for column in df.columns:
            print(f"\n📋 Column: '{column}'")
            print(f"Data type: {df[column].dtype}")

            # Get first 3 non-null elements
            first_three = df[column].dropna().head(3)

            if len(first_three) > 0:
                for i, value in enumerate(first_three, 1):
                    print(f"  {i}. {value}")
            else:
                print("  No data available")

        print("\n" + "=" * 50)
        print("📈 Sample of the data (first 3 rows):")
        print(df.head(3))

    except Exception as e:
        print(f"Error reading the Excel file: {e}")
        print("Make sure you have pandas and openpyxl installed:")
        print("pip install pandas openpyxl")


if __name__ == "__main__":
    # Ask user what they want to do
    print("🔥 IBAN Excel Processor")
    print("=" * 30)
    print("1. Just read and display Excel file")
    print("2. Process all IBANs and get Swift/BIC codes")

    choice = input("\n💋 What would you like to do? (1 or 2): ").strip()

    if choice == "1":
        read_iban_excel()
    elif choice == "2":
        process_iban_excel()
    else:
        print("😘 Running full IBAN processing by default...")
        process_iban_excel()
