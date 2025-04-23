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
    # lower case all the values in the dataframe
    return pd.unique(dataframe.values.ravel('K'))

def get_base_teacher_name(teacher_with_subject):
    # This function will return the base teacher name by removing any subject prefixes
    parts = teacher_with_subject.split('-')
    if len(parts) > 1:
        return parts[1]  # If there is a prefix, return the name without the prefix
    return parts[0]  # If there's no prefix, return the name as is


#def get_aggregated_schedule(df):
#    # This function will create an aggregated schedule
#    unique_teachers = get_unique_teachers(df.iloc[:, 1:])
#    all_teachers_schedule = {}
#
#    for teacher in unique_teachers:
#        base_teacher_name = get_base_teacher_name(teacher)
#        if base_teacher_name not in all_teachers_schedule:
#            all_teachers_schedule[base_teacher_name] = {}
#
#        # Get the schedule for the teacher
#        schedule_df, teacher_schedule = get_teacher_schedule(teacher)
#
#        for day, periods in teacher_schedule.items():
#            if day not in all_teachers_schedule[base_teacher_name]:
#                all_teachers_schedule[base_teacher_name][day] = periods
#            else:
#                # Combine the periods with the existing ones
#                combined_periods = []
#                for existing, new in zip(all_teachers_schedule[base_teacher_name][day], periods):
#                    if existing.strip() and new.strip():
#                        combined_periods.append(f"{existing}, {new}")
#                    else:
#                        combined_periods.append(existing or new)
#                all_teachers_schedule[base_teacher_name][day] = combined_periods
#
#    return all_teachers_schedule 


def get_teacher_schedule(teacher_name):
    # Building the teacher's weekly schedule
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    teacher_schedule = {day: [] for day in days_of_week}

    # Assuming df.columns are structured as 'Day-Period' after 'Class'
    # Assuming df.columns are structured as 'Day-Period' after 'Class'
    teacher_name = teacher_name.lower()  # Ensure we're using a lowercase version for comparison
    periods_per_day = {
        "Monday": 8,
        "Tuesday": 8,
        "Wednesday": 8,
        "Thursday": 8,
        "Friday": 5,  # Update based on your schedule
        "Saturday": 8,
    }

    for day, num_periods in periods_per_day.items():
        for period in range(1, num_periods + 1):
            period_column = f"{day}-{period}"
            if period_column in df.columns:
                # Fill the period with the class name or "Free" if the teacher isn't teaching that period
                class_name = df.loc[df[period_column].str.lower().str.contains(teacher_name, na=False), "Class"]
                teacher_schedule[day].append(class_name.values[0] if not class_name.empty else "  ")

    # Display the schedule in table format
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    period_columns = [f'Period {i+1}' for i in range(8)]
    schedule_rows = []

    for day in days_of_week:
        # Get the classes for each day, fill with "Free" if the teacher is free that period
        day_classes = teacher_schedule.get(day, ["  "] * 8)  # Default to "Free" for all periods
        schedule_rows.append([day] + day_classes)

    # Convert the list into a DataFrame
    schedule_df = pd.DataFrame(schedule_rows, columns=['Day'] + period_columns)

    return schedule_df, teacher_schedule




def create_teacher_pdf(teacher_name, schedule_df, filename):
    teacher_name = teacher_name.upper()
    teacher_name = teacher_name.split("-")[1]
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
    data = [[''] +['Day']+ [f"Period {i}" for i in range(1, 9)]]
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

#Get names of classes
def get_class_name(df):
    class_name = df.iloc[:, 0].tolist()
    return class_name

#Make schedule of classes
def class_schedule(df, class_with_section):
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    period_columns = [f'Period {i+1}' for i in range(5)] + ['Break'] + [f'Period {i+1}' for i in range(5, 8)]


    class_name = get_class_name(df)
    if class_with_section in class_name:
        class_index = class_name.index(class_with_section)
    
    required_row = df.iloc[class_index, 1:].tolist()
    dataframe_rows = [
        [days_of_week[0]] + required_row[0:5] + [" "] + required_row[5:8],
        [days_of_week[1]] + required_row[8:13] + [" "] + required_row[13:16],
        [days_of_week[2]] + required_row[16:21] + [" "] + required_row[21:24],
        [days_of_week[3]] + required_row[24:29] + [" "] + required_row[29:32],
        [days_of_week[4]] + required_row[32:37] + [" "],
        [days_of_week[5]] + required_row[37:42] + [" "] + required_row[42:45],
    ]

    class_schedule_dataframe = pd.DataFrame(dataframe_rows, columns = ["Days"] + period_columns)
    return class_schedule_dataframe

#Create class schedule pdf from developed dataframe
def create_class_pdf(filename, class_name, class_schedule):
    class_section = class_name.split("(")[1].split(")")[0]
    grade_name = class_name.split("(")[0]
    doc = SimpleDocTemplate(filename, pagesize=(650,840), rightMargin=30, leftMargin=30)

    story = []
    styles = getSampleStyleSheet()
    
    # School Name
    school_name = styles['Title']
    school_name.alignment = 1  # Center alignment
    story.append(Paragraph("DIVISIONAL PUBLIC SCHOOL & COLLEGE SAHIWAL", school_name))
    
    grade_style = styles["Normal"]
    grade_style.alignment = 1

    section_style = styles["Normal"]
    section_style.alignment = 1

    row_data = [
        [
            Paragraph(f"Class: {grade_name}", grade_style),
            Paragraph(f"Section: {class_section}", section_style),
            Paragraph("W.E.F: ___________", styles['Normal']),
        ]
    ]

    info_table = Table(row_data, colWidths=[180, 180, 180])  # adjust as needed
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
    ]))

    story.append(Spacer(1, 12))
    story.append(info_table)


    
    # Table
    data = [[''] +['Day']+ [f"Period {i}" for i in range(1, 6)] + ['Break'] + [f"Period {i}" for i in range(6, 9)]]
    data += [([day] + row.tolist()) for day, row in class_schedule.iterrows()]

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
    
    # lower case all the values in the dataframe
    df = df.apply(lambda x: x.str.lower())
    
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

    #st.write(df)
    
    unique_teachers = get_unique_teachers(df.iloc[1:, 1:])
    # Dropdown to select the teacher and search bar to enter the teacher's name
    teacher_name = st.selectbox('Select teacher', unique_teachers)
    
    # display the teacher's schedule which class they are teaching and on which day
    st.write(f"Schedule for {teacher_name}")

    
    schedule_df, _ = get_teacher_schedule(teacher_name)
    st.dataframe(schedule_df)

    if st.button('Generate PDF for techer') and teacher_name:
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

    #get class name from function
    class_name = get_class_name(df)
    #Select class name from dropdown
    class_with_section = st.selectbox("Select Class", class_name)

    st.write(f"Schedule for {class_with_section}")
    class_schedule_df = class_schedule(df, class_with_section)

    #write schedule to app
    st.dataframe(class_schedule_df)

    # Generate PDF button
    if st.button("Generate PDF for class") and class_with_section:
        class_filename = f"{class_with_section}_schedule.pdf"

        create_class_pdf(class_filename, class_with_section, class_schedule_df)

        with open(class_filename, "rb") as file:
            file_bytes = file.read()
        
        st.download_button(
            label="Download PDF",
            data=file_bytes,
            file_name=f'{class_with_section}_schedule.pdf',
            mime='application/octet-stream'
        )

       
