# Trivia API
This is my implementation of the Trivia API project from the Udacity Fullstack Web Developer Nanodegree.


## Running the App
This is a 3-tier app consisting of the frontend, the backend, and the database, and all of them must be running for the 
app to work.

#### Running and Initializing the Database
To start a PostgreSQL database server locally using Docker with a database created for the app, run the following 
command with Docker installed:
```shell script
docker run -d --name trivia-db -p 5432:5432 -e POSTGRES_PASSWORD=password -e POSTGRES_DB=trivia postgres:12
```

#### Starting the Backend Server 
##### Locally
To start the backend server you will need to have Python 3.7 installed (will not work on 3.8). You will also need to 
have a PostgreSQL server running locally on port `5432` with a user named `postgres` and password `password`. 

Open a terminal and navigate to the `backend` directory and do the following steps:

* Intall the dependencies:
```shell script
pip install -r requirements.txt
```
* Start the app server:
```shell script
FLASK_APP=flaskr flask run
```
* If all went well then the server will be running at `localhost:5000`

##### With Docker
To start the backend server using Docker follow the steps:

* Build the Docker image:
```shell script
docker build . -t trivia:SNAPSHOT
```
* Run the Docker image:
```shell script
docker run -it --rm --name trivia --link trivia-db:localhost -p 5000:5000 trivia:SNAPSHOT
```
* If all went well then the server will be running at `localhost:5000`

This assumes that you have already started a PostgreSQL server using Docker with name `trivia-db` as in the steps above.

#### Starting the Frontend Server
To start the frontend server you will need to have NodeJS 10 and `npm` installed. open a terminal and navigate to the `frontend` directory and execute the following 
commands:
* Install the dependencies:
```shell script
npm install
```
* Start the frontend server:
```shell script
npm start
```
Now you should be able to access the app at the URL `http://localhost:3000`.


## API Reference
#### Getting Started
* Base URL: This app can only run locally, and the backend server can be reached at `http://localhost:5000` which is set
as a proxy in the frontend app configuration.

* Authentication: This version of the app does not require authentication.

#### Error Handling
Errors are returned as JSON objects in the following format:

```json
{
  "success": false,
  "error": "bad request",
  "code": 400
}
```

The API will return the following error types when requests fail:

* 400: Bad request
* 404: Not found
* 415: Unsupported media type
* 422: Not processable
* 500: Internal error

#### Endpoints

##### `GET` `/api/categories`
* General
    * Returns all the available categories.
* Success status code: `200`
* Sample: `curl http://localhost:5000/api/categories`
```json
{
  "categories": [
    "Science",
    "Art",
    "Geography",
    "History",
    "Entertainment",
    "Sports"
  ],
  "success": true
}
```

##### `GET` `api/questions`
* General
    * Returns all questions.
    * Results are paged in sets of 10.
* Query Parameters
    * `page`: The page number starting from 1.
* Success status code: `200`
* Sample: `curl http://localhost:5000/api/questions?page=2`
```json
{
  "categories": [
    "Science",
    "Art",
    "Geography",
    "History",
    "Entertainment",
    "Sports"
  ],
  "current_category": null,
  "questions": [
    {
      "answer": "Agra",
      "category": "Geography",
      "difficulty": 2,
      "id": 15,
      "question": "The Taj Mahal is located in which Indian city?"
    },
    {
      "answer": "Escher",
      "category": "Art",
      "difficulty": 1,
      "id": 16,
      "question": "Which Dutch graphic artist–initials M C was a creator of optical illusions?"
    },
    {
      "answer": "Mona Lisa",
      "category": "Art",
      "difficulty": 3,
      "id": 17,
      "question": "La Giaconda is better known as what?"
    },
    {
      "answer": "One",
      "category": "Art",
      "difficulty": 4,
      "id": 18,
      "question": "How many paintings did Van Gogh sell in his lifetime?"
    },
    {
      "answer": "Jackson Pollock",
      "category": "Art",
      "difficulty": 2,
      "id": 19,
      "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
    },
    {
      "answer": "The Liver",
      "category": "Science",
      "difficulty": 4,
      "id": 20,
      "question": "What is the heaviest organ in the human body?"
    },
    {
      "answer": "Blood",
      "category": "Science",
      "difficulty": 4,
      "id": 22,
      "question": "Hematology is a branch of medicine involving the study of what?"
    },
    {
      "answer": "Scarab",
      "category": "History",
      "difficulty": 4,
      "id": 23,
      "question": "Which dung beetle was worshipped by the ancient Egyptians?"
    },
    {
      "answer": "When the universe was created",
      "category": "Science",
      "difficulty": 3,
      "id": 27,
      "question": "When did the big bang happen"
    },
    {
      "answer": "42",
      "category": "Science",
      "difficulty": 3,
      "id": 28,
      "question": "What is the answer to everything"
    }
  ],
  "success": true,
  "total_questions": 20
}
```

