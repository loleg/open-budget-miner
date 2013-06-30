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

# Iterate on the directorates
p_01 = re.compile(r'Direktion ')

# Drop the page number
p_00 = re.compile(r'(  +[6-7][0-9] +)')

# Correct buggy numbers
p_02 = re.compile(r'Nr\. Nr\. ')

# Extract meta
p_03 = re.compile('^(.*) Nr\. ([0-9a\.]+).*' +
				'Aufgabenfeld (.*)' +
				'Massnahme\(n\) (.*)' +
				'Kurzbeschrieb (.*)' +
				'\xc3\x84nderung Rechtsgrundlage\(n\) (.*)')

p_04 = re.compile(r'(Voranschlag[0-9].+Aufgaben-/Finanzplan)')

p_11 = re.compile(r'\nVoranschlag')

def munge_meta(txt):
	tcn = p_01.split(p_00.sub("", txt))

	for ix, d in enumerate(tcn):
		#print "\n\n----" + d + "<<<<\n\n"
		p = p_03.search(p_02.sub("Nr. ", d))
		if p: 
			#print p.groups()
			item = {
				"_ix": 				ix,
				"Direktion": 		p.groups()[0].strip(),
				"Nr": 				p.groups()[1].strip(),
				"Aufgabenfeld": 	p.groups()[2].strip(),
				"Massnahme": 		p.groups()[3].strip(),
				"Kurzbeschrieb":	p_04.sub("", p.groups()[4]).strip(),
				"Rechtsgrundlage":	p_04.sub("", p.groups()[5]).strip(),
				"Auswirkungen": {
					"Finanzielle": None,
					"Vollzeitstellen": None,
					"Gemeinden": None
				}
			}
			sys.stderr.write("Processing {" + item["Nr"] + "}\n")
			meta.append(item)
		else:
			sys.stderr.write("Skipping meta:\n---\n" + d + "<<<\n\n")

def munge_stat(txt):
	# Iterate on the directorates
	tcn = p_11.split(txt)

	p_lines = re.compile('\n')
	prevpd = False
	itemix = 0
	
	for ix, pd in enumerate(tcn):
		if not prevpd: prevpd = pd
		if "Aufgaben-/Finanzplan" in pd:
			#print "\n\n----" + pd + "<<<<\n\n"
			if r"\n" + meta[itemix]["Nr"] not in prevpd or r"Nr. " + meta[itemix]["Nr"] not in prevpd:
				try:
					item = next(x for x in meta if r"\n" + x["Nr"] in prevpd or r"Nr. " + x["Nr"] in prevpd)
					itemix = item["_ix"]
				except StopIteration: 
					item = False
				if not item: 
					sys.stderr.write("[warn] missing stat " + str(ix) + "\n")
					#sys.stderr.write("Skipping stats:\n---\n" + d + "<<<\n\n")
					continue
			else:
				itemix = itemix + 1
				item = meta[itemix]
			l = p_lines.split(pd)
			aus_fin = { "2014": l[2], "2015": l[10],  "2016": l[9], "2017": l[17] }
			aus_vol = { "2014": l[3], "2015": l[12], "2016": l[11], "2017": l[18] }
			aus_gem = { "2014": l[4], "2015": l[14], "2016": l[13], "2017": l[19] }
			item['Auswirkungen']['Finanzielle'] = aus_fin
			item['Auswirkungen']['Vollzeitstellen'] = aus_vol
			item['Auswirkungen']['Gemeinden'] = aus_gem
			sys.stderr.write("Tabulating {" + item["Nr"] + "}\n")
		#else:
			#sys.stderr.write("Skipping stats:\n---\n" + pd + "<<<\n\n")
		prevpd = pd
	for item in meta:
		del(item['_ix'])

filename = sys.argv[1].strip()
if filename.endswith(".pdf"):
	txt = convert_pdf(filename)
	munge_meta(txt)
	
	#print "Items read:", len(meta)
	#sys.stderr.write(txt)
	#print meta
	#quit

	txt = convert_pdf(filename, True)
	#print txt
	#quit
	munge_stat(txt)
	print json.dumps(meta)
	sys.stderr.write("Items read: " + str(len(meta)) + "\n")

else:
	print "Please provide PDF filename"
