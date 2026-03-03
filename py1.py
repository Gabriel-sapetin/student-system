from flask import Flask, request, jsonify, render_template
import json
import re
import os

DATA_FILE = "groups.json"

app = Flask(__name__)

#SAVE DATA
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def sort_students(groups):
    order = {'1st': 1, '2nd': 2, '3rd': 3, '4th': 4}

    def group_key(g):
        program = g['program'].upper()
        third_letter = program[2] if len(program) > 2 else ' '
        return (third_letter, g['program'], order.get(g['year'], 999))

    #SORT STUDENTS IN EACH GROUP
    for g in groups:
        g['students'] = sorted(g['students'], key=str.lower)

    #SORT GROUPS
    return sorted(groups, key=group_key)

#ROUTES
@app.route('/')
def index():
    return render_template('html1.html')

@app.route('/save_group', methods=['POST'])
def save_group():
    data = request.json
    groups = load_data()

    program = data['program']
    year = data['year']
    new_students = data['students']

    #CHECK IF GROUP EXISTS
    group_found = False
    for group in groups:
        if group['program'] == program and group['year'] == year:
            existing_students = set(group['students'])
            for student in new_students:
                if student not in existing_students:
                    group['students'].append(student)
            group_found = True
            break

    if not group_found:
        groups.append({'program': program, 'year': year, 'students': new_students})

    #SORT STUDENTS 
    for group in groups:
        group['students'] = sorted(group['students'], key=str.lower)

    save_data(groups)
    return jsonify({'status': 'success'})

@app.route('/get_groups', methods=['GET'])
def get_groups():
    groups = load_data()
    sorted_groups = sort_students(groups)
    return jsonify({'groups': sorted_groups})

@app.route('/delete_group', methods=['POST'])
def delete_group():
    data = request.json
    program = data.get('program')
    year = data.get('year', '')

    groups = load_data()
    
    if year: #DELETE SPECIFIC YEAR
        groups = [g for g in groups if not (g['program'] == program and g['year'] == year)]
    else: 
        groups = [g for g in groups if g['program'] != program]

    save_data(groups)
    return jsonify({'status': 'deleted'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    app.run()