##### `DELETE` `/api/questions/{question_id}`
* General
    * Deletes the question with the given ID.
* Success status code: `200`
* Sample: `curl -X DELETE http://localhost:5000/api/questions/28`
```json
{
  "success": true
}
```

##### `POST` `/api/questions`
* General
    * Creates a new question.
* Entity format
    * Content-Type must be `application/json`
    * Members:
        * `question` The question. Type: `string`.
        * `answer` The answer. Type: `string`.
        * `difficulty` The difficulty of the question. Type: `int`.
        * `category` The ID of the category. Type: `int`.
    * Sample entity:
    ```json
    {
      "question": "What is the answer to everything",
      "answer": "42",
      "difficulty": "3",
      "category": 1
    }
    ```
* Success status code: `201`
* Sample: `curl -X POST -H 'Content-Type: application/json' -d '{"question": "What is the answer to everything", "answer": "42", "difficulty": "3", "category": 1}' http://localhost:5000/api/questions`
```json
{
  "success": true
}
```

##### `POST` `/api/search/questions`
* General
    * Returns the questions matching the search criteria.
* Entity format
    * Content-Type must be `application/json`
    * Members:
        * `searchTerm` The search term. Type: `string`.
    * Sample entity:
    ```json
    {
      "searchTerm": "Artist"
    }
    ```
* Success status code: `200`
* Sample: `curl -X POST -H 'Content-Type: application/json' -d '{"searchTerm": "Artist"}' http://localhost:5000/api/search/questions`
```json
{
  "current_category": null,
  "questions": [
    {
      "answer": "Escher",
      "category": "Art",
      "difficulty": 1,
      "id": 16,
      "question": "Which Dutch graphic artist–initials M C was a creator of optical illusions?"
    },
    {
      "answer": "Jackson Pollock",
      "category": "Art",
      "difficulty": 2,
      "id": 19,
      "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
    }
  ],
  "success": true,
  "total_questions": 2
}
```

##### `GET` `/api/categories/{category_id}/questions`
* General
    * Returns all the questions that have the specified category ID.
* Success status code: `200`
* Sample: `curl http://localhost:5000/api/categories/1/questions`
```json
{
  "current_category": "Science",
  "questions": [
    {
      "answer": "The Liver",
      "category": "Science",
      "difficulty": 4,
      "id": 20,
      "question": "What is the heaviest organ in the human body?"
    },
    {
      "answer": "Blood",
      "category": "Science",
      "difficulty": 4,
      "id": 22,
      "question": "Hematology is a branch of medicine involving the study of what?"
    },
    {
      "answer": "42",
      "category": "Science",
      "difficulty": 3,
      "id": 29,
      "question": "What is the answer to everything"
    }
  ],
  "success": true,
  "total_questions": 3
}
```

##### `POST` `/api/quizzes`
* General
    * Returns a question from the specified category that was not returned previously.
* Entity format
    * Content-Type must be `application/json`
    * Members:
        * `quiz_category` The desired question category name. Type: `string`.
        * `previous_questions` A list of the previously obtained questions. Type: `list<question>`.
    * Sample entity:
    ```json
    {
      "previous_questions": [27],
      "quiz_category": "Science"
    }
    ```
* Success status code: `200`
* Sample: `curl -X POST -H 'Content-Type: application/json' -d '{"previous_questions": [27], "quiz_category": "Science"}' http://localhost:5000/api/search/questions`
```json
{
  "question": {
    "answer": "Alexander Fleming",
    "category": "Science",
    "difficulty": 3,
    "id": 21,
    "question": "Who discovered penicillin?"
  },
  "success": true
}
```
