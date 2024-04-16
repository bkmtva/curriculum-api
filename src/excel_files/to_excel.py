import pandas as pd
import numpy as np
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment, Font, Border, Side
import pandas as pd
import json
SOURCE_PATH = "src/excel_files/"
BASE_FILE = SOURCE_PATH+"template.xlsx"
file_save = "curriculum.xlsx"



def to_excel(curriculum: str):
    dict_train = json.loads(curriculum)
    df = get_dataframe(dict_train)
    # Load the Excel file
    wb = load_workbook(filename=BASE_FILE)
    ws = wb['CS Curriculum 2023-2024(main)']

    # Starting column and row to write the data
    start_col = 4
    start_row = 28

    # Assuming df is defined somewhere containing the data

    # Filter the DataFrame by semester and create a list of unique semesters
    semesters = df['semester'].unique()

    # Sort semesters in ascending order
    semesters.sort()

    # Initialize font properties
    bold_font = Font(name='Times New Roman', size=12, bold=True)
    regular_font = Font(name='Times New Roman', size=12)
    thin_border = Border(left=Side(style='thin'),
                         right=Side(style='thin'),
                         top=Side(style='thin'),
                         bottom=Side(style='thin'))

    last_row = 28
    # Writing the data for each semester
    for semester in semesters:
        # Filter DataFrame by semester
        df_semester = df[df['semester'] == semester]

        # Sort courses by order_in_semester
        df_semester = df_semester.sort_values(by='order_in_semester')

        # Merge cells for semester header
        merge_range = f'{get_column_letter(start_col)}{start_row}:{get_column_letter(start_col + 4)}{start_row}'
        ws.merge_cells(merge_range)

        # Write semester header with bold font
        ws[f'{get_column_letter(start_col)}{start_row}'].value = f"{semester} семестр"
        ws[f'{get_column_letter(start_col)}{start_row}'].alignment = Alignment(horizontal='center')
        ws[f'{get_column_letter(start_col)}{start_row}'].font = bold_font

        # Increment the start_row
        start_row += 1

        # Merge cells for CR total
        cr_start_row = start_row

        # Merge cells for ECTS total
        ects_start_row = start_row

        # Initialize variables to track previous order_in_semester and max CR/ECTS
        prev_order = None
        max_cr = 0
        max_ects = 0

        # Write data for each course in the semester
        for r, course in enumerate(df_semester.itertuples(), start=start_row):
            # If it's not the first row and the order_in_semester is the same as the previous one
            if prev_order == course.order_in_semester and r != start_row:
                # Merge cells for course_code and set the value to None
                ws.merge_cells(f'{get_column_letter(start_col)}{r}:{get_column_letter(start_col)}{r}')
            # ws[f'{get_column_letter(start_col)}{r}'].value = None
            # else:
            # Write course_code
            # ws[f'{get_column_letter(start_col)}{r}'].value = course.course_code

            # Write other columns
            ws[f'{get_column_letter(start_col)}{r}'].value = course.course_code
            ws[f'{get_column_letter(start_col + 1)}{r}'].value = course.combined_titles
            ws[f'{get_column_letter(start_col + 2)}{r}'].value = course.cr
            ws[f'{get_column_letter(start_col + 3)}{r}'].value = course.ects
            ws[f'{get_column_letter(start_col + 4)}{r}'].value = course.pr_value

            # Track CR and ECTS for merging
            if prev_order == course.order_in_semester:
                max_cr = max(max_cr, course.cr)
                max_ects = max(max_ects, course.ects)
            else:
                if prev_order is not None:
                    # Merge cells for CR with max value
                    merge_range_cr = f'{get_column_letter(start_col + 2)}{cr_start_row}:{get_column_letter(start_col + 2)}{r - 1}'
                    ws.merge_cells(merge_range_cr)
                    ws[f'{get_column_letter(start_col + 2)}{cr_start_row}'].value = max_cr

                    # Merge cells for ECTS with max value
                    merge_range_ects = f'{get_column_letter(start_col + 3)}{ects_start_row}:{get_column_letter(start_col + 3)}{r - 1}'
                    ws.merge_cells(merge_range_ects)
                    ws[f'{get_column_letter(start_col + 3)}{ects_start_row}'].value = max_ects

                # Update variables for the new group of courses
                cr_start_row = r
                ects_start_row = r
                max_cr = course.cr
                max_ects = course.ects
                prev_order = course.order_in_semester

            # Set font for each cell
            for col in range(start_col, start_col + 5):
                ws[f'{get_column_letter(col)}{r}'].font = regular_font
            #  ws[f'{get_column_letter(col)}{r}'].border = thin_border

        # Merge cells for CR and ECTS with max value for the last group of courses
        merge_range_cr = f'{get_column_letter(start_col + 2)}{cr_start_row}:{get_column_letter(start_col + 2)}{start_row + len(df_semester) - 1}'
        ws.merge_cells(merge_range_cr)
        ws[f'{get_column_letter(start_col + 2)}{cr_start_row}'].value = max_cr

        merge_range_ects = f'{get_column_letter(start_col + 3)}{ects_start_row}:{get_column_letter(start_col + 3)}{start_row + len(df_semester) - 1}'
        ws.merge_cells(merge_range_ects)
        ws[f'{get_column_letter(start_col + 3)}{ects_start_row}'].value = max_ects

        # Set wrap text and center alignment for the combined_titles column
        for row in ws.iter_rows(min_row=start_row, max_row=start_row + len(df_semester) - 1, min_col=start_col + 1,
                                max_col=start_col + 1):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, horizontal='center')

        # Write 'Барлығы/Итого/Total' at the end of each semester
        ws[f'{get_column_letter(start_col)}{start_row + len(df_semester)}'].value = 'Барлығы/Итого/Total'
        ws.merge_cells(
            f'{get_column_letter(start_col)}{start_row + len(df_semester)}:{get_column_letter(start_col + 1)}{start_row + len(df_semester)}')

        # Write total cr and ects
        df_semester['cr'] = df_semester['cr'].astype(int)
        df_semester['ects'] = df_semester['ects'].astype(int)

        total_cr = sum(df_semester.groupby(['semester', 'order_in_semester'])['cr'].max())
        total_ects = sum(df_semester.groupby(['semester', 'order_in_semester'])['ects'].max())
        ws[f'{get_column_letter(start_col + 2)}{start_row + len(df_semester)}'].value = total_cr
        ws[f'{get_column_letter(start_col + 3)}{start_row + len(df_semester)}'].value = total_ects

        # Set font and alignment for total row
        for col in range(start_col, start_col + 4):
            ws[f'{get_column_letter(col)}{start_row + len(df_semester)}'].font = bold_font
            ws[f'{get_column_letter(col)}{start_row + len(df_semester)}'].alignment = Alignment(horizontal='center')

        # Update start_row for the next semester
        start_row += len(df_semester) + 1
        last_row = start_row

    # Calculate total 'cr' and 'ects' for all semesters
    total_cr_all = sum(df.groupby(['semester', 'order_in_semester'])['cr'].max())
    total_ects_all = sum(df.groupby(['semester', 'order_in_semester'])['ects'].max())

    # Merge cells for total
    total_merge_range = f'{get_column_letter(start_col)}{last_row}:{get_column_letter(start_col + 1)}{last_row}'
    ws.merge_cells(total_merge_range)
    ws[f'{get_column_letter(start_col)}{last_row}'].value = 'Барлығы/Итого/Total'
    ws[f'{get_column_letter(start_col)}{last_row}'].font = bold_font

    ws[f'{get_column_letter(start_col + 2)}{last_row}'].value = total_cr_all
    ws[f'{get_column_letter(start_col + 3)}{last_row}'].value = total_ects_all
    ws[f'{get_column_letter(start_col + 2)}{last_row}'].font = bold_font
    ws[f'{get_column_letter(start_col + 3)}{last_row}'].font = bold_font
    # ws[f'{get_column_letter(start_col)}{last_row}'].font = Alignment(horizontal='center')

    # Making borders for cells
    for row in range(28, last_row + 1):
        for col in range(1, 10 + 1):
            ws.cell(row=row, column=col).border = thin_border

    # Set program information
    program_in_kz = 'Білім беру бағдарламасы: ' + dict_train.get('program', {}).get('code', '') + ' ' + dict_train.get(
        'program', {}).get('title_kz', '')
    program_in_ru = 'Образовательная программа: ' + dict_train.get('program', {}).get('code', '') + ' ' + dict_train.get(
        'program', {}).get('title_ru', '')
    program_in_en = 'Program: ' + dict_train.get('program', {}).get('code', '') + ' ' + dict_train.get('program', {}).get('title', '')

    degree_in_kz = 'Берілетін дәреже: ' + dict_train.get('program', {}).get('code', '')
    degree_in_ru = 'Присуждаемая степень: ' + dict_train.get('program', {}).get('code', '')
    degree_in_en = 'Degree: ' + dict_train.get('program', {}).get('code', '')

    # Set the values in the specified cells
    ws['A17'].value = program_in_kz
    ws['E17'].value = program_in_en
    ws['G17'].value = program_in_ru

    ws['A18'].value = degree_in_kz
    ws['E18'].value = degree_in_en
    ws['G18'].value = degree_in_ru

    # Save the workbook
    saved_file_path = SOURCE_PATH+file_save
    wb.save(saved_file_path)

    return file_save


