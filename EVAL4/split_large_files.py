import os


def split_text_file(input_file, output_folder, max_size=500):
    """
    Splits a large text file into smaller sub-files, ensuring reasonable size limits.

    :param input_file: Path to the large text file
    :param output_folder: Folder where the split files will be saved
    :param max_size: Maximum size of each output file in bytes (default: 50 KB)
    """

    os.makedirs(output_folder, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_file))[0]  # Extract base name without extension

    with open(input_file, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    paragraphs = text.split('\n')  # Splitting at paragraph boundaries
    current_size = 0
    part_number = 1
    buffer = []

    def write_part():
        """Helper function to write a file chunk."""
        nonlocal part_number, buffer, current_size
        if buffer:
            output_file = os.path.join(output_folder, f"{base_name}_part_{part_number}.txt")
            with open(output_file, 'w', encoding='utf-8') as out_f:
                out_f.write('\n\n'.join(buffer))
            part_number += 1
            buffer = []
            current_size = 0

    for para in paragraphs:
        para_size = len(para.encode('utf-8'))

        if para_size > max_size:
            # Split long paragraphs into sentences and add separately
            sentences = para.split('. ')
            sub_buffer = []
            sub_size = 0
            for sentence in sentences:
                sentence_size = len(sentence.encode('utf-8'))
                if sub_size + sentence_size > max_size and sub_buffer:
                    buffer.append('. '.join(sub_buffer))
                    write_part()
                    sub_buffer = []
                    sub_size = 0
                sub_buffer.append(sentence)
                sub_size += sentence_size
            if sub_buffer:
                buffer.append('. '.join(sub_buffer))
                write_part()
        else:
            if current_size + para_size > max_size and buffer:
                write_part()
            buffer.append(para)
            current_size += para_size

    write_part()  # Write any remaining content

    print(f"Splitting complete. {part_number - 1} files created in '{output_folder}'.")


# Example usage
split_text_file('court_case_report_1_fsm_vs_spain.txt', 'Test_reports')
