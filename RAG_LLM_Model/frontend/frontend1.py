
import streamlit as st
import PyPDF2

st.title("Student Information Form")

# Student details
name = st.text_input("Enter Name")
address = st.text_input("Enter Address")
roll_number = st.text_input("Enter Roll Number")
phone = st.text_input("Enter Phone Number")

# Capture photo
photo = st.camera_input("Capture Photo")

# Upload Resume
resume = st.file_uploader(
    "Upload Resume",
    type=["pdf", "doc", "docx"]
)

# Chat input
chat_interface = st.chat_input("Type here")

# Submit button
if st.button("Submit"):

    if name and address and roll_number and phone:

        with st.container(border=True):

            st.success("Student Information Submitted!")

            st.subheader("Student Details")

            st.write("Name:", name)
            st.write("Address:", address)
            st.write("Roll Number:", roll_number)
            st.write("Phone Number:", phone)

            # Display photo
            if photo:
                st.subheader("Student Photo")
                st.image(photo, width=200)

            # Display resume
            if resume:
                st.subheader("Student Resume")
                st.write("File Name:", resume.name)

                # Read PDF content
                if resume.name.endswith(".pdf"):

                    pdf = PyPDF2.PdfReader(resume)

                    st.subheader("Resume Content")

                    for page in pdf.pages:
                        text = page.extract_text()
                        st.write(text)

            # Display chat input
            if chat_interface:
                st.subheader("Chat Message")
                st.write(chat_interface)

    else:
        st.warning("Please fill in all required fields.")
