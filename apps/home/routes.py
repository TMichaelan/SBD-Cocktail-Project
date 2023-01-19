# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import psycopg2
from apps.home import blueprint
from flask import render_template, request, redirect, jsonify
from flask_login import login_required
from jinja2 import TemplateNotFound
import json


from apps.costyl import costyl, get_odpowiedz_koktajl, get_questions,get_questionnaire,get_coctail_sommelier,get_barmans, get_sommeliers, get_coctails
import psycopg2
import random

@blueprint.route('/index')
@login_required
def index():
    # costyl()

    conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
    cur = conn.cursor()

    querry_cotails = "select * FROM \"koktajl\" "
    cur.execute(querry_cotails)
    all_coctails = cur.fetchall()

    random_indexes = random.sample(range(len(all_coctails)), 9)
    
    coctails = []
    coctails_edited = []
    for index in random_indexes:
        coctails.append(all_coctails[index])

    

    for i in range(len(coctails)):

        querry_reviews =  "select * FROM \"odpowiedz_koktajl\" WHERE koktajl_nazwa=\'{}\'".format(coctails[i][0])
        cur.execute(querry_reviews)
        reviews = cur.fetchall()

        querry_som_reviews =  "select * FROM \"koktajl_sommelier\" WHERE koktajl_nazwa=\'{}\'".format(coctails[i][0])
        cur.execute(querry_som_reviews)
        som_reviews = cur.fetchall()


        mark = 0
        count_mark = 0

        coctails_edited.append([coctails[i][0],coctails[i][1],coctails[i][2],coctails[i][3]])
        coctails_edited[i][2] = 'There Are No Ratings Yet'
        coctails_edited[i][3] = 'There Are No Ratings Yet'

        for review in reviews:   
            print(review)
            if review[2]:
                count_mark+=1
                mark += review[2]

            if count_mark != 0:
                coctails_edited[i][2] = round(mark/count_mark,2)
            if count_mark == 0:
                coctails_edited[i][2] = 0

        mark1 = 0
        count_mark1 = 0

        for som_review in som_reviews:   
            if som_review[3]:
                count_mark1+=1
                mark1 += som_review[3]

            if count_mark1 != 0:
                coctails_edited[i][3] = round(mark1/count_mark1,2)
            if count_mark1 == 0:
                coctails_edited[i][3] = 0
            

    cur.close()
    conn.close()
 
    return render_template('home/index.html', segment='index', coctails=coctails_edited)


@blueprint.route('/index/<coctail_name>')
def product_page(coctail_name):

    coctail_name =  " ".join(coctail_name.split('-'))

    try:
        conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
        cur = conn.cursor()
        querry_cotails = "select * FROM \"koktajl\" WHERE nazwa=\'{}\'".format(coctail_name)
        cur.execute(querry_cotails)
        coctail = cur.fetchone()
        cur.close()
        conn.close()

        if coctail == None:
            return render_template('home/page-404.html'), 404
    except Exception as err:
        print(f'error occurred: {err}')
    try:
        conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
        cur = conn.cursor()
        querry_cotails = "select * FROM \"przepis\" WHERE nazwa_przepisa=\'{}\'".format(coctail_name)
        cur.execute(querry_cotails)
        recipe = cur.fetchone()

        querry_ingredients = "select * FROM \"skladnik_przepis\" WHERE przepis_nazwa_przepisa=\'{}\'".format(coctail_name)
        cur.execute(querry_ingredients)
        ingredients = cur.fetchall()

        querry_category =  "select * FROM \"kategoria_koktajli_koktajl\" WHERE koktajl_nazwa=\'{}\'".format(coctail_name)
        cur.execute(querry_category)
        category = cur.fetchall()


        querry_reviews =  "select * FROM \"odpowiedz_koktajl\" WHERE koktajl_nazwa=\'{}\'".format(coctail_name)
        cur.execute(querry_reviews)
        reviews = cur.fetchall()

        mark = 0
        count_mark = 0
        for review in reviews:
            if review[2]:
                count_mark+=1
                mark += review[2]

        coctail_edited = [coctail[0],coctail[1],coctail[2],coctail[3]]

        if count_mark != 0:
            coctail_edited[2] = round(mark/count_mark,2)
        else:
            coctail_edited[2] = 'There are no ratings yet'

        querry_sommielier =  "select * FROM \"koktajl_sommelier\" WHERE koktajl_nazwa=\'{}\'".format(coctail_name)
        cur.execute(querry_sommielier)
        sommeliers = cur.fetchall()
    
        cur.close()
        conn.close()
    except Exception as err:
        print(f'error occurred: {err}')
    
    return render_template('home/coctail.html', coctail=coctail_edited, recipe=recipe, ingredients = ingredients, category= category, reviews=reviews, sommeliers=sommeliers)

