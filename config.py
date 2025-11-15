"""Configuration constants for Datanorm-AZ processor."""

datafile = "docs/task_description/DATANORM.001"

# Default file encodings
default_input_encoding  = "latin-1"  # For DATANORM file reading
default_output_encoding = "utf-8"    # For CSV export

# Default output folder for CSV files (relative to project root)
default_output_folder = "output/"    # project-root/output

# Rounding precision for calculated prices and percentages
ROUND_TO_DEC_DIGIT = 2  # Number of decimal digits for rounding prices and percentages

