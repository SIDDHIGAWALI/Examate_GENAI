
import streamlit as st

st.title("Student Information Form")

# Text fields
name = st.text_input("Enter Name")
address = st.text_area("Enter Address")
roll_number = st.text_input("Enter Roll Number")
phone = st.text_input("Enter Phone Number")

# Image upload
image = st.file_uploader(
    "Upload Image",
    type=["jpg", "jpeg", "png"]
)

# Resume upload
resume = st.file_uploader(
    "Upload Resume",
    type=["pdf", "doc", "docx"]
)

# Submit button
if st.button("Submit"):
    if name and address and roll_number and phone:
        st.success("Information Submitted Successfully!")

        st.write("### Student Details")
        st.write("Name:", name)
        st.write("Address:", address)
        st.write("Roll Number:", roll_number)
        st.write("Phone Number:", phone)

        if image:
            st.write("### Student Image")
            st.image(image, width=200)

        if resume:
            st.write("### Resume")
            st.write("Uploaded:", resume.name)

    else:
        st.warning("Please fill in all required fields.")