@blueprint.route('/sommelier.html',methods=('GET', 'POST'))
# @login_required
def sommelier():

    if request.method == 'POST':
        name = request.form['name']
        coctail = request.form['coctail']
        recencja = request.form['recencja']
        ocena = request.form['ocena']

        conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
        cur = conn.cursor()

        try: 
            querry_add_user = 'INSERT INTO \"sommelier\" VALUES (\'{}\');'.format(name)
            cur.execute(querry_add_user)
            conn.commit()
        except Exception as err:
            print(f'error occurred: {err}')
            conn.rollback()

        querry_add_coctail = 'INSERT INTO \"koktajl_sommelier\" VALUES (\'{}\', \'{}\',\'{}\',\'{}\');'.format(coctail, name, recencja, ocena)
        cur.execute(querry_add_coctail)
        conn.commit()
        cur.close()
        conn.close()
        return redirect('sommelier.html')


    try:
        users = get_sommeliers()
        coctails = get_coctails()
        coctails_som = get_coctail_sommelier()

        # Serve the file (if exists) from app/templates/home/FILE.html
        segment = get_segment(request)
        return render_template("home/sommelier.html" , segment=segment, users=users, len = len(coctails_som), coctails = coctails, coctails_som = coctails_som)
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


@blueprint.route('/add_review.html',methods=('GET', 'POST'))
# @login_required
def review():

    if request.method == 'POST':
        coctail = request.form['coctail']
        questionnaire = request.form['questionnaire']
        question_text = request.form['question_text']
        ocena = request.form['ocena']

        # print(username, email, password, github)

        conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
        cur = conn.cursor()
        querry_add_odpowiedz= 'INSERT INTO \"odpowiedz\" VALUES (\'{}\');'.format(question_text)
        cur.execute(querry_add_odpowiedz)
        conn.commit()

        querry_add_coctail = 'INSERT INTO \"odpowiedz_koktajl\" VALUES (\'{}\', \'{}\', \'{}\');'.format(question_text, coctail, ocena)
        cur.execute(querry_add_coctail)

     
        conn.commit()
        cur.close()
        conn.close()
        return redirect('add_review.html')


    try:
        coctails = get_coctails()
        questionnaires = get_questionnaire()
        reviews = get_odpowiedz_koktajl()
        # Serve the file (if exists) from app/templates/home/FILE.html
        segment = get_segment(request)
        return render_template("home/add_review.html" , segment=segment, reviews = reviews, coctails = coctails, questionnaires = questionnaires)
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


@blueprint.route('/questionnaire.html',methods=('GET', 'POST'))
# @login_required
def questionnaire():
    if request.method == 'POST':
        name = request.form['name']
        count = request.form['count']

        conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
        cur = conn.cursor()
        querry_add_user = 'INSERT INTO \"ankieta\" VALUES (\'{}\', \'{}\');'.format(name, count)
        cur.execute(querry_add_user)
        conn.commit()

        for i in range(int(count)):
            question_name = request.form['question_name'+str(i)]
            text = request.form['question_text'+str(i)]
            
            try: 
                querry_add_pytanie = 'INSERT INTO \"pytanie\" VALUES (\'{}\', \'{}\');'.format(question_name, text)
                cur.execute(querry_add_pytanie)
            except Exception as err:
                print(f'error occurred: {err}')

            querry_add_ankieta_pytanie = 'INSERT INTO \"ankieta_pytanie\" VALUES (\'{}\', \'{}\');'.format(name, question_name)
            conn.commit()
            cur.execute(querry_add_ankieta_pytanie)
            
        conn.commit()
        cur.close()
        conn.close()
        return redirect('questionnaire.html')


    try:
        users = get_questionnaire()
        segment = get_segment(request)
        return render_template("home/questionnaire.html" , segment=segment, users=users)
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


