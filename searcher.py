import os
import json
import tkinter as tk
from tkinter import simpledialog, messagebox
import tempfile
import webbrowser

# Function to search for terms in JSON captions
def search_json_files(directory, primary_terms, additional_terms):
    results = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        for video_id, value in data.items():
                            if "captions" in value:
                                captions = value["captions"]
                                for i, caption in enumerate(captions):
                                    if any(term in caption["text"] for term in primary_terms):
                                        for offset in range(-5, 6):
                                            if offset == 0:
                                                continue
                                            idx = i + offset
                                            if 0 <= idx < len(captions):
                                                text = captions[idx]["text"]
                                                if any(term in text for term in additional_terms):
                                                    url = f"https://www.youtube.com/watch?v={video_id}&t={caption['start']}s"
                                                    results.append({
                                                        "file": os.path.join(root, file),
                                                        "primary_term": caption["text"],
                                                        "additional_term": text,
                                                        "line": idx,
                                                        "url": url
                                                    })
                    except Exception as e:
                        print(f"Error reading {file}: {e}")
    return results

# Function to write results to an HTML file and open with default browser
def display_results_in_browser(results):
    if results:
        html_content = "<html><head><title>Search Results</title></head><body>"
        html_content += "<h1>Search Results</h1><ul>"
        for result in results:
            html_content += f"<li><strong>File:</strong> {result['file']}<br>"
            html_content += f"<strong>Primary:</strong> {result['primary_term']}<br>"
            html_content += f"<strong>Additional:</strong> {result['additional_term']} (Line {result['line']})<br>"
            html_content += f"<strong>URL:</strong> <a href='{result['url']}'>{result['url']}</a><br><br></li>"
        html_content += "</ul></body></html>"
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as temp_file:
            temp_file.write(html_content)
            temp_file_path = temp_file.name
        webbrowser.open(f"file://{temp_file_path}")
    else:
        messagebox.showinfo("Search Results", "No matches found.")

# Create the Tkinter root object and set it to be always on top
root = tk.Tk()
root.withdraw()
root.attributes('-topmost', True)

# Prompt user for primary term and additional terms
primary_terms_str = simpledialog.askstring("Primary Terms", "Enter the primary search terms (comma-separated):")
if primary_terms_str:
    primary_terms = [term.strip() for term in primary_terms_str.split(',')]
    additional_terms_str = simpledialog.askstring("Additional Terms", "Enter additional search terms (comma-separated):")
    additional_terms = [term.strip() for term in additional_terms_str.split(',')] if additional_terms_str else []

    # Search and display results
    results = search_json_files(os.getcwd(), primary_terms, additional_terms)
    display_results_in_browser(results)
else:
    messagebox.showwarning("Input Error", "Primary terms are required.")

# Close the Tkinter root object
root.destroy()
