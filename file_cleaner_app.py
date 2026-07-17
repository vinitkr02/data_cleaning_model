import io
import pandas as pd
import streamlit as st
st.set_page_config(page_title="Data Cleaner Tool", page_icon="🧹", layout="centered")

st.title("🧹 Automated Data Cleaner")
st.write("Upload your messy dataset, and download the cleaned version instantly.")
uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file", type=["csv", "xlsx"]
)

if uploaded_file is not None:
    # Get the original filename
    file_name = uploaded_file.name
    st.success(f"📂 Loaded file: {file_name}")
    try:
        if file_name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

      
        st.subheader("👀 Raw Data Preview")
        st.dataframe(df.head(5))
        st.subheader("⚡ Cleaning Progress")
        init_rows = len(df)
        df.drop_duplicates(inplace=True)
        dup_rows = init_rows - len(df)
        st.info(f"✔️ Removed **{dup_rows}** identical duplicate rows.")

        text_cols = df.select_dtypes(include=["object"]).columns
        for col in text_cols:
            df[col] = df[col].astype(str).str.strip()  # Remove spaces
        df[text_cols] = df[text_cols].fillna("Unknown")  # Fill blanks
        st.info("✔️ Trimmed text spacing and filled blank text with 'Unknown'.")
        num_cols = df.select_dtypes(include=["number"]).columns
        for col in num_cols:
            df[col] = df[col].fillna(df[col].median())  # Fill with median
        st.info("✔️ Filled missing numbers with the column median.")
        st.subheader("✨ Cleaned Data Preview")
        st.dataframe(df.head(5))
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
            mime_type = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            new_filename = "cleaned_" + file_name.split(".")[0] + ".xlsx"
        st.download_button(
            label="💾 Download Cleaned File",
            data=output_data,
            file_name=new_filename,
            mime=mime_type,
        )

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
