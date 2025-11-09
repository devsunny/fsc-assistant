SPECT_TO_RUST_PROMPT = """You are an expert Rust developer tasked with creating a complete, functional Rust application based on the following user-provided specifications: 
    
{spec}

Your output must include:
- A complete Cargo.toml file with all necessary dependencies (use the latest stable versions where applicable, and minimize external crates unless explicitly required by the specs).
- The full source code structure, including src/main.rs and any additional modules or files (e.g., lib.rs, other .rs files in subdirectories if needed for organization).
- Use modern Rust best practices: idiomatic code, error handling with Result and anyhow crate if appropriate, async if the specs involve I/O or networking, and features like threads or parallelism only if relevant.
- Ensure the code compiles and runs without errors assuming a standard Rust environment (rustc and cargo installed).
- If the application involves user input, file handling, networking, or databases, handle edge cases gracefully (e.g., invalid input, connection failures).
- Do not include any placeholders or incomplete sections—generate fully working code.
- Do not include commentary, notes, or explanation in the output

Structure your response as follows:
1. Cargo.toml
2. Source code files (each in a markdown code block with the file path as header, e.g., ### src/main.rs)
3. Build and run instructions

Begin generating the application now based solely on the provided specs. Do not add features beyond what's specified.
"""
