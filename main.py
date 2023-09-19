import os
import csv
from pathlib import Path
from flask import Flask, jsonify, request, render_template

from werkzeug.utils import secure_filename

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = os.path.join(BASE_DIR, 'csv_files')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'csv_files')


@app.route('/api/files', methods=['GET'])
def get_data_files():
    files = os.listdir(DATA_DIR)
    file_info = []
    for file in files:
        with open(os.path.join(DATA_DIR, file), 'r') as f:
            reader = csv.reader(f)
            columns = next(reader)
            file_info.append({'file': file, 'columns': columns})
    return jsonify(file_info)


@app.route('/api/<name_file>', methods=['GET'])
def get_data(name_file):
    print(name_file)
    file = name_file + '.csv'
    filters = request.args.get('filters')
    sort_by = request.args.get('sort_by')
    try:
        with open(os.path.join(DATA_DIR, file), 'r') as f:
            reader = csv.DictReader(f)
            data = [row for row in reader]
    except FileNotFoundError:
        raise FileNotFoundError('Файла с таким именем не существует')
    if filters:
        filters = filters.split(',')
        data = [
            row for row in data if all(
                row[col] == val for col, val in zip(
                    filters[::2], filters[1::2]
                )
            )
        ]
    if sort_by:
        data = sorted(data, key=lambda row: row[sort_by])
    return jsonify(data)


@app.route("/", methods=["POST", "GET"])
def index():
    args = {"method": "GET"}
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        args["method"] = "POST"
    return render_template("index.html", args=args)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
