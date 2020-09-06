from flask import request, jsonify
from flask_cors import CORS, cross_origin
import configparser
from db_connection import *
from datetime import date, datetime
import time
import random
import smtplib
import configparser
import json
import os
from dotenv import load_dotenv
import jwt


from . import routes

prefix = '/admin'
load_dotenv()

# ------------------------------------APIs for TE Registration & Audio Recordings---------------------------------------



@routes.route(prefix + '/register', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def register_user():
    content = request.get_json()
    email = content['email']
    name = content['name']
    phone = content['phone']
    age = content['age']
    country = content['country']
    password = content['password']

    try:
        db = get_db_conection()
        cursor = db.cursor()

        cursor.execute(
            'INSERT INTO user_details(email_id,name,phone,age,country,password) VALUES (%s,%s,%s,%s,%s,%s)',
            (email, name, phone, age, country, password))

        return {"message": "Registered Successfully", "status": 201}, 201
    except Exception as e:
        print(e)
        return {"message": "Error"}, 400
    finally:
        db.commit()
        db.close()


@routes.route(prefix+'/login', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def user_login():
    try:
        if request.method == 'POST':
            db = get_db_conection()
            body = request.get_json()
            email = body['username']
            password = body['password']
            db = get_db_conection()
            cursor = db.cursor()
            cursor.execute(
                'SELECT * FROM user_details WHERE email_id = %s AND password = %s', (email, password,))
            account = cursor.fetchone()
            print(account)

            # If account exists in accounts table in out database
            if account:
                encoded_data = jwt.encode({'id':account[0],'name': account[1]}, 'secret', algorithm='HS256')
                encoded_data = encoded_data.decode('utf-8')
                return jsonify({"encodedData":encoded_data, "status":"1"})
            else:
                return {"status":"0"},200
    except Exception as e:
        print(e)
        db.close()
        return "error"


@routes.route(prefix + '/getPosts', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def get_posts():
    try:
        if request.method == 'GET':
            post_list = []
            db = get_db_conection()
            cursor = db.cursor()
            cursor.execute(
                "SELECT * FROM post_details order by timestamp desc")
            posts = cursor.fetchall()

            for post in posts:

                post_list.append({

                    "post_id": post[0],
                    "user_id":post[1],
                    "content": post[2],
                    "timestamp":post[3]
                })
            return jsonify({"post_list": post_list})
    except Exception as e:
        print(e)
        return jsonify({"status": "error"})
    finally:
        db.close()




@routes.route(prefix + '/getComments', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def get_comment():
    try:
        if request.method == 'POST':
            body = request.get_json()
            post_id = body['post_id']
            db = get_db_conection()
            cursor = db.cursor()
            cursor.execute(
                'select * from comment_details where post_id=%s',(post_id))
            db.commit()
            comment_list=''
            comments = cursor.fetchall()
            print(comments)


            for comment in comments:

                content='comment_id:{0},comment:{1}\n'.format(comment[0],comment[2])
                print(content)
                comment_list=comment_list+content

                # comment_list.add({
                #
                #     "comment_id": comment[0],
                #     "post_id": comment[1],
                #     "content": comment[2]
                # })

            db.close()
            print(comment_list)
            return jsonify({"comments":comment_list})




    except Exception as e:
        print(e)
        return jsonify({"status": "error"})




@routes.route(prefix + '/add_post', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def add_post():
    try:
        if request.method == 'POST':
            body = request.get_json()
            user_id = body['user_id']
            post_content = body['content']
            db = get_db_conection()
            cursor = db.cursor()
            cursor.execute(
                'INSERT INTO post_details(user_id,content) VALUES (%s,%s)', (user_id, post_content))
            db.commit()
            db.close()
            return jsonify({"status": "success"})
    except Exception as e:
        print(e)
        return jsonify({"status": "error"})


@routes.route(prefix + '/add_comment', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def add_comment():
    try:
        if request.method == 'POST':
            body = request.get_json()
            post_id = body['post_id']
            comment_content = body['comment_content']
            db = get_db_conection()
            cursor = db.cursor()
            cursor.execute(
                'INSERT INTO comment_details(post_id,content) VALUES (%s,%s)', (post_id, comment_content))
            db.commit()
            db.close()
            return jsonify({"status": "success"})
    except Exception as e:
        print(e)
        return jsonify({"status": "error"})



@routes.route(prefix + '/get_download_list', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def getDownloadList():
    try:
        body = request.get_json()
        speaker_id = body['speaker_id']
        db = get_db_conection()
        cursor = db.cursor()
        cursor.execute(
            "SELECT recordings,accent,age,gender,zipcode FROM speaker_details WHERE id = %s", (speaker_id,))
        rec = cursor.fetchone()
        recordings = rec[0]

        if recordings:
            recordings = recordings.split(',')
            today = datetime.now()
            d = today.strftime("%a, %d %b %Y %X %Z")
            cursor.execute(
                "update speaker_details set download_date = %s where id = %s", (d, speaker_id,))
            client = get_space_connection()
            download_urls = []
            if int(speaker_id) in range(1, 300):
                for recording in recordings:
                    file_name = speaker_id + 'q' + str(recording) + ".mp3"
                    key = 'speaker_id_' + speaker_id + '/' + file_name
                    url = client.generate_presigned_url(ClientMethod='get_object',
                                                        Params={'Bucket': 'pa_audio',
                                                                'Key': key},
                                                        ExpiresIn=300)
                    download_urls.append(
                        {"url": url, "title": file_name})
            else:
                accent = rec[1][0]
                age = str(rec[2])
                gender = rec[3][0]
                zipcode = rec[4]
                for recording in recordings:
                    file_name = "S" + speaker_id + "-Q" + \
                                str(recording) + "-" + age + "-" + gender + \
                                "-" + accent + "-" + zipcode + ".mp3"
                    key = "speaker_id_" + speaker_id + "/" + file_name
                    url = client.generate_presigned_url(ClientMethod='get_object',
                                                        Params={'Bucket': 'pa_audio',
                                                                'Key': key},
                                                        ExpiresIn=300)
                    download_urls.append(
                        {"q": recording, "url": url, "title": file_name})
            return {"status": "1", "download_list": download_urls}, 200
        else:
            return {"status": "0", "msg": "No recordings found for the selected speaker!!!"}, 400
    except Exception as e:
        print(e)
        return jsonify({"message": "error"})
    finally:
        db.commit()
        db.close()


@routes.route(prefix + '/analytics/locations', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def get_location_analytics():
    try:
        db = get_db_conection()
        cursor = db.cursor()
        cursor.execute(
            'select location,count(*) as count from speaker_details where location != \'\' and submitted_date != \'\' and recordings != \'\' group by location order by count desc limit 20;')
        data = cursor.fetchall()
        categories = []
        count = []
        for item in data:
            categories.append(item[0])
            count.append((item[1]))
        db.close()
        result = {"categories": categories, "count": count}

        return jsonify(result)

    except Exception as e:
        print(e)

        return "error"


@routes.route(prefix + '/analytics/registrations', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def get_registration_analytics():
    try:
        db = get_db_conection()
        cursor = db.cursor()
        cursor.execute(
            'select date,count(*) as count from speaker_details where submitted_date != \'\' group by date order by count desc limit 20;')
        data = cursor.fetchall()
        categories = []
        count = []
        for item in data:
            categories.append(item[0])
            count.append((item[1]))

        db.close()
        result = {"categories": categories, "count": count}

        return jsonify(result)

    except Exception as e:
        print(e)

        return "error"
