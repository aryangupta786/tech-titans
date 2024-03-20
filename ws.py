
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Load environment variables


# Configure GenAI
genai.configure(api_key=os.getenv("API_KEY"))
background_color = """
    <style>
    body {
        background-color: #f0f2f6; /* Change the color code as desired */
    }
    </style>
"""
# Display the background color
st.markdown(background_color, unsafe_allow_html=True)


# Function to get Gemini response
def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input, image[0], prompt])
    return response.text

# Function to set up image data
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [{"mime_type": uploaded_file.type, "data": bytes_data}]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Function to scrape Amazon and classify category
def scrape_amazon(search_query):
    url = f"https://www.amazon.in/s?k={search_query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    products = []

    # Extracting product details
    for product in soup.find_all('div', class_='sg-col-inner'):
        name_tag = product.find('span', class_='a-text-normal')
        if name_tag:
            name = name_tag.text.strip()
        else:
            name = 'Product name not available'

        price_tag = product.find('span', class_='a-offscreen')
        if price_tag:
            price = price_tag.text
        else:
            price = 'Price not available'

        link_tag = product.find('a', class_='a-link-normal')
        if link_tag:
            link = 'https://www.amazon.in' + link_tag['href']
        else:
            link = 'Link not available'

        # Classify category based on product name
        category = classify_category(name)
        
        products.append({'name': name, 'price': price, 'link': link, 'category': category})
    return products

# Function to scrape Flipkart and classify category
def scrape_flipkart(search_query):
    url = f"https://www.flipkart.com/search?q={search_query.replace(' ', '%20')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    products = []

    # Extracting product details
    for product in soup.find_all('div', class_='_1AtVbE'):
        name_tag = product.find('a', class_='IRpwTa')
        if name_tag:
            name = name_tag.text.strip()
        else:
            name = 'Product name not available'

        price_tag = product.find('div', class_='_30jeq3')
        if price_tag:
            price = price_tag.text.strip()
        else:
            price = 'Price not available'

        link_tag = product.find('a', class_='IRpwTa')
        if link_tag:
            link = 'https://www.flipkart.com' + link_tag['href']
        else:
            link = 'Link not available'

        # Classify category based on product name
        category = classify_category(name)
        
        products.append({'name': name, 'price': price, 'link': link, 'category': category})
    return products

# Function to scrape ShopClues and classify category
def scrape_shopclues(search_query):
    url = f"https://www.shopclues.com/search?q={search_query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    products = []

    # Extracting product details
    for product in soup.find_all('div', class_='column col3 search_blocks'):
        name_tag = product.find('h2')
        if name_tag:
            name = name_tag.text.strip()
        else:
            name = 'Product name not available'

        price_tag = product.find('span', class_='p_price')
        if price_tag:
            price = price_tag.text.strip()
        else:
            price = 'Price not available'

        link_tag = product.find('a')
        if link_tag:
            link = link_tag['href']
        else:
            link = 'Link not available'
            
                    # Classify category based on product name
        category = classify_category(name)
        
        products.append({'name': name, 'price': price, 'link': link, 'category': category})
    return products

# Function to classify category based on product name
def classify_category(product_name):
    # Convert product name to lowercase for case-insensitive matching
    product_lower = product_name.lower()
    
    # Define keywords for each category
    men_keywords = ['men', 'male', 'boy']
    women_keywords = ['women', 'female', 'girl']
    kids_keywords = ['kids', 'child', 'children', 'baby']
    
    # Check if product name contains any keywords
    if any(keyword in product_lower for keyword in men_keywords):
        return 'Men'
    elif any(keyword in product_lower for keyword in women_keywords):
        return 'Women'
    elif any(keyword in product_lower for keyword in kids_keywords):
        return 'Kids'
    else:
        return 'Unknown'

# Streamlit UI


st.header("Trend Suggestor Gpt")

# Input prompt and image upload
input_prompt = """
You are a talented fashion designer who excels in creating the perfect outfit combinations based on a given clothing image. Please provide only the name of the best combination of outfit pieces along with the image. Thank you!
"""
input_text = st.text_input("Input Prompt: ", key="input")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
image = ""   

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)

# Button to trigger Gemini response
submit = st.button("Tell me")
if submit:
    # Generate Gemini response
    image_data = input_image_setup(uploaded_file)
    response = get_gemini_response(input_text, image_data, input_prompt)
    if submit: 
        st.subheader("The Response is")
        st.write(response)
    # Display Gemini response in text input field

search_term = st.text_input("Enter search term based on the response:")

# Search platform selection
platform = st.selectbox("Select search platform:", ["Amazon", "Flipkart", "ShopClues"])

# Product search based on selected platform
st.title(' Product Search')
if st.button('Search'):
    if search_term:
        st.write(f'Searching for "{search_term}" on {platform}...')
        if platform == "Amazon":
            products = scrape_amazon(search_term)
        elif platform == "Flipkart":
            products = scrape_flipkart(search_term)
        elif platform == "ShopClues":
            products = scrape_shopclues(search_term)

        if products:
            st.write(f'Found {len(products)} products:')
            for product in products:
                st.write(f"Name: {product['name']}")
                st.write(f"Price: {product['price']}")
                st.write(f"Link: {product['link']}")
                st.write(f"Category: {product['category']}")
                st.write("---")
                       # Filter products without a link
            products_with_link = [product for product in products if product['link'] != 'Link not available']

            # Convert product data to DataFrame
            df = pd.DataFrame(products_with_link)

            if not df.empty:
                # Export DataFrame to CSV
                csv_filename = f"{search_term}_products.csv"
                df.to_csv(csv_filename, index=False)
                # st.write("CSV file created successfully!")
                st.success("CSV file created successfully!")
            else:
                st.write("No products with valid links found to export to CSV.")