def get_dataframe(dict_train):
    all_courses = dict_train.get('courses')
    formatted_data = []
    for course_data in all_courses:
        course_info = course_data['course']
        subcourses = course_info.get('subcourses')
        # If there are subcourses, iterate over them
        if subcourses:
            for subcourse in subcourses:
                formatted_data.append({
                    'semester': course_data['semester'],
                    'course_id': course_data['course_id'],
                    'order_in_semester': course_data['order_in_semester'],
                    'title': subcourse['title'],
                    'title_kz': subcourse.get('title_kz', course_info['title_kz']),  # Use course title_kz if subcourse title_kz is missing
                    'title_ru': subcourse.get('title_ru', course_info['title_ru']),  # Use course title_ru if subcourse title_ru is missing
                    'teor': subcourse['teor'],
                    'cr': subcourse['cr'],
                    'term': subcourse['term'],
                    'course_code': subcourse['course_code'],
                    'pr': subcourse['pr'],
                    'ects': subcourse['ects'],
                    'subcourse_title': None  # Set to None for subcourses
                })
        else:
            # If there are no subcourses, add the main course with None as subcourse_title
            formatted_data.append({
                'semester': course_data['semester'],
                'course_id': course_data['course_id'],
                'order_in_semester': course_data['order_in_semester'],
                'title': course_info['title'],
                'title_kz': course_info['title_kz'],
                'title_ru': course_info['title_ru'],
                'teor': course_info['teor'],
                'cr': course_info['cr'],
                'term': course_info['term'],
                'course_code': course_info['course_code'],
                'pr': course_info['pr'],
                'ects': course_info['ects'],
                'subcourse_title': None  # Set to None for main courses without subcourses
            })

    # Creating DataFrame
    df = pd.DataFrame(formatted_data)
    df['combined_titles'] = df['title_kz'] + ' / ' + df['title_ru'] + ' / ' + df['title']
    df['pr_value'] = df['pr'].apply(lambda x: sum(map(int, x.split('+'))))
    df['cr'] = df['cr'].astype(int)
    df['ects'] = df['ects'].astype(int)
    return df