@blueprint.route('/questions.html',methods=('GET', 'POST'))
# @login_required
def question():
    try:
        users = get_questions()
        segment = get_segment(request)
        return render_template("home/questions.html" , segment=segment, users=users)
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


@blueprint.route('/delete-questionnaire', methods=['DELETE'])
def delete_questionnaire():
    # user_id = request.json
    name = request.form.get('name')

    try:
        conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
        cursor = conn.cursor()
        querry_delete_ankieta_pytanie = f"DELETE FROM \"ankieta_pytanie\" WHERE ankieta_nazwa=\'{name}\'"
        querry_delete_ankieta = f"DELETE FROM \"ankieta\" WHERE nazwa=\'{name}\'"
        cursor.execute(querry_delete_ankieta_pytanie)
        conn.commit()
        cursor.execute(querry_delete_ankieta)
        conn.commit()
        count = cursor.rowcount
        cursor.close()
        conn.close()
        return jsonify({"message": f"{count} user deleted"}), 200
        # return redirect('/', code=302)

    except (Exception, psycopg2.Error) as error :
        return jsonify({"error": str(error)}), 500


@blueprint.route('/coctails_cards.html',methods=('GET', 'POST'))
def coctails_cards():

    if request.method == 'POST':
        nazwa = request.form['nazwa']
        obraz = request.form['obraz']
        category = request.form['coctail']
        notatka = request.form['notatka']
        count = request.form['count']
        
        if (len(obraz) == 0):
            obraz = 'https://st4.depositphotos.com/14953852/22772/v/600/depositphotos_227725020-stock-illustration-image-available-icon-flat-vector.jpg'

        conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
        cur = conn.cursor()
        querry_add_przepis = 'INSERT INTO \"przepis\" VALUES (\'{}\', \'{}\', \'{}\');'.format(nazwa, count, notatka)
        querry_add_coctail = 'INSERT INTO \"koktajl\" VALUES (\'{}\', \'{}\');'.format(nazwa, obraz)


        # try: 
        #     querry_add_category = 'INSERT INTO \"kategoria_koktajli\" VALUES (\'{}\');'.format(category)
        #     cur.execute(querry_add_category)
        # except Exception as err:
        #     print(f'error occurred: {err}')



        cur.execute(querry_add_przepis)
        cur.execute(querry_add_coctail)

        conn.commit()

        
        querry_add_category_koktail = 'INSERT INTO \"kategoria_koktajli_koktajl\" VALUES (\'{}\', \'{}\');'.format(category, nazwa)
        cur.execute(querry_add_category_koktail)

        conn.commit()


        for i in range(int(count)):
            skladnik = request.form['ingredient'+str(i)]
            miara = request.form['measure'+str(i)]
            miara = miara.replace("'", ' ')
            try: 
                querry_add_skladnik = 'INSERT INTO \"skladnik\" VALUES (\'{}\');'.format(skladnik)
                cur.execute(querry_add_skladnik)
            except Exception as err:
                print(f'error occurred: {err}')

            querry_add_skladnik_przepis = 'INSERT INTO \"skladnik_przepis\" VALUES (\'{}\', \'{}\', \'{}\');'.format(skladnik, nazwa, miara)
            conn.commit()
            cur.execute(querry_add_skladnik_przepis)
     
        conn.commit()
        cur.close()
        conn.close()
        return redirect('coctails_cards.html')


    try:
        conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
        cur = conn.cursor()

        coctails = get_coctails()

        # print(coctai)
        coctails_edited = []

        for i in range(len(coctails)):

            querry_reviews =  "select * FROM \"odpowiedz_koktajl\" WHERE koktajl_nazwa=\'{}\'".format(coctails[i][0])
            cur.execute(querry_reviews)
            reviews = cur.fetchall()

            mark = 0
            count_mark = 0

            coctails_edited.append([coctails[i][0],coctails[i][1],coctails[i][2],coctails[i][3]])
            coctails_edited[i][2] = 'There Are No Ratings Yet'

            for review in reviews:   
                print(review)
                if review[2]:
                    count_mark+=1
                    mark += review[2]

                if count_mark != 0:
                    coctails_edited[i][2] = mark/count_mark
                if count_mark == 0:
                    coctails_edited[i][2] = 0

        segment = get_segment(request)
        return render_template("home/coctails_cards.html" , segment=segment, users=coctails_edited)
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500

