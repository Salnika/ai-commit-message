import os
import subprocess
import sys
import google.generativeai as genai
from git import Repo
import re
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: Gemini API key is not defined in the environment variables.")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)
MODEL = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-2.0-flash-001"))
MAX_DIFF_SIZE = int(os.getenv("MAX_DIFF_SIZE", 2000))

def get_modified_files():
    repo = Repo(".")
    diff = repo.index.diff("HEAD")
    modified_files = [item.a_path for item in diff if item.change_type == 'M']
    added_files = [item.a_path for item in diff if item.change_type == 'A']
    deleted_files = [item.a_path for item in diff if item.change_type == 'D']
    deleted_files_staged = [item.a_path for item in repo.index.diff(None) if item.change_type == 'D']
    return modified_files, added_files, deleted_files + deleted_files_staged

def get_file_diff(file_path):
    repo = Repo(".")
    try:
        diff = repo.git.diff(file_path)
    except:
        return ""
    return diff

def generate_commit_message(modified_files, added_files, deleted_files):
    try:
        with open("commit_prompt.txt", "r") as f:
            prompt_template = f.read()
    except FileNotFoundError:
        prompt_template = """
        Please generate a concise and informative commit message following the Conventional Commits specification 1.0.0, based on the following changes:

        Modified files: {modified_file_list}
        Added files: {added_file_list}
        Deleted files: {deleted_file_list}

        Here are the diffs for the modified files:

        {diff_information}

        The commit message should be in the following format:

        <type>[optional scope]: <description>

        [optional body]

        [optional footer(s)]

        Be specific and avoid vague terms. Consider the impact of the changes. Keep the description under 70 characters. Only provide the commit message itself, not any additional explanation or greeting. Provide only ONE commit message.
        """

    modified_file_list = "\n".join(modified_files)
    added_file_list = "\n".join(added_files)
    deleted_file_list = "\n".join(deleted_files)

    diff_info = ""
    total_diff_size = 0

    for file in modified_files:
        diff = get_file_diff(file)
        diff_size = len(diff)
        total_diff_size += diff_size
        if total_diff_size <= MAX_DIFF_SIZE:
            diff_info += f"\nDiff for {file}:\n{diff}"
        else:
            diff_info += "\nDiff information truncated due to size limits."
            break

    prompt = prompt_template.format(
        modified_file_list=modified_file_list,
        added_file_list=added_file_list,
        deleted_file_list=deleted_file_list,
        diff_information=diff_info
    )

    try:
        response = MODEL.generate_content(prompt)
        message = response.text.strip()
        return message, prompt
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None, None

def is_conventional_commit_format(message):
    pattern = r"^(feat|fix|chore|docs|style|refactor|perf|test)(\([a-z0-9-]+\))?:\s.+"
    return bool(re.match(pattern, message))

def main():
    args = sys.argv[1:]
    publish = False
    if "--publish" in args:
        publish = True
        args.remove("--publish")

    modified_files, added_files, deleted_files = get_modified_files()

    if not modified_files and not added_files and not deleted_files:
        print("No modified files detected.")
        subprocess.run(["git", "commit"] + args)
        return

    message, prompt = generate_commit_message(modified_files, added_files, deleted_files)

    if not message:
        print("Unable to generate commit message. Using standard git commit.")
        subprocess.run(["git", "commit"] + args)
        return

    if not is_conventional_commit_format(message):
        print("Warning: Generated commit message may not follow Conventional Commits.")
        print("It is recommended to review and adjust the message before committing.")

    print("\nProposed commit message:")
    print(message)

    if publish:
        subprocess.run(["git", "commit", "-m", message] + args)
        return

    while True:
        print("\nChoose an option:")
        print("1. Apply commit")
        print("2. Regenerate message")
        print("3. Enter message manually")
        print("4. Cancel all")

        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            subprocess.run(["git", "commit", "-m", message] + args)
            break
        elif choice == "2":
            message, prompt = generate_commit_message(modified_files, added_files, deleted_files)
            if not message:
                print("Failed to regenerate commit message.")
                continue
            if not is_conventional_commit_format(message):
                print("Warning: Regenerated commit message may not follow Conventional Commits.")
                print("It is recommended to review and adjust the message before committing.")

            print("\nProposed commit message:")
            print(message)

        elif choice == "3":
            message = input("Enter your commit message: ")
            subprocess.run(["git", "commit", "-m", message] + args)
            break
        elif choice == "4":
            print("Commit cancelled.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4")

if __name__ == "__main__":
    main()