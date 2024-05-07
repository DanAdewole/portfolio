from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(app, model_class=Base)


def serialize(self):
    dictionary = {}
    for column in self.__table__.columns:
        dictionary[column.name] = getattr(self, column.name)
    return dictionary

# models for sqlalchemy
class Image(db.Model):
    __tablename__ = 'image'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    img_name: Mapped[str] = mapped_column(db.String(255), nullable=True, unique=True)

    def __repr__(self) -> str:
        return self.img_name
    
    # automatically serialize date from model    
    def to_dict(self):
        serialize(self)


class Link(db.Model):
    __tablename__ = 'link'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    live_link: Mapped[str] = mapped_column(db.String, nullable=True)
    github_link: Mapped[str] = mapped_column(db.String, nullable=False)

    def __repr__(self) -> str:
        return self.github_link

    # automatically serialize date from model    
    def to_dict(self):
        serialize(self)


class Description(db.Model):
    __tablename__ = 'description'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    description: Mapped[str] = mapped_column(db.String, nullable=False)

    def __repr__(self) -> str:
        return self.description
    
    # automatically serialize date from model
    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

# create database instance
with app.app_context():
    db.create_all()


# routes
@app.route('/images', methods=["POST"])
def images():
    if request.method == 'POST':
        image = request.files['image']
        
        image.save(f'static/images/{image.filename}')
        try:
            save_image = Image(img_name=image.filename)
            db.session.add(save_image)
            db.session.commit()
            return jsonify({'success': 'image saved successfully'}), 200
        except:
            db.session.rollback()
            return jsonify({'error': "Image exist already"}), 400
    

@app.route('/image/<pk>', methods=['GET'])
def image(pk):
    try:
        image = Image.query.filter_by(id=pk).first()
        static_folder_path = os.path.join(app.root_path, 'static/images')
        full_image_path = os.path.join(static_folder_path, image.img_name)
        return jsonify({"image": full_image_path})
    except:
        return jsonify({"error": "Image does not exist"})
    

@app.route('/link', methods=['GET', 'POST'])
def links():
    if request.method == 'POST':
        live_link = request.json.get('live_link')
        github_link = request.json.get('github_link')
        try:
            save_link = Link(live_link=live_link, github_link=github_link)
            db.session.add(save_link)
            db.session.commit()
            return jsonify({'success': 'link created successfully'}), 200
        except:
            db.session.rollback()
            return jsonify({'error': "Link at that index does not exist"}), 400
        
    links = Link.query.all()
    return jsonify(
        links = [link.to_dict() for link in links]
    )

@app.route('/link/<pk>', methods=['GET', 'DELETE'])
def link(pk):
    if request.method == 'GET':
        try:
            link = Link.query.filter_by(id=pk).first()
            return jsonify(
                link = link.to_dict()
            )
        except:
            return jsonify({'error': "Link item does not exist"}), 400
    elif request.method == 'DELETE':
        link = Link.query.filter_by(id=pk).first()
        db.session.delete(link)
        db.session.commit()
        return jsonify({'success': 'link deleted successfully'}), 200


@app.route('/description', methods=['POST'])
def add_description():
    if request.method == 'POST':
        description = request.json.get('description')
        try:
            save_description = Description(description=description)
            db.session.add(save_description)
            db.session.commit()
            return jsonify({'success': 'description created successfully'}), 200
        except:
            db.session.rollback()
            return jsonify({'error': "Description at that index does not exist"}), 400


@app.route('/description/<pk>', methods=['GET', 'DELETE'])
def description(pk):
    if request.method == 'GET':
        try:
            description = Description.query.filter_by(id=pk).first()
            return jsonify(
                description = description.to_dict()
            )
        except:
            return jsonify({'error': "Description item does not exist"}), 400
    elif request.method == 'DELETE':
        description = Description.query.filter_by(id=pk).first()
        db.session.delete(description)
        db.session.commit()
        return jsonify({'success': 'description deleted successfully'}), 200


if __name__ == '__main__':
    app.run(debug=False)