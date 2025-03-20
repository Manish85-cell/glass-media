import streamlit as st
import requests
from transformers import BertTokenizer, BertForSequenceClassification
import torch
from googleapiclient.discovery import build
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image
import io

# API_URL = "https://fakenewsfilter.onrender.com/predict"

embedder = SentenceTransformer('all-MiniLM-L6-v2')
API_KEY = 'AIzaSyAsJyPU-W-IiNm525tyzdakLkFi0uXAdIY'
service = build('kgsearch', 'v1', developerKey=API_KEY)
OCR_API_KEY = "K89917156688957"  # Replace with your OCRSpace API Key

misinfo_model = BertForSequenceClassification.from_pretrained("checkpoint-3321")
misinfo_tokenizer = BertTokenizer.from_pretrained("checkpoint-3321")

# Example Usage

def predict_misinformation(text):
    inputs = misinfo_tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = misinfo_model(**inputs)
        logits = outputs.logits
        prediction = torch.argmax(logits, dim=-1).item()
    return prediction
# Define OCR function using OCRSpace API
def image_to_text(image):
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    response = requests.post(
        "https://api.ocr.space/parse/image",
        files={"file": ("image.png", img_bytes)},
        data={"apikey": OCR_API_KEY, "language": "eng"},
    )
    result = response.json()
    if result["OCRExitCode"] == 1:
        return result["ParsedResults"][0]["ParsedText"].strip()
    return "Error: Unable to extract text."





# Streamlit App UI
st.set_page_config(page_title="🔍Misinformation Detection", layout="wide")
st.markdown("# 🕵️ Misinformation Detection and Fact-Checking")

uploaded_file = st.file_uploader("Upload an image for text extraction", type=["png", "jpg", "jpeg"])
user_input = ""
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)
    extracted_text = image_to_text(image)
    st.subheader("Extracted Text")
    st.write(extracted_text)
    user_input = extracted_text
else:
    user_input = st.text_area("Enter text to check", placeholder="Type or paste text to analyze...", height=200)

if st.button("Check News"):
    if user_input:
        with st.spinner("Analyzing news..."):
            prediction = predict_misinformation(user_input)
            if prediction == 1:
                st.success("This news is real.")
            else:
                st.error("This news is fake.")
    else:
        st.warning("Please enter some text or upload an image.")
import google.generativeai as genai
# import wikipediaapi
# import streamlit as st

# Initialize Gemini API
genai.configure(api_key="AIzaSyA9UeawwH7VaaViDk3QUIUJXxoet6w7-GI")



def get_fact_check_verification(user_statement):
    """ Uses Gemini AI to fact-check the user statement. """
    
    # Extract main topic (first capitalized word)
    topic = next((word for word in user_statement.split() if word[0].isupper()), None)


    
    prompt = f"""
    You are an AI fact-checking assistant. Categorize the given statement into one of the following categories:
    - ✅ True: If the statement is entirely correct.
    - ❌ False: If the statement is incorrect or contradicts known facts.
    - 🤔 Likely True: If the statement is mostly correct but lacks some details.
    - ⚠ Likely False: If the statement is misleading or lacks proper context.
    
    Statement: "{user_statement}"
    """

    # Generate Gemini response
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    response = model.generate_content(prompt)
    return response.text.strip()

if st.button("Check Facts"):
    if user_input:
        with st.spinner("Fact-checking..."):
            result = get_fact_check_verification(user_input)
            st.markdown(f"### **Result:** {result}")
    else:
        st.warning("Please enter a statement.")

with st.expander("ℹ️ How to Use"):
    st.write("""
        - Enter the text or upload image you want to verify.
        - Click the appropriate button to check for misinformation or fact-check.
        - News-check AI will categorize it as **Real or Fake**.
        - Fact-check AI will verify and categorize it as **True, False, Likely True, or Likely False**.
    """)

