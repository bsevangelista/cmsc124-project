# LOLCODE Interpreter

A Python-based **LOLCODE Interpreter** with a graphical user interface (GUI) for writing, executing, and debugging LOLCODE programs. This project supports features such as tokenization, syntax analysis, semantic analysis, and dynamic console output for LOLCODE programs.

## Overview

LOLCODE is an esoteric programming language that is designed to be humorous and easy to read. It uses a unique syntax inspired by "lolspeak" or "internet slang". This project aims to provide a comprehensive tool for working with LOLCODE, from writing and editing the code to executing and analyzing the program's behavior.

## Features

The LOLCODE Compiler and Interpreter GUI includes the following key features:

1. **File Explorer**:
   - Allows users to open and edit LOLCODE (`.lol`) files directly within the application.
   - Provides a simple interface for managing and interacting with LOLCODE source code files.

2. **Text Editor**:
   - Includes a built-in text editor for writing and modifying LOLCODE programs.
   - Enables users to seamlessly execute their LOLCODE code directly from the text editor.

3. **Tokenization**:
   - Breaks down the LOLCODE source code into individual lexemes (tokens).
   - Classifies each token according to the LOLCODE language syntax.
   - Displays the identified tokens and their classifications in a dedicated "Tokens" panel.

4. **Syntax Analysis**:
   - Parses the LOLCODE code and constructs an Abstract Syntax Tree (AST) representation.
   - Validates the syntactical correctness of the LOLCODE program.
   - Provides feedback on any syntax errors detected during the parsing process.

5. **Semantic Analysis**:
   - Performs a deeper analysis of the LOLCODE program's logic and data flow.
   - Checks for semantic errors, such as variable declaration issues, type mismatches, and other logical inconsistencies.
   - Maintains a symbol table to track the state of program variables and their associated types.

6. **Interpreter**:
   - Executes the LOLCODE program by traversing the AST and interpreting the language constructs.
   - Dynamically displays the program's output in the integrated console.
   - Handles runtime errors and provides detailed error messages to help users debug their LOLCODE programs.

## Dependencies and Installation
### Python 3.8+
The LOLCODE Compiler and Interpreter is developed using Python 3.8 or later versions. To install Python 3.8 or a later version, follow these steps:

1. Go to the official Python website: [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Click on the "Download" button for the latest version of Python 3.
3. Run the installer and follow the on-screen instructions to complete the installation.

### Tkinter
Tkinter is a standard GUI library that comes pre-installed with Python, so no additional installation is required.

### IDE (Recommended)
While the project can be run from the command line, it is recommended to use an Integrated Development Environment (IDE) for a better development experience. Here's how you can install some popular IDEs:

**Visual Studio Code**:
1. Go to the Visual Studio Code website: [https://code.visualstudio.com/](https://code.visualstudio.com/)
2. Click on the "Download" button and select the appropriate version for your operating system.
3. Run the installer and follow the on-screen instructions to complete the installation.

**PyCharm**:
1. Go to the JetBrains website: [https://www.jetbrains.com/pycharm/download/](https://www.jetbrains.com/pycharm/download/)
2. Click on the "Download" button and select the appropriate version for your operating system.
3. Run the installer and follow the on-screen instructions to complete the installation.

Once you have installed the necessary dependencies, you can proceed to run the LOLCODE Compiler and Interpreter project.

## How to Run

To run the LOLCODE Compiler and Interpreter, follow these steps:

1. Ensure you have Python 3.8 or a later version installed on your system.
2. Clone the repository or download the source code files.
3. Open a terminal or command prompt and navigate to the project directory.
4. Run the following command to start the application:

   ```
   python semantics_analyzer.py
   ```

5. The LOLCODE Compiler and Interpreter GUI will launch, allowing you to write, execute, and debug your LOLCODE programs.

## References
- https://github.com/justinmeza/lolcode-spec/blob/master/v1.2/lolcode-spec-v1.2.md
