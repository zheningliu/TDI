from flask import Flask,render_template,request
app = Flask(__name__)
   
@app.route('/', methods=['GET'])
def input_page():
   return render_template('stock_main.html')

@app.route('/forecast', methods=['POST'])
def result_page():
   return render_template('result.html')

if __name__ == "__main__":
   app.run(debug=True)


