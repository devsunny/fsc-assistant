
from pathlib import Path
from assistant.utils.llm.img_utils import to_multipart_message
from assistant.llm.agent_client import AgentOrchestrator
from copy import deepcopy

PROMPT = """Perform Optical Character Recognition (OCR) on the following image/document text.

Output the result in Markdown format. Ensure that the original text content is extracted accurately, and the layout and structure (e.g., headings, bullet points, tables, line breaks, bolding) are preserved as closely as possible to the original source. Treat tables as Markdown tables."""



def debug_print_message_content(message):
    print("Message content for debugging:")
    role = message.get("role", "unknown")
    content = message.get("content", [])
    print(f"Role: {role}")
    for part in content:
        if isinstance(part, dict):
            if part.get("type") == "text":
                text = part.get("text", "")
                print(f"Text part: {text[:100]}...")  # Print first 100 chars
            elif part.get("type") == "image_url":
                url = part.get("image_url", {}).get("url", "")
                print(f"Image URL part: {url[:100]}...")  # Print first 100 chars
            else:
                print(f"Unknown content part: {part}")
        else:
            print(f"Non-dict content part: {part}")     


def ocr(image_path: Path) -> str:
    """Perform OCR on the given image using the AgentOrchestrator."""
    orchestrator = AgentOrchestrator(stream_handler=lambda x: print(x, end=""))
    message = to_multipart_message(
        prompt=PROMPT,
        image_path=image_path,
        max_bytes=4 * 1024 * 1024,  # 4 MB
    )
    try:
        response = orchestrator.invoke_chat_stream(inputs=[message])
        outf = image_path.parent / f"{image_path.stem}_ocr.md"
        with open(outf, "w", encoding="utf-8") as f:
            f.write(response)
        return response
    except Exception as e:
        print(f"Error during OCR: {e}")
        msg = deepcopy(message)
        debug_print_message_content(msg)       
        raise e


def main():
    image_dir = Path("images")
    for image_path in image_dir.iterdir():
        if image_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif"}:
            print(f"Processing image: {image_path}")
            result = ocr(image_path)         
    
    pass

if __name__ == "__main__":
    main()