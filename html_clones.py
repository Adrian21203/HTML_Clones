import os
from tkinter import Tk, filedialog, messagebox, Button, Label, Text, Scrollbar
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN
from collections import defaultdict
import numpy as np

# Function to extract text from an HTML file
def extract_text_from_html(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
        return soup.get_text().strip()

# Function to load all HTML files from a folder
def load_documents(folder_path):
    documents = {}
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".html"):
            file_path = os.path.join(folder_path, file_name)
            documents[file_name] = extract_text_from_html(file_path)
    return documents

# Function to compute the similarity matrix between documents
def compute_similarity(documents):
    if not documents:  
        return None
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents.values())
    similarity_matrix = cosine_similarity(tfidf_matrix)
    return similarity_matrix

# Function to group similar documents using DBSCAN
def group_similar_documents(documents, similarity_matrix, eps=0.2):
    if similarity_matrix is None:
        return []

    # Convert similarity matrix to distance matrix
    distance_matrix = 1 - similarity_matrix

    # Ensure that there are no negative values in the distance matrix
    distance_matrix[distance_matrix < 0] = 0

    # Perform DBSCAN clustering on the distance matrix
    clustering = DBSCAN(metric="precomputed", eps=eps, min_samples=1)
    labels = clustering.fit_predict(distance_matrix)

    # Group the documents based on the labels
    groups = defaultdict(list)
    for file_name, label in zip(documents.keys(), labels):
        groups[label].append(file_name)

    return list(groups.values())

def choose_folder():
    folder_path = filedialog.askdirectory(title="Select Main Folder")
    if not folder_path:
        return None
    return folder_path

def process_documents():
    folder_path = choose_folder()
    
    if folder_path is None:
        messagebox.showerror("Error", "No folder was selected!")
        return
    
    if not os.path.isdir(folder_path):
        messagebox.showerror("Error", f"Folder {folder_path} does not exist.")
        return

    output_text.config(state="normal")  
    output_text.delete(1.0, "end") 

    for tier in sorted(os.listdir(folder_path)):
        tier_path = os.path.join(folder_path, tier)
        
        if os.path.isdir(tier_path):  
            output_text.insert("end", f"\n\nProcessing {tier}...\n\n")
            
            documents = load_documents(tier_path)
          
            similarity_matrix = compute_similarity(documents)
            
            grouped_documents = group_similar_documents(documents, similarity_matrix)

            output_text.insert("end", f"\nGrouped Similar Documents in {tier}:\n")
            for i, group in enumerate(grouped_documents, 1):
                output_text.insert("end", f"\nGroup {i}:  [{', '.join(group)}]\n")
            output_text.insert("end", "-" * 50 + "\n")

    output_text.config(state="disabled") 

def reset_output():
    output_text.config(state="normal")  
    output_text.delete(1.0, "end")  
    output_text.config(state="disabled") 


root = Tk()
root.title("Group HTML Documents")
root.geometry("900x700")  

label = Label(root, text="Press the button below to choose a folder and process HTML documents.", font=("Helvetica", 12))
label.pack(pady=20)

process_button = Button(root, text="Choose Folder", command=process_documents, font=("Helvetica", 12))
process_button.pack(pady=20)

reset_button = Button(root, text="Reset", command=reset_output, font=("Helvetica", 12), bg="lightgrey")
reset_button.pack(pady=10)

output_text = Text(root, wrap="word", height=25, width=90, font=("Helvetica", 12))
output_text.pack(pady=10)

scrollbar = Scrollbar(root, command=output_text.yview)
scrollbar.pack(side="right", fill="y")
output_text.config(yscrollcommand=scrollbar.set)

output_text.config(state="disabled")

root.mainloop()
