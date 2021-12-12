"""
Auther : Ashish Bhoi

Description : Program to do OCR in Exact sciences medical form

Date : 29/06/2020
"""
import os, io
from pdf2image import convert_from_path
from google.cloud import vision
from google.cloud.vision import types
import argparse 

#parse Argument
ap = argparse.ArgumentParser()
ap.add_argument('-i','--image',help='Path to input file')
ap.add_argument('-k','--key', help='Path to Secure access key')
args = vars(ap.parse_args())

#enable the enviroment key
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args["key"]

#assign the file path
filepath = args["image"]

ext = os.path.splitext(filepath)[-1].lower()

#if file is pdf then convert to image
if(ext == ".pdf"):
	img_counter = 1
	pages = convert_from_path(filepath, 500)
	print("Image files are created")
	for page in pages:
		img_name = "img_"+str(img_counter)+".jpg"
		IMG_PATH =  img_name
		page.save(IMG_PATH,'JPEG')
		img_counter += 1
	print("Enter image name on which you want to do OCR : ")
	IMAGE_FILE = input()

#if image file is already given
else:
	IMAGE_FILE  = args["image"]

client = vision.ImageAnnotatorClient()

FILE_PATH = IMAGE_FILE

with io.open(FILE_PATH, 'rb') as image:
	content = image.read()

image = types.Image(content=content)

response = client.document_text_detection(image = image)

doc = response.full_text_annotation

#counter variable for only first 10 lines
i = 0

#Variable to get the page number according to which diff
#part of code will activate
# 0 -> not set
# 1 -> First page
# 2 -> Second page 
page_num = 0

#Code to check page 1 for page 2
for line in doc.text.splitlines():
	#find the word cologuard order in first 10 lines
	if(line.find("REQUISITION") != -1):
		page_num = 1
		break
	elif(line.find("cologuard") != -1):
		page_num = 2
		break
	#check if 10 line are over
	if(i>10):
		break
	i = i+1

