import MySQLdb


def connection():
	
	conn =  MySQLdb.connect(host="localhost",
							 user = "root",
							 passwd = "password",
							 db = "debts")
	c = conn.cursor()
	return c, conn