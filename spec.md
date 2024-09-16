# **Commonplace: A smarter personal knowledge management system**

We are constantly consuming information from a variety of sources each day. From books, articles, youtube and podcasts. Many of us are bought into the idea of “1% smarter each day” which drives us to take copious notes to compound our knowledge. Today’s tools are great storehouses but lack intelligent features that can augment our knowledge. Breakthroughs in predictive and generative AI however, have paved the way for an AI native application to offer value.

Why do people capture notes? For many reasons but amongst those as a store of ideas to stimulate content creation. Content creators like Maria Popova, Ryan Holiday and David Senra are known to take heaps of notes which underpins the content they generate. 

The market is crowded but very few are focused on differentiating themselves with search features. We know this is valuable because many people are bought into features like Sage AI from Founder’s founder David Senra.

## **Vision**

A home for all the information you are capturing across the web powered by an intelligent search assistant to query and explore your data. We imagine a web and mobile application that is a repository for your notes and information. Baked in will be an AI copilot that can help answer questions based on your personal knowledge base. This will help explore what you already know, reveal gaps, help generate new ideas and insight by making connections between your content.

## **MVP**

To prove this idea, the MVP will focus only on kindle notes. It will be a highlight and notes viewer powered by AI search. The AI search will be a premium feature and adoption will be proof that it is a desirable feature. 

Why kindle?

* There is a passionate community of users who read non-fiction on e-books and already use websites like Readwise and Clippings.io. However, these websites do not offer AI features that can significantly lift the experience and value to the user.

We could start in other places like articles, but people tend to engage less with the articles they are reading. 

### **MPV Spec**

MVP Features. Goal is to get something out in 2-3 weeks. Any longer is a waste of time\! 

- [ ] A user can create a profile and login with social login  
- [ ] A user can import Kindle highlights from clippings text file and from read website in one-click. (The website is the best source of highlights)  
- [ ] A user can refresh their highlights to pull in the latest   
- [ ] A user can view all their book highlights   
- [ ] A user can share their highlights to twitter (shared with …)   
- [ ] A user should be able to modify their notes to avoid pollution. Delete and edit text.  
- [ ] A user should be able to tag their notes.  
- [ ] A user can search their note repository using natural language and have a conversation with their notes using natural language.  
- [ ] A user can see the history of their conversations.

Spec out the search and chat feature.  
Model it after perplexity. You should be able to ask questions and search over all your notes. Check perplexica.ai. See open source. 

- [ ] Basic keyword search for free tier  
- [ ] A user should be able to search their notes with standard text based search (no. We just accept that if the user types in some crap then they get some random results back??)  
- [ ] A user should be able to have a conversation with their notes  
- [ ] A user should be able to perform a smart search and ask a question and receive information including sources where that information has been pulled from  
- [ ] A user should see this information relatively quickly \< 1s  
- [ ] A user should be able to ask follow up conversations which retain context  
- [ ] Results should not hallucinate by providing details outside of book not~~e~~s  
      - [ ] (Try to ground but don’t go overboard)  
- [ ] A user should never see information from other people’s notes  
- [ ] Add source to collect feedback e.g. thumbs up / down

What about normal search? How would this work well?

### **MVP Implementation design**

We will need the following tables to implement this

* User: Stores user credentials  
  * ID: UUID  
  * Email: string (social / otherwise)  
  * Password: (depends on login)  
  * Last logged in: string?  
  * created\_at: timestamp (when account was created)  
  * pricing\_plan: string  
* Usage: Event store to track information  
  * Event ID  
  * Timestamp  
  * User ID  
  * Login  
* Books: Source of books with curated metadata  
  * ID: UUID  
  * Book Title: string  
  * Book ISBN: string  
  * First Author: string  
  * Authors: list\[string\]  
  * thumbnail\_url: string  
  * publish\_date: Optional\[timestamp\]  
  * created\_at: timestamp  
* Book Annotations: Place to store all book (kindle) annotations for a user. Could be any book from other sources as well.  
  * Annotation ID: UUID  
  * Content ID  
  * Book ID: UUID  
  * User ID: UUID  
  * Original Text: string  
  * Edited Text: string  
  * Tags: \[List str\]  
  * Annotation Type: string  
  * Location: string  
  * Share\_count: number (number of times social shared)  
  * Created\_at: timestamp  
* Tags  
  * tag\_id SERIAL PRIMARY KEY,  
  * user\_id INTEGER REFERENCES users(user\_id),  
  * name VARCHAR(50) NOT NULL,  
  * created\_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT\_TIMESTAMP,  
  * UNIQUE(user\_id, name) (tag unique for each user but not unique for all users)  
