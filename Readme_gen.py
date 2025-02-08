# import os
# import ollama

# def generate_readme(directory):
#     """
#     Generate a README.md file for the given directory using Deepseek LLM.
#     """
#     # Get all files in the directory
#     files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
#     # Prepare content for LLM
#     file_content_summary = ""
#     for file in files:
#         file_path = os.path.join(directory, file)
#         try:
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 file_content = f.read()
#                 # Truncate file content to avoid sending too much data to LLM
#                 truncated_content = file_content[:1000]  # First 1000 characters
#                 file_content_summary += f"File: {file}\nContent:\n{truncated_content}\n\n"
#         except Exception as e:
#             print(f"Error reading {file}: {e}")
    
#     # Generate project description and file summaries using Deepseek
#     prompt = f"""
#     You are an AI assistant that generates README.md content for a project.
#     Below is the list of files and their partial content from the project directory.
#     Please provide:
#     1. A brief project description based on the files.
#     2. A short description of what each file does.

#     Files and Content:
#     {file_content_summary}
#     """
    
#     response = ollama.chat(model='deepseek-r1:latest', messages=[
#         {
#             'role': 'user',
#             'content': prompt,
#         }
#     ])
    
#     generated_content = response['message']['content']
    
#     # Write the generated content to README.md
#     readme_path = os.path.join(directory, "README.md")
#     with open(readme_path, 'w', encoding='utf-8') as readme_file:
#         readme_file.write(generated_content)
    
#     print(f"Generated README.md for directory: {directory}")

# def process_directory(root_dir):
#     """
#     Recursively process all directories and subdirectories to generate README.md files.
#     """
#     for dirpath, dirnames, filenames in os.walk(root_dir):
#         if filenames:  # Only process directories with files
#             print(f"Processing directory: {dirpath}")
#             generate_readme(dirpath)

# if __name__ == "__main__":
#     # Specify the root directory where your projects are located
#     root_directory = input("Enter the root directory path: ").strip()
    
#     if os.path.isdir(root_directory):
#         process_directory(root_directory)
#     else:
#         print(f"The provided path '{root_directory}' is not a valid directory.")



# ----------------------------------------- METHOD 2 ---------------------------------

import logging
from pathlib import Path
import argparse
import ollama

# Configure logging for better traceability
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def is_text_file(file_path: Path, blocksize: int = 512) -> bool:
    """
    Check if a file is a text file by reading a block of data.
    If a null byte is found, it is likely binary.
    """
    try:
        with file_path.open('rb') as f:
            block = f.read(blocksize)
            return b'\0' not in block
    except Exception as e:
        logging.error(f"Error determining file type for {file_path}: {e}")
        return False

def generate_file_summary(file_path: Path, max_chars: int = 1000) -> str:
    """
    Generate a summary of a file's content by reading up to max_chars.
    """
    try:
        with file_path.open('r', encoding='utf-8') as f:
            content = f.read(max_chars)
        return f"File: {file_path.name}\nContent:\n{content}\n\n"
    except Exception as e:
        logging.error(f"Error reading {file_path}: {e}")
        return f"File: {file_path.name}\nContent: [Error reading file]\n\n"

def generate_readme_for_directory(directory: Path, max_chars: int = 1000) -> None:
    """
    Generate a README.md file for the given directory using the Deepseek LLM.
    This function gathers file summaries, builds a prompt, sends it to the LLM,
    and writes the generated content to README.md.
    """
    file_summaries = []
    # Process each file in the directory (non-recursive)
    for file_path in directory.iterdir():
        if file_path.is_file() and file_path.name.lower() != "readme.md":  # skip README.md
            if is_text_file(file_path):
                summary = generate_file_summary(file_path, max_chars)
                file_summaries.append(summary)
            else:
                logging.info(f"Skipping non-text file: {file_path.name}")

    if not file_summaries:
        logging.info(f"No text files found in {directory}. Skipping README generation.")
        return

    file_content_summary = "\n".join(file_summaries)

    # Improved LLM prompt with more context and detailed instructions:
    prompt = f"""
You are a seasoned technical writer tasked with creating a comprehensive README.md for a software project repository.
Using the file names and partial contents provided below, please perform the following steps:

1. **Project Overview:**  
   - Identify the main purpose and functionality of the project.  
   - Draft a clear, concise, and engaging overview that outlines the project's goals.

2. **File Descriptions:**  
   - For each file, provide a brief description explaining its role within the project.  
   - If possible, note how the files interact or contribute to the overall functionality.

3. **Formatting:**  
   - Organize your response using Markdown.  
   - Use headings (e.g., `# Project Overview`, `## File Descriptions`) and bullet points where appropriate.  
   - Maintain clarity and brevity in your descriptions.

4. **Additional Suggestions:**  
   - Optionally, suggest any additional sections (such as Installation, Usage, or Contribution guidelines) that might enhance the documentation, if relevant.

Below is the list of files and their partial content:

{file_content_summary}
"""
    logging.info(f"Sending refined prompt to LLM for directory: {directory}")

    try:
        response = ollama.chat(
            model='deepseek-r1:latest',
            messages=[{'role': 'user', 'content': prompt.strip()}]
        )
    except Exception as e:
        logging.error(f"Error communicating with the LLM for {directory}: {e}")
        return

    # Validate the response
    if not response or 'message' not in response or 'content' not in response['message']:
        logging.error("Invalid response structure received from the LLM.")
        return

    generated_content = response['message']['content'].strip()

    # Write the generated README.md to the directory
    readme_path = directory / "README.md"
    try:
        with readme_path.open('w', encoding='utf-8') as f:
            f.write(generated_content)
        logging.info(f"Generated README.md for directory: {directory}")
    except Exception as e:
        logging.error(f"Error writing README.md in {directory}: {e}")

def process_directories(root_dir: Path, recursive: bool = True, max_chars: int = 1000) -> None:
    """
    Process directories to generate README.md files.
    If recursive is True, all subdirectories are processed.
    """
    if recursive:
        # Use rglob to recursively traverse directories
        for directory in root_dir.rglob("*"):
            if directory.is_dir():
                logging.info(f"Processing directory: {directory}")
                generate_readme_for_directory(directory, max_chars)
    else:
        logging.info(f"Processing directory: {root_dir}")
        generate_readme_for_directory(root_dir, max_chars)

def main():
    parser = argparse.ArgumentParser(
        description="Generate README.md files for project directories using the Deepseek LLM."
    )
    parser.add_argument("root_directory", type=str, help="Path to the root directory containing project folders.")
    parser.add_argument(
        "--non-recursive", action="store_true",
        help="Process only the root directory, not subdirectories."
    )
    parser.add_argument(
        "--max_chars", type=int, default=1000,
        help="Maximum number of characters to read from each file (default is 1000)."
    )
    args = parser.parse_args()

    root_dir = Path(args.root_directory)
    if not root_dir.is_dir():
        logging.error(f"The provided path '{args.root_directory}' is not a valid directory.")
        return

    process_directories(root_dir, recursive=not args.non_recursive, max_chars=args.max_chars)

if __name__ == "__main__":
    main()
