import xml.etree.ElementTree as ET
tree = ET.parse('shows.xml')
root = tree.getroot()

print("~~~~~~~~~~~~~~~~~~~~~~~~")
print("DEMO: Get list of shows:")
print("~~~~~~~~~~~~~~~~~~~~~~~~\n")

for date in root:
    print(date.attrib['name'])
    print("\t", "Free Play/Unscripted")
    for show in date.findall('show'):
        for status in show.findall('status'):
            if status.text.upper() == "ACTIVE":
                print("\t", show.attrib['name'])
                for aka in show.findall('aka'):
                    print("\t", aka.text)
print("")

print("~~~~~~~~~~~~~~~~~~~~~~~~")
print("DEMO: Get list of emails:")
print("~~~~~~~~~~~~~~~~~~~~~~~~\n")
for date in root:
    for show in date.findall('show'):
        for status in show.findall('status'):
            if status.text.upper() == "ACTIVE":
                for dj in show.findall('dj'):
                    print(dj.attrib['email'], end=", ")
# backspace added to remove the most recent comma
print("\b\b  \n")

community_count = 0
student_count   = 0
faculty_count   = 0
print("~~~~~~~~~~~~~~~~~~~~~~~~")
print("DEMO: Get DJ Statistics:")
print("~~~~~~~~~~~~~~~~~~~~~~~~\n")
for date in root:
    for show in date.findall('show'):
        for status in show.findall('status'):
            if status.text.upper() == "ACTIVE":
                for dj in show.findall('dj'):
                    if dj.attrib['type'] == "community":
                        community_count += 1            
                    elif dj.attrib['type'] == "student":
                        student_count += 1            
                    elif dj.attrib['type'] == "faculty":
                        faculty_count += 1

print("Community  DJs:", community_count)
print("Student    DJs:", student_count)
print("Faculty    DJs:", faculty_count)
print("")
print("Total DJ Count:", community_count + student_count + faculty_count)
