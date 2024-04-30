import pandas as pd

file_path = 'add_courses.xlsx'
async def get_courses(file_name):
    excel_data_df = pd.read_excel(file_name)
    excel_data_df = excel_data_df.rename(columns={'Title': 'title',
                                              'Title KZ': 'title_kz',
                                              'Title RU': 'title_ru',
                                              'Course Code': 'course_code',
                                              'Theoretical Hours':'teor',
                                              'Practical Hours':'pr',
                                              'ECTS':'ects',
                                              'Credit Hours':'cr',
                                              'Term':'term',
                                             })
    excel_data_df['pr'] = excel_data_df['pr'].astype(str)
    excel_data_df['teor'] = excel_data_df['teor'].astype(int)
    excel_data_df['cr'] = excel_data_df['cr'].astype(int)
    excel_data_df['ects'] = excel_data_df['ects'].astype(int)
    
    list_of_courses = excel_data_df.to_dict('records')
    list_of_courses_new = []
    for i in list_of_courses:
        dic = i
        dic['user_id'] = ''
        dic['sub_ids'] = []
        dic['pre_ids'] = []
        list_of_courses_new.append(dic)
    
    return list_of_courses_new

get_courses(file_path)