#if page 1 execute this code
if(page_num == 1):
	items = []
	lines = {}
	
	#for sector 1 fields
	print("\n"+"***********************"+"\n"+"S1"+"\n"+"***********************"+"\n")
	for text in response.text_annotations[1:]:
	    top_x_axis = text.bounding_poly.vertices[0].x
	    top_y_axis = text.bounding_poly.vertices[0].y
	    bottom_y_axis = text.bounding_poly.vertices[3].y

	    if top_y_axis not in lines:
	        lines[top_y_axis] = [(top_y_axis, bottom_y_axis), []]
	    for k, v in lines.items():
	        if (top_y_axis <= (v[0][0])+47 and top_y_axis < 1800 and top_x_axis < 990):
	            if bottom_y_axis >= (v[0][1]-30):
	                    lines[k][1].append((top_x_axis, text.description))
	                    break
	
	for _, item in lines.items():
	    if item[1]:
	        words = (item[1])
	        items.append((' '.join([word for _, word in words]))+'\n')
	
	for i in items:
		#health care org name
		 x = 0
		 for i in range(len(items)):
		     if((items[i].find("Healthcare Organization Name :")) != -1):
		     	x = i
		     	break
	hc_org_name_res = (items[x].replace('Healthcare Organization Name : ','')).strip('\n')

	#phone number
	provider_ph_num = ''
	for i in range(len(items)):
		if((items[i].strip().replace("-","").isnumeric()) == True):
			provider_ph_num = items[i].replace("\n","")
			break
		else:
			provider_ph_num = "None"

	#NPI number
	npi_res = ''
	count = 0
	for i in range(len(items)):
	    if((items[i].find("NPI")) != -1):
		    npi_res = items[i].replace("NPI # ","")
		    npi_res = npi_res.replace("/","")
		    npi_res = npi_res.replace('\n','')
		    npi_res = npi_res.replace(' ','')


    #location address
	loca_addr = ''
	flag = False
	for i in range(len(items)):
		if((items[i].find("Location Address"))!=-1) or flag == True:
			if((items[i].find("City , State"))!=-1):
				break
			flag = True
			loca_addr += items[i]
	loca_addr = loca_addr.replace('Location','')
	loca_addr = loca_addr.replace('Address','')
	loca_addr = loca_addr.replace(' : ','')
	loca_addr = loca_addr.replace(',','')
	loca_addr = loca_addr.replace('\n',' ').strip()


	#City, state, zip
	x = 0
	city_zip_res = []
	for i in range(len(items)):
		if(x == 2):
			break
		if((items[i].find("Zip")) != -1):
			temp = (items[i].replace('City , State , Zip : ',''))
			temp = temp.replace("\n","")
			city_zip_res.append(temp)
			x=x+1

	#Secure Fax Number 
	x = 0
	for i in range(len(items)):
	    if((items[i].find("Fax Number")) != -1):
	    	x = i
	    	break
	Secure_Fax_res = (items[x].replace('Secure',''))
	Secure_Fax_res = (Secure_Fax_res.replace('Fax',''))
	Secure_Fax_res = (Secure_Fax_res.replace('Number',''))
	Secure_Fax_res = (Secure_Fax_res.replace('*',''))
	Secure_Fax_res = (Secure_Fax_res.replace(':',''))
	Secure_Fax_res = (Secure_Fax_res.replace('.',''))
	Secure_Fax_res = Secure_Fax_res.replace(' ','')
	Secure_Fax_res = Secure_Fax_res.replace('\n','')

	#Patient ID / MRN 
	for i in items:
		x = 0
		for i in range(len(items)):
		    if((items[i].find("Patient ID / MRN")) != -1):
		    	x = i
		    	break
	MRN_res = (items[x].replace('Patient ID',''))
	MRN_res = (MRN_res.replace('/',''))
	MRN_res = (MRN_res.replace('MRN : ',''))
	MRN_res = (MRN_res.replace(': ',''))
	MRN_res = (MRN_res.replace(' ',''))
	MRN_res = (MRN_res.replace('\n',''))

	# #First Name and Last Name
	for i in items:
		x = 0
		for i in range(len(items)):
		    if((items[i].find("First Name :")) != -1):
		    	x = i
		    	break
	name_res = (items[x].replace('First Name :',''))
	name_res = (name_res.replace('Last Name :',''))
	name_res = (name_res.replace('\n',''))
	name_res = name_res.strip()

	##DOB 
	x = 0
	for i in range(len(items)):
		if((items[i].find("DOB")) != -1):
			x=i
			break
	DOB = str(''.join(filter(str.isdigit, items[x])))	
	dd_res = DOB[:2]
	mm_res = DOB[2:4]
	yy_res = DOB[4:]

	#Patient Sex
	patient_sex = ''
	x = 0
	for i in range(len(items)):
		if((items[i].find("Sex")) != -1):
			x=i
			break
	if((items[x].find("O Male")) != -1):
		patient_sex = "Female"
	else:
		patient_sex = "Male"

	#shipping address
	addr = ''
	flag = False
	for i in range(len(items)):
		if((items[i].find("Shipping"))!=-1) or flag == True:
			if((items[i].find("City , State"))!=-1):
				break
			flag = True
			addr += items[i]
	
	addr = addr.replace('Shipping Address : ','')
	addr = addr.replace(',','')
	addr = addr.replace('\n',' ').strip()

	#printing all extracted fields
	print("Provider Healthcare Org Name : ",hc_org_name_res)
	print("Provider NPI Number : ",npi_res)
	print("Provider Location Address : ",loca_addr)
	print("Provider City : ",city_zip_res[0])
	print("Provider Phone Number : ",provider_ph_num)
	print("Provider Fax Number : ",Secure_Fax_res)
	print("Patient ID/MRN : ",MRN_res)
	print("Patient Full Name : ",name_res)
	print("Patient DOB : {}/{}/{}".format(dd_res, mm_res, yy_res))
	print("Patient Gender : ",patient_sex)
	print("Patient Shipping Address : ",addr)
	print("Patient City :",city_zip_res[1])
	
	#for sector 2 fields
	print("\n"+"***********************"+"\n"+"S2"+"\n"+"***********************"+"\n")
	items = []
	lines = {}
	
	#for sector one fields
	for text in response.text_annotations[1:]:
	    top_x_axis = text.bounding_poly.vertices[0].x
	    top_y_axis = text.bounding_poly.vertices[0].y
	    bottom_y_axis = text.bounding_poly.vertices[3].y

	    if top_y_axis not in lines:
	        lines[top_y_axis] = [(top_y_axis, bottom_y_axis), []]
	    for k, v in lines.items():
	        if (top_y_axis <= (v[0][0])+20 and top_y_axis > 1000 and top_y_axis < 1800 and top_x_axis > 1000):
	            if bottom_y_axis >= (v[0][1]-20):
	                    lines[k][1].append((top_x_axis, text.description))
	                    break
	
	for _, item in lines.items():
	    if item[1]:
	        words = (item[1])
	        items.append((' '.join([word for _, word in words]))+'\n')

	#Phone Number ( required )
	ph_num_req_res = ''
	for i in range(len(items)):
		if((items[i].find("Phone Number ( required ) :")) != -1):
			ph_num_req_res = items[i].replace("Phone Number ( required ) :",'').strip()

	#Home mobile work
	num_type_res = ''
	for i in range(len(items)):
		if((items[i].find("Home")) != -1):
			num_type_res = items[i].replace("\n",'')
			break

	#Language Preference
	lang_res = ''
	for i in range(len(items)):
		if((items[i].find("Language Preference")) != -1):
			lang_res = items[i].replace("Language Preference","")
			lang_res = lang_res.replace("Language Preference","")
			lang_res = lang_res.replace("( optional )",'')
			lang_res = lang_res.replace(":",'')
			lang_res = lang_res.replace(" ",'')
			lang_res = lang_res.replace("\n",'')

	#Billing Address
	billing_addr = ''
	flag = False
	for i in range(len(items)):
		if((items[i].find("Billing Address")) != -1) or flag == True:
			if((items[i].find("City , State")) != -1):
				break
			else:
				billing_addr += items[i].strip()
				flag = True
	billing_addr = billing_addr.replace("Billing Address",'')
	billing_addr = billing_addr.replace(":",'')
	billing_addr = billing_addr.replace("Same",'')
	billing_addr = billing_addr.replace("as",'')
	billing_addr = billing_addr.replace("Shipping",'')
	billing_addr = billing_addr.replace("\n",'')

	#City, state, zip
	city_zip_s2_res = ''
	for i in range(len(items)):
		if((items[i].find("City , State , Zip")) != -1):
			city_zip_s2_res = items[i]
	city_zip_s2_res = city_zip_s2_res.replace("City","")
	city_zip_s2_res = city_zip_s2_res.replace("State","")
	city_zip_s2_res = city_zip_s2_res.replace("Zip","")
	city_zip_s2_res = city_zip_s2_res.replace(",","")
	city_zip_s2_res = city_zip_s2_res.replace(":","")
	city_zip_s2_res = city_zip_s2_res.replace(" ","")
	city_zip_s2_res = city_zip_s2_res.replace("\n","")

	print("Patient Ph. num(required) : ",ph_num_req_res)
	print("Mobile Type : ",num_type_res)
	print("Language : ",lang_res)
	print("Billing Address : ",billing_addr)
	print("Patient City : ",city_zip_s2_res)

	#for sector 3 fields
	print("\n"+"***********************"+"\n"+"S3"+"\n"+"***********************"+"\n")
	items = []
	lines = {}
	
	#for sector one fields
	for text in response.text_annotations[1:]:
	    top_x_axis = text.bounding_poly.vertices[0].x
	    top_y_axis = text.bounding_poly.vertices[0].y
	    bottom_y_axis = text.bounding_poly.vertices[3].y
	
	    if top_y_axis not in lines:
	        lines[top_y_axis] = [(top_y_axis, bottom_y_axis), []]

	    for s_top_y_axis, s_item in lines.items():
	        if top_y_axis < s_item[0][1]-20 and top_y_axis > 1800:
	            lines[s_top_y_axis][1].append((top_x_axis, text.description))
	            break	

	for _, item in lines.items():
	    if item[1]:
	        words = (item[1])
	        items.append((' '.join([word for _, word in words]))+'\n')
	
	#Patient wants to bill their insurance ?
	insurance_y_n = ''
	for i in range(len(items)):
		if((items[i].find("bill their insurance ?")) != -1):
			if((items[i].find("O Yes")) != -1):
				insurance_y_n = "No"
			elif((items[i].find("O No")) != -1):
				insurance_y_n = "Yes"
			else:
				insurance_y_n = "None"
	print("Does Patient wish Exact Sciences to bill their insurance : ",insurance_y_n)

	# #s3 fields Name DOB
	policyholder_name_res = ''
	res = ''
	flag = False
	for i in range(len(items)):
		if((items[i].find("Policyholder Name :")) != -1):
			res = items[i]

	#Policyholder Name	
	for i in res.split():
		if(i == 'DOB'):
			break
		policyholder_name_res += i

	policyholder_name_res = policyholder_name_res.replace("Policyholder","")
	policyholder_name_res = policyholder_name_res.replace("Name","")
	policyholder_name_res = policyholder_name_res.replace(":","")
	print("Policyholder Name : ",policyholder_name_res)


	#PolicyHolder DOB
	PolicyHolder_DOB_res = str(''.join(filter(str.isdigit, res)))	
	PolicyHolder_dd_res = PolicyHolder_DOB_res[:2]
	PolicyHolder_mm_res = PolicyHolder_DOB_res[2:4]
	PolicyHolder_yy_res = PolicyHolder_DOB_res[4:]
	print("Policyholder DOB : {}/{}/{}".format(PolicyHolder_dd_res,PolicyHolder_mm_res,
													PolicyHolder_yy_res))

	#Primary insurance carrier
	insurance_carrier = ''
	for i in range(len(items)):
		if((items[i].find("Primary Insurance Carrier")) != -1):
			temp = items[i].split()
			insurance_carrier = temp[4]

	print("Primary Insurance Carrier : ", insurance_carrier)
	
	#claim submission address
	submis_addr = ''
	for i in range(len(items)):
		if((items[i].find("Claims Submission Address")) != -1):
			submis_addr = items[i]

	submis_addr = submis_addr.replace("Claims Submission Address :","")
	submis_addr = submis_addr.replace("\n","")
	print("Sub Addr :", submis_addr)

	#Sub id, Group number and plan
	Sub_id_policy_num = ''
	group_num_res = ''
	plan_res = ''

	for i in range(len(items)):
		if(items[i].find("Group Number") != -1):
			group_num_res = items[i].replace('_',' ')
			group_num_res = group_num_res.split()
			Sub_id_policy_num = group_num_res[6]
			plan_res      = group_num_res[-1]
			group_num_res = group_num_res[10]			

	print("Sub_id_policy_num: ",Sub_id_policy_num)
	print("Group Number 	: ",group_num_res)
	print("Plan         	: ",plan_res)

	#Authorization code
	ath_code = ''
	for i in range(len(items)):
		if(items[i].find("Authorization Code") != -1):
			ath_code = items[i].split(":",1)[1]
			ath_code = ath_code.strip()
	print("Authorization Code : ",ath_code)

	with open("Image_1_Data.txt","w") as f:
		f.write("Provider Healthcare Org Name : ")
		f.write(hc_org_name_res)
		f.write("\n\n")
		f.write("Provider NPI Number : ")
		f.write(npi_res)
		f.write("\n\n")
		f.write("Provider Location Address : ")
		f.write(loca_addr)
		f.write("\n\n")
		f.write("Provider City : ")
		f.write(city_zip_res[0])
		f.write("\n\n")
		f.write("Provider Phone Number : ")
		f.write(provider_ph_num)
		f.write("\n\n")
		f.write("Provider Fax Number : ")
		f.write(Secure_Fax_res)
		f.write("\n\n")
		f.write("Patient ID/MRN : ")
		f.write(MRN_res)
		f.write("\n\n")
		f.write("Patient Full Name : ")
		f.write(name_res)
		f.write("\n\n")
		f.write("Patient DOB : ")
		f.write("{}/{}/{}".format(dd_res, mm_res, yy_res))
		f.write("\n\n")
		f.write("Patient Gender : ")
		f.write(patient_sex)
		f.write("\n\n")
		f.write("Patient Shipping Address : ")
		f.write(addr)
		f.write("\n\n")
		f.write("Patient City : ")
		f.write(city_zip_res[1])
		f.write("\n\n")
		f.write("Patient Ph. num(required) : ")
		f.write(ph_num_req_res)
		f.write("\n\n")
		f.write("Mobile Type : ")
		f.write(num_type_res)
		f.write("\n\n")
		f.write("Language : ")
		f.write(lang_res)
		f.write("\n\n")
		f.write("Billing Address : ")
		f.write(billing_addr)
		f.write("\n\n")
		f.write("Patient City : ")
		f.write(city_zip_s2_res)
		f.write("\n\n")
		f.write("Does Patient wish Exact Sciences to bill their insurance : ")
		f.write(insurance_y_n)
		f.write("\n\n")
		f.write("Policyholder Name : ")	
		f.write(policyholder_name_res)
		f.write("\n\n")
		f.write("Policyholder DOB : ")
		f.write("{}/{}/{}".format(PolicyHolder_dd_res,PolicyHolder_mm_res,PolicyHolder_yy_res))
		f.write("\n\n")
		f.write("Primary Insurance Carrier : ")
		f.write(insurance_carrier)
		f.write("\n\n")
		f.write("Sub Addr :")
		f.write(submis_addr)
		f.write("\n\n")
		f.write("Sub_id_policy_num: ")
		f.write(Sub_id_policy_num)
		f.write("\n\n")
		f.write("Group Number 	: ")
		f.write(group_num_res)
		f.write("\n\n")
		f.write("Plan         	: ")
		f.write(plan_res)
		f.write("\n\n")
		f.write("Authorization Code : ")
		f.write(ath_code)
		f.write("\n\n")
	print("****************** File is written ******************")

#if page 2 then execute this code
if(page_num == 2):
	items = []
	lines = {}
	
	for text in response.text_annotations[1:]:
	    top_x_axis = text.bounding_poly.vertices[0].x
	    top_y_axis = text.bounding_poly.vertices[0].y
	    bottom_y_axis = text.bounding_poly.vertices[3].y
	
	    if top_y_axis not in lines and top_y_axis > 1800:
	        lines[top_y_axis] = [(top_y_axis, bottom_y_axis), []]
	
	    for s_top_y_axis, s_item in lines.items():
	        if top_y_axis < s_item[0][1]-20:
	            lines[s_top_y_axis][1].append((top_x_axis, text.description))
	            break
	
	for _, item in lines.items():
	    if item[1]:
	        words = sorted(item[1], key=lambda t: t[0])
	        #items.append((item[0], ' '.join([word for _, word in words]), words))
	        items.append((' '.join([word for _, word in words]))+'\n')

	with open("image_2_data.txt","w") as f2:
		for i in items:
			print(i)
			f2.write(i)
			f2.write("\n\n")