@blueprint.route('/delete-review', methods=['DELETE'])
def delete_review():
    # user_id = request.json
    name = request.form.get('name')
    print(name)

    try:
        conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
        cursor = conn.cursor()
        query = f"DELETE FROM \"odpowiedz_koktajl\" WHERE odpowiedz_tekst_odpowiedzi=\'{name}\'"
        querry_delete_review = f"DELETE FROM \"odpowiedz\" WHERE tekst_odpowiedzi=\'{name}\'"
        cursor.execute(query)
        conn.commit()

        cursor.execute(querry_delete_review)
        conn.commit()
        count = cursor.rowcount
        cursor.close()
        conn.close()
        return jsonify({"message": f"{count} user deleted"}), 200
    except (Exception, psycopg2.Error) as error :
        return jsonify({"error": str(error)}), 500


@blueprint.route('/delete-sommelier', methods=['DELETE'])
def delete_sommelier():
    # user_id = request.json
    name = request.form.get('name')
    try:
        conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
        cursor = conn.cursor()
        query = f"DELETE from \"koktajl_sommelier\" WHERE id=\'{name}\'"
        cursor.execute(query)
        conn.commit()
        count = cursor.rowcount
        cursor.close()
        conn.close()
        return jsonify({"message": f"{count} user deleted"}), 200
        # return redirect('/', code=302)

    except (Exception, psycopg2.Error) as error :
        return jsonify({"error": str(error)}), 500


@blueprint.route('/modify-barman', methods=['PUT'])
def modifyBarman():
    id = request.form.get('id')
    name = request.form.get('name')
    surname = request.form.get('surname')
    phone = request.form.get('phone')
    adress = request.form.get('adress')

    try:
        conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
        cursor = conn.cursor()
        query = f"UPDATE \"barman\" SET imie=\'{name}\',nazwisko=\'{surname}\',numer_telefonu=\'{phone}\',adres=\'{adress}\' WHERE id=\'{id}\';"
        cursor.execute(query)
        conn.commit()
        count = cursor.rowcount
        cursor.close()
        conn.close()
        return jsonify({"message": f"{count} user modified"}), 200
    except (Exception, psycopg2.Error) as error :
        return jsonify({"error": str(error)}), 500 


@blueprint.route('/modify-questionnaire', methods=['PUT'])
def modifyQuestionnaire():
   
    name = request.form.get('name')
    count = request.form.get('count')
    
    question_names_desc = request.form.get('questions')

    print(request.form)
    print(request.form['questions'])
    print(name)
    print(count)
    # print(question_names_desc)
    return jsonify({}), 200
    # conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
    # cur = conn.cursor()
    # # querry_add_user = 'INSERT INTO \"ankieta\" VALUES (\'{}\', \'{}\');'.format(name, count)
    # update_add_pytaniee = f"UPDATE \"ankieta\" SET nazwa=\'{name}\',ilosc_pytan=\'{count}\' WHERE nazwa=\'{name}\';"
    # cur.execute(update_add_pytaniee)
    # conn.commit()

    # for i in range(int(count)):
    #     question_name = question_names_desc[i][0]
    #     text = question_names_desc[i][1]
 
    #     try: 
    #         # querry_add_pytanie = 'INSERT INTO \"pytanie\" VALUES (\'{}\', \'{}\');'.format(question_name, text)
    #         update_add_pytanie = f"UPDATE \"pytanie\" SET nazwa_pytanie=\'{question_name}\',tekst_pytania=\'{text}\' WHERE nazwa_pytanie=\'{question_name}\';"
    #         cur.execute(update_add_pytanie)
    #     except Exception as err:
    #         print(f'error occurred: {err}')

        # querry_add_ankieta_pytanie = 'INSERT INTO \"ankieta_pytanie\" VALUES (\'{}\', \'{}\');'.format(name, question_name)
        # update_add_pytanie = f"UPDATE \"ankieta_pytanie\" SET ankieta_nazwa=\'{name}\',pytanie_nazwa_pytanie=\'{text}\' WHERE nazwa_pytanie=\'{question_name}\';"
        # conn.commit()
        # cur.execute(querry_add_ankieta_pytanie)
                
    # conn.commit()
    # cur.close()
    # conn.close()
    # return redirect('questionnaire.html')

    # id = request.form.get('id')

    # surname = request.form.get('surname')
    # phone = request.form.get('phone')
    # adress = request.form.get('adress')

    # try:
    #     conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
    #     cursor = conn.cursor()
    #     query = f"UPDATE \"barman\" SET imie=\'{name}\',nazwisko=\'{surname}\',numer_telefonu=\'{phone}\',adres=\'{adress}\' WHERE id=\'{id}\';"
    #     cursor.execute(query)
    #     conn.commit()
    #     count = cursor.rowcount
    #     cursor.close()
    #     conn.close()
    #     return jsonify({"message": f"{count} user modified"}), 200
    # except (Exception, psycopg2.Error) as error :
    #     return jsonify({"error": str(error)}), 500 


