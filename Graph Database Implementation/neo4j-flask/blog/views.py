from .models import User, show_courses, search_by_name, search_by_pname, search_by_school
from flask import Flask, request, session, redirect, url_for, render_template, flash,jsonify
from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher
from neo4j import GraphDatabase

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/query'
driver = GraphDatabase.driver("bolt://localhost:7687")

@app.route('/')
def index():
    # posts = get_todays_recent_posts()
    return render_template('login.html')
	
def buildNodes(nodeRecord):
    data = {"id": nodeRecord._id, "label": list(nodeRecord._labels)[0]} #将集合元素变为list，然后取出值
    data.update(dict(nodeRecord._properties))

    return {"data": data}

def buildEdges(relationRecord):
    data = {"source": relationRecord.start_node._id,
            "target":relationRecord.end_node._id,
            "relationship": relationRecord.type}

    return {"data": data}

@app.route('/query')
def send_query():
    return

@app.route('/graph')
def get_graph():

#    matcher = NodeMatcher(graph)
#    existing_u1 = matcher.match("Students", name = session['username'])
#    print(existing_u1)
#    result=(graph.match((existing_u1,None), "修"))
#    print(result)   
    results=session.run('MATCH (s {name: "越祈"})-[t:修]->(c1:Courses)<-[p:先修*1..2]-(c2:Courses) RETURN s, c1, c2, t, p').values()
    nodeList=[]
    edgeList=[]
    for result in results:
        nodeList.append(result[0])
        nodeList.append(result[1])
        nodeList.append(result[2])
        nodeList=list(set(nodeList))
        edgeList.append(result[3])
#        edgeList.append(result[4])
 
    nodes = list(map(buildNodes, nodeList))
    edges= list(map(buildEdges,edgeList))
    return jsonify(elements = {"nodes": nodes, "edges": edges})
	
@app.route('/course', methods=['GET','POST'])
def course():
    if request.method == 'GET':
        courses = []
        courses.append(show_courses())
    elif request.method == 'POST':
        cond = request.form['condition']
        if request.form['search'] == "依課名查詢":
            courses = []
            courses.append(search_by_name(cond))
        elif request.form['search'] == "依教授查詢":
            courses = []
            courses.append(search_by_pname(cond))
        elif request.form['search'] == "依學校查詢":
            courses = []
            courses.append(search_by_school(cond))
        # elif request.form['search'] == "增加課名":
        #     courses = []
        #     courses.append(User(session['username']).add_course(cond))

    return render_template('course.html', courses = courses)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not User(username).verify_password(password):
            flash('Invalid login.')
        else:
            session['username'] = User(username).find()['name']
            flash('Logged in.')
            return redirect(url_for('profile', username = session['username']))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out.')
    return redirect(url_for('login'))

@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    logged_in_username = session.get('username')
    logged_in_user = User(logged_in_username)

    if request.method == 'POST':
        input1 = request.form['input1']
        input2 = request.form['input2']
        if request.form['submit'] == "增加課程":
            User(session['username']).add_course_history(input1, input2)
        elif request.form['submit'] == "刪除課程":
            User(session['username']).del_course_history(input1, input2)
        elif request.form['submit'] == "修改課程名稱":
            User(session['username']).mod_course_history(input1, input2)
        elif request.form['submit'] == "修改課程時間":
            User(session['username']).mod_time_history(input1, input2)

    histories = []
    histories.append(list(logged_in_user.get_course_history()))

    commons = []
    commons.append(list(logged_in_user.get_commonality_of_user()))
    
    recommend = []
    recommend.append(list(logged_in_user.course_recommend()))

    

    return render_template('profile.html', 
                           username=username, 
                           histories=histories, 
                           commons = commons,
                           recommend = recommend)
