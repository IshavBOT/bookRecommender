from flask import Flask,render_template,request
import pickle
import numpy as np

popular_df = pickle.load(open('popular.pkl','rb'))

pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
popular_df = popular_df.merge(books[['Book-Title', 'Book-Author', 'Image-URL-M']].drop_duplicates('Book-Title'),
                              on='Book-Title',
                              how='left')

similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num-ratings'].values),
                           rating=list(popular_df['avg-rating'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books',methods=['post'])
def recommend():
    try:
        user_input = request.form.get('user_input')
        
        if not user_input:
            return render_template('recommend.html', error="Please enter a book title")
            
        if user_input not in pt.index:
            return render_template('recommend.html', error="Book not found in database")
            
        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            if not temp_df.empty:
                item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
                item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
                item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
                data.append(item)

        if not data:
            return render_template('recommend.html', error="No recommendations found")

        return render_template('recommend.html', data=data)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return render_template('recommend.html', error="An error occurred while processing your request")

if __name__ == '__main__':
    app.run(debug=True)