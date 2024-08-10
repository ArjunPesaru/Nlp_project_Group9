import streamlit as st
import nltk
import spacy
import psycopg2
from psycopg2 import sql
import pandas as pd
import base64
import random
import time
import datetime
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io
from streamlit_tags import st_tags
from PIL import Image
import plotly.express as px
# Importing course data from the Courses.py file
from Courses import ds_course, web_course, android_course, ios_course, uiux_course


# Load NLTK data and Spacy model
nltk.download('stopwords')
spacy.load('en_core_web_sm')

# Database connection setup
def get_db_connection():
    return psycopg2.connect(
        host='localhost',
        user='postgres',
        password='12345678',
        database='sra',
        port=5432
    )

def initialize_database():
    connection = psycopg2.connect(
        host='localhost',
        user='postgres',
        password='12345678',
        port=5432
    )
    cursor = connection.cursor()
    db_name = 'sra'
    cursor.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [db_name])
    exists = cursor.fetchone()
    if not exists:
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
    cursor.close()
    connection.close()

    # Reconnect to the new database
    connection = get_db_connection()
    cursor = connection.cursor()

    # Create table
    DB_table_name = 'user_data'
    table_sql = sql.SQL("""
        CREATE TABLE IF NOT EXISTS {} (
            ID SERIAL PRIMARY KEY,
            Name VARCHAR(100) NOT NULL,
            Email_ID VARCHAR(50) NOT NULL,
            resume_score VARCHAR(8) NOT NULL,
            Timestamp VARCHAR(50) NOT NULL,
            Page_no VARCHAR(5) NOT NULL,
            Predicted_Field VARCHAR(25) NOT NULL,
            User_level VARCHAR(30) NOT NULL,
            Actual_skills VARCHAR(300) NOT NULL,
            Recommended_skills VARCHAR(300) NOT NULL,
            Recommended_courses VARCHAR(600) NOT NULL
        )
    """).format(sql.Identifier(DB_table_name))
    cursor.execute(table_sql)
    connection.commit()
    cursor.close()
    connection.close()

initialize_database()

