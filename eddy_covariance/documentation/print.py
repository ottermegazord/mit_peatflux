import os
import xmlformatter

fo = open("li840_log.xml", "r")
num_lines = sum(1 for line in open('li840_log.xml'))
fw = open("cleaned.xml", "a")
formatter = xmlformatter.Formatter(indent="1", indent_char="\t", encoding_output="ISO-8859-1", preserve=["literal"])

fw.write("<peatflux>")
for z in range (0, num_lines):
	try:
		stringy = fo.readline() 
		x = formatter.format_string(stringy)
		print(x)
		fw.write(x + '\n')
	except:
		pass
fw.write("</peatflux>")
fo.close()
fw.close()