@blueprint.route('/get-questionnaire-data', methods=(['GET']))
def getQuestionnaireData():
    name = request.args.get('name')
    try:
        conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
        cursor = conn.cursor()
        query = f"SELECT * FROM \"ankieta\" WHERE nazwa=\'{name}\'"
        cursor.execute(query)
        questionnaire_data = cursor.fetchone()
        cursor.close()
        conn.close()

        try:
            conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
            cursor = conn.cursor()
            query = f"SELECT pytanie_nazwa_pytanie FROM \"ankieta_pytanie\" WHERE ankieta_nazwa=\'{name}\'"
            cursor.execute(query)
            questions_name = cursor.fetchall()
            cursor.close()
            conn.close()
        except (Exception, psycopg2.Error) as error :
            return jsonify({"error": str(error)}), 500

        questions_name_list = []

        for questions_name in questions_name:
            questions_name_list.append(questions_name[0])

        questions = []
        try:
            for question in questions_name_list:
                conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
                cursor = conn.cursor()
                query = f"SELECT tekst_pytania FROM \"pytanie\" WHERE nazwa_pytanie=\'{question}\'"
                cursor.execute(query)
                questions_desc = cursor.fetchone()

                questions.append([question,questions_desc[0]])
                cursor.close()
                conn.close()
        except (Exception, psycopg2.Error) as error :
            return jsonify({"error": str(error)}), 500

        return jsonify({"name": questionnaire_data[0], "count": questionnaire_data[1],"questions": questions}), 200

    except (Exception, psycopg2.Error) as error :
        return jsonify({"error": str(error)}), 500


@blueprint.route('/modify-sommelier', methods=['PUT'])
def modifySommelier():
    id = request.form.get('id')
    name = request.form.get('name')
    coctail = request.form.get('coctail')
    recenzja = request.form.get('recenzja')
    ocena = request.form.get('ocena')

    try:
        conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
        cursor = conn.cursor()

        try: 
            querry_add_sommelier = 'INSERT INTO \"sommelier\" VALUES (\'{}\');'.format(name)
            cursor.execute(querry_add_sommelier)
            conn.commit()
        except Exception as err:
            print(f'error occurred: {err}')
            conn.rollback()

        query = f"UPDATE \"koktajl_sommelier\" SET koktajl_nazwa=\'{coctail}\',sommelier_pseudonim=\'{name}\',recenzja=\'{recenzja}\',ocena=\'{ocena}\' WHERE id=\'{id}\';"
        cursor.execute(query)
        conn.commit()
        count = cursor.rowcount
        cursor.close()
        conn.close()
        return jsonify({"message": f"{count} user modified"}), 200
    except (Exception, psycopg2.Error) as error :
        return jsonify({"error": str(error)}), 500 