def show_pdf(file_path):
    # Extract text from PDF
    with open(file_path, 'rb') as f:
        resource_manager = PDFResourceManager()
        fake_file_handle = io.StringIO()
        laparams = LAParams()
        converter = TextConverter(resource_manager, fake_file_handle, laparams=laparams)
        page_interpreter = PDFPageInterpreter(resource_manager, converter)
        for page in PDFPage.get_pages(f, check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()

        # Close open handles
        converter.close()
        fake_file_handle.close()

    # Display extracted text in Streamlit
    st.text_area("PDF Content", text, height=300)

# Now when you call show_pdf, it should work:
# show_pdf(save_image_path)
def pdf_reader(file_path):
    # Extract text from the PDF
    with open(file_path, 'rb') as f:
        resource_manager = PDFResourceManager()
        fake_file_handle = io.StringIO()
        laparams = LAParams()
        converter = TextConverter(resource_manager, fake_file_handle, laparams=laparams)
        page_interpreter = PDFPageInterpreter(resource_manager, converter)
        for page in PDFPage.get_pages(f, check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()

        # Close open handles
        converter.close()
        fake_file_handle.close()

def course_recommender(course_list):
    """
    This function takes a list of courses as input and returns a formatted string
    with the course names and URLs for display in Streamlit.
    """
    course_recommendations = []
    for course in course_list:
        course_name, course_url = course
        course_recommendations.append(f"{course_name}: {course_url}")
    
    return "\n".join(course_recommendations)

    return text
def insert_data(name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses):
    connection = get_db_connection()
    cursor = connection.cursor()
    DB_table_name = 'user_data'
    
    # Truncate the courses string if it exceeds the column limit
    courses = courses[:600]  # Truncate to 600 characters
   
    insert_sql = sql.SQL("""
        INSERT INTO {} (Name, Email_ID, resume_score, Timestamp, Page_no, Predicted_Field, User_level, Actual_skills, Recommended_skills, Recommended_courses)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """).format(sql.Identifier(DB_table_name))
    
    rec_values = (name, email, str(res_score), timestamp, str(no_of_pages), reco_field, cand_level, skills, recommended_skills, courses)
    cursor.execute(insert_sql, rec_values)
    connection.commit()
    cursor.close()
    connection.close()


# Streamlit app
st.set_page_config(page_title="NLP Project Group 9", page_icon='/Users/arjunpesaru/Desktop/Project_NLP/Smart_Resume_Analyser_App-master/Logo/RESUME ANALYSIS CHATBOT.jpg')

def run():
    st.title("NLP CS6120 PROJECT- GROUP 9  Title:Resume Analysis Chatbot")
    st.sidebar.markdown("# Choose User")
    activities = ["Normal User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
    
    # Load and display the GIF instead of an image
    gif_path = '/Users/arjunpesaru/Desktop/Project_NLP/Smart_Resume_Analyser_App-master/Logo/Group9nlp.gif'
    st.image(gif_path, use_column_width=True)

    if choice == 'Normal User':
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            save_image_path = './Uploaded_Resumes/' + pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                resume_text = pdf_reader(save_image_path)

                st.header("**Resume Analysis**")
                st.success("Hello " + resume_data['name'])
                st.subheader("**Your Basic info**")
                try:
                    st.text('Name: ' + resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Resume pages: ' + str(resume_data['no_of_pages']))
                except:
                    pass
                
                cand_level = ''
                if resume_data['no_of_pages'] == 1:
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>You are looking Fresher.</h4>''', unsafe_allow_html=True)
                elif resume_data['no_of_pages'] == 2:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''', unsafe_allow_html=True)
                elif resume_data['no_of_pages'] >= 3:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!</h4>''', unsafe_allow_html=True)

                st.subheader("**Skills Recommendation💡**")
                keywords = st_tags(label='### Skills that you have', text='See our skills recommendation', value=resume_data['skills'], key='1')

                ds_keyword = ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep Learning', 'flask', 'streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress', 'javascript', 'angular js', 'c#', 'flask']
                android_keyword = ['android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy']
                ios_keyword = ['ios', 'ios development', 'swift', 'cocoa', 'cocoa touch', 'xcode']
                uiux_keyword = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes', 'storyframes', 'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator', 'illustrator', 'adobe after effects', 'after effects', 'adobe premier pro', 'premier pro', 'adobe indesign', 'indesign', 'wireframe', 'solid', 'grasp', 'user research', 'user experience']

                recommended_skills = []
                reco_field = ''
                rec_course = ''
                for i in resume_data['skills']:
                    if i.lower() in ds_keyword:
                        reco_field = 'Data Science'
                        st.success("** Our analysis says you are looking for Data Science Jobs.**")
                        recommended_skills = ['Data Visualization', 'Predictive Analysis', 'Statistical Modeling', 'Data Mining', 'Clustering & Classification', 'Data Analytics', 'Quantitative Analysis', 'Web Scraping', 'ML Algorithms', 'Keras', 'Pytorch', 'Probability', 'Scikit-learn', 'Tensorflow', "Flask", 'Streamlit']
                        recommended_keywords = st_tags(label='### Recommended skills for you.', text='Recommended skills generated from System', value=recommended_skills, key='2')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''', unsafe_allow_html=True)
                        rec_course = course_recommender(ds_course)
                        break

                    elif i.lower() in web_keyword:
                        reco_field = 'Web Development'
                        st.success("** Our analysis says you are looking for Web Development Jobs **")
                        recommended_skills = ['React', 'Django', 'Node JS', 'React JS', 'php', 'laravel', 'Magento', 'wordpress', 'Javascript', 'Angular JS', 'c#', 'Flask', 'SDK']
                        recommended_keywords = st_tags(label='### Recommended skills for you.', text='Recommended skills generated from System', value=recommended_skills, key='3')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''', unsafe_allow_html=True)
                        rec_course = course_recommender(web_course)
                        break

                    elif i.lower() in android_keyword:
                        reco_field = 'Android Development'
                        st.success("** Our analysis says you are looking for Android Development Jobs **")
                        recommended_skills = ['Android SDK', 'Android Studio', 'Java', 'Kotlin', 'XML', 'Flutter', 'Dagger', 'Room', 'Gradle']
                        recommended_keywords = st_tags(label='### Recommended skills for you.', text='Recommended skills generated from System', value=recommended_skills, key='4')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''', unsafe_allow_html=True)
                        rec_course = course_recommender(android_course)
                        break

                    elif i.lower() in ios_keyword:
                        reco_field = 'iOS Development'
                        st.success("** Our analysis says you are looking for iOS Development Jobs **")
                        recommended_skills = ['Swift', 'Cocoa', 'Objective-C', 'Xcode', 'CoreData', 'UIKit', 'AutoLayout', 'APIs', 'REST', 'MVC', 'MVVM']
                        recommended_keywords = st_tags(label='### Recommended skills for you.', text='Recommended skills generated from System', value=recommended_skills, key='5')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''', unsafe_allow_html=True)
                        rec_course = course_recommender(ios_course)
                        break

                    elif i.lower() in uiux_keyword:
                        reco_field = 'UI/UX Design'
                        st.success("** Our analysis says you are looking for UI/UX Design Jobs **")
                        recommended_skills = ['UX Research', 'Prototyping', 'Wireframing', 'User Testing', 'Interaction Design', 'Visual Design', 'Adobe XD', 'Figma', 'Sketch', 'Balsamiq']
                        recommended_keywords = st_tags(label='### Recommended skills for you.', text='Recommended skills generated from System', value=recommended_skills, key='6')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''', unsafe_allow_html=True)
                        rec_course = course_recommender(uiux_course)
                        break

                st.subheader("**Courses Recommendation📚**")
                try:
                    st.text("**Courses: **")
                    st.text(rec_course)
                except:
                    pass
                
                st.subheader("**Download/Print Your Resume**")
                with open(save_image_path, "rb") as file:
                    st.download_button(label="Download Your Resume", data=file, file_name=pdf_file.name, mime="application/pdf")
                
                insert_data(
                    name=resume_data.get('name', 'Unknown'),
                    email=resume_data.get('email', 'Unknown'),
                    res_score=resume_data.get('score', '0'),
                    timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    no_of_pages=resume_data.get('no_of_pages', 1),
                    reco_field=reco_field,
                    cand_level=cand_level,
                    skills=", ".join(resume_data.get('skills', [])),
                    recommended_skills=", ".join(recommended_skills),
                    courses=rec_course
                )

    if choice == 'Admin':
        st.header("**Admin Panel**")
        st.subheader("**View All User Data**")

        connection = get_db_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM user_data"
        df = pd.read_sql_query(query, connection)

        st.dataframe(df)
        cursor.close()
        connection.close()

        # Pie chart for Predicted Field Recommendations
        if not df.empty:
            field_counts = df['predicted_field'].value_counts()
            field_pie_chart = px.pie(
                field_counts,
                values=field_counts.values,
                names=field_counts.index,
                title="📊 Pie-Chart for Predicted Field Recommendations",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(field_pie_chart)

            # Pie chart for User's Experienced Level
            level_counts = df['user_level'].value_counts()
            level_pie_chart = px.pie(
                level_counts,
                values=level_counts.values,
                names=level_counts.index,
                title="📊 Pie-Chart for User's 🧑‍💻 Experienced Level",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(level_pie_chart)

if __name__ == '__main__':
    run()
