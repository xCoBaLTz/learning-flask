import cgi
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from restaurant_setup import Base, Restaurant
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///restaurants.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>List of Restaurants</h1>"
                output += "<h2><a href='/restaurants/new'>Make a new Restaurant</a></h2></br>"
                restaurants = session.query(Restaurant).all()
                for res in restaurants:
                    output += "<h2>" + res.name + "</h2>"
                    output += "<a href='restaurants/%s/edit'>Edit</a><br>" % res.id
                    output += "<a href='restaurants/%s/delete'>Delete</a>" % res.id
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = "<html><body>"
                output += "<h1>Make a new Restaurant<h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action="/restaurants/new"><input name="message" type="text" placeholder="New Restaurant Name"><input type="submit" value="Create"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/edit"):
                resID = self.path.split("/")[2]
                myResQuery = session.query(Restaurant).filter_by(id=resID).one()
                if myResQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = "<html><body><h1>"
                    output += myResQuery.name
                    output += "</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>" % resID
                    output += "<input name='newResName' type='text' placeholder='%s'>" % myResQuery.name
                    output += "<input type='submit' value='Rename'></form></body></html>"
                    self.wfile.write(output)

            if self.path.endswith("/delete"):
                resID = self.path.split("/")[2]
                myResQuery = session.query(Restaurant).filter_by(id=resID).one()
                if myResQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = "<html><body><h1>"
                    output += "Are you sure you want to delete %s?" % myResQuery.name
                    output += "</h1>"
                    output += "<form method='POST' action='/restaurants/%s/delete'>" % resID
                    output += "<input type='submit' value='Delete'></form></body></html>"
                    self.wfile.write(output)
                    
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('message')
                    res = Restaurant(name = messagecontent[0])
                    session.add(res)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newResName')
                    resID = self.path.split("/")[2]
                    myResQuery = session.query(Restaurant).filter_by(id=resID).one()
                    if myResQuery != []:
                        myResQuery.name = messagecontent[0]
                        session.add(myResQuery)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()

            if self.path.endswith("/delete"):
                resID = self.path.split("/")[2]
                myResQuery = session.query(Restaurant).filter_by(id=resID).one()
                if myResQuery != []:
                    session.delete(myResQuery)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
        except:
            pass

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()
