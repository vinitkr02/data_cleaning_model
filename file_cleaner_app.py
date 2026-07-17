import io
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Data Cleaner Tool",
    page_icon="🧹",
    layout="centered"
)

st.title("🧹 Automated Data Cleaner")
st.write("Upload your messy dataset, clean it automatically, and download the cleaned version instantly.")

uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    file_name = uploaded_file.name
    st.success(f"📂 Loaded file: {file_name}")

    try:
 
        if file_name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

     
        st.subheader("👀 Raw Data Preview")
        st.dataframe(df.head())

        st.write(f"**Rows:** {df.shape[0]} | **Columns:** {df.shape[1]}")


        st.subheader("⚡ Cleaning Progress")

        # Remove duplicate rows
        init_rows = len(df)
        df.drop_duplicates(inplace=True)
        dup_rows = init_rows - len(df)

        st.info(f"✔️ Removed **{dup_rows}** duplicate rows.")

       
        before = len(df)
        df.dropna(how="all", inplace=True)
        removed_blank = before - len(df)

        st.info(f"✔️ Removed **{removed_blank}** completely empty rows.")

        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        st.info("✔️ Standardized column names.")

      
        text_cols = df.select_dtypes(include=["object"]).columns

        for col in text_cols:
            df[col] = (
                df[col]
                .fillna("Unknown")
                .str.strip()
                .replace("", "Unknown")
            )

        st.info("✔️ Cleaned text columns and filled missing values.")

     
        num_cols = df.select_dtypes(include="number").columns

        for col in num_cols:
            df[col] = df[col].fillna(df[col].median())

        st.info("✔️ Filled missing numeric values with the column median.")

  
        st.subheader("✨ Cleaned Data Preview")
        st.dataframe(df.head())

  
        st.subheader("📋 Remaining Null Values")

        null_values = df.isnull().sum()

        st.dataframe(
            pd.DataFrame({
                "Column": null_values.index,
                "Null Values": null_values.values
            })
        )

        st.success(f"✅ Total Remaining Null Values: {null_values.sum()}")

        st.subheader("📊 Cleaned Dataset Summary")

        st.dataframe(df.describe(include="all").T)

        output_buffer = io.BytesIO()

        if file_name.endswith(".csv"):
            df.to_csv(output_buffer, index=False)
            output_data = output_buffer.getvalue()
            mime_type = "text/csv"
            new_filename = "cleaned_" + file_name

        else:
            with pd.ExcelWriter(output_buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False)

            output_data = output_buffer.getvalue()
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            new_filename = "cleaned_" + file_name.split(".")[0] + ".xlsx"

        st.download_button(
            label="💾 Download Cleaned File",
            data=output_data,
            file_name=new_filename,
            mime=mime_type,
            use_container_width=True
        )

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