@blueprint.route('/modify-review', methods=['PUT'])
def modifyReview():
    id = request.form.get('id')
    coctail = request.form.get('coctail')
    questionnaire = request.form.get('questionnaire')
    question_text = request.form.get('question_text')
    ocena = request.form.get('ocena')

    conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
    cursor = conn.cursor()

    try: 
        querry_add_odpowiedz = 'INSERT INTO \"odpowiedz\" VALUES (\'{}\');'.format(question_text)
        cursor.execute(querry_add_odpowiedz)
        conn.commit()
    except Exception as err:
        print(f'error occurred: {err}')
        conn.rollback()

    query = f"UPDATE \"odpowiedz_koktajl\" SET odpowiedz_tekst_odpowiedzi=\'{question_text}\',koktajl_nazwa=\'{coctail}\',ocena_uzytkownika=\'{ocena}\' WHERE id=\'{id}\';"
    cursor.execute(query)
    conn.commit()
    count = cursor.rowcount
    cursor.close()
    conn.close()
    return jsonify({"message": f"{count} user modified"}), 200
    
    # try:
    #     conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
    #     cursor = conn.cursor()

    #     try: 
    #         querry_add_odpowiedz = 'INSERT INTO \"odpowiedz\" VALUES (\'{}\');'.format(question_text)
    #         cursor.execute(querry_add_odpowiedz)
    #         conn.commit()
    #     except Exception as err:
    #         print(f'error occurred: {err}')
    #         conn.rollback()

    #     query = f"UPDATE \"odpowiedz_koktajl\" SET odpowiedz_tekst_odpowiedzi=\'{question_text}\',koktajl_nazwa=\'{coctail}\',ocena_uzytkownika=\'{ocena}\' WHERE id=\'{id}\';"
    #     cursor.execute(query)
    #     conn.commit()
    #     count = cursor.rowcount
    #     cursor.close()
    #     conn.close()
    #     return jsonify({"message": f"{count} user modified"}), 200
    # except (Exception, psycopg2.Error) as error :
    #     return jsonify({"error": str(error)}), 500 


@blueprint.route('/get-barman-data', methods=(['GET']))
def getBarmanData():
    name = request.args.get('name')
    try:
        conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
        cursor = conn.cursor()
        query = f"SELECT * FROM \"barman\" WHERE imie=\'{name}\'"
        cursor.execute(query)
        barman_data = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify({"name": barman_data[0], "surname": barman_data[1],"phone": barman_data[2], "address": barman_data[3],"id": barman_data[4], }), 200

    except (Exception, psycopg2.Error) as error :
        return jsonify({"error": str(error)}), 500


@blueprint.route('/get-sommelier-data', methods=(['GET']))
def getSommelierData():
    id = request.args.get('id')
    try:
        conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
        cursor = conn.cursor()
        query = f"SELECT * FROM \"koktajl_sommelier\" WHERE id=\'{id}\'"
        cursor.execute(query)
        sommelier_data = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify({"coctail": sommelier_data[0], "sommelier": sommelier_data[1],"recenzja": sommelier_data[2], "grade": sommelier_data[3],"id": sommelier_data[4], }), 200

    except (Exception, psycopg2.Error) as error :
        return jsonify({"error": str(error)}), 500


@blueprint.route('/get-review-data', methods=(['GET']))
def getReviewData():
    id = request.args.get('id')

    try:
        conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
        cursor = conn.cursor()
        query = f"SELECT * FROM \"odpowiedz_koktajl\" WHERE id=\'{id}\'"
        cursor.execute(query)
        review_data = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify({"review": review_data[0], "coctail": review_data[1], "grade": review_data[2],"id": review_data[3]}), 200

    except (Exception, psycopg2.Error) as error :
        return jsonify({"error": str(error)}), 500



@blueprint.route('/get-questionnaire-data', methods=(['GET']))
def getQuestionnaire():
    name = request.args.get('name')
    try:
        conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
        cursor = conn.cursor()
        query = f"SELECT * FROM \"ankieta_pytanie\" WHERE ankieta_nazwa=\'{name}\'"
        cursor.execute(query)
        questionnaire = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(questionnaire), 200


    except (Exception, psycopg2.Error) as error :
        return jsonify({"error": str(error)}), 500


  
