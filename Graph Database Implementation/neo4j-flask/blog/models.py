from py2neo import Graph, Node, Relationship, NodeMatcher
from passlib.hash import bcrypt
from datetime import datetime
import os
import uuid
import requests

url = os.environ.get('GRAPHENEDB_URL', 'http://localhost:7474')
username = os.environ.get('NEO4J_USERNAME')
password = os.environ.get('NEO4J_PASSWORD')

graph = Graph(url + '/db/data/', username=username, password=password)
matcher = NodeMatcher(graph)

class User:
    def __init__(self, username):
        self.username = username

    def find(self, ID = True):
        # user = graph.find_one('Students', 'sID', self.username)
        if ID:
            user = matcher.match('Students', ID = self.username).first()
        else:
            user = matcher.match('Students', name = self.username).first()
        return user
    
    def save_query(self, q):
        with open('blog/query.txt', 'w+', encoding = 'utf-8') as f:
            f.write(q)
            f.close()

        with open('blog/query.txt', 'r', encoding = 'utf-8') as f:
            query = f.read()
            r = requests.post('http://127.0.0.1:5000/query.txt', data = query.encode('utf-8'))
            r.text

    def register(self, password):
        if not self.find():
            # user = Node('User', username=self.username, password=password)
            # graph.create(user)
            return True
        else:
            return False

    def verify_password(self, password):
        user = self.find()
        if user:
            if str(password) == "000000":
                return True
            else:
                return False
        else:
            return False

    def get_commonality_of_user(self):
        query = '''
        MATCH (you:Students {name:{username}})-[:`修`]->(c:Courses)<-[:`修`]-(they:Students) 
        RETURN c.name, they.name
        ORDER BY c.name
        '''
        return graph.run(query, username=self.find(ID = False)['name']).to_table()
    
    def get_course_history(self):
        query = '''
        MATCH (Students {name:{username}})-[t:修]->(c:Courses)<-[:教]-(p:Professors)
        RETURN t.date, c.name, p.name
        ORDER BY t.date DESC
        '''
        return graph.run(query, username=self.find(ID = False)['name']).to_table()
        
    def course_recommend(self):
        q = "MATCH p=(:Students {name:{username}})-[:修]->(:Courses)<-[:先修*1..2]-(c:Courses) RETURN p"
        self.save_query(q)
        query = '''
        MATCH (:Students {name:{username}})-[:修]->(:Courses)<-[:先修*1..2]-(c:Courses)
        RETURN c.name, c.pre, c.stop
        '''
        return graph.run(query, username=self.find(ID = False)['name']).to_table()
		
    def add_course(self, condition):
        query = '''
        MATCH (a:Students),(c:Courses)
        WHERE a.name = { username } AND c.name = { condition }
        CREATE (a)-[r:修]->(c)
        '''
        return graph.run(query, username = self.find(ID = False)['name'], 
                         condition = condition).to_table()
	
    def add_course_history(self, time, condition):
        query = '''
		MATCH (s:Students {name: {username}}), (c:Courses {name: {condition}})
        CREATE (s)-[r:修 {date: {time}}]->(c)
        '''
        return graph.run(query, username = self.find(ID = False)['name'] ,
                        time=time, condition = condition).to_table()
    
    def del_course_history(self, time, condition):
        query = '''
		MATCH (:Students {name: {username}})-[t:修 {date: {time}}]->(:Courses {name: {condition}})
        DELETE t
        '''
        return graph.run(query, username = self.find(ID = False)['name'],
                        time=time, condition = condition).to_table()
    
    def mod_time_history(self, time, condition):
        query = '''
        MATCH (a:Students)-[t:`修`]->(c:Courses)
        WHERE a.name = { username } AND c.name = { condition }
        SET t.date = { time }
        '''
        return graph.run(query, username = self.find(ID = False)['name'] ,time=time, condition = condition).to_table()
		
    def mod_course_history(self, course1, course2):
        query = '''
        MATCH (a:Students)-[t:`修`]->(c:Courses),(c2:Courses)
        WHERE a.name = { username } AND c.name = { course1 } AND c2.name= { course2 } 
        create (a)-[x:`修`]->(c2)
        SET x.date = t.date 
        delete t
        '''
        return graph.run(query, username = self.find(ID = False)['name'] ,course1=course1, course2 = course2).to_table()
    
    # def course_recommend(self):
    #     query = '''
    #     MATCH (s:Students {name: {username}})-
    #     '''

def show_courses():
    query = '''
    MATCH (c:Courses)
    RETURN c.name, c.teacher, c.school, c.pre, c.stop, c.data
    '''
    return graph.run(query).to_table()

def search_by_name(condition):
    query = '''
    MATCH (c:Courses) 
    WHERE c.name CONTAINS { condition }
    RETURN c.name, c.teacher, c.school, c.pre, c.stop, c.data
    '''
    return graph.run(query, condition = condition).to_table()

def search_by_pname(condition):
    query = '''
    MATCH (p:Professors {name: { condition }}) 
    MATCH (c:Courses)
    WHERE (p)-[:教]->(c)
    RETURN c.name, c.teacher, c.school, c.pre, c.stop, c.data 
    '''
    return graph.run(query, condition = condition).to_table()

def search_by_school(condition):
    query = '''
    MATCH (c:Courses) 
    WHERE c.school = { condition }
    RETURN c.name, c.teacher, c.school, c.pre, c.stop, c.data
    '''
    return graph.run(query, condition = condition).to_table()

def date():
    return datetime.now().strftime('%Y-%m-%d')