* Embeddings Store: A place to store all embeddings related to text. Text should be chunked by a processing pipeline for better performance.  
  * Embedding ID  
  * Original Source ID (should map to annotation ID or whatever other table is used\!)  
  * chunking strategy: str  
  * Embedding: Vector  
  * created\_at: timestamp  
* Content tableL potential for   
  * content\_item\_id SERIAL PRIMARY KEY,  
  * user\_id INTEGER REFERENCES users(user\_id),  
  * content\_type VARCHAR(50) NOT NULL,  
  * created\_at TIMESTAMP WITH TIME ZONE DEFAULT\_CURRENT\_TIMESTAMP,  
  * updated\_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT\_TIMESTAMP  
* Conversations   
  * conversation\_id SERIAL PRIMARY KEY,  
  * user\_id INTEGER REFERENCES users(user\_id),  
  * title VARCHAR(255),  
  * created\_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT\_TIMESTAMP,  
  * updated\_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT\_TIMESTAMP  
* Messages  
  * message\_id SERIAL PRIMARY KEY,  
  * conversation\_id INTEGER REFERENCES conversations(conversation\_id),  
  * content TEXT NOT NULL,  
  * is\_user\_message BOOLEAN NOT NULL,  
  * created\_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT\_TIMESTAMP

Pre-populating data

* Take the 10k most popular books across various categories and add their metadata to the book table  
* Embeddings should be created on import (see question below)

Workflows / Pipelines

1. Create login  
2. Import annotations  
   1. When empty should just be option to import content  
3. Initial embedding workflow  
   1. This should happen as a background task and when it does  
   2. This can be polled by frontend  
4. Index pipeline  
   1. Takes a new text item, chunks it, creates an embedding and adds it to the vector store  
5. Search  
   1. Take query \+ relevant historical context   
   2. Classify query?   
   3. Runs query through constructor to extract question / query and metadata e.g. book title, book author etc  
   4. Embed query  
   5. Perform similarity search of vector store filtering for metadata  
   6. Return top most results  
   7. Generate output with sources

**Backend API**  
Design of the backend APi will depend on what we want to do on the frontend\!

* Login:   
  * Input:  
    * Creds  
  * Returns   
    * session token  
* Import from file  
  * Input  
    * Filename  
  * Output  
    * Success  
* Import from kindle (requires going to kindle and signing in).   
  * Input  
    * ? Copy from readwise  
  * Output  
    * Success  
* Fetch books  
  * All  
  * By title  
  * By author  
* Fetch annotations  
  * By tag  
* Keyword search: based on user tier \+ input  
  * query  
* Intelligent search: based on user tier \+ input  
  * Query

### **AI Features**

* Will start with Postgres vector for the vector store  
* We need a service for embeddings to perform RAG. We cannot afford to have multiple embeddings at this stage. We need a system that can do question answering very well as we expect our users to ask questions in copilot style. Multiple options for embedding model.  
  * Start with Ada? Alex recommended [https://www.voyageai.com/](https://www.voyageai.com/)  
* Use Claude as output language model

Fall back?

* How will chat scale to multiple people?  
  * Need to at least make it work with 100 people.

* Some dumb algorithm?  
* What if service is down?  
  * Can’t provide chat then.  
* Can I afford this as an MVP?

Feedback

* How can I start to build my own repository of user data?  
  * 

### **MVP Testing**

* Test fully yourself  
* Get an alpha set of 5-10 users to see if they would be willing to pay. Use your own API  
  * How frequently does someone use it?

### **Questions**

* Do you create embeddings for a user if they are not on a paid pricing plan? Probably a waste of money. (How much does something like that cost?) But if offering a free trial for search then you need to index their stuff.   
* How to handle different languages?  
  * Just english for now  
  * Whatever is free from model  
* ~~Do I need GDPR? (it’s just an MVP. No\!)~~ 

### **Pricing** 

* Free tier  
  * Import all notes  
  * View all notes  
  * Edit notes  
  * Basic keyword search  
  * Share notes

* Pro tier  
  * Export notes to other formats  
  * AI-powered search

### **Post-MVP**

* New content types.  
  * Articles?  
  * YT?  
  * Podcasts?  
* Themes  
  * User can explore themes

## **Distribution**

* Recurse  
* Twitter  
* David Senra Followers  
* Readwise accounts

Use NotebookLM as a guide