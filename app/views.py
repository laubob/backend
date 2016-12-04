import MySQLdb
from flask import render_template,g
from app import app

def get_db():
    """Connects to the specific database."""
 #   rv = sqlite3.connect(app.config['DATABASE'])
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = MySQLdb.connect(host='localhost',user='root',passwd='111111',db='monitor_db',charset='utf8')
    return db
	
@app.route('/')
@app.route('/index')
def index():
	db = get_db()
	cur = db.cursor()
	str="select b.*,r.count from branch b join (select left(checkerid,4) as branchid,count(actid) as count from checkresult group by  branchid) r on b.branchid=r.branchid"
	cur.execute(str)
	subs = []
	rows = cur.fetchall()
	for row in rows:
		sub = dict()
		sub['id']=row[0]
		sub['name']=row[1]
		sub['longitude']=row[3]
		sub['latitude']=row[4]
		sub['count']=row[5]
		subs.append(sub)
	cur.close()
	center = { 'longitude': 121.478549,
			   'latitude': 31.232672
	}
	return render_template("index.html",
        center = center,
        subs = subs)

@app.route('/<id>')
def quju(id):
	db = get_db()
	cur = db.cursor()
	cur.execute("select longitude,latitude from branch where branchid='"+id+"'")
	row = cur.fetchone()
	center = dict()
	center['longitude']=row[0]
	center['latitude']=row[1]
	if len(id) < 6:
		str="select b.*,r.count from branch b join (select left(checkerid,6) as branchid,count(actid) as count from checkresult group by  branchid) r where b.branchid=r.branchid and left(b.branchid,4)='"+id+"'";
		cur.execute(str)
		subs = []
		rows = cur.fetchall()
		for row in rows:
			sub = dict()
			sub['id']=row[0]
			sub['name']=row[1]
			sub['longitude']=row[3]
			sub['latitude']=row[4]
			sub['count']=row[5]
			subs.append(sub)
		url = "index.html"
	else:
		str="select r.actid,r.longitude,r.latitude,r.CheckResultQuan,r.checkresultqual,c.checkername,i.checkitemname,o.objname,e.name,e.address from checkresult r,checker c,checktype t,checkitem i,checkobj o,enterprise e where r.checkerid=c.checkerid and r.checktypeid=t.checktypeid and r.itemid=i.itemid and r.objid=o.objid and r.entid=e.id and left(r.checkerid,6)='"+id+"' order by actid desc" ;
		cur.execute(str)
		subs = []
		rows = cur.fetchall()
		for row in rows:
			sub = dict()
			sub['id']=row[0]
			sub['object']=row[7]
			sub['item'] = row[6]
			sub['store']=row[8]
			sub['address']=row[9]
			sub['longitude']=row[1]
			sub['latitude']=row[2]
			sub['qual']=row[4]
			sub['quan']=row[3]
			sub['checker']=row[5]
			subs.append(sub)
		url = "detail.html"
	cur.close()
	return render_template(url,
        center = center,
        subs = subs)

@app.route('/chart1')
def chart1():
	db = get_db()
	cur = db.cursor()
	cur.execute("select c.checkername,r.count from checker c join (select checkerid,count(actid) as count from checkresult group by  checkerid) r where c.checkerid=r.checkerid order by r.count desc")
	datas = []
	
	rows = cur.fetchall()
	for row in rows:
		data = dict()
		data['user']=row[0]
		data['count']=row[1]
		datas.append(data)
	url = "chart1.html"
	cur.close()
	return render_template(url,
		datas = datas)

@app.route('/chart2')
def chart2():
	url = "chart2.html"
	return render_template(url)	
	
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()