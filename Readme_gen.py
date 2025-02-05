import os
import ollama

def generate_readme(directory):
    """
    Generate a README.md file for the given directory using Deepseek LLM.
    """
    # Get all files in the directory
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
    # Prepare content for LLM
    file_content_summary = ""
    for file in files:
        file_path = os.path.join(directory, file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
                # Truncate file content to avoid sending too much data to LLM
                truncated_content = file_content[:1000]  # First 1000 characters
                file_content_summary += f"File: {file}\nContent:\n{truncated_content}\n\n"
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    # Generate project description and file summaries using Deepseek
    prompt = f"""
    You are an AI assistant that generates README.md content for a project.
    Below is the list of files and their partial content from the project directory.
    Please provide:
    1. A brief project description based on the files.
    2. A short description of what each file does.

    Files and Content:
    {file_content_summary}
    """
    
    response = ollama.chat(model='deepseek-r1:latest', messages=[
        {
            'role': 'user',
            'content': prompt,
        }
    ])
    
    generated_content = response['message']['content']
    
    # Write the generated content to README.md
    readme_path = os.path.join(directory, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as readme_file:
        readme_file.write(generated_content)
    
    print(f"Generated README.md for directory: {directory}")

def process_directory(root_dir):
    """
    Recursively process all directories and subdirectories to generate README.md files.
    """
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if filenames:  # Only process directories with files
            print(f"Processing directory: {dirpath}")
            generate_readme(dirpath)

if __name__ == "__main__":
    # Specify the root directory where your projects are located
    root_directory = input("Enter the root directory path: ").strip()
    
    if os.path.isdir(root_directory):
        process_directory(root_directory)
    else:
        print(f"The provided path '{root_directory}' is not a valid directory.")