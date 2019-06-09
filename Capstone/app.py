from flask import Flask,render_template,request
app_lulu = Flask(__name__)
   
@app_lulu.route('/', methods=['GET'])
def input_page():
   return render_template('stock_main.html')

@app_lulu.route('/forecast', methods=['POST'])
def result_page():
   return render_template('result.html')

if __name__ == "__main__":
   app_lulu.run(debug=True)


