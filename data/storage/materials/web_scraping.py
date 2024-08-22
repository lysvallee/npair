from bs4 import BeautifulSoup
from statistics import mean
from os import chdir

html_file = "/data/storage/materials/Material References Documentation - Roblox Creator Hub.html"
# Open the HTML file
with open(html_file, "r") as file:
    html_content = file.read()

# Parse the HTML content
soup = BeautifulSoup(html_content, "html.parser")

# Find all 'figure' elements within the 'div' with class 'MuiGrid-root'
material_sections = soup.find_all(
    "div",
    class_="MuiGrid-root web-blox-css-tss-spvy06-Grid-root MuiGrid-item MuiGrid-grid-xs-6 MuiGrid-grid-lg-3 web-blox-css-mui-1y5f5z7",
)

# Loop through each section
for section in material_sections:
    # Find the 'figcaption' element within the section
    figcaption = section.find("figcaption")
    # Find the bold text element (<b>) containing the material name
    material_name = figcaption.find("b").text.strip()
    # Find roughness and metalness
    info_lines = figcaption.text.split(material_name)[1].split("  ")
    material_info = {}
    for info_line in info_lines:
        key, value = info_line.split(": ")
        # Caclculate the mean value when there is a range
        if "-" in value:
            value_low = float(value.split("-")[0])
            value_high = float(value.split("-")[1])
            value = mean([value_low, value_high])
        material_info[key] = round(float(value), 2)
    # Print the extracted information
    print(f"Material: {material_name}")
    print(f"Roughness: {material_info['Roughness']}")
    print(f"Metalness: {material_info['Metalness']}")
