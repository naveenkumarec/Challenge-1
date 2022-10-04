from __future__ import annotations
import os
from flask import Flask, abort, request,Response,json,jsonify
from flask_sqlalchemy import Model, SQLAlchemy
from marshmallow import Schema,fields


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
         'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Person(db.Model):
    __tablename__ = 'people'
    
    id = db.Column(db.Integer,primary_key=True)
    passengerClass = db.Column(db.String(10))
    name = db.Column(db.String(255))
    sex = db.Column(db.String(4))
    
    def __init__(self,id,passengerClass,name,sex):
        self.id = id
        self.passengerClass = passengerClass
        self.name = name
        self.sex = sex
    

class PersonSchema(Schema):
    id = fields.Int(required=True)
    passengerClass = fields.String(required=True)
    name = fields.String(required=True)
    sex = fields.String(required=True)



@app.route('/')
def get_all():
    person = Person.query.all()
    person_schema = PersonSchema(many=True)
    output = person_schema.dump(person)
    return custom_response(output, 200)

@app.route('/<int:person_id>/')
def get_by_id(person_id: int):
    person = Person.query.get(person_id)
    if person is None:
       return custom_response({'message': 'Person not found'},404)
    else:
        person_schema = PersonSchema()
        output = person_schema.dump(person)
        return custom_response(output,200)

@app.route('/<int:person_id>/delete/')
def delete(person_id: int):
    person = Person.query.get(person_id)
    db.session.delete(person)
    db.session.commit()
    return custom_response({'message': 'Person deleted'},200)

@app.route('/create/',methods=['POST'])
def create():
    request_data = request.get_json()
    person_schema = PersonSchema()
    data = person_schema.load(request_data)
    new_passenger = Person(id=data.get('id'),passengerClass=data.get('passengerClass'),name=data.get('name'),sex=data.get('sex'))
    db.session.add(new_passenger)
    db.session.commit()
    return custom_response({'message': 'New Person Added'},200)

@app.route('/<int:person_id>/update/',methods=['PUT'])
def update_person(person_id: int):
    person = Person.query.get(person_id)
    if person is None:
       return custom_response({'message': 'Person not found'},404)
    else:       
        request_data = request.get_json()
        for key,item in request_data.items():
            setattr(person,key,item)
        db.session.commit()
        person_schema = PersonSchema()
        people_serialized = person_schema.dump(person)
        return custom_response(people_serialized,200)

        

def custom_response(response_body: dict, status_code: int):
    return Response(
        mimetype="application/json",
        response=json.dumps(response_body),
        status=status_code
    )


if __name__ == '__main__':
    app.run(debug=True)