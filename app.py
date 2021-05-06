
from flask import Flask, render_template, request, jsonify
from sqlalchemy import create_engine

from datetime import datetime 
import json
import pytz


app = Flask(__name__)
#set up database connectivity to flask app.
app._engine = create_engine('mysql://'+ "root" +':'+ "password" +'@'+ "localhost" +'/'+ "cargofl" + '?charset=utf8',echo=False,pool_size=50,max_overflow=16,pool_recycle=300)


@app.route("/add_question", methods = ['GET','POST'])
def add_question():
	data= {}
	try:
		if request.method=='POST' :
			'''Add entry to the database'''
			data["question"] = str(request.form['question']).strip().replace("'", "\\'")
			data["answer"] = str(request.form['answer']).strip().replace("'", "\\'") 
			data["module_name"] = str(request.form['module_name']).strip().replace("'", "\\'")
			data["submodule"] = str(request.form['submodule']).strip().replace("'", "\\'")
			data["notes"] = str(request.form['notes']).strip()
			data["language"] = str(request.form['language']).strip()
			data["added_by"] = "Rutvick"
			i = datetime.now(pytz.timezone('Asia/Kolkata'))
			data["added_on"] = i.strftime('%Y-%m-%d %H:%M:%S')
			data["enabled"] = "yes"
			result_add_status = add_ques_info(data)
			if result_add_status['status'] == True:
				return jsonify(result_add_status)
			else:
				return jsonify(result_add_status)
	except Exception as e:
		print(str(e))
		return jsonify({"message" : "Error while adding FAQ"})

def add_ques_info(data):
	response = {"status":False, "message":""}
	try:
		app._engine.execute("INSERT INTO `tl_faq_question_bank` (`question`, `answer`, `module_name`, `submodule`, `notes`,`language`,`added_by`, `added_on`, `enabled`) VALUES ('{question}', '{answer}', '{module_name}', '{submodule}', '{notes}', '{language}', '{added_by}', '{added_on}','{enabled}')"\
			.format(question = data['question'], answer =data['answer'], module_name = data['module_name'], submodule =data['submodule'] , notes =data['notes'] ,language=data['language'], added_by =data['added_by'] , added_on = data['added_on'], enabled = data['enabled']))
		response["status"] = True
		response["message"] = "Successfully added FAQ";
		return response
	except Exception as e:
		print(str(e))
		response["status"] = False
		response["message"] = "Error while adding FAQ";
		return response

@app.route('/', methods = ['GET'])
def manage_faq():
	faq_list = []
	raw_faq_dict = {}
	response = {"status" : "", "message" : ""}	
	try:
		# Get data from tl_faq_question bank table from the database.
		
		result_get_metadata = app._engine.execute("select tlfqb.question_id, tlfqb.module_name, tlfqb.submodule, tlfqb.question, tlfqb.answer from tl_faq_question_bank tlfqb")		
		for row in result_get_metadata:
			faq_list.append(dict(row.items()))
			#appends dictionary to list of dictionaries(faq_list).

		#for each dictionary in faq_list, add new module or add new question to the module if module and submodule name is same.
		for question in faq_list:
			if str(question["module_name"]+"-"+question['submodule']) in raw_faq_dict:
				raw_faq_dict[str(question["module_name"]+"-"+question['submodule'])].append(question)
			else:
				raw_faq_dict.update({str(question["module_name"]+"-"+question['submodule']):[question]})

		response['data'] = raw_faq_dict
		# to display questions and answers in UI.

		return render_template('/manage_faq.html', response = response)
	except Exception as e:
		return render_template('/manage_faq.html', response = response)


app.run(debug=True)