@blueprint.route('/delete-barman', methods=['DELETE'])
def delete_user():
    # user_id = request.json
    name = request.form.get('name')

    try:
        conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
        cursor = conn.cursor()
        query = f"DELETE FROM \"barman\" WHERE imie=\'{name}\'"
        cursor.execute(query)
        conn.commit()
        count = cursor.rowcount
        cursor.close()
        conn.close()
        return jsonify({"message": f"{count} user deleted"}), 200
        # return redirect('/', code=302)

    except (Exception, psycopg2.Error) as error :
        return jsonify({"error": str(error)}), 500

@blueprint.route('/get_coctail_data', methods=(['GET']))
def getCoctaildata():
    name = request.args.get('name')
    print(name)

    try:
        conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
        cursor = conn.cursor()
        query = f"SELECT * FROM \"koktajl\" WHERE nazwa=\'{name}\'"
        cursor.execute(query)
        coctail_data = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify(coctail_data), 200

    except (Exception, psycopg2.Error) as error :
        return jsonify({"error": str(error)}), 500
        

@blueprint.route('/delete-user', methods=['DELETE'])
def delete_users():
    # user_id = request.json
    name = request.form.get('name')
    print(name)

    try:
        conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
        cursor = conn.cursor()
        query_delete_skladnik_przepis = f"DELETE FROM \"skladnik_przepis\" WHERE przepis_nazwa_przepisa=\'{name}\'"
        querry_delete_kategoria_koktajli_koktajl = f"DELETE FROM \"kategoria_koktajli_koktajl\" WHERE koktajl_nazwa=\'{name}\'"
        querry_delete_koktajl = f"DELETE FROM \"koktajl\" WHERE nazwa=\'{name}\'"
        querry_delete_przepis = f"DELETE FROM \"przepis\" WHERE nazwa_przepisa=\'{name}\'"

        cursor.execute(query_delete_skladnik_przepis)
        conn.commit()

        cursor.execute(querry_delete_kategoria_koktajli_koktajl)
        conn.commit()

        cursor.execute(querry_delete_koktajl)
        conn.commit()

        cursor.execute(querry_delete_przepis)
        conn.commit()

        count = cursor.rowcount
        cursor.close()
        conn.close()
        return jsonify({"message": f"{count} user deleted"}), 200
        # return redirect('/', code=302)

    except (Exception, psycopg2.Error) as error :
        return jsonify({"error": str(error)}), 500



@blueprint.route('/barman.html',methods=('GET', 'POST'))
@login_required
def barman():
    if request.method == 'POST':

        name = request.form['name']
        surname = request.form['surname']
        phone = request.form['phone']
        adres = request.form['adres']

        # print(username, email, password, github)

        conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
        cur = conn.cursor()
        querry_add_barman = 'INSERT INTO \"barman\" VALUES (\'{}\', \'{}\', \'{}\',\'{}\');'.format(name, surname, phone, adres)
        cur.execute(querry_add_barman)
     
        conn.commit()
        cur.close()
        conn.close()
        return redirect('barman.html')

    try:
        barmans = get_barmans()
        # Serve the file (if exists) from app/templates/home/FILE.html
        segment = get_segment(request)
        return render_template("home/barman.html" , segment=segment, barmans=barmans)
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404
        
        if username and email and password:
            conn = psycopg2.connect('postgresql://joramba:admin@localhost:5432/bazy_danych')
            cur = conn.cursor()
            querry_add_user = 'INSERT INTO \"Users\" (username, email, password, oauth_github) VALUES (\'{}\', \'{}\', \'{}\',\'{}\');'.format(username, email, password, github)
            cur.execute(querry_add_user)
        
            conn.commit()
            cur.close()
            conn.close()
            return redirect('coctails_cards.html')


    try:
        users = costyl()
        # Serve the file (if exists) from app/templates/home/FILE.html
        segment = get_segment(request)
        return render_template("home/coctails_cards.html" , segment=segment, users=users)
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500



@blueprint.route('/<template>', methods=('GET', 'POST'))
@login_required
def route_template(template):

    try:
        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)        
        
        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None