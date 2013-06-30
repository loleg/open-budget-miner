from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
import StringIO
import json
import sys
import re

meta = []

# See http://www.unixuser.org/~euske/python/pdfminer/
def convert_pdf(filename, with_params=False):
	rsrcmgr = PDFResourceManager()
	retstr = StringIO.StringIO()
	codec = 'utf-8'
	laparams = LAParams(
		line_overlap=0.5,
		char_margin=2.0,
		line_margin=2.0,
		word_margin=0.3,
		boxes_flow=0.5,
		detect_vertical=False,
		all_texts=False)

	if with_params:
		device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
	else:
		device = TextConverter(rsrcmgr, retstr, codec=codec)

	fp = file(filename, 'rb')
	process_pdf(rsrcmgr, device, fp)
	fp.close()
	device.close()

	str = retstr.getvalue()
	retstr.close()
	return str

def munge_meta(txt):
	# Drop the page number
	p_00 = re.compile('( +[6-7][0-9] +)')

	# Iterate on the directorates
	p_01 = re.compile('Direktion ')

	# Correct buggy numbers
	p_02 = re.compile('Nr\. Nr\. ')

	# Extract meta
	p_meta = '^(.*) Nr\. ([0-9a\.]+).*'
	p_meta += 'Aufgabenfeld (.*)'
	p_meta += 'Massnahme\(n\) (.*)'
	p_meta += 'Kurzbeschrieb (.*)'
	p_meta += '\xc3\x84nderung Rechtsgrundlage\(n\) (.*)'
	p_03 = re.compile(p_meta)
	
	p_04 = re.compile('(Voranschlag.+Aufgaben-/Finanzplan)')

	tcn = p_01.split(p_00.sub("", txt))

	for d in tcn:
		#print "\n\n----" + d + "<<<<\n\n"
		p = p_03.search(p_02.sub("Nr. ", d))
		if p: 
			#print p.groups()
			item = {
				"Direktion": 		p.groups()[0].strip(),
				"Nr": 				p.groups()[1],
				"Aufgabenfeld": 	p.groups()[2].strip(),
				"Massnahme": 		p.groups()[3].strip(),
				"Kurzbeschrieb":	p_04.sub("", p.groups()[4]).strip(),
				"Rechtsgrundlage":	p_04.sub("", p.groups()[5]).split('Voranschlag')[0].strip(),
				"Auswirkungen": {
					"Finanzielle": None,
					"Vollzeitstellen": None,
					"Gemeinden": None
				}
			}
			sys.stderr.write("Processing {" + item["Nr"] + "}\n")
			meta.append(item)

def munge_stat(txt):
	# Iterate on the directorates
	p_11 = re.compile('Voranschlag')
	tcn = p_11.split(txt)
	
	p_12 = re.compile('Aufgaben-/Finanzplan')
	
	p_lines = re.compile('\n')

	ix = 0
	for d in tcn:
		p = p_12.search(d)
		if p:
			#print "\n\n----" + d + "<<<<\n\n"
			l = p_lines.split(d)
			aus_fin = { "2014": l[2], "2015": l[10],  "2016": l[9], "2017": l[17] }
			aus_vol = { "2014": l[3], "2015": l[12], "2016": l[11], "2017": l[18] }
			aus_gem = { "2014": l[4], "2015": l[14], "2016": l[13], "2017": l[19] }
			meta[ix]['Auswirkungen']['Finanzielle'] = aus_fin
			meta[ix]['Auswirkungen']['Vollzeitstellen'] = aus_vol
			meta[ix]['Auswirkungen']['Gemeinden'] = aus_gem
			#print "\n\nNr: " + meta[ix]["Nr"]
			#print meta[ix]['Auswirkungen']
			sys.stderr.write("Tabulating {" + meta[ix]["Nr"] + "}\n")
			ix = ix + 1


filename = sys.argv[1].strip()
if filename.endswith(".pdf"):
	txt = convert_pdf(filename)
	munge_meta(txt)
	#print "Items read:", len(meta)
	#print txt
	print meta
	quit

	txt = convert_pdf(filename, True)
	munge_stat(txt)
	print json.dumps(meta)
	sys.stderr.write("Items read: " + str(len(meta)) + "\n")

else:
	print "Please provide PDF filename"
