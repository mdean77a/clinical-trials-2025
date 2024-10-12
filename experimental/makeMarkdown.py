from IPython.display import display, Markdown
import os

""" 
This procedure writes the full Markdown document to disk.
"""

def makeMarkdown(markdownFile):

    # Combine all summaries into one string
    combined_markdown = "\n\n---\n\n".join(markdownFile)

    # Add a title to the combined document
    full_document = "# Full Informed Consent Document\n\n" + combined_markdown

    # Display the full document in the notebook
    display(Markdown(full_document))

    # Save the Markdown content to a file
    file_path = 'informed_consent_document.md'
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(full_document)

    print(f"Markdown document has been created: {os.path.abspath(file_path)}")