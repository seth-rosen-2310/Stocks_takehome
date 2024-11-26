import base64
import os
from openai import OpenAI
from pdf2image import convert_from_path

API_KEY = ""
DEFAULT_PDF = "sample_doc.pdf"
DEFAULT_TOPICS = ["Account owner name", "Portfolio value", "Name and Total Cost Basis of each holding"]

#Function to handle all parts of pipeline in order to return information to user
def llm_call(query: str) -> dict:
    pdf = pdf_to_jpeg(DEFAULT_PDF)
    print(pdf)
    images = load_images()
    print(images)
    topics = DEFAULT_TOPICS
    content = build_content(topics, images)
    client = OpenAI(
    api_key=API_KEY
    )
    results = get_requested_info(client, content)
    return {"results":results}

#Encodes image for use in OpenAI api call to vision model
def encode_image(image_path: str) -> str:
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

#loads the pdf and saves it as jpeg for use in OpenAI api call
def pdf_to_jpeg(path_to_pdf: str) -> None:
    try:
        pages = convert_from_path(path_to_pdf, 500)
        for count, page in enumerate(pages):
            page.save(f'pages/pdf_page_{count}.jpg', 'JPEG')
    except:
       return ValueError

#Loads the Jpg images to be sent to OpenAI model in the content of call
def load_images(path_to_images: str = 'pages/'):
    try:
        images = [i for i in os.listdir(path_to_images)]
        images = list(filter(lambda i: i.endswith(('.jpg')), images))
        return images
    except:
       return ValueError

#Splits users topics if multiple are present
def split_topics(query: str) -> list:
   topics = query.split(",")
   return topics

#Creates the bulk of the prompt content needed to extract information from images using LLM
def build_content(topics: list, images: list) -> str:
    prompt_text = "Extract all the relevant text from the images to cover the categories below:"

    for t in topics:
       prompt_text += "\n- " + t + "\n"

    prompt_text += "Do not return any other value than the specified topic. If the specified topic cannot be found return N/A instead."

    prompt = [
          {"type": "text", "text": prompt_text }]
    
    for i in range(len(images)):
        base64_image = encode_image("pages/pdf_page_"+str(i)+".jpg")
        image_prompt = {
            "type": "image_url",
            "image_url": {
              "url": f"data:image/jpeg;base64,{base64_image}",
            },
          }
        prompt.append(image_prompt)

    return prompt

#Send the request to OpenAI model and returns the relevant information found by LLM
def get_requested_info(client: OpenAI, content: str) -> str:

  response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
      {
        "role": "user",
        "content": content
      }
    ],
    max_tokens=1000,
    temperature=0.01,
  )

  return response.choices[0].message.content