from flask import Flask,request,render_template,redirect
from neo4j import GraphDatabase

id="neo4j"
pwd="datta"
driver=GraphDatabase.driver(uri="bolt://localhost:7687",auth=(id,pwd))
session=driver.session()

app=Flask(__name__)

@app.route("/")
def index():
    return render_template("keyword.html")


@app.route("/keyword",methods=["GET","POST"])
def keyword_discovery():
    if request.method=="POST":
        research_topic=request.form["rtopic"]
        limit=request.form["limit"]
        limitval=int(limit)
        #print(research_topic)
        #print(limit)
        order=request.form["order"]
        query="""MATCH (k:keyword) <-[s:RESEARCH_TOPIC] - (a:Author)
                WHERE k.key = $research_topic
                WITH k,a,s 
        RETURN a.name as name,s.score as score, round(s.relevence,2,'CEILING') as relevance limit $limitval"""
        parameter={"research_topic":research_topic,"limitval":limitval,"order":order}
        results=session.run(query,parameter)
        resea=[]
        for result in results:
            #print(dict(results)) 
            #name=result["name"]
            resea.append(result)
        return render_template("keywordoutput.html",list=resea)
    else:
        return render_template("keyword.html")


@app.route("/researcher",methods=["GET","POST"])
def research_profiling():
    if request.method=="POST":
        author_name=request.form["aname"]
        limit=request.form["limit"]
        limitval=int(limit)
        order=request.form.get('order')
        orderval=int(order)
        if orderval==1:
            query=""" MATCH (b:Author) - [l:RESEARCH_TOPIC] -> (k:keyword) <- [r:RESEARCH_TOPIC] - (a:Author)
WHERE a.name= $author_name
WITH b,k,round(l.score,2,'CEILING') as sugg_author_score,
    round(l.relevence,2,'CEILING') as sugg_author_relevence,
    round(r.score,2,'CEILING') as author_score,
    round(r.relevence,2,'CEILING') as author_relevence
WITH collect([b,author_relevence,author_score,sugg_author_relevence,
        sugg_author_score]) as researchers_data, k
UNWIND researchers_data[0..3] AS r
WITH k,(r[0]).name as name, r[3] as sugg_author_relevence, r[4] as
    sugg_author_score, r[1] as author_relevence, r[2] as author_score
RETURN k.key as Topic, name, author_score, author_relevence,
    sugg_author_relevence, sugg_author_score ORDER BY sugg_author_relevence ASC, sugg_author_score ASC limit $limitval
 """
        else:
            query=""" MATCH (b:Author) - [l:RESEARCH_TOPIC] -> (k:keyword) <- [r:RESEARCH_TOPIC] - (a:Author)
WHERE a.name= $author_name
WITH b,k,round(l.score,2,'CEILING') as sugg_author_score,
    round(l.relevence,2,'CEILING') as sugg_author_relevence,
    round(r.score,2,'CEILING') as author_score,
    round(r.relevence,2,'CEILING') as author_relevence
WITH collect([b,author_relevence,author_score,sugg_author_relevence,
        sugg_author_score]) as researchers_data, k
UNWIND researchers_data[0..3] AS r
WITH k,(r[0]).name as name, r[3] as sugg_author_relevence, r[4] as
    sugg_author_score, r[1] as author_relevence, r[2] as author_score
RETURN k.key as Topic, name, author_score, author_relevence,
    sugg_author_relevence, sugg_author_score ORDER BY sugg_author_relevence DESC, sugg_author_score DESC limit $limitval
 """
        parameter={"author_name":author_name,"limitval":limitval,"order":order}
        results=session.run(query,parameter)
        friends=[]
        for result in results:
            #print(dict(results))
            #name=result["name"]
            friends.append(result)
        return render_template("researcheroutput.html",list=friends)
    else:
        return render_template("researcher.html")



@app.route("/influencer",methods=["GET","POST"])
def influencing_author():
    if request.method=="POST":
        research_topic=request.form["rtopic"]
        limit=request.form["limit"]
        limitval=int(limit)
        order=request.form.get('order')
        orderval=int(order)
        if orderval==1:
            query="""MATCH (k:keyword) <- [s:RESEARCH_TOPIC] - (a:Author)
WHERE k.key = $research_topic WITH k,a,s
RETURN a.name as name,round(a.pagerank,2,'CEILING') as pagerank ORDER BY a.pagerank ASC limit $limitval"""
        else:
            query="""MATCH (k:keyword) <- [s:RESEARCH_TOPIC] - (a:Author)
WHERE k.key = $research_topic WITH k,a,s
RETURN a.name as name,round(a.pagerank,2,'CEILING') as pagerank ORDER BY a.pagerank DESC limit $limitval"""
        parameter={"research_topic":research_topic,"limitval":limitval}
        results=session.run(query,parameter)
        values=[]
        for result in results:
            #print(dict(results))
            #name=result["name"]
            values.append(result)
        return render_template("influenceroutput.html",list=values)
    else:
        return render_template("influencer.html")


if __name__ == "__main__":
    app.run(debug=True,port=5000)