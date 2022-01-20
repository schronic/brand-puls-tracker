from google.cloud import vision

from dotenv import load_dotenv
load_dotenv()

def google_vision(uri):

    # Instantiates a client
    client = vision.ImageAnnotatorClient()
    response = client.annotate_image({
      'image': {'source': {'image_uri': uri}}
    })
    
    labels = response.label_annotations
    
    return labels

def image_describer(labels):

    image_details = []

    for label in labels:
        image_labels = {}
        image_labels["Label"] = label.description
        image_labels["Score"] = label.score
        image_labels["Topicality"] = label.topicality

    image_details.append(image_labels)

    return image_details