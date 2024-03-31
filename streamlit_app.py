import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Paragraph

# Function to extract unique teacher names from the dataframe
def get_unique_teachers(dataframe):
    return pd.unique(dataframe.values.ravel('K'))

# Function to create a PDF report for the selected teacher


def create_teacher_pdf(teacher_name, schedule_df, filename):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # School Name
    school_name = styles['Title']
    school_name.alignment = 1  # Center alignment
    story.append(Paragraph("DIVISIONAL PUBLIC SCHOOL & COLLEGE SAHIWAL", school_name))
    
    # Teacher Name
    teacher_name_style = styles['Normal']
    teacher_name_style.alignment = 1  # Center alignment
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Teacher's Name: {teacher_name}", teacher_name_style))
    
    # Table
    data = [[''] + [f"Period {i}" for i in range(1, 9)]]
    data += [([day] + row.tolist()) for day, row in schedule_df.iterrows()]

    table = Table(data)
    table_style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 10)
    ])
    table.setStyle(table_style)

    story.append(Spacer(1, 12))
    story.append(table)

    # Principal Signature Line
    principal_style = styles['Normal']
    principal_style.alignment = 2  # Right alignment
    story.append(Spacer(1, 12))
    story.append(Paragraph("Principal:", principal_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("_________________________", principal_style))
    
    # Build PDF
    doc.build(story)

    return filename


# Start of the Streamlit app
st.title('Teacher Schedule PDF Generator')

# File uploader allows user to add their own excel
uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx'])
if uploaded_file:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    df = pd.read_excel(bytes_data, sheet_name='BOYS&GIRLS')
    # Extract unique teacher names
    # get unique teachers except for the first column and first row
    
    # remove the first row
    df = df.iloc[1:]
    
    #first 8 columns are monday and next 8 columns are tuesday and so on only friday have 6 columns
    # add the column names as days
    
    
    df.columns = [
        "Class", "Monday-1", "Monday-2", "Monday-3", "Monday-4", "Monday-5", "Monday-6", "Monday-7", "Monday-8",
        "Tuesday-1", "Tuesday-2", "Tuesday-3", "Tuesday-4", "Tuesday-5", "Tuesday-6", "Tuesday-7", "Tuesday-8",
        "Wednesday-1", "Wednesday-2", "Wednesday-3", "Wednesday-4", "Wednesday-5", "Wednesday-6", "Wednesday-7", "Wednesday-8",
        "Thursday-1", "Thursday-2", "Thursday-3", "Thursday-4", "Thursday-5", "Thursday-6", "Thursday-7", "Thursday-8",
        "Friday-1", "Friday-2", "Friday-3", "Friday-4", "Friday-5",
        "Saturday-1", "Saturday-2", "Saturday-3", "Saturday-4", "Saturday-5", "Saturday-6", "Saturday-7", "Saturday-8",
    ]

    
    
    
    st.write(df)
    
    unique_teachers = get_unique_teachers(df.iloc[1:, 1:])
    # Dropdown to select the teacher and search bar to enter the teacher's name
    teacher_name = st.selectbox('Select teacher', unique_teachers)
    
    
    # display the teacher's schedule which class they are teaching and on which day
    st.write(f"Schedule for {teacher_name}")
    # we have classes on the columns and days on the rows
#     CLASS	MONDAY							
# 2 (B)	U-khalida	SP-M	M-IRUM	E-TANIA	E-TANIA	GK-MAIRA	D-AYESHA	GK-MAIRA    

    # Display the schedule for the selected teacher like for U-khalida on Monday she will teach 2 (B) class
    # search which row has the teacher name and then display the class by check the entry in first column 
    # and check the coloumn name for the day
    
    # give the weekly schedule of the teacher
    
    # Building the teacher's weekly schedule
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    teacher_schedule = {day: [] for day in days_of_week}

        # Assuming df.columns are structured as 'Day-Period' after 'Class'
    teacher_name = teacher_name.lower()  # Ensure we're using a lowercase version for comparison
    periods_per_day = {
        "Monday": 8,
        "Tuesday": 8,
        "Wednesday": 8,
        "Thursday": 8,
        "Friday": 5,
        "Saturday": 8,
    }

    for day, num_periods in periods_per_day.items():
        for period in range(1, num_periods + 1):
            period_column = f"{day}-{period}"
            # Check if the period column exists to avoid KeyError
            if period_column in df.columns:
                class_name = df.loc[df[period_column].str.lower().str.contains(teacher_name, na=False), "Class"]
                if not class_name.empty:
                    # Append class name and period to the schedule
                    teacher_schedule[day].append(f"{class_name.values[0]}")

    # Display the schedule in table 

    
    # Assuming teacher_schedule is already defined
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    period_columns = [f'Period {i+1}' for i in range(8)]
    schedule_rows = []

    for day in days_of_week:
        # Get the classes for each day, pad with empty strings if less than 8
        day_classes = teacher_schedule.get(day, []) + [''] * (8 - len(teacher_schedule.get(day, [])))
        # Create a row for the current day
        day_row = pd.DataFrame([{**{'Day': day}, **dict(zip(period_columns, day_classes))}])
        schedule_rows.append(day_row)

    # Concatenate all the day rows to form the complete schedule DataFrame
    schedule_df = pd.concat(schedule_rows).set_index('Day')

    # Display the DataFrame
    st.write("Weekly Schedule for:", teacher_name)
    st.dataframe(schedule_df)

    

# Generate PDF button
if st.button('Generate PDF') and teacher_name:
    filename = f'{teacher_name.replace(" ", "_")}_schedule.pdf'
    create_teacher_pdf(teacher_name, schedule_df, filename)

    # Provide the download link for the PDF
    with open(filename, "rb") as file:
        st.download_button(
            label="Download PDF",
            data=file,
            file_name=f'{teacher_name}_schedule.pdf',
            mime='application/octet-stream'
        )