import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

# Function to extract unique teacher names from the dataframe
def get_unique_teachers(dataframe):
    return pd.unique(dataframe.values.ravel('K'))

# Function to create a PDF report for the selected teacher
def create_teacher_pdf(teacher_name, dataframe, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    c.drawString(100, height - 40, f"Time Table for Teacher: {teacher_name}")

    # Assuming the dataframe is in the correct format
    for index, row in dataframe.iterrows():
        day = index[0]
        classes = row[row == teacher_name].index
        text = f"{day}: " + ", ".join(classes)
        c.drawString(100, height - 70 - (10 * index), text)

    c.save()

# Start of the Streamlit app
st.title('Teacher Schedule PDF Generator')

# File uploader allows user to add their own excel
uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx'])
if uploaded_file:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    df = pd.read_excel(bytes_data, sheet_name='BOYS&GIRLS')

    # Extract unique teacher names
    unique_teachers = get_unique_teachers(df)

    # Dropdown to select the teacher
    teacher_name = st.selectbox('Select the Teacher:', unique_teachers)

    # Input for entering the teacher's name (optional)
    input_teacher_name = st.text_input("Enter the teacher's name (Optional):")
    if input_teacher_name:
        teacher_name = input_teacher_name

    # When the button is clicked, generate the PDF
    if st.button('Generate PDF'):
        filename = f'/mnt/data/{teacher_name}_schedule.pdf'
        create_teacher_pdf(teacher_name, df, filename)

        # Download link for the PDF
        with open(filename, "rb") as file:
            btn = st.download_button(
                label="Download PDF",
                data=file,
                file_name=f'{teacher_name}_schedule.pdf',
                mime="application/octet-stream"
            )
